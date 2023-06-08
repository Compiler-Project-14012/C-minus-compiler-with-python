S = [";", ":", ",", "[", "]", "(", ")", "{", "}", "+", "-", "*", "<", "="]
D = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
L = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w',
     'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T',
     'U', 'V', 'W', 'X', 'Y', 'Z']
W = [13, 10, 9, 11, 12, 32, 0]
key_words = ["if", "else", "void", "int", "repeat", "break", "until", "return"]
line_number = 1
index = 0
symbol_table = {}


def put_keywords_in_table():
    symbol_table = {}
    for key in key_words:
        symbol_table[len(symbol_table) + 1] = key
    return symbol_table


def get_next_token(text):
    global index
    global line_number
    current_state = 0
    start_index = index
    end_index = index
    error = ""

    while True:

        if current_state == 0:
            char = text[end_index]
            if D.__contains__(char):
                current_state = 1
                end_index += 1
            elif L.__contains__(char):
                current_state = 3
                end_index += 1
            elif S.__contains__(char) and char != "=" and char != "*":
                current_state = 5
                end_index += 1
            elif char == "*":
                current_state = 14
                end_index += 1
            elif char == "=":
                current_state = 6
                end_index += 1
            elif text[end_index] == "/":
                current_state = 9
                end_index += 1
            elif W.__contains__(ord(char)):
                current_state = 13
                end_index += 1
            else:
                end_index += 1
                error = error + text[start_index:end_index]
                start_index = end_index
                return start_index, end_index, "ERROR-Invalid input", error

        elif current_state == 1:
            char = text[end_index]
            if D.__contains__(char):
                current_state = 1
                end_index += 1
            elif W.__contains__(ord(char)) or S.__contains__(char) or char == "/":
                current_state = 2
                end_index += 1
            else:
                end_index += 1
                error = error + text[start_index:end_index]
                start_index = end_index
                return start_index, end_index, "ERROR-Invalid number", error

        elif current_state == 2:
            return start_index, end_index - 1, "NUM", error
        elif current_state == 3:
            char = text[end_index]
            if L.__contains__(char) or D.__contains__(char):
                current_state = 3
                end_index += 1
            elif S.__contains__(char) or W.__contains__(ord(char)) or char == "/":
                current_state = 4
                end_index += 1
            else:
                end_index += 1
                error = error + text[start_index:end_index]
                start_index = end_index
                return start_index, end_index, "ERROR-Invalid input", error

        elif current_state == 4:
            if key_words.__contains__(text[start_index: end_index - 1]):
                return start_index, end_index - 1, "KEYWORD", error
            else:
                return start_index, end_index - 1, "ID", error
        elif current_state == 5:
            return start_index, end_index, "SYMBOL", error
        elif current_state == 6:
            char = text[end_index]
            if char == "=":
                current_state = 8
                end_index += 1
            elif D.__contains__(char) or L.__contains__(char) or S.__contains__(char) or W.__contains__(ord(char)) \
                    or char == "/":
                current_state = 7
                end_index += 1
            else:
                end_index += 1
                error = error + text[start_index:end_index]
                start_index = end_index
                return start_index, end_index, "ERROR-Invalid input", error
        elif current_state == 7:
            return start_index, end_index - 1, "SYMBOL", error
        elif current_state == 8:
            return start_index, end_index, "SYMBOL", error
        elif current_state == 9:
            char = text[end_index]
            if char == "*":
                current_state = 10
                end_index += 1
            elif D.__contains__(char) or L.__contains__(char) or S.__contains__(char) or W.__contains__(ord(char)) \
                    or char == "/":
                error = error + text[start_index:end_index]
                start_index = end_index
                return start_index, end_index, "ERROR-Invalid input", error
            else:
                end_index += 1
                error = error + text[start_index:end_index]
                start_index = end_index
                return start_index, end_index, "ERROR-Invalid input", error

        elif current_state == 10:
            char = text[end_index]
            if char == "*":
                current_state = 11
                end_index += 1
            elif char != "*" and char != "\x00":
                if char == '\n':
                    line_number += 1
                current_state = 10
                end_index += 1
            else:
                error = error + text[start_index:end_index]
                start_index = end_index
                return start_index, end_index, "ERROR-Unclosed comment", error
        elif current_state == 11:
            char = text[end_index]
            if char == "*":
                current_state = 11
                end_index += 1
            elif char == "/":
                current_state = 12
                end_index += 1
            elif char == "\x00":
                error = error + text[start_index:end_index]
                start_index = end_index
                return start_index, end_index, "ERROR-Unclosed comment", error
            else:
                current_state = 10
                end_index += 1
        elif current_state == 12:
            return start_index, end_index, "COMMENT", error
        elif current_state == 13:
            return start_index, end_index, "WHITESPACE", error
        elif current_state == 14:
            char = text[end_index]
            if char == "/":
                end_index += 1
                error = error + text[start_index:end_index]
                start_index = end_index
                return start_index, end_index, "ERROR-Unmatched comment", error

            elif D.__contains__(char) or L.__contains__(char) or S.__contains__(char) or W.__contains__(ord(char)):
                current_state = 7
                end_index += 1
            else:
                end_index += 1
                error = error + text[start_index:end_index]
                start_index = end_index
                return start_index, end_index, "ERROR-Invalid input", error


def get_token():
    symbol_table = put_keywords_in_table()
    i = open("input.txt", "r")
    # e = open("lexical_errors.txt", "w")
    # t = open("tokens.txt", "w")
    text = i.read()
    text = text + "\x00"
    global line_number
    global index
    # line_errors = []
    # line_tokens = []
    start_index, end_index, token_type, error = get_next_token(text)
    lexim = text[start_index:end_index]
    is_error = True if token_type[0:5] == "ERROR" else False
    if not is_error:
        if not ["WHITESPACE", "COMMENT"].__contains__(token_type):
            if token_type == "ID":
                if lexim not in symbol_table.values():
                    symbol_table[len(symbol_table) + 1] = lexim

    # else:
    #     if token_type[6:] == 'Unclosed comment':
    #         error_message = error if len(error) < 8 else error[0:7] + "..."
    #     else:
    #         line_errors.append((error, token_type[6:]))

    if token_type == "WHITESPACE":
        if ord(lexim) == 10:
            # writing_into_file(t, line_number, line_tokens)
            # writing_into_file(e, line_number, line_errors)
            # line_tokens = []
            # line_errors = []
            line_number += 1
    # elif text[end_index] == "\x00":
    #     return line_number, ("EOF", "$")
    # writing_into_file(t, line_number, line_tokens)
    # writing_into_file(e, line_number, line_errors)
    index = end_index
    if not ["WHITESPACE", "COMMENT"].__contains__(token_type) and not is_error:
        return line_number, (token_type, lexim)
    elif lexim == '\x00':
        return line_number, ("EOF", "$")
    else:
        return get_token()

    # t.close()
    # e.close()
    # e = open("lexical_errors.txt", "r")
    # if len(e.read()) == 0:
    #     e = open("lexical_errors.txt", "w")
    #     e.write("There is no lexical error.")
