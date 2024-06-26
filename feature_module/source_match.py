from data_module.db_access import load_from_pickle, load_from_json
from graph_module import graph_class
from data_module.method_set import *
from config import db_path

# 用作缓冲区溢出的安全检查
compare_operator = {
    "<operator>.greaterThan",
    "<operator>.greaterEqualsThan",
    "<operator>.lessThan",
    "<operator>.lessEqualsThan",
    "<operator>.equals",
    "<operator>.notEquals",
}

def compose_cv(node_dict, node):
    if 'lineNumber' in node_dict[node]:
        return node_dict[node]['code'] + ":" + str(node_dict[node]['lineNumber'])
    else:
        return node_dict[node]['code'] + ":no lineNumber"
def get_compare_statements_list(
    node_dict,
    ast,
    sub_ast,
    node,
):
    compare_statements = [] # 比较语句列表
    for sub_node in sub_ast:
        # 将 sub_ast 分为以 && 和 || 连接的多个节点：都是比较语句
        if node_dict[sub_node]['_label'] == 'CALL' and node_dict[sub_node]['methodFullName'] in ('<operator>.logicalAnd', '<operator>.logicalOr'):
            # 若内部还有 && 和 || 连接，则去除自身，并将子节点加入
            if node in compare_statements:
                compare_statements.remove(node)
            compare_statements += ast.edge_dict.get(node, [])
    if compare_statements == []:    # 没有通过 && 和 || 连接，则为自身
        compare_statements = [node]
    return compare_statements
    
def solve_logical_operation(
    node_dict,
    ast,
    sub_ast,
    node,
    cv,
):
    return any(
        # 所规定的比较运算符
        node_dict[state]['_label'] == 'CALL' 
        and node_dict[state]['name'] in compare_operator 
        # 包括了 cv 
        and any(node_dict[sub_node]['code'] == cv for sub_node in ast.edge_dict.get(state, []))
        # 对每个语句
        for state in get_compare_statements_list(node_dict, ast, sub_ast, node)
    )

def security_check_OF(node, node_dict, ast, sub_ast, cv):
    """Buffer Overflow：AU, PU, FC, AE"""
    obj = node_dict[node]
    sub = ast.edge_dict.get(node, [])
    if obj['_label'] == 'CONTROL_STRUCTURE':
        if obj["controlStructureType"] == "FOR" and len(sub) >= 3 and solve_logical_operation(node_dict, ast, sub_ast, sub[1], cv):
            return True
        if obj["controlStructureType"] == "WHILE" and len(sub) >= 2 and solve_logical_operation(node_dict, ast, sub_ast, sub[0], cv):
            return True
        if obj["controlStructureType"] == "IF" and len(sub) >= 2 and solve_logical_operation(node_dict, ast, sub_ast, sub[0], cv):
            return True
    if obj['_label'] == 'CALL' and obj['methodFullName'] in compare_operator and solve_logical_operation(node_dict, ast, sub_ast, node, cv):
        return True
    # 通过min函数进行安全检查：index = min(a, len)。类似的 index = a > len ? len: a;
    flag_condition = flag_compare = False
    if node_dict[node]['_label'] == 'CALL' and node_dict[node]['name'] == "<operator>.assignment" and cv in node_dict[node]['code'].split('=')[0]:
        for sub_node in sub_ast:
            if node_dict[sub_node]['_label'] == 'CALL':
                # 若包含 min 函数
                if node_dict[sub_node]['methodFullName'] == 'min':
                    return True
                # 若包含 ?: 运算符且右侧是大小比较运算符
                if node_dict[sub_node]['methodFullName'] == '<operator>.conditional':
                    flag_condition = True
                if node_dict[sub_node]['name'] in compare_operator:
                    flag_compare = True
                if flag_condition and flag_compare:
                    return True
    return False

