import heapq, bisect, re, queue
from typing import Dict
from config import db_path, sr_path
from config import PREPARE_DEBUG, SLICE_ALL
from config import FDG_CTRL, BSLICE_TOPO, FSLICE_TOPO
from config import sink_total_num
from config import proj_num, top10_software_proj, top10_software_vulnerable_proj
from igraph import *
from data_module.method_set import *

from data_module.db_access import dump_to_json, dump_to_pickle
from .graph_patch import ast_patcher
from syvc_module import syvc_matcher


def get_edge_set(edge_dict_list, *, reverse=False):
    edge_set = set()
    for edge_dict in edge_dict_list:
        for source, t_list in edge_dict.items():
            [
                edge_set.add((target, source) if reverse else (source, target))
                for target in t_list
                if source != target
            ]
    return edge_set


class AST:
    def get_sub_ast(self, node, node_dict, blk_flag=False, *, fa=None):
        if not blk_flag and (
            node_dict[node]["_label"] == "BLOCK"
            or (
                fa is not None
                and node_dict[fa]["_label"] == "CONTROL_STRUCTURE"
                and node_dict[node]["order"] == len(self.edge_dict[fa])
            )
        ):
            return []

        sub_ast = [node]
        for ch in self.edge_dict.get(node, []):
            sub_ast.extend(self.get_sub_ast(ch, node_dict, blk_flag, fa=node))
        return sub_ast
    
    def get_leaves(self, node_):
        """获取叶子节点"""
        q = queue.Queue()
        leaves = []
        q.put(node_)
        while not q.empty():
            node = q.get()
            subs = self.edge_dict.get(node, [])
            for i in subs:
                q.put(i)
            if len(subs) == 0:
                leaves.append(node)
        return leaves

    def get_operator_separated_leaves(self, node_, node_dict):
        """获取按照运算符分割的变量叶子节点：叶子节点不包括常量，a[i], a->b, a.b三类需单独考虑"""
        leaves = [node_]
        pre_leaves = []
        tmp_container = []
        custom_function_flag = c_function_flag = False
        bad_func_flag = False
        key_words = ['unref', 'destroy', 'free', 'clear', 'destruct',"close", "release", "delete", "realloc", "unregister", "clean"]
        while pre_leaves != leaves:
            pre_leaves = leaves.copy()
            for node in pre_leaves:
                obj = node_dict[node]
                if obj['_label'] == 'CALL':
                    subs = self.edge_dict.get(node, [])
                    if obj['methodFullName'] in ternary_operators | {'<operator>.cast'}:
                        subs = subs[1:]
                    if obj['methodFullName'] in {'<operator>.indirectFieldAccess', '<operator>.fieldAccess'}:
                        # a->b，为 a->b, a；同理 a.b 为 a.b和a
                        subs = subs[:1]
                    if (obj['methodFullName'] in 
                        unary_operators |
                        binary_operators |
                        ternary_operators |
                        access_operators |
                        {'<operator>.cast'}
                    ):
                        leaves.remove(node)
                        if obj['methodFullName'] != "<operator>.sizeOf":
                            leaves.extend(
                                sub for sub in subs
                                if sub not in leaves
                                and not isConstant(node_dict[sub])
                            )
                        if obj['methodFullName'] in {'<operator>.indirectFieldAccess', '<operator>.fieldAccess'}:
                            tmp_container.append(node)
                    if 'operator' not in obj['methodFullName']:     # operator 和 operators 都有可能
                        # 函数调用类型的，还是要将其参数放进去。不然 FC 等类型的关键变量就为空了。
                        leaves.extend(
                            sub for sub in subs
                            if sub not in leaves
                            and not isConstant(node_dict[sub])
                        )
                        for key in key_words:
                            match = re.search(key, obj['methodFullName'], re.IGNORECASE)
                            if bool(match):
                                bad_func_flag = True
                        if bad_func_flag == False:
                            if obj['methodFullName'] in cfuns:
                                c_function_flag = True
                            else:
                                custom_function_flag = True
                        leaves.remove(node)
                elif obj['_label'] == 'BLOCK':    # 块 {...} ，不好分析，也删去
                    leaves.remove(node)
                elif isConstant(obj):
                    leaves.remove(node)
        leaves.extend(i for i in tmp_container if i not in leaves)
        leaves = list(set(leaves))  # 再进行一次去重，因为可能有多个同时加入
        return leaves, bad_func_flag, custom_function_flag, c_function_flag

    def get_slice_src(
        self,
        node: str,
        node_dict: Dict[str, Dict[str, str]],
        sinkcode_dict: Dict[str, list[list]],
        pdg_node,
        def_flag,
        ae_flag,
    ):
        def solve_sub(node_) -> list:
            """内部函数：若关键变量是直接子节点，则将其按算术、逻辑、比较、单目分解，并去除其中的常量，再作为关键变量"""
            leaves, _, _, _ = self.get_operator_separated_leaves(node_, node_dict)
            return [node_dict[i]['code'] for i in leaves]
            
        def solve_dict(
            obj, 
            sinkcode_dict: Dict[str, list[list]],
            pdg_node: str,
            keyVar: list | str,
            tp: str
        ):
            """内部函数：去重（保留最后一个）与增加节点"""
            if (pdg_node == None or keyVar == []):  # 关键变量列表为空的，不视为 sink 点
                return
            for index, sub_node in enumerate(sinkcode_dict[tp].copy()):
                if keyVar == sub_node[-1]:                # 若关键变量出现过，移除它
                    sinkcode_dict[tp].pop(index)
                    break
            if 'lineNumber' in obj:         # 如果有行号信息，加入行号信息；否则行号为0
                sinkcode_dict[tp].append([pdg_node, obj['id'], obj['lineNumber'], obj['code'], keyVar])
            else:
                sinkcode_dict[tp].append([pdg_node, obj['id'], 0, obj['code'], keyVar])

        if node_dict[node]["inpdg"]:
            pdg_node = node

        asgn_flag = (
            pdg_node == node
            and node_dict[node]["_label"] == "CALL"
            and "<operator>.assignment" in node_dict[node]["methodFullName"]
        )

        ae_flag &= not asgn_flag

        obj = node_dict[node]
        sub = self.edge_dict.get(node, [])      # 直接相连的子节点

        if syvc_matcher.fc_matcher(node, node_dict):
            # 风险函数类型：关键变量是函数参数，即直接子节点
            keyVar = solve_sub(node)
            solve_dict(obj, sinkcode_dict, pdg_node, keyVar, 'FC')

        if syvc_matcher.array_matcher(node, node_dict, self):
            # 数组越界类型：关键变量是数组名和索引，即直接子节点
            keyVar = solve_sub(node)
            solve_dict(obj, sinkcode_dict, pdg_node, keyVar, 'AU')

        if syvc_matcher.pointer_matcher(node, node_dict, self):
            # 指针越界类型：关键变量为所有直接子节点的代码
            keyVar = solve_sub(node)
            solve_dict(obj, sinkcode_dict, pdg_node, keyVar, 'PU')

        if syvc_matcher.integerOverflow(node, node_dict, ae_flag, self):
            # 整数溢出：关键变量为最左侧的操作数（学姐认为两个操作数都考虑，感觉两种想法都可以）
            keyVar = solve_sub(node)
            solve_dict(obj, sinkcode_dict, pdg_node, keyVar, 'AE')
        
        if syvc_matcher.NPD_matcher(node, node_dict):
            # 空指针解引用：关键变量为去除最后一个 -> 后的变量
            keyVar = solve_sub(sub[0])
            solve_dict(obj, sinkcode_dict, pdg_node, keyVar, 'NPD')

        if syvc_matcher.pathTraversal_matcher(node, node_dict, self):
            # 路径穿越：关键变量为函数参数
            keyVar = solve_sub(node)
            solve_dict(obj, sinkcode_dict, pdg_node, keyVar, 'PT')

        if syvc_matcher.divideByZero_matcher(node, node_dict, self):
            # 除以0：关键变量是分母（最后一个元素）
            keyVar = solve_sub(sub[-1])
            solve_dict(obj, sinkcode_dict, pdg_node, keyVar, 'DZ')
            
        if syvc_matcher.assert_matcher(node, node_dict, self):
            # 断言：关键变量为函数参数
            keyVar = solve_sub(node)
            solve_dict(obj, sinkcode_dict, pdg_node, keyVar, 'AS')

        if syvc_matcher.free_matcher(node, node_dict, self):
            # 释放：关键变量为函数参数
            keyVar = solve_sub(node)
            solve_dict(obj, sinkcode_dict, pdg_node, keyVar, 'FR')
        
        if SLICE_ALL:       # 若配置为SLICE_ALL，则增加所有；否则在GraphDB的init中将上面的所有合并到ALL中
            if 'lineNumber' in obj:         # 如果有行号信息，加入行号信息；否则行号为0
                sinkcode_dict["ALL"].append([pdg_node, obj['id'], obj['lineNumber'], obj['code'], ''])
            else:
                sinkcode_dict["ALL"].append([pdg_node, obj['id'], 0, obj['code'], ''])
        
        for ch in self.edge_dict.get(node, []):
            def_flag = node_dict[ch]["order"] == 1 if asgn_flag else def_flag
            self.get_slice_src(ch, node_dict, sinkcode_dict, pdg_node, def_flag, ae_flag)

    def __init__(self, proj, fid, edge_dict_list, node_dict):
        self.fid = fid
        self.proj = proj
        self.edge_dict = {}
        [
            self.edge_dict.setdefault(a, []).append(b)
            for a, b in get_edge_set(edge_dict_list)
        ]
        [
            self.edge_dict[v].sort(key=lambda x: node_dict[x]["order"])
            for v in self.edge_dict
        ]

        ast_patcher.patch_main(self, node_dict)
        self.fa_dict = {v: f for f in self.edge_dict for v in self.edge_dict[f]}
        self.fa_dict[fid] = None

        if PREPARE_DEBUG:
            dump_to_json(self.edge_dict, f"{db_path}/{proj}/ast_{fid}.json")


