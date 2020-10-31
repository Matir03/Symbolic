"""
Package: symbolic.diff
Provides a module for symbolic treatment of calculus

Module: calc.py
Provides functions for symbolic evaluation of limits, differentiation and series expansions

Functions:
diff - differentiates the given expression
taylor - computes a taylor series approximation of a function at a point
limit - computes the limit of a function at a point
"""

import sys
from symbolic.parser import *
from symbolic.symb.manip import * 

def diff(expr, var = 'x'):
    """
    Function: symbolic.diff.calc.diff
    Differentiates the given expression

    Parameters:
    expr(parse tree) - function to differentiate
    var(string) - variable differentiated with respect ('x' by default)

    Return:
    Parse tree representing derivative
    """

    op = expr[0]
    d = ('val', 0.0) # value of derivative

    if op[0] == 'op':
        if op[1] in ['+', '-']:
            d = (op, diff(expr[1], var), diff(expr[2], var)) # linearity
        elif op[1] == '*':
            d = (('op', '+'), (('op', '*'), diff(expr[1], var), expr[2]), (('op', '*'), expr[1], diff(expr[2], var))) # product rule
        elif op[1] == '/':
            d = (('op', '*'), (('op', '-'), (('op', '*'), diff(expr[1], var), expr[2]), (('op', '*'), expr[1], diff(expr[2], var))), (('op', '^'), expr[2], ('val', -2.0))) # quotient rule
        elif op[1] == '^':
            d = (diff((('fn', 'exp'), (('op', '*'), expr[2], (('fn', 'log'), expr[1]))), var)) # a^b = exp(b log a)

    elif op[0] == 'fn': # for functions we use chain rule
        dout = None # dout is the outer derivative wrt expr[1]

        if op[1] == 'sin':
            dout = (('fn', 'cos'), expr[1])
        elif op[1] == 'cos':
            dout = (('fn', '-'),(('fn', 'sin'), expr[1]))
        elif op[1] == 'tan':
            dout = (('op', '^'),(('fn', 'sec'), expr[1]), (('val', 2.0)))
        elif op[1] == 'cot':
            dout = (('fn', '-'),(('op', '^'),(('fn', 'csc'), expr[1]), (('val', 2.0))))
        elif op[1] == 'sec':
            dout = (('op', '*'),(('fn', 'tan'), expr[1]), (('fn', 'sec'), expr[1]))
        elif op[1] == 'csc':
            dout = (('fn', '-'),(('op', '*'),(('fn', 'cot'), expr[1]), (('fn', 'csc'), expr[1])))
        elif op[1] == 'log':
            dout = (('op', '^'), expr[1], ('val', -1.0))
        elif op[1] == 'exp':
            dout = (('fn', 'exp'), expr[1])
        elif op[1] == '-':
            dout = ('val', -1.0)
        elif op[1] == '+':
            dout = ('val', 1.0)    
        else:
            print("Unsupported function", file = sys.stderr)
            return None

        d = (('op', '*'), diff(expr[1], var), dout)

    elif op == 'var' and expr[1] == var:
        d = ('val', 1.0)

    return simplify(d)
        
def taylor(expr, terms = 4, pos = 0.0, var = 'x'):
    """
    Function: symbolic.diff.calc.taylor
    Computes a taylor series approximation of a function at a point

    Parameters:
    expr(parse tree) - given function
    terms(int) - number of terms before truncation (4 by default)
    pos(float) - point of expansion (0.0 by default)
    var(string) - name of variable ('x' by default)

    Return:
    list of floats [c0, c1, c2, ...] such that expr = c0 + c1 (x-a) + c2(x-a)^2 + ...
    """

    n = 0 # term number
    nfact = 1 # factorial of n
    nderiv = expr # n-th derivative
    coeffs = [] # taylor coefficients
    
    for n in range(terms):
        coeffs.append(evaluate(substitute(nderiv, ('val', pos), var)) / nfact)
        nfact *= (n+1)  
        nderiv = diff(nderiv, var)

    return coeffs

def limit(expr, pos = 0.0, var = 'x'):
    """
    Function: symbolic.diff.calc.limit
    Computes the limit of a function at a point

    Parameters:
    expr(parse tree) - given function
    pos(float) - point of expansion (0.0 by default)
    var(string) - name of variable ('x' by default)

    Return:
    A float with the value of the limit, or None if a finite limit does not exist or the procedure failed
    """
    
    try: # return the evaluation directly if possible
        return evaluate(substitute(expr, ('val', pos), var))
    except:
        pass

    op = expr[0]

    if op == 'val':
        return evaluate(expr)

    elif op == 'var':
        if expr[1] == var:
            return pos
        else:
            print("Unknown variable in limit", file = sys.stderr)

    elif op[0] == 'fn':
        try:
            return evaluate((op, limit(expr[1], pos, var)))
        except:
            return None
            
    elif op[0] == 'op':
        if op[1] == '/': 
            try:
                evaluate(substitute(expr[1], ('val', pos), var))
            except:
                try:
                    evaluate(substitute(expr[2], ('val', pos), var))
                except:
                    pass
                else:
                    return None                    
            else:
                try:
                    evaluate(substitute(expr[1], ('val', pos), var))
                except:
                    return 0.0
                else:
                    pass      
                
            return limit((op, diff(expr[1], var), diff(expr[2], var)), pos, var) # L'hospital
        
        elif op[1] == '*':
            return limit((('op', '/'), expr[1], (('op', '/'), ('val', 1.0), expr[2])), pos, var
                         )
        elif op[1] in ['+', '-']:
            return limit((('op', '/'), (op, (('op', '/'), expr[1], expr[2]), ('val', 1.0)), (('op', '/'), ('val', 1.0), expr[2])), pos, var)

        elif op[1] == '^':
            return limit((('fn', 'exp'), (('op', '*'), expr[2], (('fn', 'log'), expr[1]))), pos, var)

    else:
        print("Bad expression", file = sys.stderr)
        return None
        
        
            
                
            
            

    

    
   