def security_check_NPD(node, node_dict, ast, sub_ast, cv):
    obj = node_dict[node]
    sub = ast.edge_dict.get(node, [])
    # strm = &strm1 
    if (
        obj['_label'] == '<operator>.assignment' 
        and node_dict[sub[0]]['code'] == cv
        and node_dict[sub[-1]]['_label'] == 'CALL' 
        and node_dict[sub[-1]]['methodFullName'] == '<operator>.addressOf'
    ):
        return True
    if (
        obj['_label'] == "CONTROL_STRUCTURE" 
        and obj['controlStructureType'] == "IF" 
        and len(sub) >= 2
        or
        obj['_label'] == 'CALL' 
        and obj['methodFullName'] in compare_operator 
    ):
        compare_statements = get_compare_statements_list(node_dict, ast, sub_ast, node)
        for state in compare_statements:
            # 对每个比较语句进行判断
            subs = ast.edge_dict.get(state, [])
            if any(cv == node_dict[sub_node]['code'] for sub_node in subs):
                # "cv"
                if len(subs) == 1:
                    return True
                # "!cv"
                if node_dict[state]['_label'] == 'CALL' and node_dict[state]['methodFullName'] == '<operator>.logicalNot':
                    return True
                # "cv == NULL, cv != NULL"
                if any(node_dict[sub_node]['code'] == 'NULL' for sub_node in subs):
                    return True
    return False

def security_check_DZ(node,node_dict, ast, sub_ast, cv): 
    obj = node_dict[node]
    sub = ast.edge_dict.get(node, [])
    if (
        obj['_label'] == "CONTROL_STRUCTURE" 
        and obj['controlStructureType'] == "IF" 
        and len(sub) >= 2
        or
        obj['_label'] == 'CALL' 
        and obj['methodFullName'] in compare_operator 
    ):
        compare_statements = get_compare_statements_list(node_dict, ast, sub_ast, node)
        for state in compare_statements:
            subs = ast.edge_dict.get(state, [])
            if any(cv == node_dict[sub_node]['code'] for sub_node in subs):
                # "cv"
                if len(subs) == 1:
                    return True
                # "!cv, cv < a, cv > a"
                if node_dict[state]['_label'] == 'CALL' and node_dict[state]['methodFullName'] in compare_operator | {'<operator>.logicalNot'}:
                    return True
                # "cv == 0, cv != 0"
                if any(node_dict[sub_node]['code'] == '0' for sub_node in subs):
                    return True
    return False

def isReference_value_modification(
    cv,
    solve_node,    # 进行搜索的node，可能是一个赋值语句的右边（若左边不是 cv 的话）
    ast,
    node_dict, 
):
    obj = node_dict[solve_node]
    sub_ast = ast.get_sub_ast(solve_node, node_dict)
    return (
        obj['_label'] == 'CALL'
        and 'operator' not in obj['methodFullName']
        and obj['methodFullName'] not in cfuns
        and any(cv == node_dict[sub_node]['code'].lstrip('&')
            and "name" in node_dict[sub_node]
            and node_dict[sub_node]['name'] == '<operator>.addressOf' 
            for sub_node in sub_ast
        )
    )

def c_function_good_source(
    cv,
    tp,
    sub_ast,
    node_dict
):
    return (
        (tp in ["AU","PU","FC"]
        and any(node_dict[sub_node]['_label'] == "CALL" and "allc" in node_dict[sub_node]['name'] for sub_node in sub_ast))
        or
        # Free 类型，且 cv 和 NULL 都存在于节点之中
        (tp == "FR"
        and all(item in (node_dict[sub_node]['code'] for sub_node in sub_ast) for item in (cv, 'NULL') ))
    )

