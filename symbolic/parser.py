"""
Package: symbolic
Package for using symbolic expressions

Sub-packages:
ritam - provides a module for symbolic manipulation 
nag   - provides a module for symbolic treatment of calculus

Module: parser.py
Module for parsing and numeric evaluation of symbolic expressions

Functions:
tokenize - splits the given expression into tokens
parse    - converts a list of tokens into a parse tree

Constants:
ops  = ['+','-','*','/','^']
obrs = ['(','{','[']
cbrs = [')','}',']'] 
fns  = ['sin', 'cos', 'tan', 'sec', 'csc', 'cot', 'log', 'exp']
spcs = {'e': 2.7182818285, 'pi': 3.1415926535}
"""

import sys
from math import *

#Constants

ops  = ['+','-','*','/','^']
obrs = ['(','{','[']
cbrs = [')','}',']'] 
fns  = ['sin', 'cos', 'tan', 'sec', 'csc', 'cot', 'log', 'exp']
spcs = {'e': 2.718281, 'pi': 3.141593}

#Functions

def tokenize(expr):
    """
    Function: symbolic.parser.tokenize
    Splits the given expression into tokens

    Parameters:
    expr(string) - infix expression

    Return:
    List of tokens in order, as [token1, token2, ...]

    Token format:(token_type, value)
    token_type is one of 
    "op" for operators <+,-,*,/,^>
    "obr" for opening brackets <(, { and [>
    "cbr" for closing brackets <), } and ]>
    "fn" for functions <sin, log, exp, etc.>
    "val" for constant values (numeric constants like 7, 23.45 and special constants pi and e) 
    "var" for variables (any other sequence of symbols)
    value is the value of the token, which can be a number for token_type == "val" and is a string otherwise
    """

    tok_ends = ops + obrs + cbrs + [' '] # list of characters that terminate previous token

    cur_tok = '' # variable to hold the token currently being created
    numeric = True # True if cur_tok is empty or a number
    decimal = False # True if numeric == True and '.' in cur_tok 
    tok_lst = [] # list of already evaluated tokens
    tok_typ = '' # type of the current token
    
    for c in expr + ' ': # the last whitespace is ignored but ensures last token is terminated

        if c in tok_ends: # token terminating character
            
            if cur_tok != '': # push current token to tok_lst if non-empty

                if numeric:
                    tok_lst.append(('val', float(cur_tok)))
                elif cur_tok in spcs.keys():
                    tok_lst.append(('val', cur_tok))
                else:
                    if cur_tok in fns:
                        tok_typ = 'fn'
                    else:
                        tok_typ = 'var'

                    tok_lst.append((tok_typ, cur_tok))

            # if c is a singular token, append c 
            if c in ops:
                tok_lst.append(("op", c))
            elif c in obrs:
                tok_lst.append(("obr", c))
            elif c in cbrs:
                tok_lst.append(("cbr", c))

            # prepare blank cur_tok
            cur_tok = ''
            numeric = True 
            decimal = False 

        else: # append all non-terminating characters
            
            cur_tok += c

            if c == '.': # alter decimal; second decimal makes number invalid
                if decimal == True:
                    numeric = False

                decimal = not decimal

            elif not '0' <= c <= '9': # c is not a decimal or a number
                numeric = False

    return tok_lst

