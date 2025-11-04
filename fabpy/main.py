from models.values import Variable, Values
from models.calculation import Calculation

t = Values('t', values=[1.2, 1.3, 1.25], unit=r'с', error=0.05, roundoff=2)
v = Values('v', values=[10.5, 10.7, 10.7], unit=r'\frac{м}{с}', error=0.1, roundoff=3)

# print(v.standart_deviation())
# form = v * t

# s = Calculation(
#     formula=form,
#     name='S',
#     unit=r'м',
#     roundoff=2
# )

format_md = r"$$ {} $$"
format_tex = r"\[ {} \]"

# print(format_md.format(v.standart_deviation()))
print(v.standart_deviation)

# from models.utils import string_russian_to_tex

# print(string_russian_to_tex("fasaавыаfdsfsdf231ыфвф"))