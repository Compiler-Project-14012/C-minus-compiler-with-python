from anytree import Node

from code_generator import CodeGenerator

e = open("syntax_errors.txt", "a")

Program_node = Node("s")
st = []
line_index = 0
look_ahead = ('', '')
cg = CodeGenerator()


def parse_token(token, stack, current_cg):
    global st, look_ahead, line_index, cg
    cg = current_cg
    st = stack
    look_ahead = token[1]
    line_index = token[0]
    while len(st):
        try:
            A = st.pop()
            if len(A) == 1:
                A[0].__call__()
            else:
                A[0].__call__(A[1])
        except Exception as ex:
            if str(ex) == "next_token":
                break
            else:
                e.close()
                return Program_node, stack, True
    if not len(st):
        Node('$', Program_node)
        e.close()
    return Program_node, st, len(st) == 0


def Match(inp):
    A = inp[0]
    parent = inp[1]
    global look_ahead
    if A == '#':
        cg.call_routine(parent, look_ahead)
    elif (
            (look_ahead[0] == 'ID' and A == 'ID') or
            (look_ahead[0] == 'NUM' and A == 'NUM') or
            (look_ahead[1] == A)
    ):
        Node(str(look_ahead), parent=parent)
        raise Exception("next_token")
    elif look_ahead == ('EOF', '$'):
        return
    else:
        e.write('#' + str(line_index) + ' : syntax error, missing ' + A + '\n')


def Error():
    global look_ahead
    if (look_ahead[0] == 'ID') or (look_ahead[0] == 'NUM'):
        e.write('#' + str(line_index) + ' : syntax error, illegal ' + look_ahead[0] + '\n')
    elif look_ahead == ('EOF', '$'):
        e.write('#' + str(line_index) + ' : syntax error, Unexpected EOF \n')
        raise Exception("EOF")
    else:
        e.write('#' + str(line_index) + ' : syntax error, illegal ' + look_ahead[1] + '\n')
    raise Exception("next_token")


def Program():
    global Program_node
    if look_ahead == ('KEYWORD', 'int') or look_ahead == ('KEYWORD', 'void'):
        Program_node = Node('Program')
        st.append((Declaration_list, Program_node))
    elif look_ahead == ('EOF', '$'):
        Program_node = Node('Program')
    else:
        st.append((Program,))
        Error()


def Declaration_list(parent):
    if look_ahead == ('KEYWORD', 'int') or look_ahead == ('KEYWORD', 'void'):
        Declaration_list_node = Node('Declaration-list', parent=parent)
        st.append((Declaration_list, Declaration_list_node))
        st.append((Declaration, Declaration_list_node))
    elif (
            look_ahead == ('EOF', '$') or look_ahead[0] == 'ID' or look_ahead == ('SYMBOL', ';')
            or look_ahead[0] == 'NUM' or look_ahead == ('SYMBOL', '(') or look_ahead == ('SYMBOL', '{')
            or look_ahead == ('SYMBOL', '}') or look_ahead == ('KEYWORD', 'break')
            or look_ahead == ('KEYWORD', 'if') or look_ahead == ('KEYWORD', 'repeat')
            or look_ahead == ('KEYWORD', 'return')
    ):
        Declaration_list_node = Node('Declaration-list', parent=parent)
        Node('epsilon', parent=Declaration_list_node)

    else:
        st.append((Declaration_list, parent))
        Error()


def Declaration(parent):
    if look_ahead == ('KEYWORD', 'int') or look_ahead == ('KEYWORD', 'void'):
        Declaration_node = Node('Declaration', parent=parent)
        st.append((Declaration_prime, Declaration_node))
        st.append((Declaration_initial, Declaration_node))

    elif(
            look_ahead == ('EOF', '$') or look_ahead[0] == 'ID' or look_ahead == ('SYMBOL', ';')
            or look_ahead[0] == 'NUM' or look_ahead == ('SYMBOL', '(') or look_ahead == ('SYMBOL', '{')
            or look_ahead == ('SYMBOL', '}') or look_ahead == ('KEYWORD', 'break')
            or look_ahead == ('KEYWORD', 'if') or look_ahead == ('KEYWORD', 'repeat')
            or look_ahead == ('KEYWORD', 'return')
    ):
        e.write('#' + str(line_index) + ' : syntax error, missing Declaration' + '\n')
    else:
        st.append((Declaration, parent))
        Error()


def Declaration_initial(parent):
    if look_ahead == ('KEYWORD', 'int') or look_ahead == ('KEYWORD', 'void'):
        Declaration_initial_node = Node('Declaration-initial', parent=parent)
        st.append((Match, ("ID", Declaration_initial_node)))
        st.append((Match, ('#', 'save_id')))
        st.append((Type_specifier, Declaration_initial_node))
        st.append((Match, ('#', 'save_type')))

    elif (
            look_ahead == ('EOF', '$') or look_ahead == ('SYMBOL', ';')
            or look_ahead == ('SYMBOL', '[') or look_ahead == ('SYMBOL', '{')
            or look_ahead == ('SYMBOL', ')') or look_ahead == ('SYMBOL', '(')
    ):
        e.write('#' + str(line_index) + ' : syntax error, missing Declaration-initial' + '\n')
    else:
        st.append((Declaration_initial, parent))
        Error()


