"""
Package: symbolic.symb
Provides a module for symbolic manipulation

Module: manip.py
Provides functions for substitution, simplification, and reduction of parse trees to infix expressions

Functions:
substitue - substitutes an expression in place of a variable
simplify  - simplifies the given expression
infixify  - creates an infix expression out of a parse tree
"""

import sys
from symbolic.parser import *

def substitute(main_expr, sub_expr, var = 'x'):
    """
    Function: symbolic.symb.manip.substitute
    Substitutes an expression in place of a variable

    Parameters:
    main_expr(parse tree) - given expression
    sub_expr(parse tree) - expression to substitute in place of the variable
    var(string) - name of varibale ('x' by default)

    Return:
    A single parse tree representing the expression after substitution
    """
    
    op = main_expr[0]

    if op == 'var' and main_expr[1] == var: # direct substitution
        return sub_expr

    elif op in ['var', 'val']: # no substitution
        return main_expr

    elif op[0] == 'fn': # recursively substitute argument
        return (op, substitute(main_expr[1], sub_expr, var))

    elif op[0] == 'op': # recursively substitute both arguments
        return (op, substitute(main_expr[1], sub_expr, var), substitute(main_expr[2], sub_expr, var))

    else:
        print("Bad expression", file = sys.stderr)
        return None