class XDG:
    def slice(self, src, node_dict):
        pq = [(self.topo_rank[v], v) for v in src]
        heapq.heapify(pq)

        visited_node_set = set(src)
        no_dfs_node_set = set()
        slice_list = []

        last_v = pq[0][1]

        while pq:
            node = heapq.heappop(pq)[1]
            to_list = self.edge_dict.get(node, [])
            slice_list.append(node)
            if node not in no_dfs_node_set:
                if (node,) in self.slice_data:
                    v_list = self.slice_data[(node,)]
                    v_list = v_list[
                        bisect.bisect(
                            v_list,
                            last_v,
                            key=lambda x: self.topo_rank[x],
                        ) :
                    ]
                    for v in v_list:
                        if v not in visited_node_set:
                            heapq.heappush(pq, (self.topo_rank[v], v))
                            visited_node_set.add(v)
                        no_dfs_node_set.add(v)

                    to_list = to_list[
                        : bisect.bisect(
                            to_list,
                            last_v,
                            key=lambda x: self.topo_rank[x],
                        )
                    ]

                    if v_list:
                        last_v = v_list.pop()

                for v in to_list:
                    if v not in visited_node_set:
                        heapq.heappush(pq, (self.topo_rank[v], v))
                        visited_node_set.add(v)

        if not (FSLICE_TOPO, BSLICE_TOPO)[self.reverse]:
            slice_list.sort(
                key=lambda x: (
                    node_dict[self.cluster_list[x][0]].get("lineNumber",0),             # 修改了一下，如果没有lineNumber则为0
                    node_dict[self.cluster_list[x][0]].get("columnNumber",0),
                ),
                reverse=self.reverse,
            )

        return slice_list

    def get_std_src(self, raw_src):
        return tuple(
            sorted(
                {self.cluster_dict[v] for v in raw_src if v in self.cluster_dict},
                key=lambda x: self.topo_rank[x],
            )
        )

    def compute_all_slice_data(self, src_list, node_dict):
        std_src_list = []
        for raw_src in src_list:
            std_src = self.get_std_src(raw_src)
            if std_src:
                std_src_list.append(std_src)

        for std_src in sorted(
            std_src_list,
            key=lambda x: self.topo_rank[x[0]],
            reverse=True,
        ):
            if std_src not in self.slice_data:
                self.slice_data[std_src] = self.slice(std_src, node_dict)

    def get_slice_data(self, raw_src, node_dict):
        std_src = self.get_std_src(raw_src)
        if not std_src:
            return []
        else:
            if std_src not in self.slice_data:
                self.slice_data[std_src] = self.slice(std_src, node_dict)
            return self.slice_data[std_src]

    def topo_sort(self, node_dict):
        self.topo_list = []
        self.topo_rank = [None] * len(self.dag.vs)
        in_degree_list = self.dag.indegree()
        """在数据依赖边修复后，将下面修改为：
        stack = [self.cluster_dict[self.src]]
        """
        stack = [i for i, d in enumerate(in_degree_list) if not d]
        while stack:
            node = stack.pop()
            self.topo_list.append(node)
            target_list = sorted(
                self.dag.successors(node),
                key=lambda x: (
                    node_dict[self.cluster_list[x][0]].get("lineNumber",0),                 # 修改了一下，如果没有lineNumber则为0
                    node_dict[self.cluster_list[x][0]].get("columnNumber",0),
                ),
                reverse=not self.reverse,
            )

            # print(node, [self.cluster_list[v] for v in target_list])

            for target in target_list:
                in_degree_list[target] -= 1
                if not in_degree_list[target]:
                    stack.append(target)

        # assert not any(in_degree_list)

        for rank, node in enumerate(self.topo_list):
            self.topo_rank[node] = rank

    def __init__(
        self,
        proj,
        fid,
        src,
        edge_dict_list,
        node_dict,
        *,
        reverse=False,
    ) -> None:
        self.src = src
        self.fid = fid
        self.proj = proj
        self.reverse = reverse
        self.xdg = Graph.TupleList(
            get_edge_set(edge_dict_list, reverse=reverse), directed=True
        )
        c = self.xdg.clusters()
        self.cluster_list = [
            sorted(
                [self.xdg.vs[v]["name"] for v in node_list],
                key=lambda x: (
                    node_dict[x].get("lineNumber",0),               # 修改了一下，如果没有lineNumber则为0
                    node_dict[x].get("columnNumber",0),
                ),
                reverse=self.reverse,
            )
            for node_list in c
        ]
        self.cluster_dict = {
            v: i for i, cluster in enumerate(self.cluster_list) for v in cluster
        }
        self.dag = c.cluster_graph()

        self.topo_sort(node_dict)

        self.edge_dict = {}
        [self.edge_dict.setdefault(e.source, []).append(e.target) for e in self.dag.es]
        [
            self.edge_dict[v].sort(key=lambda x: self.topo_rank[x])
            for v in self.edge_dict
        ]

        self.slice_data = {}

        if PREPARE_DEBUG:
            prefix_path = f"{db_path}/{proj}/{'fb'[reverse]}dg_{fid}"
            self.xdg.write_dot(f"{prefix_path}.dot")
            self.dag.write_dot(f"{prefix_path}_dag.dot")
            dump_to_json(self.cluster_dict, f"{prefix_path}_cluster_dict.json")
            dump_to_json(self.cluster_list, f"{prefix_path}_cluster_list.json")
            dump_to_json(self.topo_list, f"{prefix_path}_topo_list.json")
            dump_to_json(self.topo_rank, f"{prefix_path}_topo_rank.json")
            dump_to_json(self.edge_dict, f"{prefix_path}_edge_dict.json")