def Declaration_prime(parent):
    if look_ahead == ('SYMBOL', '('):
        Declaration_prime_node = Node('Declaration-prime', parent=parent)
        st.append((Fun_declaration_prime, Declaration_prime_node))

    elif look_ahead == ('SYMBOL', ';') or look_ahead == ('SYMBOL', '['):
        Declaration_prime_node = Node('Declaration-prime', parent=parent)
        st.append((Var_declaration_prime, Declaration_prime_node))
    elif (
            look_ahead == ('EOF', '$') or look_ahead[0] == 'ID' or look_ahead[0] == 'NUM'
            or look_ahead == ('KEYWORD', 'int')
            or look_ahead == ('KEYWORD', 'void') or look_ahead == ('SYMBOL', '{')
            or look_ahead == ('SYMBOL', '}') or look_ahead == ('KEYWORD', 'break')
            or look_ahead == ('KEYWORD', 'if') or look_ahead == ('KEYWORD', 'repeat')
            or look_ahead == ('KEYWORD', 'return')
    ):
        e.write('#' + str(line_index) + ' : syntax error, missing Declaration-prime' + '\n')
    else:
        st.append((Declaration_prime, parent))
        Error()


def Var_declaration_prime(parent):
    if look_ahead == ('SYMBOL', ';'):
        Var_declaration_prime_node = Node('Var-declaration-prime', parent=parent)
        st.append((Match, (';', Var_declaration_prime_node)))
        st.append((Match, ('#', 'add_variable')))
    elif look_ahead == ('SYMBOL', '['):
        Var_declaration_prime_node = Node('Var-declaration-prime', parent=parent)
        st.append((Match, (';', Var_declaration_prime_node)))
        st.append((Match, (']', Var_declaration_prime_node)))
        st.append((Match, ('NUM', Var_declaration_prime_node)))
        st.append((Match, ('#', 'save_array')))
        st.append((Match, ('[', Var_declaration_prime_node)))
    elif (
            look_ahead == ('EOF', '$') or look_ahead[0] == 'ID'
            or look_ahead[0] == 'NUM' or look_ahead == ('SYMBOL', '(') or look_ahead == ('KEYWORD', 'int')
            or look_ahead == ('KEYWORD', 'void') or look_ahead == ('SYMBOL', '{')
            or look_ahead == ('SYMBOL', '}') or look_ahead == ('KEYWORD', 'break')
            or look_ahead == ('KEYWORD', 'if') or look_ahead == ('KEYWORD', 'repeat')
            or look_ahead == ('KEYWORD', 'return')
    ):
        e.write('#' + str(line_index) + ' : syntax error, missing Var-declaration-prime' + '\n')
    else:
        st.append((Var_declaration_prime, parent))
        Error()


def Fun_declaration_prime(parent):
    if look_ahead == ('SYMBOL', '('):
        Fun_declaration_prime_node = Node('Fun-declaration-prime', parent=parent)
        st.append((Match, ('#', 'fill_return_indexes')))
        st.append((Compound_stmt, Fun_declaration_prime_node))
        st.append((Match, ('#', 'collect_return_indexes')))
        st.append((Match, ('#', 'create_AR')))
        st.append((Match, (')', Fun_declaration_prime_node)))
        st.append((Params, Fun_declaration_prime_node))
        st.append((Match, ('(', Fun_declaration_prime_node)))
        st.append((Match, ('#', 'collect_params')))
    elif (
            look_ahead == ('EOF', '$') or look_ahead[0] == 'ID' or look_ahead == ('SYMBOL', ';')
            or look_ahead[0] == 'NUM' or look_ahead == ('KEYWORD', 'int')
            or look_ahead == ('KEYWORD', 'void') or look_ahead == ('SYMBOL', '{')
            or look_ahead == ('SYMBOL', '}') or look_ahead == ('KEYWORD', 'break')
            or look_ahead == ('KEYWORD', 'if') or look_ahead == ('KEYWORD', 'repeat')
            or look_ahead == ('KEYWORD', 'return')
    ):
        e.write('#' + str(line_index) + ' : syntax error, missing Fun-declaration-prime' + '\n')
    else:
        st.append((Fun_declaration_prime, parent))
        Error()


def Type_specifier(parent):
    if look_ahead == ('KEYWORD', 'int'):
        Type_specifier_node = Node('Type-specifier', parent=parent)
        st.append((Match, ('int', Type_specifier_node)))
    elif look_ahead == ('KEYWORD', 'void'):
        Type_specifier_node = Node('Type-specifier', parent=parent)
        st.append((Match, ('void', Type_specifier_node)))
    elif look_ahead[0] == 'ID':
        e.write('#' + str(line_index) + ' : syntax error, missing Type-specifier' + '\n')
    else:
        st.append((Type_specifier, parent))
        Error()


def Params(parent):
    if look_ahead == ('KEYWORD', 'int'):
        Params_node = Node('Params', parent=parent)
        st.append((Param_list, Params_node))
        st.append((Param_prime, Params_node))
        st.append((Match, ('#', 'add_variable')))
        st.append((Match, ('ID', Params_node)))
        st.append((Match, ('#', 'save_id')))
        st.append((Match, ('int', Params_node)))
        st.append((Match, ('#', 'save_type')))
    elif look_ahead == ('KEYWORD', 'void'):
        Params_node = Node('Params', parent=parent)
        st.append((Match, ('void', Params_node)))
    elif look_ahead == ('SYMBOL', ')'):
        e.write('#' + str(line_index) + ' : syntax error, missing Params' + '\n')
    else:
        st.append((Params, parent))
        Error()


