import os, shelve
from multiprocessing import Pool
from typing import Callable, Set, Union
from config import pr_path, db_path, sr_path
from config import RECTIFY_DEBUG
from data_module.db_access import *
from alive_progress import alive_bar


def rectify_out1():
    data = dict()
    rdata = load_from_json(f"{pr_path}/out1.json")
    for d in rdata:
        for k, v in d.items():
            data.setdefault(k, set()).add(v)

    for target in (db_path, sr_path):
        [os.makedirs(f"{target}/{proj}") for proj in data]

    # 大多数的 bug 都是因为一个 proj 里有多个 func 导致的，因此直接将这些不好的样本删去
    for k, v in data.copy().items():
        if len(v) != 1:
            data.pop(k)

    dump_to_pickle(data, f"{db_path}/proj_dict.db")

    if RECTIFY_DEBUG:
        data = {k: list(v) for k, v in data.items()}
        dump_to_json(data, f"{db_path}/proj_dict.json")


def p_classify_func_x(proj: str, fid_set: Set[str], obj: str) -> None:
    with shelve.open(f"{db_path}/{obj}.db", flag="r") as db:
        dump_to_pickle(
            {fid: db.get(fid, {}) for fid in fid_set},
            f"{db_path}/{proj}/{obj}.db",
        )


def classify_dispatch(obj: str, p_func: Callable, title: str) -> None:
    proj_dict = load_from_pickle(f"{db_path}/proj_dict.db")
    with alive_bar(len(proj_dict)) as bar:
        bar.title = title
        if RECTIFY_DEBUG:
            for proj, fid_set in proj_dict.items():
                p_func(proj, fid_set, obj)
                bar()
        else:
            with Pool() as p:
                for proj, fid_set in proj_dict.items():
                    p.apply_async(
                        p_func,
                        (proj, fid_set, obj),
                        callback=lambda x: bar(),
                    )
                p.close()
                p.join()


def rectify_out2() -> None:
    data = {}
    rdata = load_from_json(f"{pr_path}/out2a.json")
    for d in rdata:
        for p, obj_list in d.items():
            for obj in obj_list:
                data.setdefault(p, {}).setdefault(str(obj["id"]), obj)

    rdata = load_from_json(f"{pr_path}/out2b.json")
    for d in rdata:
        for p, obj in d.items():
            data.setdefault(p, {}).setdefault(str(obj["id"]), obj)

    proj_dict = load_from_pickle(f"{db_path}/proj_dict.db")
    [dump_to_pickle(data[proj], f"{db_path}/{proj}/node_dict.db") for proj in proj_dict]

    dump_to_pickle(data.get("<includes>", {}), f"{db_path}/shared_node_dict.db")

    if RECTIFY_DEBUG:
        dump_to_json(data, f"{db_path}/node_dict.json")


def modify_dispatch(obj: str, p_func: Callable, tag: Union[str, bool], title) -> None:
    proj_dict = load_from_pickle(f"{db_path}/proj_dict.db")
    with alive_bar(len(proj_dict)) as bar:
        bar.title = title
        if RECTIFY_DEBUG:
            for proj, fid_set in proj_dict.items():
                p_func(proj, obj, tag)
                bar()
        else:
            with Pool() as p:
                for proj, fid_set in proj_dict.items():
                    p.apply_async(
                        p_func,
                        (proj, obj, tag),
                        callback=lambda x: bar(),
                    )
                p.close()
                p.join()


def p_modify_func_x(proj: str, obj: str, tag: str) -> None:
    ch_dict = load_from_pickle(f"{db_path}/{proj}/{obj}.db")
    node_dict = load_from_pickle(f"{db_path}/{proj}/node_dict.db")

    for fid in ch_dict:
        for id, t in ch_dict[fid].items():
            node_dict[id][tag] = t
            if isinstance(t, str) and t.isdigit():
                node = get_node(t, node_dict)
                node_dict[t] = node

    dump_to_pickle(node_dict, f"{db_path}/{proj}/node_dict.db")


