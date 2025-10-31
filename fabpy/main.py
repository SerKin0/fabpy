from models.values import Variable
from models.calculation import Calculation

t = Variable('t', values=[1.2, 1.3, 1.25], unit=r'\text{}', error=0.05)
v = Variable('v', values=[10.5, 10.7, 10.6], unit=r'\frac{\text{м}}{\text{с}}', error=0.1)

form = v * t

s = Calculation(
    formula=form,
    name='S',
    unit=r'\text{м}',
    roundoff=2
)

format_md = r"$$ {} $$"
format_tex = r"\[ {} \]"

print(format_md.format(s.latex()))
print()