def Param_list(parent):
    if look_ahead == ('SYMBOL', ','):
        Param_list_node = Node('Param-list', parent=parent)
        st.append((Param_list, Param_list_node))
        st.append((Match, ('#', 'add_variable')))
        st.append((Param, Param_list_node))
        st.append((Match, (',', Param_list_node)))
    elif look_ahead == ('SYMBOL', ')'):
        Param_list_node = Node('Param-list', parent=parent)
        Node('epsilon', parent=Param_list_node)
    else:
        st.append((Param_list, parent))
        Error()


def Param(parent):
    if look_ahead == ('KEYWORD', 'int') or look_ahead == ('KEYWORD', 'void'):
        Param_node = Node('Param', parent=parent)
        st.append((Param_prime, Param_node))
        st.append((Declaration_initial, Param_node))
    elif look_ahead == ('SYMBOL', ')') or look_ahead == ('SYMBOL', ','):
        e.write('#' + str(line_index) + ' : syntax error, missing Param' + '\n')
    else:
        st.append((Param, parent))
        Error()


def Param_prime(parent):
    if look_ahead == ('SYMBOL', '['):
        Param_prime_node = Node('Param-prime', parent=parent)
        st.append((Match, (']', Param_prime_node)))
        st.append((Match, ('[', Param_prime_node)))
        st.append((Match, ('#', 'define_array_argument')))
    elif look_ahead == ('SYMBOL', ')') or look_ahead == ('SYMBOL', ','):
        Param_prime_node = Node('Param-prime', parent=parent)
        Node('epsilon', parent=Param_prime_node)
    else:
        st.append((Param_prime, parent))
        Error()


def Compound_stmt(parent):
    if look_ahead == ('SYMBOL', '{'):
        Compound_stmt_node = Node('Compound-stmt', parent=parent)
        st.append((Match, ('#', 'get_out_of_scope')))
        st.append((Match, ('}', Compound_stmt_node)))
        st.append((Statement_list, Compound_stmt_node))
        st.append((Declaration_list, Compound_stmt_node))
        st.append((Match, ('{', Compound_stmt_node)))
        st.append((Match, ('#', 'get_new_scope')))
    elif (
            look_ahead == ('EOF', '$') or look_ahead[0] == 'ID' or look_ahead == ('SYMBOL', ';')
            or look_ahead[0] == 'NUM' or look_ahead == ('SYMBOL', '(') or look_ahead == ('KEYWORD', 'int')
            or look_ahead == ('KEYWORD', 'void') or look_ahead == ('SYMBOL', '}') or look_ahead == ('KEYWORD', 'break')
            or look_ahead == ('KEYWORD', 'if') or look_ahead == ('KEYWORD', 'else')
            or look_ahead == ('KEYWORD', 'repeat') or look_ahead == ('KEYWORD', 'until')
            or look_ahead == ('KEYWORD', 'return')
    ):
        e.write('#' + str(line_index) + ' : syntax error, missing Compound-stmt' + '\n')
    else:
        st.append((Compound_stmt, parent))
        Error()


def Statement_list(parent):
    if (
            look_ahead[0] == 'ID' or look_ahead == ('SYMBOL', ';')
            or look_ahead[0] == 'NUM' or look_ahead == ('SYMBOL', '(') or look_ahead == ('SYMBOL', '{')
            or look_ahead == ('KEYWORD', 'break') or look_ahead == ('KEYWORD', 'if')
            or look_ahead == ('KEYWORD', 'repeat') or look_ahead == ('KEYWORD', 'return')
    ):
        Statement_list_node = Node('Statement-list', parent=parent)
        st.append((Statement_list, Statement_list_node))
        st.append((Statement, Statement_list_node))

    elif look_ahead == ('SYMBOL', '}'):
        Statement_list_node = Node('Statement-list', parent=parent)
        Node('epsilon', parent=Statement_list_node)
    else:
        st.append((Statement_list, parent))
        Error()


def Statement(parent):
    if look_ahead == ('SYMBOL', '{'):
        Statement_node = Node('Statement', parent=parent)
        st.append((Compound_stmt, Statement_node))
    elif (
            look_ahead[0] == 'ID' or look_ahead == ('SYMBOL', ';')
            or look_ahead[0] == 'NUM' or look_ahead == ('SYMBOL', '(') or look_ahead == ('KEYWORD', 'break')
    ):
        Statement_node = Node('Statement', parent=parent)
        st.append((Expression_stmt, Statement_node))
    elif look_ahead == ('KEYWORD', 'if'):
        Statement_node = Node('Statement', parent=parent)
        st.append((Selection_stmt, Statement_node))
    elif look_ahead == ('KEYWORD', 'repeat'):
        Statement_node = Node('Statement', parent=parent)
        st.append((Iteration_stmt, Statement_node))
    elif look_ahead == ('KEYWORD', 'return'):
        Statement_node = Node('Statement', parent=parent)
        st.append((Return_stmt, Statement_node))
    elif (
            look_ahead == ('SYMBOL', '}') or look_ahead == ('KEYWORD', 'else') or look_ahead == ('KEYWORD', 'until')
    ):
        e.write('#' + str(line_index) + ' : syntax error, missing Statement' + '\n')
    else:
        st.append((Statement, parent))
        Error()