def simplify(expr):
    """
    Function: symbolic.symb.manip.simplify
    Simplifies the given expression 

    Parameters:
    expr(parse tree) - given expression
    
    Return:
    A parse tree representing the expression after simplification
    """

    op = expr[0]

    if op in ['val', 'var']: # a values and variables are already fully simplified 
        return expr

    elif op[0] == 'fn': # recursively simplify argument
        sim1 = simplify(expr[1])

        if op[1] == '+': # unary + is redundant
            return sim1 
        elif sim1[0] == 'val': # evaluate all functions that can be evaluated
            return ('val', evaluate((op, sim1)))
        elif op[1] == '-' and sim1[0] == ('fn', '-'):
            return sim1[1]
        elif op[1] == '-' and sim1[0] == ('op', '+'):
            return simplify((('op', '+'), (('fn', '-'), sim1[1]), (('fn', '-'), sim1[2]))) 
        elif op[1] == '-' and sim1[0] == ('op', '-'):
            return simplify((('op', '-'), sim1[2], sim1[1]))
        elif op[1] == '-' and sim1[0] == ('op', '*') and sim1[1][0] == 'val':
            return simplify((('op', '*'), (('fn', '-'), sim1[1]), sim1[2]))
        elif op[1] == 'exp' and sim1[0] == ('fn', 'log'):
            return sim1[1]
        elif op[1] == 'log' and sim1[0] == ('fn', 'exp'):
            return sim1[1]
        elif op[1] == 'exp' and sim1[0] == ('op', '*') and sim1[2][0] == ('fn', 'log'):
            return (('op', '^'), sim1[2][1], sim1[1])
        elif op[1] == 'exp' and sim1[0] == ('fn', '-') and sim1[1][0] == ('fn', 'log'):
            return (('op', '^'), sim1[1][1], ('val', -1.0))
        else:
            return (op, sim1)

    elif op[0] == 'op': # recursively simplify both arguments
        sim1 = simplify(expr[1])
        sim2 = simplify(expr[2])

        if sim1[0] == 'val' and sim2[0] == 'val': # if both are values, perform evaluation
            return ('val', evaluate((op, sim1, sim2)))

        elif op[1] == '+':
            if sim2[0] == 'val':
                return simplify((('op', '+'), sim2, sim1))
            elif sim1 == ('val', 0.0):
                return sim2
            elif sim2[0] in [('op', '+'), ('op', '-')]:
                return simplify((sim2[0], (op, sim1, sim2[1]), sim2[2]))
            elif sim2[0] == ('fn', '-'):
                return simplify((('op', '-'), sim1, sim2[1]))
            elif sim1[0] == ('op', '-') and sim1[2] == sim2:
                return sim1[1]
    
        elif op[1] == '-':
            if sim2 == ('val', 0.0):
                return sim1
            elif sim1 == sim2:
                return ('val', 0.0)
            elif sim2[0] == ('fn', '-'):
                return simplify((('op', '+'), sim1, sim2[1]))
            elif sim2[0] == ('op', '-'):
                return simplify((op, (('op', '+'), sim1, sim2[2]), sim2[1]))
            elif sim1[0] == 'val' and sim2[0] == ('op', '+') and sim2[1][0] == 'val':
                return simplify((op, (op, sim1, sim2[1]), sim2[2]))
            elif sim1[0] == ('op', '+') and sim1[2] == sim2:
                return sim1[1]
            
        elif op[1] == '*':
            if sim2[0] == 'val':
                return simplify((op, sim2, sim1))
            elif sim1 == ('val', 0.0):
                return sim1
            elif sim1 == ('val', 1.0):
                return sim2
            elif sim1 == ('val', -1.0):
                return simplify((('fn', '-'), sim2))
            elif sim1[0] == ('fn', '-'):
                return simplify((('fn', '-'), (op, sim1[1], sim2)))
            elif sim2[0] == ('fn', '-'):
                return simplify((('fn', '-'), (op, sim1, sim2[1])))
            elif sim2[0] in [('op', '*'), ('op', '/')]:
                return simplify((sim2[0], (op, sim1, sim2[1]), sim2[2]))
            elif sim1[0] == ('op', '/') and sim1[2] == sim2:
                return sim1[1]
            elif sim1[0] == ('op', '^') and sim2[0] == ('op', '^') and sim1[1] == sim2[1]:
                return simplify((('op', '^'), sim1[1], (('op', '+'), sim1[2], sim2[2])))
            elif sim1[0] == ('op', '^') and sim1[1] == sim2:
                return simplify((('op', '^'), sim1[1], (('op', '+'), sim1[2], ('val', 1.0))))
            elif sim2[0] == ('op', '^') and sim2[1] == sim1:
                return simplify((('op', '^'), sim1, (('op', '+'), sim2[2], ('val', 1.0))))
            elif sim1[0] == ('op', '^') and sim2[1] == sim1:
                return simplify((('op', '^'), sim1, (('op', '+'), sim2[2], ('val', 1.0))))
            elif sim1[0] == ('op', '*') and sim1[2][0] == ('op', '^') and sim2[0] == ('op', '^') and sim2[1] == sim1[2][1]:
                return simplify((op, sim1[1], (('op', '^'), sim2[1], (('op', '+'), sim1[2][2], sim2[2]))))
            elif sim1[0] == ('op', '*') and sim1[1][0] == ('op', '^') and sim2[0] == ('op', '^') and sim2[1] == sim1[1][1]:
                return simplify((op, (('op', '^'), sim2[1], (('op', '+'), sim1[1][2], sim2[2])), sim1[2]))
             
        elif op[1] == '/':
            if sim2 == ('val', 1.0):
                return sim1
            elif sim1 == ('val', 0.0):
                return sim1
            elif sim1 == sim2:
                return ('val', 1.0)
            elif sim2 == ('val', -1.0):
                return simplify((('fn', '-'), sim2))
            elif sim1[0] == ('fn', '-'):
                return simplify((('fn', '-'), (op. sim1[1], sim2)))
            elif sim2[0] == ('fn', '-'):
                return simplify((('fn', '-'), (op. sim1, sim2[1])))
            elif sim2[0] == ('op', '/'):
                return simplify((op, (('op', '*'), sim1, sim2[2]), sim2[1]))
            elif sim1[0] == 'val' and sim2[0] == ('op', '*') and sim2[1][0] == 'val':
                return simplify((op, (op, sim1, sim2[1]), sim2[2])) 
            elif sim1[0] == ('op', '*') and sim1[2] == sim2:
                return sim1[1]
            elif sim1[0] == ('op', '^') and sim1[1] == sim2:
                return simplify((('op', '^'), sim1[1], (('op', '-'), sim1[2], ('val', 1.0))))
            elif sim2[0] == ('op', '^'):
                return simplify((('op', '*'), sim1, (('op', '^'), sim2[1], (('fn', '-'), sim2[2]))))
            else:
                return simplify((('op', '*'), sim1, (('op', '^'), sim2, ('val', -1.0))))
        
        elif op[1] == '^':
            if sim2 == ('val', 0.0):
                return ('val', 1.0)
            elif sim1 in [('val', 0.0), ('val', 1.0)] or sim2 == ('val', 1.0):
                return sim1
            elif sim1[0] == ('op', '^'):
                return simplify(((op, sim1[1], (('op', '*'), sim1[2], sim2)))) 
        
        return (op, sim1, sim2)
    
    else:
        print("Bad expression", file = sys.stderr)
        return None
    

def infixify(expr):
    """
    Function: symbolic.symb.manip.infixify
    Creates an infix expression out of a parse tree

    Parameters:
    expr(parse tree) - given expression
    
    Return:
    A string with the infix expression
    """

    op = expr[0]

    if op in ['var', 'val']: 
        return str(expr[1])

    elif op[0] == 'fn': # recursively get infix expression of argument
        return op[1] + '(' + infixify(expr[1]) + ')'

    elif op[0] == 'op': # recursively get infix of both arguments
        return '(' + infixify(expr[1]) + ' ' + op[1] + ' '  + infixify(expr[2]) + ')'

    else:
        print("Bad expression", file = sys.stderr)
        return None
