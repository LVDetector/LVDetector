import time

from clean import clean, clean2
from parse_module import parse_main
from rectify_module import rectify_main
from graph_module import graph_main
from slice_module import slice_main
from feature_module import feature_main
import config

"""
在不更改测试样例的情况下，调用clean2()而非clean()时，
不会删除parse_main.parse的结果文件，
第二次调用时可以减少调试时间。注意需要同时注释掉parse_main.parse()才有作用
"""
# clean2()    
clean()

with open("time.txt", "w") as t_log:
    start = time.perf_counter()
    parse_main.parse()                  # 解析代码，获取所需数据
    t_log.write(
        f"[{'Parsing the testcase':^25}]"
        f"  used {time.perf_counter() - start:>7.2f}s\n"
    )

with open("time.txt", "a+") as t_log:
    start = time.perf_counter()
    rectify_main.rectify()              # 纠正？
    t_log.write(
        f"[{'Rectifying the result':^25}]"
        f"  used {time.perf_counter() - start:>7.2f}s\n"
    )

with open("time.txt", "a+") as t_log:
    start = time.perf_counter()
    graph_main.generate()               # 生成？
    t_log.write(
        f"[{'Preparing for slicing':^25}]"
        f"  used {time.perf_counter() - start:>7.2f}s\n"
    )

with open("time.txt", "a+") as t_log:
    start = time.perf_counter()
    slice_main.compute()
    t_log.write(
        f"[{'Computing slice result':^25}]"
        f"  used {time.perf_counter() - start:>7.2f}s\n"
    )

with open("time.txt", "a+") as t_log:
    start = time.perf_counter()
    feature_main.feature()
    t_log.write(
        f"[{'Computing slice result':^25}]"
        f"  used {time.perf_counter() - start:>7.2f}s\n"
    )
# 将统计信息输出到log.txt
# config.output_to_log()
# # 将non_vulnerable_proj.txt中的项目从testcase中挑出来，放到non_vulnerable_proj文件夹中
# config.copy_non_vulnerable_proj()       # 复制项目中所有的.c文件（目前仅有一个）
# # 累加统计数据，如果需要重新累计，需要手动删除statistics_data.json文件
# config.accumulate_statistics_data()