def Expression_stmt(parent):
    if look_ahead[0] == 'ID' or look_ahead[0] == 'NUM' or look_ahead == ('SYMBOL', '('):
        Expression_stmt_node = Node('Expression-stmt', parent=parent)
        st.append((Match, ('#', 'pop_extras')))
        st.append((Match, (';', Expression_stmt_node)))
        st.append((Expression, Expression_stmt_node))

    elif look_ahead == ('KEYWORD', 'break'):
        Expression_stmt_node = Node('Expression-stmt', parent=parent)
        st.append((Match, ('#', 'save_break_address')))
        st.append((Match, (';', Expression_stmt_node)))
        st.append((Match, ('break', Expression_stmt_node)))

    elif look_ahead == ('SYMBOL', ';'):
        Expression_stmt_node = Node('Expression-stmt', parent=parent)
        st.append((Match, (';', Expression_stmt_node)))
    elif (
            look_ahead == ('SYMBOL', '{') or look_ahead == ('SYMBOL', '}') or look_ahead == ('KEYWORD', 'if')
            or look_ahead == ('KEYWORD', 'else') or look_ahead == ('KEYWORD', 'repeat')
            or look_ahead == ('KEYWORD', 'until') or look_ahead == ('KEYWORD', 'return')
    ):
        e.write('#' + str(line_index) + ' : syntax error, missing Expression-stmt' + '\n')
    else:
        st.append((Expression_stmt, parent))
        Error()


def Selection_stmt(parent):
    if look_ahead == ('KEYWORD', 'if'):
        Selection_stmt_node = Node('Selection-stmt', parent=parent)
        st.append((Match, ('#', 'jump')))
        st.append((Statement, Selection_stmt_node))
        st.append((Match, ('else', Selection_stmt_node)))
        st.append((Match, ('#', 'jpf')))
        st.append((Statement, Selection_stmt_node))
        st.append((Match, ('#', 'save_index')))
        st.append((Match, (')', Selection_stmt_node)))
        st.append((Expression, Selection_stmt_node))
        st.append((Match, ('(', Selection_stmt_node)))
        st.append((Match, ('if', Selection_stmt_node)))
    elif (
            look_ahead[0] == 'ID' or look_ahead == ('SYMBOL', ';') or look_ahead[0] == 'NUM'
            or look_ahead == ('SYMBOL', '(') or look_ahead == ('SYMBOL', '{') or look_ahead == ('SYMBOL', '}')
            or look_ahead == ('KEYWORD', 'break') or look_ahead == ('KEYWORD', 'else')
            or look_ahead == ('KEYWORD', 'repeat') or look_ahead == ('KEYWORD', 'until')
            or look_ahead == ('KEYWORD', 'return')
    ):
        e.write('#' + str(line_index) + ' : syntax error, missing Selection-stmt' + '\n')
    else:
        st.append((Selection_stmt, parent))
        Error()


def Iteration_stmt(parent):
    if look_ahead == ('KEYWORD', 'repeat'):
        Iteration_stmt_node = Node('Iteration-stmt', parent=parent)
        st.append((Match, ('#', 'until_jump')))
        st.append((Match, (')', Iteration_stmt_node)))
        st.append((Expression, Iteration_stmt_node))
        st.append((Match, ('(', Iteration_stmt_node)))
        st.append((Match, ('until', Iteration_stmt_node)))
        st.append((Statement, Iteration_stmt_node))
        st.append((Match, ('#', 'save_index')))
        st.append((Match, ('#', 'add_to_breaks')))
        st.append((Match, ('repeat', Iteration_stmt_node)))
    elif (
            look_ahead[0] == 'ID' or look_ahead == ('SYMBOL', ';') or look_ahead[0] == 'NUM'
            or look_ahead == ('SYMBOL', '(') or look_ahead == ('SYMBOL', '{') or look_ahead == ('SYMBOL', '}')
            or look_ahead == ('KEYWORD', 'break') or look_ahead == ('KEYWORD', 'if')
            or look_ahead == ('KEYWORD', 'else')
            or look_ahead == ('KEYWORD', 'until') or look_ahead == ('KEYWORD', 'return')
    ):
        e.write('#' + str(line_index) + ' : syntax error, missing Iteration-stmt' + '\n')
    else:
        st.append((Iteration_stmt, parent))
        Error()


def Return_stmt(parent):
    if look_ahead == ('KEYWORD', 'return'):
        Return_stmt_node = Node('Return-stmt', parent=parent)
        st.append((Match, ('#', 'save_returns')))
        st.append((Return_stmt_prime, Return_stmt_node))
        st.append((Match, ('return', Return_stmt_node)))

    elif (
            look_ahead[0] == 'ID' or look_ahead == ('SYMBOL', ';') or look_ahead[0] == 'NUM'
            or look_ahead == ('SYMBOL', '(') or look_ahead == ('SYMBOL', '{') or look_ahead == ('SYMBOL', '}')
            or look_ahead == ('KEYWORD', 'break') or look_ahead == ('KEYWORD', 'if')
            or look_ahead == ('KEYWORD', 'else') or look_ahead == ('KEYWORD', 'repeat')
            or look_ahead == ('KEYWORD', 'until')
    ):
        e.write('#' + str(line_index) + ' : syntax error, missing Return-stmt' + '\n')
    else:
        st.append((Return_stmt, parent))
        Error()


