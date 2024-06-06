from data_module.db_access import load_from_pickle
ae_func_1 = {
    "<operator>.multiplication",
    "<operator>.division",
    "<operator>.shiftLeft",
    "<operator>.assignmentMultiplication",
    "<operator>.assignmentDivision",
    "<operators>.assignmentShiftLeft",  # operator 是否为复数，后期名称可能改正
}

ae_func_2 = {
    "<operator>.subtraction",
    "<operator>.addition",
    "<operator>.assignmentMinus",
    "<operator>.assignmentPlus",
}

# unsigned 在类型的前还是后，这通过具体例子确定，挺奇怪的
int_types = {
    "char", "unsigned char","char unsigned"
    "short", "unsigned short", "short unsigned",
    "int", "unsigned int", "int unsigned",
    "long", "unsigned long", "long unsigned",
    "long long", "unsigned long long", "long long unsigned",
    "<empty>"
}

cfuns = load_from_pickle("feature_module/cfuns.db")

# 访问运算符
access_operators = {
   '<operator>.indirectIndexAccess' ,
   '<operator>.indirectFieldAccess',
   '<operator>.fieldAccess'
}

# 单目运算符
unary_operators = {
    "<operator>.addressOf",
    "<operator>.indirection",
    "<operator>.plus",
    "<operator>.minus",
    "<operator>.postIncrement",
    "<operator>.preIncrement",
    "<operator>.postDecrement",
    "<operator>.preDecrement",
    "<operator>.logicalNot",
    "<operator>.not",
    "<operator>.sizeOf"
}

# 算术运算符
arithmetic_operators = {
    "<operator>.addition",
    "<operator>.subtraction",
    "<operator>.multiplication",
    "<operator>.division",
    "<operator>.modulo"
}
# 关系运算符
comparison_operations = {
    '<operator>.greaterThan',
    '<operator>.greaterEqualsThan',
    '<operator>.lessThan',
    '<operator>.lessEqualsThan',
    '<operator>.equals',
    '<operator>.notEquals',
}
# 逻辑运算符
boolean_operations = {
    '<operator>.logicalAnd',
    '<operator>.logicalOr',
    '<operator>.logicalNot'
}
# 位运算符
bit_operators = {
    "<operator>.and",
    "<operator>.or",
    "<operator>.xor",
    "<operator>.shiftLeft",
    "<operator>.arithmeticShiftRight"
}

assignment_operators = {
    "<operator>.assignment",
    "<operator>.assignmentPlus",
    "<operator>.assignmentMinus",
    "<operator>.assignmentMultiplication",
    "<operator>.assignmentDivision",
    "<operators>.assignmentModulo",
    "<operators>.assignmentAnd",
    "<operators>.assignmentOr",
    "<operators>.assignmentXor",
    "<operators>.assignmentShiftLeft",
    "<operators>.assignmentArithmeticShiftRight",
}

# 双目运算符
binary_operators = (
    arithmetic_operators |
    comparison_operations |
    boolean_operations |     # '!'虽然是单目的，但放在这里也不会造成问题
    bit_operators |
    assignment_operators
)

# 三目运算符
ternary_operators = {
    "<operator>.conditional"
}

def isConstant(obj) -> bool:
    """判断一个节点是否为常量"""
    return (
        obj['_label'] == 'LITERAL'
        # sizeOf运算符看做常量
        or (obj['_label'] == 'CALL' and obj['methodFullName'] == '<operator>.sizeOf')
        # 大写的宏看做常量
        or (obj['_label'] == 'IDENTIFIER' and all(char.isupper() or char.isdigit() for char in obj['name'].replace('_', '')))
    )