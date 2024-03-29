class CodeGenerator:
    """
                symbol table :
                [
                    id | lexim | scope | address | type
                ]
    """

    '''
        function table :
            name | vars | return_value | return_to | jump_index | scope
    '''

    '''
       parameters :
                lexim | scope | address | type
    '''

    '''
        return_indexes :
                index | return_value
    
    '''

    def __init__(self):
        self.temps = []
        self.last_id = 0
        self.current_scope = 0
        self.last_address = 0
        self.last_index = 0
        self.function_table = []
        self.scope_stack = []
        self.dec_type = ""
        self.stack = list()
        self.params = list()
        self.generated_code = dict()
        self.break_states = list()
        self.return_indexes = []
        self.symbol_table = []

    def call_routine(self, routine_name, look_ahead):
        print(self.stack)
        self.__getattribute__(routine_name)(look_ahead)
        print(self.last_index)

    def get_temp_address(self, number_of_words=1):
        number_of_words = int(number_of_words)
        start_address = self.last_address
        for i in range(number_of_words):
            self.generated_code[self.last_index] = f'(ASSIGN, #0, {self.last_address}, )'
            self.temps.append(self.last_address)
            self.last_index += 1
            self.last_address += 4
        return str(start_address)

    # save the_type_of_dec
    def save_type(self, lookahead):
        self.dec_type = lookahead

    def save_id(self, lookahead):
        self.stack.append(lookahead[1])

    def add_variable(self, lookahead):
        var_name = self.stack.pop()
        var_address = self.get_temp_address()
        self.symbol_table.append((self.last_id, var_name, self.current_scope, var_address, "int"))
        self.last_id += 1

    def add_variable_params(self, lookahead):
        var_name = self.stack.pop()
        var_address = self.get_temp_address()
        self.symbol_table.append((self.last_id, var_name, self.current_scope + 1, var_address, "int"))
        self.params.append((self.last_id, var_name, self.current_scope + 1, var_address, "int"))
        self.last_id += 1

    def save_num(self, lookahead):
        self.stack.append('#' + str(lookahead[1]))

    def save_array(self, lookahead):
        size = lookahead[1]
        array_name = self.stack.pop()
        var_address = self.get_temp_address()
        array_address = self.get_temp_address(size)
        self.generated_code[self.last_index] = f'(ASSIGN, #{array_address}, {var_address}, )'
        self.last_index += 1
        self.symbol_table.append((self.last_id, array_name, self.current_scope, var_address, "int[]"))
        self.last_id += 1

    def result_to(self, lookahead):
        value = self.stack.pop()
        address = self.stack.pop()
        self.generated_code[self.last_index] = f'(ASSIGN, {str(value)}, {str(address)}, )'
        self.last_index += 1
        self.stack.append(address)

    def find_index(self, lookahead):
        index_of_array = self.stack.pop()
        array_pointer = self.stack.pop()
        t1 = self.get_temp_address()
        t2 = self.get_temp_address()
        t3 = self.get_temp_address()
        self.generated_code[self.last_index] = f'(ASSIGN, {str(array_pointer)}, {t1}, )'
        self.last_index += 1
        self.generated_code[self.last_index] = f'(MULT, #4, {str(index_of_array)}, {t2})'
        self.last_index += 1
        self.generated_code[self.last_index] = f'(ADD, {t1}, {t2}, {t1})'
        self.last_index += 1
        self.stack.append(f'@{t1}')

    def get_new_scope(self, lookahead):
        self.current_scope += 1

    def get_out_of_scope(self, lookahead):
        ids = self.symbol_table
        for i in reversed(ids):
            if i[2] == self.current_scope:
                self.symbol_table.remove(i)
        self.current_scope -= 1

    '''
        pop the address of lhs
    '''

    def pop_extras(self, lookahead):
        self.stack.pop()

    def save_break_address(self, lookahead):
        self.break_states.append(self.last_index)
        self.last_index += 1

    def save_index(self, lookahead):
        self.stack.append(self.last_index)
        self.last_index += 1

    def jpf(self, lookahead):
        jump_to = self.stack.pop()
        condition = self.stack.pop()
        self.generated_code[jump_to] = f"(JPF, {condition}, {self.last_index + 1}, )"
        self.save_index(lookahead)

    def jump(self, lookahead):
        destination = self.stack.pop()
        self.generated_code[destination] = f"(JP, {self.last_index}, , )"

    def add_to_breaks(self, lookahead):
        self.break_states.append("new-break")

    def until_jump(self, lookahead):
        condition = self.stack.pop()
        repeat_start = self.stack.pop()
        self.generated_code[repeat_start] = f'(ASSIGN, #0, {self.get_temp_address()}, )'
        self.generated_code[self.last_index] = f'(JPF, {condition}, {repeat_start}, )'
        self.last_index += 1
        last_break = 0
        for i in reversed(range(len(self.break_states))):
            if self.break_states[i] == "new-break":
                last_break = i
                break
        print(last_break)
        breaks = self.break_states[last_break + 1:]
        print(breaks)
        print(self.break_states)
        for i in self.break_states[last_break + 1:]:
            self.generated_code[i] = f"(JP, {self.last_index}, , )"

        self.break_states = self.break_states[:last_break]

    def push_to_stack(self, inp):
        print(inp)
        self.generated_code[self.last_index] = f'(ASSIGN, {inp}, @0, )'
        print(inp)
        self.last_index += 1
        self.generated_code[self.last_index] = f'(SUB, 0, #4, 0)'
        self.last_index += 1


    def start(self, lookahead):
        self.get_temp_address()
        self.generated_code[self.last_index] = f'(ASSIGN, #5000, 0, )'
        self.last_index += 1

    def get_into_function(self, lookahead):
        if self.stack[-1] != 'output':
            func = 0
            args = []
            for i in self.stack[::-1]:
                if isinstance(i, tuple):
                    func = i
                    break
                args.append(i)
            args.reverse()
            func_args = func[1]
            print(func_args, func)
            self.push_to_stack(func[3])

            for i in range(len(func_args)):
                self.push_to_stack(func_args[i][3])
            cnt = 0
            for i in reversed(range(len(self.temps))):
                if self.temps[i] == 'new_func':
                    cnt = i
                    break
                self.push_to_stack(self.temps[i])

            for i in range(len(args)):
                var = func_args[i][3]
                value = args[i]
                self.generated_code[self.last_index] = f'(ASSIGN, {str(value)}, {str(var)}, )'
                self.last_index += 1
                self.stack.pop()
            self.stack.pop()

            print(func)

            self.generated_code[self.last_index] = f'(ASSIGN, #{self.last_index + 2}, {func[3]}, )'
            self.last_index += 1

            self.generated_code[self.last_index] = f'(JP, {func[4]}, , )'
            self.last_index += 1

            for i in reversed(range(len(func_args))):
                self.generated_code[self.last_index] = '(ADD, 0, #4, 0)'
                self.last_index += 1
                self.generated_code[self.last_index] = f'(ASSIGN, @0, {func_args[i][3]}, )'
                self.last_index += 1
            for i in range(cnt, len(self.temps)):
                self.generated_code[self.last_index] = '(ADD, 0, #4, 0)'
                self.last_index += 1
                self.generated_code[self.last_index] = f'(ASSIGN, @0, {self.temps[i]}, )'
                self.last_index += 1
            self.generated_code[self.last_index] = '(ADD, 0, #4, 0)'
            self.last_index += 1
            self.generated_code[self.last_index] = f'(ASSIGN, @0, {func[3]}, )'
            self.last_index += 1

            result = self.get_temp_address()
            self.generated_code[self.last_index] = f'(ASSIGN, {func[2]}, {result}, )'
            self.last_index += 1
            print(func)

            self.stack.append(result)
            print(self.symbol_table)

    def output(self, lookahead):
        if self.stack[-2] == 'output':
            self.generated_code[self.last_index] = f'(PRINT, {self.stack.pop()}, , )'
            self.last_index += 1

    def find_address(self, lookahead):
        if lookahead[1] == 'output':
            self.stack.append(lookahead[1])
        else:
            for record in self.symbol_table[::-1]:
                if record[1] == lookahead[1]:
                    if record[4] == 'function':
                        func = self.function_table[record[3]]
                        self.stack.append(func)
                    else:
                        print(record)
                        self.stack.append(record[3])
                    break

    def mult(self, lookahead):
        a = self.stack.pop()
        b = self.stack.pop()
        temp = self.get_temp_address()
        self.generated_code[self.last_index] = f'(MULT, {a}, {b}, {temp})'
        self.last_index += 1
        self.stack.append(temp)

    def save_op(self, lookahead):
        self.stack.append(lookahead[1])

    def make_op(self, lookahead):
        a = self.stack.pop()
        op = self.stack.pop()
        b = self.stack.pop()
        temp = self.get_temp_address()
        print(temp)

        if op == '+':
            self.generated_code[self.last_index] = f'(ADD, {b}, {a}, {temp})'
            self.last_index += 1
        elif op == '-':
            self.generated_code[self.last_index] = f'(SUB, {b}, {a}, {temp})'
            self.last_index += 1
        elif op == '<':
            self.generated_code[self.last_index] = f'(LT, {b}, {a}, {temp})'
            self.last_index += 1
        elif op == '==':
            self.generated_code[self.last_index] = f'(EQ, {b}, {a}, {temp})'
            self.last_index += 1
        self.stack.append(temp)

    def collect_params(self, lookahead):
        self.params.append('|new_func|')

    def create_AR(self, lookahead):
        return_to = self.get_temp_address()
        self.stack.append(self.last_index)
        self.last_index += 1
        self.temps.append("new_func")
        jump_to = self.last_index
        return_value = self.get_temp_address()
        self.stack.append(return_to)
        self.stack.append(return_value)
        func_name = self.stack[-4]


        func_vars = self.params[self.params.index('|new_func|'):]


        self.params = self.params[:self.params.index('|new_func|')]
        func_vars = func_vars[1:]

        AR = (func_name, func_vars, return_value, return_to, jump_to, self.current_scope)
        self.function_table.append(AR)
        self.symbol_table.append(
            (self.last_id, func_name, self.current_scope, len(self.function_table) - 1, "function"))
        self.last_id += 1
        print(self.function_table)

    def collect_return_indexes(self, lookahead):
        self.return_indexes.append("|func_returns|")

    def fill_return_indexes(self, lookahead):
        last_returns_index = len(self.return_indexes)
        for i in reversed(range(last_returns_index)):
            if self.return_indexes[i] == '|func_returns|':
                last_returns_index = i
                break
        return_indexes = self.return_indexes[last_returns_index:]
        return_indexes = return_indexes[1:]
        self.return_indexes = self.return_indexes[:last_returns_index]
        print(self.stack)
        return_value = self.stack.pop()
        return_to = self.stack.pop()
        for index in return_indexes:
            self.generated_code[index[0]] = f'(ASSIGN, {index[1]}, {return_value}, )'
            self.generated_code[index[0] + 1] = f'(JP, @{return_to}, , )'

        # for void functions
        if self.stack[-2] != "main":
            self.generated_code[self.last_index] = f'(JP, @{return_to}, , )'
            self.last_index += 1

        print(self.stack)
        jump_over_index = self.stack.pop()
        func_name = self.stack.pop()
        print(jump_over_index)
        if func_name != 'main':
            self.generated_code[jump_over_index] = f'(JP, {self.last_index}, , )'
        else:
            self.generated_code[jump_over_index] = f'(ASSIGN, #0, {self.get_temp_address()}, )'
        print(self.symbol_table)
        for i in reversed(range(len(self.temps))):
            if self.temps[i] == 'new_func':
                self.temps = self.temps[:i]
                break

    def save_returns(self, lookahead):
        self.return_indexes.append((self.last_index, self.stack.pop()))
        self.last_index += 2

    def fake_value(self, lookahead):
        self.stack.append('0')