###########################################################################################
# 在这里对新增的sink类型进行初始化
class GraphDB:
    def get_slice_src(self, node_dict):
        self.type_list = ["ALL", "AU", "PU", "AE", "FC", "NPD", "PT", "DZ", "AS", "FR"]
        self.src_dict = {type: set() for type in self.type_list}
        self.sinkcode_dict = {type: list() for type in self.type_list}
        self.ast.get_slice_src(self.fid, node_dict, self.sinkcode_dict, None, False, False)


    def get_bslice_data(self, src, node_dict):
        return [
            v
            for c in self.bdg.get_slice_data(src, node_dict)
            for v in self.bdg.cluster_list[c]
        ][::-1]

    def get_fslice_data(self, src, node_dict):
        return [
            v
            for c in self.fdg.get_slice_data(src, node_dict)
            for v in self.fdg.cluster_list[c]
        ]

    def __init__(self, proj, fid, ast, cdg, ddg, node_dict):
        self.fid = fid
        self.proj = proj
        self.ast_edge_dict = ast
        self.cdg_edge_dict = cdg
        self.ddg_edge_dict = ddg
        self.fdg = self.bdg = None
        self.ast = AST(
            self.proj,
            self.fid,
            [self.ast_edge_dict],
            node_dict,
        )
        self.ret = self.ast.edge_dict[fid][-1]

        self.bdg = XDG(
            self.proj,
            self.fid,
            self.ret,
            [self.cdg_edge_dict, self.ddg_edge_dict],
            node_dict,
            reverse=True,
        )
        self.fdg = XDG(
            self.proj,
            self.fid,
            self.fid,
            [self.cdg_edge_dict, self.ddg_edge_dict]
            if FDG_CTRL
            else [self.ddg_edge_dict],
            node_dict,
        )

        self.get_slice_src(node_dict)
        
        # 从结果中筛选出符合类型的sink点作为切片的起始节点，如果符合类型的为空，则给出no_sink结果
        if not SLICE_ALL:       # 将所有类型的合并到ALL中，用于切片和查看
            self.sinkcode_dict['ALL'] = [v for vs in self.sinkcode_dict.values() for v in vs]
        for tp in self.type_list:
            self.src_dict[tp] = set(v[0] for v in self.sinkcode_dict[tp])
        self.src_list = [[v] for v in self.src_dict["ALL"]]
        sink_num = len(self.sinkcode_dict["ALL"])

        for tp in self.type_list:
            sink_total_num[tp] += len(self.sinkcode_dict[tp])
        if sink_num == 0:
            with open("log.txt","a") as l:
                l.write(f"\tproject {proj} has !:{sink_num}:! sink\n")

        self.bdg.compute_all_slice_data(self.src_list, node_dict)
        self.fdg.compute_all_slice_data(self.src_list, node_dict)
        if PREPARE_DEBUG:
            tmp_src_dict = {}
            for k in self.src_dict:
                tmp_src_dict[k] = [
                    (src, node_dict[src]["code"]) for src in self.src_dict[k]
                ]
            dump_to_json(tmp_src_dict, f"{db_path}/{proj}/src_dict_{fid}.json")
            dump_to_json(
                list(self.fdg.slice_data.items()),
                f"{db_path}/{proj}/fdg_{fid}_slice_data.json",
            )
            dump_to_json(
                list(self.bdg.slice_data.items()),
                f"{db_path}/{proj}/bdg_{fid}_slice_data.json",
            )