def parse(token_list):
    """
    Function: symbolic.parser.parse
    Converts a list of tokens into a parse tree

    Parameters:
    token_list(list of 2-tuples) - list of tokens from tokenize

    Return:
    A parse tree, whose form can be defined recursively as
    parse_tree := <var/val token> | (<op/fn token>, parse_tree1, [optionalparse_tree2])

    Each parse tree represents a hierarchy of functions/operations performed on values or variables, and return value is equivalent to token_list
    """

    # This function implements the Shunting-Yard algorithm

    pr = {'+': 1, '-': 1, '*': 2, '/': 2, '^': 3} # operator priority
    
    trees = [] # stack of parse trees in order of evaluation
    opstk = [] # stack of operators (including parentheses and functions)
    unary = True # True if the next operator token must be unary (that is, there is no free first argument)

    # unary distinguishes between unary and binary + and -, and is used to mark unary tokens 'fn' instead of 'op'
    
    for token in [('obr', '(')] + token_list + [('cbr', ')')]: # brackets added for simpler code

        if token[0] in ['obr', 'fn']: 
            opstk.append(token)
            unary = True
        
        elif token[0] in ['var', 'val']:
            trees.append(token)
            unary = False
            
        elif token[0] == 'cbr': # closing bracket [note that the exact bracket used does not matter]
            # pop out all operators till the opening bracket

            if opstk == []: # no opening bracket
                print("Missing bracket", file = sys.stderr)
                return None
                
            op = opstk.pop()

            while op[0] != 'obr':

                if op[0] in 'fn':
                    if len(trees) == 0: # insufficient argmuents
                        print("Bad expression", file = sys.stderr)
                        return None

                    e1 = trees.pop()
                    trees.append((op, e1))
                        
                else:
                    if len(trees) == 0: # insufficient argmuents
                        print("Bad expression", file = sys.stderr)
                        return None

                    e2 = trees.pop()
                    e1 = trees.pop()
                    trees.append((op, e1, e2))

                if opstk == []: # no opening bracket
                    print("Missing bracket", file = sys.stderr)
                    return None

                op = opstk.pop()

            unary = False

        elif token[0] == 'op':
            if unary:
                
                if token[1] not in ['+', '-']:
                   print("Bad expression", file = sys.stderr)
                   return None 

                opstk.append(('fn', token[1])) # unary operators are basically one variable functions
                
            else:
                # pop all functions, same priority left-associative and higher priority operators out of stack

                if opstk != []:
                    op = opstk[-1]
                    while op[1] != "(" and (op[0] == 'fn' or (op[0] == 'op' and (pr[op[1]]>pr[token[1]] or (pr[op[1]]==pr[token[1]] and token[1] != "^")))):
                        opstk.pop()
                        
                        if op[0] in 'fn':
                            if len(trees) == 0: # insufficient argmuents
                                print("Bad expression", file = sys.stderr)
                                return None

                            e1 = trees.pop()
                            trees.append((op, e1))
                                
                        else:
                            if len(trees) == 0: # insufficient argmuents
                                print("Bad expression", file = sys.stderr)
                                return None

                            e2 = trees.pop()
                            e1 = trees.pop()
                            trees.append((op, e1, e2))

                        if opstk == []:
                            break
                        
                        op = opstk[-1]

                opstk.append(token)
                unary = True;

    return trees[0] # trees should be a single parse tree of length 0 at this point   
                
def evaluate(tree):
    """
    Function: symbolic.parser.evaluate
    Evaluates a given variable-free parse tree
    
    Parameters:
    tree (parse tree) - tree to evaluate

    Return:
    A single float representing the computed value
    """

    fnames = {'sin': sin, 'cos': cos, 'tan': tan, 'cot': lambda x : 1/tan(x), 'sec': lambda x : 1/cos(x), 'csc': lambda x : 1/sin(x), 'log': log, 'exp': exp, '-': lambda x : -x, '+': lambda x : x}

    if tree[0] == 'val':
        if tree[1] in spcs.keys():
            return spcs[tree[1]]
        else:
            return tree[1]

    op = tree[0]

    if op[0] == 'op':
        e1 = evaluate(tree[1])
        e2 = evaluate(tree[2])
    
        if op[1] == '+':
            return e1 + e2
        elif op[1] == '-':
            return e1 - e2
        if op[1] == '*':
            return e1 * e2
        elif op[1] == '/':
            return e1 / e2
        if op[1] == '^':                
            return e1 ** e2
        
    elif op[0] == 'fn':
        e1 = evaluate(tree[1])
        return round(fnames[op[1]](e1), 6)
        
            
            
                

            
                
        
        
        

    
