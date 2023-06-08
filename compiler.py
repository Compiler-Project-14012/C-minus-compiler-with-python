import parser_man
import scanner
import os

from anytree import Node, RenderTree

'''
    Mohammadreza Pirpiran 99101319
    Mohammad Esteki 99100296
'''

stack = []
stack.append((parser_man.Program, ))
while True:
    token = scanner.get_token()
    Program_node, stack, ended = parser_man.parse_token(token, stack)
    if ended:
        break

parse_tree = open("parse_tree.txt", "a", encoding="utf-8")
for pre, fill, node in RenderTree(Program_node):
    strings = pre + node.name.replace('\'', '')
    parse_tree.write(strings + '\n')
parse_tree.close()
if os.stat("syntax_errors.txt").st_size == 0:
    e = open("syntax_errors.txt", "a")
    e.write("There is no syntax error.")
    e.close()