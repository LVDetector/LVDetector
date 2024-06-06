from data_module.db_access import load_from_pickle
ae_func_1 = {
    "<operator>.multiplication",
    "<operator>.division",
    "<operator>.shiftLeft",
    "<operator>.assignmentMultiplication",
    "<operator>.assignmentDivision",
    "<operators>.assignmentShiftLeft",  
}

ae_func_2 = {
    "<operator>.subtraction",
    "<operator>.addition",
    "<operator>.assignmentMinus",
    "<operator>.assignmentPlus",
}


int_types = {
    "char", "unsigned char","char unsigned"
    "short", "unsigned short", "short unsigned",
    "int", "unsigned int", "int unsigned",
    "long", "unsigned long", "long unsigned",
    "long long", "unsigned long long", "long long unsigned",
    "<empty>"
}

cfuns = load_from_pickle("feature_module/cfuns.db")


access_operators = {
   '<operator>.indirectIndexAccess' ,
   '<operator>.indirectFieldAccess',
   '<operator>.fieldAccess'
}


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


arithmetic_operators = {
    "<operator>.addition",
    "<operator>.subtraction",
    "<operator>.multiplication",
    "<operator>.division",
    "<operator>.modulo"
}

comparison_operations = {
    '<operator>.greaterThan',
    '<operator>.greaterEqualsThan',
    '<operator>.lessThan',
    '<operator>.lessEqualsThan',
    '<operator>.equals',
    '<operator>.notEquals',
}

boolean_operations = {
    '<operator>.logicalAnd',
    '<operator>.logicalOr',
    '<operator>.logicalNot'
}

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


binary_operators = (
    arithmetic_operators |
    comparison_operations |
    boolean_operations |     # Although '!' is monocular, placing it here will not cause any issues.

    bit_operators |
    assignment_operators
)


ternary_operators = {
    "<operator>.conditional"
}

def isConstant(obj) -> bool:
    """Determine whether a node is a constant."""
    return (
        obj['_label'] == 'LITERAL'
        # sizeOf
        or (obj['_label'] == 'CALL' and obj['methodFullName'] == '<operator>.sizeOf')
        # Treat uppercase macros as constants.
        or (obj['_label'] == 'IDENTIFIER' and all(char.isupper() or char.isdigit() for char in obj['name'].replace('_', '')))
    )