def Return_stmt_prime(parent):
    if look_ahead == ('SYMBOL', ';'):
        Return_stmt_prime_node = Node('Return-stmt-prime', parent=parent)
        st.append((Match, (';', Return_stmt_prime_node)))
        st.append((Match, ('#', 'push_index')))
    elif look_ahead[0] == 'ID' or look_ahead[0] == 'NUM' or look_ahead == ('SYMBOL', '('):
        Return_stmt_prime_node = Node('Return-stmt-prime', parent=parent)
        st.append((Match, (';', Return_stmt_prime_node)))
        st.append((Expression, Return_stmt_prime_node))
    elif (
            look_ahead == ('SYMBOL', '{') or look_ahead == ('SYMBOL', '}')
            or look_ahead == ('KEYWORD', 'break') or look_ahead == ('KEYWORD', 'if')
            or look_ahead == ('KEYWORD', 'else') or look_ahead == ('KEYWORD', 'repeat')
            or look_ahead == ('KEYWORD', 'until') or look_ahead == ('KEYWORD', 'return')
    ):
        e.write('#' + str(line_index) + ' : syntax error, missing Return-stmt-prime' + '\n')
    else:
        st.append((Return_stmt_prime, parent))
        Error()


def Expression(parent):
    if look_ahead[0] == 'ID':
        Expression_node = Node('Expression', parent=parent)
        st.append((B, Expression_node))
        st.append((Match, ('ID', Expression_node)))
        st.append((Match, ('#', 'push_id_address')))
    elif look_ahead[0] == 'NUM' or look_ahead == ('SYMBOL', '('):
        Expression_node = Node('Expression', parent=parent)
        st.append((Simple_expression_zegond, Expression_node))
    elif (
            look_ahead == ('SYMBOL', ';') or look_ahead == ('SYMBOL', ']') or look_ahead == ('SYMBOL', ')')
            or look_ahead == ('SYMBOL', ',')
    ):
        e.write('#' + str(line_index) + ' : syntax error, missing Expression' + '\n')
    else:
        st.append((Expression, parent))
        Error()


def B(parent):
    if look_ahead == ('SYMBOL', '='):
        B_node = Node('B', parent=parent)
        st.append((Match, ('#', 'result_to')))
        st.append((Expression, B_node))
        st.append((Match, ('=', B_node)))

    elif look_ahead == ('SYMBOL', '['):
        B_node = Node('B', parent=parent)
        st.append((H, B_node))
        st.append((Match, ('#', 'find_index')))
        st.append((Match, (']', B_node)))
        st.append((Expression, B_node))
        st.append((Match, ('[', B_node)))
    elif (
            look_ahead == ('SYMBOL', ';') or look_ahead == ('SYMBOL', ']') or look_ahead == ('SYMBOL', '(')
            or look_ahead == ('SYMBOL', ')')
            or look_ahead == ('SYMBOL', ',')
            or look_ahead == ('SYMBOL', '<') or look_ahead == ('SYMBOL', '==')
            or look_ahead == ('SYMBOL', '+') or look_ahead == ('SYMBOL', '-') or look_ahead == ('SYMBOL', '*')
    ):
        B_node = Node('B', parent=parent)
        st.append((Simple_expression_prime, B_node))
    else:
        st.append((B, parent))
        Error()


def H(parent):
    if look_ahead == ('SYMBOL', '='):
        H_node = Node('H', parent=parent)
        st.append((Match, ('#', 'result_to')))
        st.append((Expression, H_node))
        st.append((Match, ('=', H_node)))
    elif (
            look_ahead == ('SYMBOL', '<') or look_ahead == ('SYMBOL', '==')
            or look_ahead == ('SYMBOL', '+') or look_ahead == ('SYMBOL', '-') or look_ahead == ('SYMBOL', '*')
            or look_ahead == ('SYMBOL', ';') or look_ahead == ('SYMBOL', ']') or look_ahead == ('SYMBOL', ')')
            or look_ahead == ('SYMBOL', ',')
    ):
        H_node = Node('H', parent=parent)
        st.append((C, H_node))
        st.append((D, H_node))
        st.append((G, H_node))
    else:
        st.append((H, parent))
        Error()


def Simple_expression_zegond(parent):
    if look_ahead[0] == 'NUM' or look_ahead == ('SYMBOL', '('):
        Simple_expression_zegond_node = Node('Simple-expression-zegond', parent=parent)
        st.append((C, Simple_expression_zegond_node))
        st.append((Additive_expression_zegond, Simple_expression_zegond_node))
    elif (
            look_ahead == ('SYMBOL', ';') or look_ahead == ('SYMBOL', ']')
            or look_ahead == ('SYMBOL', ')') or look_ahead == ('SYMBOL', ',')
    ):
        e.write('#' + str(line_index) + ' : syntax error, missing Simple-expression-zegond' + '\n')
    else:
        st.append((Simple_expression_zegond, parent))
        Error()


