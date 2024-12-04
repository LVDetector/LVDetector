import time
import collections
from multiprocessing import Pool
from alive_progress import alive_bar
from config import FEATURE_DEBUG
from config import db_path, sr_path
from config import slice_source_total_num
from config import proj_num
from config import top10_software_vulnerable_proj, top10_software_proj
from data_module.db_access import *
from .source_match import match_source


def extract_cv(proj):
    # {fid: {tp: [...]}}
    sink_cv_dict = load_from_pickle(f"{sr_path}/{proj}/sink_code.db")
    newsink_dict = {}
    for fid, v1 in sink_cv_dict.items():
        newsink_dict[fid] = {}
        for tp, vs in v1.items():
            for v in vs:
                key = v[0] + "_" + tp
                newsink_dict[fid][key] = {
                    "type": tp,
                    "line": v[2],
                    "code": v[3],
                    "key_value": v[4]
                }
    dump_to_pickle(newsink_dict, f"{sr_path}/{proj}/sink_cv_dict.db")
    return newsink_dict

def is_vulnerable(source_dict:dict, security_check:dict):
    # 一个切片中有bad_source/ 无security_check就是漏洞的
    if source_dict["bad_source"] != {} and security_check == {}:
        return "Manifest_vulnerability"
    # 一个切片中有good_source/security_check就是无漏洞的
    if source_dict['good_source'] != {} or security_check != {}:
        return "Non_vulnerable"
    # 上述为空且有unknow_source是有隐式漏洞的
    else:
        if source_dict['unknow_source'] != {}:
            return "Latent_vulnerability"
    return "-1"

def extract_feature(proj, fid_set):
    node_dict = load_from_pickle(f"{db_path}/{proj}/node_dict.db")
    graph_dict = load_from_pickle(f"{db_path}/{proj}/graph_dict.db")
    # slice_dict 格式：{id_func:{id_sink: [(id_slice, bool), ]}
    slice_dict = load_from_pickle(f"{sr_path}/{proj}/all_slice_result_dict.db" )
    ddg_dict = load_from_pickle(f'{db_path}/{proj}/ddg_edge_dict.db')
    sink_dict = extract_cv(proj)

    # 需要将每个切片拆分出来，获取到对应切片的类型
    # feature_result = collections.defaultdict(int,feature_result)
    feature_result = {}
    source_num = 0  # 单个项目的source个数
    is_custom_function = 0
    is_function_parameter = 0
    is_global_variable = 0
    flag_is_vulnerable = False
    for fid in fid_set:
        feature_result[fid] = {}
        feature_result[fid] = collections.defaultdict(int,feature_result[fid])
        for tp in ("FR","NPD","PT","DZ","AS","FC", "AU", "PU", "AE"):
            for src in graph_dict[fid].src_dict[tp]:
                # 在切片db中获取到对应src的切片
                # slice_result 中是 id_slice 列表
                slice_result = [item[0] for item in slice_dict[fid][src][0]]
                key = src+"_"+tp
                # 匹配
                match_source_res = match_source(fid, node_dict, graph_dict, ddg_dict, slice_result, sink_dict[fid][key]["key_value"], tp)
                feature_result[fid][key] = {
                    "type": tp,
                    "slice": slice_result,
                    "key_value": sink_dict[fid][key]["key_value"],
                    "sink_code": sink_dict[fid][key]["code"],
                    "sink_lineNumber": sink_dict[fid][key]["line"],
                    "source": match_source_res[0],
                    "security_check": match_source_res[1],
                    "label": is_vulnerable(match_source_res[0], match_source_res[1])
                }
                # 依据label判断是否有隐式漏洞
                if feature_result[fid][key]["label"] == "Latent_vulnerability":
                    flag_is_vulnerable = True
                # 统计source个数以及不同source源的个数；由于同一sink可能有多个关键变量，所以source个数可能大于sink个数
                tmp_l = feature_result[fid][key]["source"]
                source_not_exist = True
                if tmp_l["good_source"]:
                    source_num += 1
                    source_not_exist = False
                if tmp_l["unknow_source"]["custom_function"]:
                    is_custom_function += 1
                    source_num += 1
                    #flag_is_vulnerable = True
                    source_not_exist = False
                if tmp_l["unknow_source"]["function_parameter"][fid]:
                    is_function_parameter += len(tmp_l["unknow_source"]["function_parameter"][fid])
                    source_num += len(tmp_l["unknow_source"]["function_parameter"][fid])
                    #flag_is_vulnerable = True
                    source_not_exist = False
                if tmp_l["unknow_source"]["global_variable"][fid]:
                    is_global_variable += len(tmp_l["unknow_source"]["global_variable"][fid])
                    source_num += len(tmp_l["unknow_source"]["global_variable"][fid])
                    #flag_is_vulnerable = True
                    source_not_exist = False
                if source_not_exist:       # 无source(有sink但是没有source，这种情况暂时还没有考虑)
                    pass
                    #with open("log.txt","a") as l:              # 注释掉上面的pass后，可以记录没有source的slice
                    #    l.write(f"ATTENTION: project {proj} has slice without source,src_tp is {src}_{tp}\n")


    dump_to_json(feature_result,f"{sr_path}/{proj}/feature_dict.json")


def feature():
    start = time.perf_counter()
    print("Extract slice feature... ")
    proj_dict = load_from_pickle(f"{db_path}/proj_dict.db")
    with open("log.txt","a") as l:
        l.write("开始获取feature\n")
    with open("non_vulnerable_proj.txt","w") as l:      # 清空文件
        pass
    with alive_bar(len(proj_dict)) as bar:
        bar.title = f"{'Extract slice feature':^30}"
        if FEATURE_DEBUG:
            for proj, fid_set in proj_dict.items():
                extract_feature(proj, fid_set)
                bar()
        else:
            with Pool() as p:
                for proj, fid_set in proj_dict.items():
                    p.apply_async(
                        extract_feature,
                        (proj, fid_set),
                        callback=lambda x: bar(),
                    )
                p.close()
                p.join()
    with open("log.txt","a") as l:
        # 已经转移到其他位置输出
        #l.write(f"all_slice_source_total_num:\t\t{slice_source_total_num}\n")
        #l.write(f"num_of_vulnerable_proj:\t\t{vulnerable_proj}\n")
        #l.write(f"num_of_non_vulnerable_proj:\t\t{non_vulnerable_proj}\n")
        #
        l.write("获取结束\n\n")
    print(f"Done, used {time.perf_counter() - start:<.2f}s\n")

    # # 先不做多进程处理
    # for proj,fid_set in proj_dict.items():
    #     extract_feature(proj, fid_set)