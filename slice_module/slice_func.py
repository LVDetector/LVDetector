from copy import copy
from config import fslice_depth, bslice_depth
from config import BSLICE_CALL


def get_fixed_list(fid, node_list, node_dict, graph_dict):

    # print([(node, node_dict[node]["code"]) for node in node_list])

    tmp_node_list = []
    all_node_set = set()
    for node in reversed(node_list):
        if node not in all_node_set:
            all_node_set.add(node)
            tmp_node_list.append(node)

    node_list = []
    tmp_node_set = set()
    del_node_set = set()
    for node in reversed(tmp_node_list):

        # print(node, graph_dict[fid].ast.get_sub_ast(node, node_dict))

        for v in graph_dict[fid].ast.get_sub_ast(node, node_dict):
            if node_dict[v]["_label"] == "IDENTIFIER":
                r = node_dict[v]["refto"]
                if r != "LOST" and r not in all_node_set:
                    node_list.append(r)
                    all_node_set.add(r)

                    del_node_set.add(r) if r in tmp_node_set else tmp_node_set.add(r)

            del_node_set.add(v) if v in tmp_node_set else tmp_node_set.add(v)

        fa = graph_dict[fid].ast.fa_dict[node]
        fa_is_ctrl_statement = (
            fa is not None
            and node_dict[fa]["_label"] == "CONTROL_STRUCTURE"
            and node_dict[fa]["controlStructureType"]
            in ("IF", "FOR", "WHILE", "SWITCH")
        )

        if fa_is_ctrl_statement and fa not in all_node_set:
            node_list.append(fa)
            all_node_set.add(fa)

            # print("for", fa, graph_dict[fid].ast.get_sub_ast(fa, node_dict))

            [
                del_node_set.add(v) if v in tmp_node_set else tmp_node_set.add(v)
                for v in graph_dict[fid].ast.get_sub_ast(fa, node_dict)
            ]

        node_list.append(node)

    return [
        (p, p not in del_node_set and node_dict[p]["_label"] != "METHOD_RETURN")
        for p in node_list
        if p not in del_node_set
        or node_dict[p]["_label"] == "CALL"
        and node_dict[p]["callto"] != "EXTN"
    ]


def get_fslice_result(
    fid,
    src,
    node_dict,
    graph_dict,
    fslice_depth,
    visited_callee,
):
    slice_result = []
    if not fslice_depth:
        return slice_result

    current_result = get_fixed_list(
        fid,
        graph_dict[fid].get_fslice_data(src, node_dict),
        node_dict,
        graph_dict,
    )

    for t in current_result:
        v = t[0]
        if (
            node_dict[v]["_label"] == "CALL"
            and node_dict[v]["callto"] != "EXTN"
            and v not in visited_callee
        ):
            cfid = node_dict[v]["callto"]
            """可以实现基于函数调用参数的出发点的筛选"""
            visited_callee.add(v)
            slice_result.extend(
                get_fslice_result(
                    cfid,
                    [cfid],
                    node_dict,
                    graph_dict,
                    fslice_depth - 1,
                    visited_callee,
                )
            )
        slice_result.append(t)

    return slice_result


def get_bfslice_result(
    fid,
    src,
    node_dict,
    graph_dict,
    callin_dict,
    bslice_depth,
    fslice_depth,
    slice_result,
    current_result,
    visited_callee,
):
    if not bslice_depth:
        slice_result.append(current_result)
        return

    current_visited_callee = copy(visited_callee)

    slice_data = get_fixed_list(
        fid,
        # graph_dict[fid].get_bslice_data(src, node_dict)
        # + graph_dict[fid].get_fslice_data(src, node_dict),
        graph_dict[fid].get_bslice_data(src, node_dict),
        node_dict,
        graph_dict,
    )

    flag = BSLICE_CALL
    tmp = current_result
    current_result = []

    for v, p in slice_data:
        if v == src[0]:
            """这里假定 src 只有一个节点，如果有多个则需要修改"""
            current_result.extend(tmp)
            flag = True
        elif (
            flag
            and node_dict[v]["_label"] == "CALL"
            and node_dict[v]["callto"] != "EXTN"
            and v not in visited_callee
        ):
            cfid = node_dict[v]["callto"]
            """可以实现基于函数调用参数的出发点的筛选"""
            visited_callee.add(v)
            # current_result.extend(
            #     get_fslice_result(
            #         cfid,
            #         [cfid],
            #         node_dict,
            #         graph_dict,
            #         fslice_depth - 1,
            #         visited_callee,
            #     )
            # )
        current_result.append((v, p))

    flag = False

    for cfid, cid_list in callin_dict[fid].items():
        for cid in cid_list:
            if cid not in visited_callee:
                visited_callee.add(cid)
                get_bfslice_result(
                    cfid,
                    [cid],
                    node_dict,
                    graph_dict,
                    callin_dict,
                    bslice_depth - 1,
                    fslice_depth - 1,
                    slice_result,
                    current_result,
                    visited_callee,
                )
                visited_callee = copy(current_visited_callee)
                flag = True
    if not flag:
        slice_result.append(current_result)


def get_slice_result(
    fid,
    src,
    node_dict,
    graph_dict,
    callin_dict,
    bslice_depth,
    fslice_depth,
):
    slice_result = []
    get_bfslice_result(
        fid,
        src,
        node_dict,
        graph_dict,
        callin_dict,
        bslice_depth,
        fslice_depth,
        slice_result,
        list(),
        set(),
    )
    # print(fid, src, [node_dict[v]["code"] for v in src], slice_result)
    return slice_result


def get_all_slice_result(
    fid,
    node_dict,
    graph_dict,
    callin_dict,
):
    return {
        src[0]: get_slice_result(
            fid,
            src,
            node_dict,
            graph_dict,
            callin_dict,
            bslice_depth,
            fslice_depth,
        )
        for src in graph_dict[fid].src_list
    }
