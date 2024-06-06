import time

from clean import clean, clean2
from parse_module import parse_main
from rectify_module import rectify_main
from graph_module import graph_main
from slice_module import slice_main
from feature_module import feature_main
import config

"""
Without changing the test cases, when calling clean2() instead of clean(),
the result file of parse_main.parse will not be deleted,
which can reduce debugging time on the second call. Note that you need to comment out parse_main.parse() for this to take effect.
"""
# clean2()    
clean()

with open("time.txt", "w") as t_log:
    start = time.perf_counter()
    parse_main.parse()                  # Parse the code to obtain the required data.
    t_log.write(
        f"[{'Parsing the testcase':^25}]"
        f"  used {time.perf_counter() - start:>7.2f}s\n"
    )

with open("time.txt", "a+") as t_log:
    start = time.perf_counter()
    rectify_main.rectify()              
    t_log.write(
        f"[{'Rectifying the result':^25}]"
        f"  used {time.perf_counter() - start:>7.2f}s\n"
    )

with open("time.txt", "a+") as t_log:
    start = time.perf_counter()
    graph_main.generate()               
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
