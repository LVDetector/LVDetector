import os
import shutil
import json

PARSE_DEBUG = False
RECTIFY_DEBUG = True
PREPARE_DEBUG = False
SLICE_DEBUG = True
FEATURE_DEBUG = True

DEBUG_ALL = True
SLICE_ALL = False


FDG_CTRL = False
BSLICE_CALL = False
BSLICE_TOPO = False
FSLICE_TOPO = True

server_port = 8080
fslice_depth = 3
bslice_depth = 3


tc_path = "./testcase"
td_path = f"{tc_path}/tmp"

pr_path = "parse_module/parse_result"
db_path = "data_module/database"
sr_path = "slice_module/slice_result"

cpg_path = f"{pr_path}/cpg.bin"


PARSE_DEBUG |= DEBUG_ALL
RECTIFY_DEBUG |= DEBUG_ALL
PREPARE_DEBUG |= DEBUG_ALL
SLICE_DEBUG |= DEBUG_ALL

# 用于sink点数量统计
sink_total_num = {"ALL" : 0,"AU" : 0,"PU" : 0,"AE" : 0,"FC" : 0,"NPD" : 0,"PT" : 0,"DZ" : 0,"AS" : 0,"FR" : 0}
# 用于slice数量统计
slice_total_num = {"ALL" : 0,"AU" : 0,"PU" : 0,"AE" : 0,"FC" : 0,"NPD" : 0,"PT" : 0,"DZ" : 0,"AS" : 0,"FR" : 0}
# 用于切片的source源的数量统计
slice_source_total_num = {"custom_function" : 0,"function_parameter" : 0,"global_variable" : 0}
# 用于有无隐式漏洞的项目数量统计
proj_num = {"ALL" : 0,"vulnerable" : 0,"non_vulnerable" : 0}
# 用于各种漏洞类型的项目数量统计(依据slice来统计)
vulnerable_type_proj = {"ALL" : 0,"AU" : 0,"PU" : 0,"AE" : 0,"FC" : 0,"NPD" : 0,"PT" : 0,"DZ" : 0,"AS" : 0,"FR" : 0}
# top10软件中参与统计的项目数
top10_software_proj = {"Chrome" : 0,"linux" : 0,"Android" : 0,"ImageMagick" : 0,"savannah" : 0,"FFmpeg" : 0,"gpac" : 0,"php-src" : 0,"qemu" : 0,"radare2" : 0}
# top10软件中隐式漏洞的项目数
top10_software_vulnerable_proj = {"Chrome" : 0,"linux" : 0,"Android" : 0,"ImageMagick" : 0,"savannah" : 0,"FFmpeg" : 0,"gpac" : 0,"php-src" : 0,"qemu" : 0,"radare2" : 0}

def output_to_log():
    with open("log.txt","a") as l:
        l.write(f"有结果的项目总数：{proj_num['ALL']}\n")
        l.write(f"无漏洞项目总数：{proj_num['non_vulnerable']}\n")
        l.write(f"有隐式漏洞项目总数：{proj_num['vulnerable']}\n")
        l.write(f"各种漏洞类型的项目数量：{vulnerable_type_proj}\n")            # 一个项目可以对应多个漏洞类型
        l.write(f"top10软件中参与统计的项目数：{top10_software_proj}\n")
        l.write(f"top10软件中有隐式漏洞的项目数：{top10_software_vulnerable_proj}\n")
        l.write(f"sink点数量统计：{sink_total_num}\n")
        l.write(f"slice数量统计：{slice_total_num}\n")
        l.write(f"切片的source源的数量统计：{slice_source_total_num}\n")          # 一个切片可以对应多个source源

def copy_non_vulnerable_proj():
    # 创建一个non_vulnerable_proj文件夹
    if os.path.exists("non_vulnerable_proj"):
        # 如果文件夹已经存在，则全部删除
        shutil.rmtree("non_vulnerable_proj")
    os.makedirs("non_vulnerable_proj")
    with open("non_vulnerable_proj.txt","r") as f:
        lines = f.readlines()
        for line in lines:
            # 在testcase文件夹中寻找同名的文件夹，将其中的.c文件复制到non_vulnerable_proj文件夹中
            proj = line.strip()     # 去掉首尾的空白字符
            proj_path = f"{tc_path}/{proj}"
            # 判断是否存在该文件夹（默认文件夹一定存在）
            if os.path.exists(proj_path):
                # 将该文件夹中的所有.c文件复制到non_vulnerable_proj文件夹中（当下情况仅有一个.c文件）
                for root, dirs, files in os.walk(proj_path):
                    for file in files:
                        if file.endswith(".c"):
                            # 构建源文件路径和目标文件路径
                            source_file_path = os.path.join(root, file)
                            destination_file_path = os.path.join("non_vulnerable_proj", file)
                            # 复制文件
                            shutil.copy(source_file_path, destination_file_path)

# 用于统计数据的累积，如果需要重新统计，需要手动删除statistics_data.json文件
def accumulate_statistics_data():
    if os.path.exists("statistics_data.json"):
        # 读取JSON文件中的统计数据
        with open("statistics_data.json", "r") as file:
            statistics_data = json.load(file)

        # 累加统计数据
        statistics_data["sink_total_num"] = {key: statistics_data["sink_total_num"][key] + sink_total_num[key] for key in sink_total_num}
        statistics_data["slice_total_num"] = {key: statistics_data["slice_total_num"][key] + slice_total_num[key] for key in slice_total_num}
        statistics_data["slice_source_total_num"] = {key: statistics_data["slice_source_total_num"][key] + slice_source_total_num[key] for key in slice_source_total_num}
        statistics_data["proj_num"] = {key: statistics_data["proj_num"][key] + proj_num[key] for key in proj_num}
        statistics_data["vulnerable_type_proj"] = {key: statistics_data["vulnerable_type_proj"][key] + vulnerable_type_proj[key] for key in vulnerable_type_proj}
        statistics_data["top10_software_proj"] = {key: statistics_data["top10_software_proj"].get(key, 0) + top10_software_proj.get(key, 0) for key in set(statistics_data["top10_software_proj"]) | set(top10_software_proj)}
        statistics_data["top10_software_vulnerable_proj"] = {key: statistics_data["top10_software_vulnerable_proj"].get(key, 0) + top10_software_vulnerable_proj.get(key, 0) for key in set(statistics_data["top10_software_vulnerable_proj"]) | set(top10_software_vulnerable_proj)}
        # 对top10_software_proj和top10_software_vulnerable_proj进行排序，按照键值对中的键进行排序
        statistics_data["top10_software_proj"] = dict(sorted(statistics_data["top10_software_proj"].items(), key=lambda x: x[0]))
        statistics_data["top10_software_vulnerable_proj"] = dict(sorted(statistics_data["top10_software_vulnerable_proj"].items(), key=lambda x: x[0]))


        # 更新JSON文件中的统计数据
        with open("statistics_data.json", "w") as file:
            json.dump(statistics_data, file, indent=4)
    else:
        # 创建JSON文件并写入统计数据
        statistics_data = {
            "sink_total_num": sink_total_num,
            "slice_total_num": slice_total_num,
            "slice_source_total_num": slice_source_total_num,
            "proj_num": proj_num,
            "vulnerable_type_proj": vulnerable_type_proj,
            "top10_software_proj": top10_software_proj,
            "top10_software_vulnerable_proj": top10_software_vulnerable_proj
        }

        with open("statistics_data.json", "w") as file:
            json.dump(statistics_data, file, indent=4)