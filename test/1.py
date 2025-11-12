from fabpy.values import Variable, Values
from fabpy.calculation import Calculation
from fabpy.formula import Formula

# t = Values('t', values=[1.2], unit=r'с', error=0.05, roundoff=1, delta=0.1)
v = Values('v', values=[10.5, 10.7, 10.6], unit=r'\frac{м}{с}', 
           error=0.1, roundoff=2, rounded=False, delta=0.1)

format_md = r"$$ {} $$"
format_tex = r"\[ {} \]"

def printmd(string) -> None:
    print(format_md.format(string))

def printex(string) -> None:
    print(format_tex.format(string))

# printmd(v.standart_deviation.latex())
# printmd(v.random.latex())
# printmd(v.instrumental.latex())
# v.instrumental = 10
# printmd(v.instrumental.latex())
# printmd(v.absolute.latex())
    
t = Values(
    name='t', values=[10.5, 10.7, 10.6], error=None, unit=r'с',
    roundoff=1, rounded=True, float_point=',', alpha=0.95, delta=0.1
)

printmd(t.random.latex())
printmd(t.absolute.latex())
# t.random = 10
printmd(t.random.latex())
printmd(t.absolute.latex())


s = Formula(formula=2*t**2, name='s', rounded=True)
printmd(s.latex())
printmd(t.absolute.value)
printmd(t.value)
printmd(s.error.latex())