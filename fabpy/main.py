from models.values import Variable, Values
from models.calculation import Calculation

t = Values('t', values=[1.2], unit=r'с', error=0.05, roundoff=1, delta=0.1)
v = Values('v', values=[10.5, 10.7, 10.6], unit=r'\frac{м}{с}', 
           error=0.1, roundoff=2, rounded=False, delta=0.1)

format_md = r"$$ {} $$"
format_tex = r"\[ {} \]"

def printmd(string) -> None:
    print(format_md.format(string))

def printex(string) -> None:
    print(format_tex.format(string))

printmd(v.standart_deviation.latex())
printmd(v.random.latex())
printmd(v.instrumental.latex())
v.instrumental = 1
printmd(v.instrumental.latex())
printmd(v.absolute.latex())
    