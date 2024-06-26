import time
from alive_progress import alive_bar
from multiprocessing import Pool
from config import db_path, sr_path
from config import PREPARE_DEBUG
from config import sink_total_num
from data_module.db_access import *
from .graph_class import *


def get_graph_dict(proj, fid_set):
    ast = load_from_pickle(f"{db_path}/{proj}/ast_edge_dict.db")
    cdg = load_from_pickle(f"{db_path}/{proj}/cdg_edge_dict.db")
    ddg = load_from_pickle(f"{db_path}/{proj}/ddg_edge_dict.db")
    node_dict = load_from_pickle(f"{db_path}/{proj}/node_dict.db")
    graph_dict = {
        fid: GraphDB(proj, fid, ast[fid], cdg[fid], ddg[fid], node_dict)
        for fid in fid_set
    }
    dump_to_pickle(graph_dict, f"{db_path}/{proj}/graph_dict.db",)
    type_list = ["AU", "PU", "AE", "FC", "NPD", "PT", "DZ", "AS", "FR"]
    # {fid: {tp: [...]}}
    sinkcode = {}
    for fid in fid_set:
        sinkcode[fid] = {}
        for tp in type_list:
            sinkcode[fid][tp] = graph_dict[fid].sinkcode_dict[tp]
    dump_to_json(sinkcode, f"{sr_path}/{proj}/sink_code.json")
    dump_to_pickle(sinkcode, f"{sr_path}/{proj}/sink_code.db")

    dump_to_pickle(node_dict, f"{db_path}/{proj}/node_dict.db")

    if PREPARE_DEBUG:
        dump_to_json(node_dict, f"{db_path}/{proj}/node_dict_modified_astpatch.json")


def generate():
    start = time.perf_counter()
    print("Preparing for slicing...")
    proj_dict = load_from_pickle(f"{db_path}/proj_dict.db")
    with open("log.txt","a") as l:
        l.write("开始搜索sink点\n")
    with alive_bar(len(proj_dict)) as bar:
        bar.title = f"{'Preparing for slicing':^30}"
        if PREPARE_DEBUG:
            for proj, fid_set in proj_dict.items():
                get_graph_dict(proj, fid_set)
                bar()
        else:
            with Pool() as p:
                for proj, fid_set in proj_dict.items():
                    p.apply_async(
                        get_graph_dict,
                        (proj, fid_set),
                        callback=lambda x: bar(),
                    )
                p.close()
                p.join()
    with open("log.txt","a") as l:      # 输出所有项目的总sink数以及各个sink类型的总数
        #l.write("\tALL project\n")
        #for tp,value in sink_total_num.items(): # 已经转移到其他位置输出
        #    l.write(f"\t\t{tp}\t\t{value}\n")
        l.write("搜索结束\n\n")
    print(f"Done, used {time.perf_counter() - start:<.2f}s\n")
