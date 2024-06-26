import os, time
from typing import List
from cpgqls_client import CPGQLSClient
from config import tc_path, pr_path, cpg_path, PARSE_DEBUG


def query(query_list: List[str], client: CPGQLSClient, step):
    for idx, query in enumerate(query_list):
        print(f"{idx + 1} of all {len(query_list)} (step: {step})")
        print("  query  :", query)
        start = time.perf_counter()
        res = client.execute(query)
        print("  result :", repr("None" if not res["stdout"] else res["stdout"]))
        print(f"  time   : {time.perf_counter() - start:<.2f}s\n")
#        assert len(res["stderr"]) < 50, f"stderr too long as follows:\n{res['stderr']}"

    query_list.clear()


def parse_testcase(client: CPGQLSClient) -> None:

    """
    注意以下 json 文件输出由于 joern 的 map 语法的限制，每个字典中的每个字典项被单独存入了各自的列表中，需要修正
    修正部分可以使用多进程优化，故不在此处进行
    """

    query_list = [f'importCpg("{cpg_path}")']

    query(query_list, client, "LOAD")

    """1. 获取项目和待分析函数对应关系
    只分析项目内的非 global 函数
    
    List[Dict[str: proj -> str: fid]
    """
    query_list.append(
        f'cpg.method.isExternal(false).nameNot("<global>").filterNot(node=> node.filename=="<empty>").'
        f'map(node => Map((node.filename.split("/").apply(1), node.id + ""))).' #
        f'toJsonPretty |> "{pr_path}/out1.json"'
    )

    """2.a 获取项目 和 非头文件中所有节点（包含全局变量）的字典
    
    List[Dict[str: proj -> List[Dict[str: projk -> str: projv]]]]
    """
    query_list.append(
        f'cpg.method("<global>").filenameNot(".*<includes>").'
        f'map(g => (g.filename.split("/").apply(1),g.ast.l)).'
        f'toJsonPretty |> "{pr_path}/out2a.json"'
    )

    """2.b 获取项目 和 头文件中所有节点（包含全局变量） 的字典
    
    List[Dict[str: proj -> Dict[str: projk -> str: projv]]]
    """
    query_list.append(
        f'cpg.method.filename(".*<includes>").ast.'
        f'map(v => {{val fn = v.file.name.head; if(fn.startsWith("{os.path.realpath(tc_path)}")) '
        f'Map(fn.split("[/:]").apply({len(os.path.realpath(tc_path).split("/"))}) -> v) else None}}).'
        f'toJsonPretty |> "{pr_path}/out2b.json"'
    )

    """3. 获取 dot 文件
    
    List[Dict[str: fid -> List[str: astdotedge,str: pdgdotedge]]]
    """
    query_list.append(
        f'cpg.method.isExternal(false).nameNot("<global>").'
        f'map(f => Map(f.id -> {{val ast = f.dotAst.head.split("]\\n ", 2); val pdg = f.dotPdg.head.split("]\\n ", 2); '
        f'List(if(ast.size == 2) ast.apply(1).split("\\n}}",2).apply(0) else "", '
        f'if(pdg.size == 2) pdg.apply(1).split("\\n}}",2).apply(0) else "")}})).'
        f'toJsonPretty |> "{pr_path}/out3.json"'
    )

    """4. 获取函数调用信息
    
    List[Dict[str: fid -> Dict[str: cid -> str: fid]]]]
    """
    query_list.append(
        f'cpg.method.isExternal(false).nameNot("<global>").'
        f"map(f => Map((f.id, f.call.map(c => c.id -> ({{"
        f"val t = c.callee.head; if(t.method.isExternal || "
        f'f.filename != t.filename)'
        f'"EXTN" else c.callee.head.id.toString}})).toMap))).'
        f'toJsonPretty |> "{pr_path}/out4.json"'
    )

    """5. 获取变量引用信息
    
    List[Dict[str: fid -> Dict[str: lid -> List[str: iid]]]]
    """
    query_list.append(
        f'cpg.identifier.where(_.method).map(i => List(i.method.id + "", i.id + "", '
        f'{{val l = i.refsTo.id.l; if(l.size > 0) l.apply(0) + "" else "LOST"}})).'
        f'toJsonPretty |> "{pr_path}/out5.json"'
    )

    query(query_list, client, "EXPORT")

    """
    以下代码用于
        1. 生成各种图
        2. 测试 各种图 的生成速度
    """
    if PARSE_DEBUG:
        import time

        time_result = []
        gpraph_type_list = ["Ast", "Cfg", "Cdg", "Pdg", "Ddg", "Cpg14"]

        for graph_type in gpraph_type_list:
            start = time.perf_counter()

            query_list = [
                f"cpg.method.isExternal(false)."
                f'dot{graph_type}.l |> "{f"{pr_path}/fid_{graph_type.lower()}"}.dot"'
            ]
            query(query_list, client, "DEBUG")
            time_result.append((graph_type, time.perf_counter() - start))

        print("time :", time_result, "\n\n")

    query_list = ["save", "close"]
    query(query_list, client, "QUIT")