def assignment_source_match(
    node_dict,
    node,
    sub,        # 直接相连的子节点
    cv_list,    # cv列表
    cv,
    tp,         # type
    ast,
    sub_ast,    # node处的ast
    unknow_source,
    good_source,
    bad_source
):
    """value_modified_flag, break_flag, continue_flag"""
    flags = [False, False, False]   # value_modified_flag = False break_flag = False continue_flag = False
    right_node = sub[-1]
    right_obj = node_dict[right_node]
    # 若左节点不是 cv 
    if cv != node_dict[sub[0]]['code']:
        # 例子： CVE-2014-0143-CWE-190-qemu-cab60de-expand_zero_clusters_in_l1()-0.c 的 FR
        if isReference_value_modification(cv, right_node, ast, node_dict):
            unknow_source['custom_function'][node] = node_dict[node]['code']+"  cv: "+cv
            # value_modified_flag = True
            # break
            value_modified_flag = break_flag = True
            return [True, True, False]
        # continue
        return [False, False, True]
    # 若赋值语句的左节点是 cv
    # cv = var, IDENTIFIER
    # value_modified_flag = True
    flags[0] = True
    if right_obj['_label'] == 'IDENTIFIER':
        if compose_cv(node_dict, right_node) not in cv_list and not isConstant(right_obj):   # 宏常量也不行
            cv_list.append(compose_cv(node_dict, right_node))
        # break
        flags[1] = True
        return flags
    
    # 赋值为NULL的是badsource
    elif any(node_dict[sub_node]['code'] == 'NULL' for sub_node in ast.get_sub_ast(right_node, node_dict)):
        bad_source[node] =node_dict[node]['code']+"  cv: "+cv
        flags[1] = True
        return flags    
    # 若右侧都是常数，为 good_source
    elif all(isConstant(node_dict[sub_node]) for sub_node in ast.get_sub_ast(right_node, node_dict)):
        
        good_source[node] = node_dict[node]['code']+"  cv: "+cv
        flags[1] = True
        return flags
        # break
    elif right_obj['_label'] == 'CALL':
        right_leaves,bad_func_flag, custom_function_flag, c_function_flag = ast.get_operator_separated_leaves(right_node, node_dict)
        # 函数调用类型的
        # 包含free关键字等的函数调用是bad source
        if bad_func_flag:
            bad_source[node] = node_dict[node]['code']+"  cv: "+cv
            flags[1] = True
            return flags
        if custom_function_flag:
            unknow_source['custom_function'][node] = node_dict[node]['code']+"  cv: "+cv
            flags[1] = True
            return flags
            # break
        if c_function_flag:
            if c_function_good_source(cv, tp, sub_ast, node_dict):
                good_source[node] = node_dict[node]['code']+"  cv: "+cv
            else:
                cv_list.extend(compose_cv(node_dict, i) for i in right_leaves if compose_cv(node_dict, i) not in cv_list)
            flags[1] = True
            return flags
            # break
        # 运算类型的，将子节点加入即可
        cv_list.extend(compose_cv(node_dict, i) for i in right_leaves if compose_cv(node_dict, i) not in cv_list)
        flags[2] = True
        return flags
    else:
        # 记录一下可能发生的其他情况
        with open("log.txt","a") as l:
            l.write(f"In assignment but not considered: \n\tnode: {node}, cv: {cv}, code: {node_dict[node]['code']}\n")
        flags[1] = True
        return flags

