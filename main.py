from symbolic.parser import *
from symbolic.symb.manip import *
from symbolic.diff.calc import *

e1 = input("Enter numeric expression for evaluation: ")
t1 = tokenize(e1)
print("Your expression contains the following tokens:", t1)
p1 = parse(t1)
print("Your expression parsed into the following tree:", p1)
val = evaluate(p1)
print("Your expression evaluated to the following value:", val)

print()

e2 = input("Enter an expression with variables: ")
t2 = tokenize(e2)
p2 = parse(t2)
v2 = input("Name one of your variables: ")
se = input("Substitute " + v2 + " = ")
st = tokenize(se)
sp = parse(st)
ps = substitute(p2, sp, v2)
print("Substituted expression as a tree:", ps)
inf = infixify(ps)
print("Substituted expression in infix:", inf)
print("Substituted expression after simplification:", infixify(simplify(ps)))

print()

e3 = input("Enter a function to differentiate: ")
v3 = input("Variable with respect to which you wish differentiate: ")
t3 = tokenize(e3)
p3 = parse(t3)
print("Derivative:", infixify(diff(p3, v3)))

print()

e4 = input("Enter a function to expand in series: ")
n4 = int(input("Number of terms: "))
v4 = input("Variable name: ")
l4 = float(input("Expand at " + v4 + " = "))
t4 = tokenize(e4)
p4 = parse(t4)
seq = ""
px = 0

for c in taylor(p4, n4, l4, v4):
    seq += str(c) + "*(" + v4 + '-' + str(l4) + ")^" + str(px) + '+'
    px += 1

seq += "O((" + v4 + '-' + str(l4) + ")^" + str(n4) + ')'

print("The required Taylor series expansion is", seq)

print()

e5 = input("Enter a function to compute limit: ")
v5 = input("Variable name: ")
l5 = float(input("Find limit as " + v5 + " approaches "))
t5 = tokenize(e5)
p5 = parse(t5)

print("The required limit is", limit(p5, l5, v5))