def Simple_expression_prime(parent):
    if (
            look_ahead == ('SYMBOL', '(') or look_ahead == ('SYMBOL', '<') or look_ahead == ('SYMBOL', '==')
            or look_ahead == ('SYMBOL', '+') or look_ahead == ('SYMBOL', '-') or look_ahead == ('SYMBOL', '*')
            or look_ahead == ('SYMBOL', ';') or look_ahead == ('SYMBOL', ']') or look_ahead == ('SYMBOL', ')')
            or look_ahead == ('SYMBOL', ',')
    ):
        Simple_expression_prime_node = Node('Simple-expression-prime', parent=parent)
        st.append((C, Simple_expression_prime_node))
        st.append((Additive_expression_prime, Simple_expression_prime_node))
    else:
        st.append((Simple_expression_prime, parent))
        Error()


def C(parent):
    if look_ahead == ('SYMBOL', '<') or look_ahead == ('SYMBOL', '=='):
        C_node = Node('C', parent=parent)
        st.append((Match, ('#', 'make_op')))
        st.append((Additive_expression, C_node))
        st.append((Relop, C_node))
        st.append((Match, ('#', 'save_op')))
    elif (
            look_ahead == ('SYMBOL', ';') or look_ahead == ('SYMBOL', ']')
            or look_ahead == ('SYMBOL', ')') or look_ahead == ('SYMBOL', ',')
    ):
        C_node = Node('C', parent=parent)
        Node('epsilon', C_node)
    else:
        st.append((C, parent))
        Error()


def Relop(parent):
    if look_ahead == ('SYMBOL', '<'):
        Relop_node = Node('Relop', parent=parent)
        st.append((Match, ('<', Relop_node)))
    elif look_ahead == ('SYMBOL', '=='):
        Relop_node = Node('Relop', parent=parent)
        st.append((Match, ('==', Relop_node)))
    elif look_ahead[0] == 'ID' or look_ahead[0] == 'NUM' or look_ahead == ('SYMBOL', '('):
        e.write('#' + str(line_index) + ' : syntax error, missing Relop' + '\n')
    else:
        st.append((Relop, parent))
        Error()


def Additive_expression(parent):
    if look_ahead[0] == 'ID' or look_ahead[0] == 'NUM' or look_ahead == ('SYMBOL', '('):
        Additive_expression_node = Node('Additive-expression', parent=parent)
        st.append((D, Additive_expression_node))
        st.append((Term, Additive_expression_node))
    elif (
            look_ahead == ('SYMBOL', ';') or look_ahead == ('SYMBOL', ']')
            or look_ahead == ('SYMBOL', ')') or look_ahead == ('SYMBOL', ',')
    ):
        e.write('#' + str(line_index) + ' : syntax error, missing Additive-expression' + '\n')
    else:
        st.append((Additive_expression, parent))
        Error()


def Additive_expression_prime(parent):
    if (
            look_ahead == ('SYMBOL', '(')
            or look_ahead == ('SYMBOL', '+') or look_ahead == ('SYMBOL', '-') or look_ahead == ('SYMBOL', '*')
            or look_ahead == ('SYMBOL', ';') or look_ahead == ('SYMBOL', ']') or look_ahead == ('SYMBOL', ')')
            or look_ahead == ('SYMBOL', ',') or look_ahead == ('SYMBOL', '<')
            or look_ahead == ('SYMBOL', '==')
    ):
        Additive_expression_prime_node = Node('Additive-expression-prime', parent=parent)
        st.append((D, Additive_expression_prime_node))
        st.append((Term_prime, Additive_expression_prime_node))
    else:
        st.append((Additive_expression_prime, parent))
        Error()


def Additive_expression_zegond(parent):
    if look_ahead[0] == 'NUM' or look_ahead == ('SYMBOL', '('):
        Additive_expression_zegond_node = Node('Additive-expression-zegond', parent=parent)
        st.append((D, Additive_expression_zegond_node))
        st.append((Term_zegond, Additive_expression_zegond_node))
    elif (
            look_ahead == ('SYMBOL', ';') or look_ahead == ('SYMBOL', ']')
            or look_ahead == ('SYMBOL', ')') or look_ahead == ('SYMBOL', ',') or look_ahead == ('SYMBOL', '<')
            or look_ahead == ('SYMBOL', '==')
    ):
        e.write('#' + str(line_index) + ' : syntax error, missing Additive-expression-zegond' + '\n')
    else:
        st.append((Additive_expression_zegond, parent))
        Error()


def D(parent):
    if look_ahead == ('SYMBOL', '+') or look_ahead == ('SYMBOL', '-'):
        D_node = Node('D', parent=parent)
        st.append((D, D_node))
        st.append((Match, ('#', 'make_op')))
        st.append((Term, D_node))
        st.append((Addop, D_node))
        st.append((Match, ('#', 'save_op')))
    elif (
            look_ahead == ('SYMBOL', ';') or look_ahead == ('SYMBOL', ']')
            or look_ahead == ('SYMBOL', ')') or look_ahead == ('SYMBOL', ',') or look_ahead == ('SYMBOL', '<')
            or look_ahead == ('SYMBOL', '==')
    ):
        D_node = Node('D', parent=parent)
        Node('epsilon', parent=D_node)
    else:
        st.append((D, parent))
        Error()


def Addop(parent):
    if look_ahead == ('SYMBOL', '+'):
        Addop_node = Node('Addop', parent=parent)
        st.append((Match, ('+', Addop_node)))
    elif look_ahead == ('SYMBOL', '-'):
        Addop_node = Node('Addop', parent=parent)
        st.append((Match, ('-', Addop_node)))
    elif look_ahead[0] == 'ID' or look_ahead[0] == 'NUM' or look_ahead == ('SYMBOL', '('):
        e.write('#' + str(line_index) + ' : syntax error, missing Additive-expression-zegond' + '\n')
    else:
        st.append((Addop, parent))
        Error()