def rectify_out3() -> None:
    rdata = load_from_json(f"{pr_path}/out3.json")

    def get_info(fid: str, s: str) -> Dict:
        edge_dict = {}
        inpdg_dict.setdefault(fid, {})
        for t in s.splitlines():    # t的样例：\"240\" -> \"242\"  [ label = \"DDG: &lt;RET&gt;\"]  ，，，   \"131\" -> \"132\" 
            l = t.split('"', 4)     # 将t分成至多5个部分，以"为分界线
            if len(l) >= 5 and (tag == "AST" or  tag + ":" in l[4]):       # 解决当1为空列表时的BUG
                edge_dict.setdefault(l[1], set()).add(l[3])
                inpdg_dict[fid][l[1]] = inpdg_dict[fid][l[3]] = pdg
        return edge_dict

    inpdg_dict = {}
    for graph, tag, pdg in [
        ("ast_edge_dict", "AST", False),
        ("cdg_edge_dict", "CDG", True),
        ("ddg_edge_dict", "DDG", True),
    ]:
        data = {fid: get_info(fid, d[fid][pdg]) for d in rdata for fid in d}

        dump_to_shelve(data, f"{db_path}/{graph}.db")
        classify_dispatch(
            graph,
            p_classify_func_x,
            f"{'Classifying ' + tag + ' dot file':^30}",
        )

        if RECTIFY_DEBUG:
            data = {k1: {k2: list(v2) for k2, v2 in data[k1].items()} for k1 in data}
            dump_to_json(data, f"{db_path}/{graph}.json")

    dump_to_shelve(inpdg_dict, f"{db_path}/inpdg_dict.db")
    classify_dispatch(
        "inpdg_dict",
        p_classify_func_x,
        f"{'Classifying inpdg_dict':^30}",
    )
    modify_dispatch(
        "inpdg_dict",
        p_modify_func_x,
        "inpdg",
        f"{'Modifying inpdg info':^30}",
    )
    if RECTIFY_DEBUG:
        dump_to_json(inpdg_dict, f"{db_path}/inpdg_dict.json")

        proj_dict = load_from_pickle(f"{db_path}/proj_dict.db")
        for proj in proj_dict:
            dump_to_json(
                load_from_pickle(f"{db_path}/{proj}/node_dict.db"),
                f"{db_path}/{proj}/node_dict_modified_inpdg.json",
            )


def rectify_out4() -> None:
    rdata = load_from_json(f"{pr_path}/out4.json")
    data = {k: d[k] for d in rdata for k in d}

    dump_to_shelve(data, f"{db_path}/callee_dict.db")
    classify_dispatch(
        "callee_dict",
        p_classify_func_x,
        f"{'Classifying callee_dict':^30}",
    )
    modify_dispatch(
        "callee_dict",
        p_modify_func_x,
        "callto",
        f"{'Modifying callto info':^30}",
    )
    if RECTIFY_DEBUG:
        dump_to_json(data, f"{db_path}/callee_dict.json")

    rdata = {}
    for fid in data:
        for cid, tid in data[fid].items():
            if tid != "EXTN":
                rdata.setdefault(tid, {}).setdefault(fid, set()).add(cid)

    dump_to_shelve(rdata, f"{db_path}/callin_dict.db")
    classify_dispatch(
        "callin_dict",
        p_classify_func_x,
        f"{'Classifying callin_dict':^30}",
    )
    if RECTIFY_DEBUG:
        data = {k1: {k2: list(v2) for k2, v2 in rdata[k1].items()} for k1 in rdata}
        dump_to_json(data, f"{db_path}/callin_dict.json")

        proj_dict = load_from_pickle(f"{db_path}/proj_dict.db")
        for proj in proj_dict:
            dump_to_json(
                load_from_pickle(f"{db_path}/{proj}/node_dict.db"),
                f"{db_path}/{proj}/node_dict_modified_callto.json",
            )


def rectify_out5() -> None:
    data = {}
    rdata = load_from_json(f"{pr_path}/out5.json")
    for fid, iid, lid in rdata:
        data.setdefault(fid, {}).setdefault(iid, lid)

    dump_to_shelve(data, f"{db_path}/ref_dict.db")
    classify_dispatch(
        "ref_dict",
        p_classify_func_x,
        f"{'Classifying ref_dict':^30}",
    )
    modify_dispatch(
        "ref_dict",
        p_modify_func_x,
        "refto",
        f"{'Modifying refto info':^30}",
    )
    if RECTIFY_DEBUG:
        dump_to_json(data, f"{db_path}/ref_dict.json")

        proj_dict = load_from_pickle(f"{db_path}/proj_dict.db")
        for proj in proj_dict:
            dump_to_json(
                load_from_pickle(f"{db_path}/{proj}/node_dict.db"),
                f"{db_path}/{proj}/node_dict_modified_refto.json",
            )
