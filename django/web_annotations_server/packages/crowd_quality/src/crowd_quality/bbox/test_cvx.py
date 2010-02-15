
from cvxmod import *

A=transpose(matrix([1,0,0,1]));

S=transpose(matrix([[1, 1, 0, 0 ],[0, 0, 1, 1]]));

x = optvar(name='x', rows=4,cols=1);

p=problem(maximize(A*x));
p.constr.append(x<=1)
p.constr.append(x>=0)

p.constr.append(S*x<=1)

p.solve()
printval(x)
printval(sum(sum(A*x)))
printval(S*x)
assert(abs(2-value(p))<0.001)



A=transpose(matrix([1,0,1,0.8]));

S=transpose(matrix([[1, 1, 0, 0 ],[0, 0, 1, 1]]));
S2=transpose(matrix([[1, 0, 1, 0 ],[0, 1, 0, 1]]));

x = optvar(name='x', rows=4,cols=1);

p=problem(maximize(A*x));
p.constr.append(x<=1)
p.constr.append(x>=0)

p.constr.append(S*x<=1)
p.constr.append(S2*x<=1)

p.solve()
printval(x)
printval(sum(sum(A*x)))
printval(S*x)
assert(abs(1.8-value(p))<0.001)