def Term(parent):
    if look_ahead[0] == 'ID' or look_ahead[0] == 'NUM' or look_ahead == ('SYMBOL', '('):
        Term_node = Node('Term', parent=parent)
        st.append((G, Term_node))
        st.append((Factor, Term_node))
    elif (
            look_ahead == ('SYMBOL', ';') or look_ahead == ('SYMBOL', ']')
            or look_ahead == ('SYMBOL', ')') or look_ahead == ('SYMBOL', ',')
            or look_ahead == ('SYMBOL', '<') or look_ahead == ('SYMBOL', '==')
            or look_ahead == ('SYMBOL', '+') or look_ahead == ('SYMBOL', '-')
    ):
        e.write('#' + str(line_index) + ' : syntax error, missing Term' + '\n')
    else:
        st.append((Term, parent))
        Error()


def Term_prime(parent):
    if (
            look_ahead == ('SYMBOL', '(') or look_ahead == ('SYMBOL', '*')
            or look_ahead == ('SYMBOL', ';') or look_ahead == ('SYMBOL', ']')
            or look_ahead == ('SYMBOL', ')') or look_ahead == ('SYMBOL', ',')
            or look_ahead == ('SYMBOL', '<') or look_ahead == ('SYMBOL', '==')
            or look_ahead == ('SYMBOL', '+') or look_ahead == ('SYMBOL', '-')
    ):
        Term_prime_node = Node('Term-prime', parent=parent)
        st.append((G, Term_prime_node))
        st.append((Factor_prime, Term_prime_node))
    else:
        st.append((Term_prime, parent))
        Error()


def Term_zegond(parent):
    if look_ahead[0] == 'NUM' or look_ahead == ('SYMBOL', '('):
        Term_zegond_node = Node('Term-zegond', parent=parent)
        st.append((G, Term_zegond_node))
        st.append((Factor_zegond, Term_zegond_node))

    elif (
            look_ahead == ('SYMBOL', ';') or look_ahead == ('SYMBOL', ']')
            or look_ahead == ('SYMBOL', ')') or look_ahead == ('SYMBOL', ',')
            or look_ahead == ('SYMBOL', '<') or look_ahead == ('SYMBOL', '==')
            or look_ahead == ('SYMBOL', '+') or look_ahead == ('SYMBOL', '-')
    ):
        e.write('#' + str(line_index) + ' : syntax error, missing Term-zegond' + '\n')
    else:
        st.append((Term_zegond, parent))
        Error()


def G(parent):
    if look_ahead == ('SYMBOL', '*'):
        G_node = Node('G', parent=parent)
        st.append((G, G_node))
        st.append((Match, ('#', 'mult')))
        st.append((Factor, G_node))
        st.append((Match, ('*', G_node)))
    elif (
            look_ahead == ('SYMBOL', ';') or look_ahead == ('SYMBOL', ']')
            or look_ahead == ('SYMBOL', ')') or look_ahead == ('SYMBOL', ',')
            or look_ahead == ('SYMBOL', '<') or look_ahead == ('SYMBOL', '==')
            or look_ahead == ('SYMBOL', '+') or look_ahead == ('SYMBOL', '-')
    ):
        G_node = Node('G', parent=parent)
        Node('epsilon', G_node)
    else:
        st.append((G, parent))
        Error()


def Factor(parent):
    if look_ahead[0] == 'ID':
        Factor_node = Node('Factor', parent=parent)
        st.append((Var_call_prime, Factor_node))
        st.append((Match, ('ID', Factor_node)))
        st.append((Match, ('#', 'save_id')))
    elif look_ahead[0] == 'NUM':
        Factor_node = Node('Factor', parent=parent)
        st.append((Match, ('NUM', Factor_node)))
        st.append((Match, ('#', 'save_num')))
    elif look_ahead == ('SYMBOL', '('):
        Factor_node = Node('Factor', parent=parent)
        st.append((Match, (')', Factor_node)))
        st.append((Expression, Factor_node))
        st.append((Match, ('(', Factor_node)))
    elif (
            look_ahead == ('SYMBOL', ';') or look_ahead == ('SYMBOL', ']')
            or look_ahead == ('SYMBOL', ')') or look_ahead == ('SYMBOL', ',')
            or look_ahead == ('SYMBOL', '<') or look_ahead == ('SYMBOL', '==')
            or look_ahead == ('SYMBOL', '+') or look_ahead == ('SYMBOL', '-')
            or look_ahead == ('SYMBOL', '*')
    ):
        e.write('#' + str(line_index) + ' : syntax error, missing Factor' + '\n')
    else:
        st.append((Factor, parent))
        Error()


