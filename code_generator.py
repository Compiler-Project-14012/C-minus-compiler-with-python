from scanner import symbol_table


class CodeGenerator:
    """
                symbol table :
                keywords : [] ,
                ids : [
                    id | lexim | scope | address | type
                ]
    """

    '''
        function table :
            name | vars | return_value_address | return_address | jump_index | scope
    '''

    def __init__(self):
        self.last_id = 0
        self.function_table = []
        self.scope_stack = []
        self.current_scope = 0
        self.last_address = 0
        self.dec_type = ""
        self.stack = list()
        self.generated_code = dict()
        self.last_index = 0
        self.break_states = list()
        self.return_values = []

    def call_routine(self, routine_name, look_ahead):
        self.__getattribute__(routine_name)(look_ahead)

    def get_temp_address(self, number_of_words):
        start_address = self.last_address
        for i in range(number_of_words):
            self.add_code("ASSIGN", "#0", str(self.last_address))
            self.last_address += 4
        return str(start_address)

    # save the_type_of_dec
    def save_type(self, lookahead):
        self.dec_type = lookahead

    def save_id(self, lookahead):
        self.stack.append(lookahead[1])

    def add_variable(self, lookahead):
        var_name = self.stack.pop()
        var_address = self.get_temp_address(1)
        symbol_table["ids"].append((self.last_index, var_name, self.current_scope, var_address, "int"))
        self.last_id += 1

    def save_array(self, lookahead):
        size = lookahead[1]
        array_name = self.stack.pop()
        var_address = self.get_temp_address(1)
        array_address = self.get_temp_address(size)
        self.generated_code[self.last_index] = f'(ASSIGN, #{array_address}, {var_address}, )'
        self.last_index += 1
        symbol_table["ids"].append((array_address, array_name, "Integer[]", self.current_scope))
        self.last_id += 1

    def add_code(self, first_operand, second_operand, third_operand='', fourth_operand=''):
        self.generated_code[self.last_index] = f'({first_operand}, {second_operand}, {third_operand}, {fourth_operand})'
        self.last_index += 1

    def save_var_address(self, lookahead):
        var_address = ""
        for symbole in symbol_table.get("ids")[::-1]:
            if lookahead[1] == symbole[1]:
                var_address = symbole[3]
                break
        self.stack.append(var_address)

    def result_to(self, lookahead):
        value = self.stack.pop()
        address = self.stack.pop()
        self.generated_code[self.last_index] = f'(ASSIGN, {str(value)}, {str(address)}, )'
        self.last_index += 1
        self.stack.pop()

    def find_index(self, lookahead):
        index_of_array = self.stack.pop()
        array_pointer = self.stack.pop()
        t1 = self.get_temp_address(1)
        t2 = self.get_temp_address(1)
        t3 = self.get_temp_address(1)
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
        ids = symbol_table["ids"]
        for i in reversed(ids):
            if i[3] == self.current_scope:
                symbol_table["ids"].remove(i)
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
        self.generated_code[self.last_index] = f'(JPF, {self.stack.pop()}, {self.last_index + 2}, )'
        self.last_index += 1
        self.generated_code[self.last_index] = f'(JP, {self.stack.pop()}, , )'
        self.last_index += 1
        last_break = 0
        for index, i in enumerate(reversed(self.break_states)):
            if i == "new-break":
                last_break = index
        for i in self.break_states[last_break + 1:]:
            self.generated_code[i] = f"(JP, {self.last_index}, , )"

        self.break_states = self.break_states[:last_break]
