import time
from alive_progress import alive_bar
from multiprocessing import Pool
from config import SLICE_DEBUG, SLICE_ALL
from config import db_path, sr_path
from config import slice_total_num
from config import vulnerable_type_proj
from data_module.db_access import *
from .slice_func import get_all_slice_result

def compute_slice_result(proj, fid_set):
    node_dict = load_from_pickle(f"{db_path}/{proj}/node_dict.db")
    graph_dict = load_from_pickle(f"{db_path}/{proj}/graph_dict.db")
    callin_dict = load_from_pickle(f"{db_path}/{proj}/callin_dict.db")
    
    slice_result_dict = {
        fid: get_all_slice_result(
            fid,
            node_dict,
            graph_dict,
            callin_dict,
        )
        for fid in fid_set
    }
    dump_to_pickle(slice_result_dict, f"{sr_path}/{proj}/all_slice_result_dict.db")
    # 下面的字典用于统计各个类型的切片数量
    tmp_slice_num_dict = {"ALL" : 0, "AU" : 0, "PU" : 0, "AE" : 0, "FC" : 0, "NPD" : 0, "PT" : 0, "DZ" : 0, "AS" : 0, "FR" : 0}
    # 在输出的地方加上新增的sink类型
    for tp in ( "ALL", "AU", "PU", "AE", "FC", "NPD", "PT", "DZ", "AS", "FR"):
        if not SLICE_ALL and tp == "ALL":
            continue

        slice_result = {}
        for fid in slice_result_dict:                   # 函数头id{id:{src:[[],[]],src:[[],[]]}}
            slice_result[fid] = {}
            for src in graph_dict[fid].src_dict[tp]:            # 关注点 相关的每个节点id
                slice_result_list = slice_result_dict[fid][src]
                # 增加输出行号信息，如果没有行号信息则不输出
                slice_result[fid][src] = [
                    [node_dict[t[0]]["code"] + "         " + "LineNumber:"+str(node_dict[t[0]]["lineNumber"]) for t in slice_result if t[1] and "lineNumber" in node_dict[t[0]]] # 提取的代码一定是节点上的代码，且是节点内的全部代码
                    for slice_result in slice_result_list
                ]
                
            tmp_slice_num_dict[tp] += len(slice_result[fid])        # 累加单个项目内一个类型的切片数目
        tmp_slice_num_dict["ALL"] += tmp_slice_num_dict[tp]         # 累加单个项目内所有类型的切片数目
        dump_to_json(slice_result, f"{sr_path}/{proj}/slice_result_{tp}.json")
    with open("log.txt","a") as l:
        tmp_int = tmp_slice_num_dict["ALL"]
        l.write(f"\tproject {proj} has !:{tmp_int}:! slices\n")
    for tp,value in tmp_slice_num_dict.items():    
        slice_total_num[tp] += value            # 累加每个类型的切片数量
        if value > 0:                           # 统计各种漏洞类型出现的项目数
            vulnerable_type_proj[tp] += 1
#        with open("log.txt","a") as l:      # 输出单个项目的每个类型的切片数目
#            l.write(f"\t\t{tp}\t\t{value}\n")
    if SLICE_DEBUG:
        dump_to_json(slice_result_dict, f"{sr_path}/{proj}/slice_result_dict.json") #记录当前数据所有切片起始节点和切片内节点


def compute():
    start = time.perf_counter()
    print("Computing program slice...")
    proj_dict = load_from_pickle(f"{db_path}/proj_dict.db")
    # print("========================")
    # print(proj_dict)    # 试验
    # print("========================")
    with open("log.txt","a") as l:
        l.write("开始切片\n")
    with alive_bar(len(proj_dict)) as bar:
        bar.title = f"{'Computing program slice':^30}"
        if SLICE_DEBUG:
            for proj, fid_set in proj_dict.items():
                compute_slice_result(proj, fid_set)
                bar()
        else:
            with Pool() as p:
                for proj, fid_set in proj_dict.items():
                    p.apply_async(
                        compute_slice_result,
                        (proj, fid_set),
                        callback=lambda x: bar(),
                    )
                p.close()
                p.join()
    with open("log.txt","a")as l:

        l.write("切片结束\n\n")
    print(f"Done, used {time.perf_counter() - start:<.2f}s\n")