def Var_call_prime(parent):
    if look_ahead == ('SYMBOL', '('):
        Var_call_prime_node = Node('Var-call-prime', parent=parent)
        st.append((Match, ('#', 'call_function')))
        st.append((Match, (')', Var_call_prime_node)))
        st.append((Args, Var_call_prime_node))
        st.append((Match, ('(', Var_call_prime_node)))
    elif (
            look_ahead == ('SYMBOL', '[')
            or look_ahead == ('SYMBOL', ';') or look_ahead == ('SYMBOL', ']')
            or look_ahead == ('SYMBOL', ')') or look_ahead == ('SYMBOL', ',')
            or look_ahead == ('SYMBOL', '<') or look_ahead == ('SYMBOL', '==')
            or look_ahead == ('SYMBOL', '+') or look_ahead == ('SYMBOL', '-')
            or look_ahead == ('SYMBOL', '*')
    ):
        Var_call_prime_node = Node('Var-call-prime', parent=parent)
        st.append((Var_prime, Var_call_prime_node))
    else:
        st.append((Var_call_prime, parent))
        Error()


def Var_prime(parent):
    if look_ahead == ('SYMBOL', '['):
        Var_prime_node = Node('Var-prime', parent=parent)
        st.append((Match, ('#', 'find_index')))
        st.append((Match, (']', Var_prime_node)))
        st.append((Expression, Var_prime_node))
        st.append((Match, ('[', Var_prime_node)))
    elif (
            look_ahead == ('SYMBOL', ';') or look_ahead == ('SYMBOL', ']')
            or look_ahead == ('SYMBOL', ')') or look_ahead == ('SYMBOL', ',')
            or look_ahead == ('SYMBOL', '<') or look_ahead == ('SYMBOL', '==')
            or look_ahead == ('SYMBOL', '+') or look_ahead == ('SYMBOL', '-')
            or look_ahead == ('SYMBOL', '*')
    ):
        Var_prime_node = Node('Var-prime', parent=parent)
        Node('epsilon', Var_prime_node)
    else:
        st.append((Var_prime, parent))
        Error()


def Factor_prime(parent):
    if look_ahead == ('SYMBOL', '('):
        Factor_prime_node = Node('Factor-prime', parent=parent)
        st.append((Match, ('#', 'call_function')))
        st.append((Match, (')', Factor_prime_node)))
        st.append((Args, Factor_prime_node))
        st.append((Match, ('(', Factor_prime_node)))
    elif (
            look_ahead == ('SYMBOL', ';') or look_ahead == ('SYMBOL', ']')
            or look_ahead == ('SYMBOL', ')') or look_ahead == ('SYMBOL', ',')
            or look_ahead == ('SYMBOL', '<') or look_ahead == ('SYMBOL', '==')
            or look_ahead == ('SYMBOL', '+') or look_ahead == ('SYMBOL', '-')
            or look_ahead == ('SYMBOL', '*')
    ):
        Factor_prime_node = Node('Factor-prime', parent=parent)
        Node('epsilon', Factor_prime_node)
    else:
        st.append((Factor_prime, parent))
        Error()


def Factor_zegond(parent):
    if look_ahead == ('SYMBOL', '('):
        Factor_zegond_node = Node('Factor-zegond', parent=parent)
        st.append((Match, (')', Factor_zegond_node)))
        st.append((Expression, Factor_zegond_node))
        st.append((Match, ('(', Factor_zegond_node)))
    elif look_ahead[0] == 'NUM':
        Factor_zegond_node = Node('Factor-zegond', parent=parent)
        st.append((Match, ('NUM', Factor_zegond_node)))
        st.append((Match, ('#', 'save_num')))
    elif (
            look_ahead == ('SYMBOL', ';') or look_ahead == ('SYMBOL', ']')
            or look_ahead == ('SYMBOL', ')') or look_ahead == ('SYMBOL', ',')
            or look_ahead == ('SYMBOL', '<') or look_ahead == ('SYMBOL', '==')
            or look_ahead == ('SYMBOL', '+') or look_ahead == ('SYMBOL', '-')
            or look_ahead == ('SYMBOL', '*')
    ):
        e.write('#' + str(line_index) + ' : syntax error, missing Factor-zegond' + '\n')
    else:
        st.append((Factor_zegond, parent))
        Error()


def Args(parent):
    if look_ahead[0] == 'ID' or look_ahead[0] == 'NUM' or look_ahead == ('SYMBOL', '('):
        Args_node = Node('Args', parent=parent)
        st.append((Arg_list, Args_node))
    elif look_ahead == ('SYMBOL', ')'):
        Args_node = Node('Args', parent=parent)
        Node('epsilon', Args_node)
    else:
        st.append((Args, parent))
        Error()


def Arg_list(parent):
    if look_ahead[0] == 'ID' or look_ahead[0] == 'NUM' or look_ahead == ('SYMBOL', '('):
        Arg_list_node = Node('Arg-list', parent=parent)
        st.append((Arg_list_prime, Arg_list_node))
        st.append((Expression, Arg_list_node))

    elif look_ahead == ('SYMBOL', ')'):
        e.write('#' + str(line_index) + ' : syntax error, missing Arg-list' + '\n')
    else:
        st.append((Arg_list, parent))
        Error()


def Arg_list_prime(parent):
    if look_ahead == ('SYMBOL', ','):
        Arg_list_prime_node = Node('Arg-list-prime', parent=parent)
        st.append((Arg_list_prime, Arg_list_prime_node))
        st.append((Expression, Arg_list_prime_node))
        st.append((Match, (',', Arg_list_prime_node)))
    elif look_ahead == ('SYMBOL', ')'):
        Arg_list_prime_node = Node('Arg-list-prime', parent=parent)
        Node('epsilon', Arg_list_prime_node)
    else:
        st.append((Arg_list_prime, parent))
        Error()