def match_source(
    fid, 
    node_dict, 
    graph_dict, 
    ddg_dict,
    slice_result:list, 
    cv_s, 
    tp
):
    slice_result.reverse()
    cv_list = []
    for cv in cv_s:
        if "lineNumber" in node_dict[slice_result[0]]: cv_list.append(cv+":"+str(node_dict[slice_result[0]]['lineNumber']))
        else: cv_list.append(cv+":"+"no lineNumber")
    good_source = {}
    bad_source = {}
    unknow_source = {i: {} for i in ("custom_function", "function_parameter", "global_variable")}
    # 可能多个关键变量都是函数参数，因此需要写成一个列表
    unknow_source['function_parameter'][fid] = []
    unknow_source['global_variable'][fid] = []
    security_check = {}
    ast = graph_dict[fid].ast
    for cv_line in cv_list:     # 之后都是放在 cv_list 的末尾的，并不会影响循环
        # 对每个关键变量
        line = cv_line.split(":")[1]
        cv = cv_line.split(":")[0]

        # 是否存在值修改语句
        value_modified_flag = False
        for node in slice_result:
            # 从下到上，对切片结果中的每一个语句节点
            if "lineNumber" in node_dict[node] and line.isdigit() and node_dict[node]['lineNumber'] >= int(line):   # 若在 cv 下方，不考虑
                continue

            # 下面所需要的重要变量
            sub_ast = ast.get_sub_ast(node,node_dict)
            sub = ast.edge_dict.get(node, [])   # 直接相连的子节点
            obj = node_dict[node]
            
            # 首先判断当前语句是不是安全检查语句（根据类型）：不单独放一个循环是因为需要在值改语句之后的检查才有意义。
            if tp in ["AU","PU","FC","AE"] and security_check_OF(node,node_dict, ast, sub_ast, cv):# 对于缓存区溢出和整数溢出，安全检查为比较大小
                security_check[node] = node_dict[node]['code'] +"  cv: "+cv
            if tp == "NPD" and security_check_NPD(node,node_dict, ast, sub_ast, cv):# 对于空指针解引用来说，安全检查为判断是否为空
                security_check[node] = node_dict[node]['code'] +"  cv: "+cv    
            if tp == "DZ" and security_check_DZ(node,node_dict, ast, sub_ast, cv):
                security_check[node] = node_dict[node]['code'] +"  cv: "+cv   

            # source 点匹配
            # 值修改语句：赋值语句
            if obj['_label'] == 'CALL' and obj['name'] == "<operator>.assignment":
                flags = assignment_source_match(node_dict, node, sub, cv_list, cv, tp, ast, sub_ast, unknow_source, good_source,bad_source)
                value_modified_flag |= flags[0]
                if flags[1]:
                    break
                if flags[2]:
                    continue
            # 值修改语句：自定义函数的引用传递的参数
            elif isReference_value_modification(cv, node, ast, node_dict):
                unknow_source['custom_function'][node] = node_dict[node]['code']+"  cv: "+cv
                value_modified_flag = True
                break
        # 若一个值修改语句都没有
        if not value_modified_flag:
            # 若关键变量在函数参数中
            if any(
                node_dict[sub_node]['_label'] == "METHOD_PARAMETER_IN"
                and cv == node_dict[sub_node]['name']
                for sub_node in ast.get_sub_ast(fid,node_dict)
            ):
                if cv not in unknow_source['function_parameter'][fid]:
                    unknow_source['function_parameter'][fid].append(cv)
            # 若关键变量是局部定义的变量，说明切片不够好，倒序遍历pdg(ddg)图查找。
            elif any(
                node_dict[node]['_label'] == "LOCAL"
                and cv == node_dict[node]['name']
                for node in slice_result
            ):
                ddg_keys = list(ddg_dict)[::-1]
                found_flag = False   # 是否在下面找到赋值语句
                for node in ddg_keys:    # 键
                    sub_ast = ast.get_sub_ast(node,node_dict)
                    sub = ast.edge_dict.get(node, [])   # 直接相连的子节点
                    obj = node_dict[node]
                    if obj['_label'] == 'CALL' and obj['name'] == '<operator>.assignment':
                        found_flag = True
                        flags = assignment_source_match(node_dict, node, sub, cv_list, cv, tp, ast, sub_ast, unknow_source, good_source,bad_source)
                        if flags[1]:
                            break
                # if not found_flag:
                #     with open("log.txt","a") as l:
                #         l.write(f"not found: \n\tnode: {node}, cv: {cv}, code: {node_dict[node]['code']}\n")
            # 不是上面几种情况，则应该是全局变量
            else:
                # 这几种，我已经将其孩子放入了关键变量，若孩子找到了source，不认为它是全局变量
                if any(i in cv for i in ('[', '->', '.')):
                    continue
                if cv not in unknow_source['global_variable'][fid]:
                    unknow_source['global_variable'][fid].append(cv)
    source_dict = {}
    source_dict["good_source"] = good_source
    source_dict["unknow_source"] = unknow_source
    source_dict["bad_source"] = bad_source
    return source_dict, security_check
