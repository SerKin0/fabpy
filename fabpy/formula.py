from sympy import Expr, diff, sqrt, Add, Float
from typing import List

from calculation import Calculation
from models import Variable
from constants import name_default, float_point_defualt
from utils import string_russian_to_tex
from values import Values


from sympy import Expr, diff, sqrt, Add, Float
from typing import List

from calculation import Calculation
from models import Variable
from constants import name_default, float_point_defualt
from utils import string_russian_to_tex
from values import Values


class Formula(Calculation):
    """Класс для вычисления значения формулы и её погрешности, наследующий от Calculation.
    Работает с Values для распространения погрешностей."""
    
    def __init__(self,
                 formula: Expr,
                 unit: str = '',
                 name: str = name_default,
                 roundoff: int = 1, 
                 float_point: str = float_point_defualt,
                 rounded: bool = False):
        super().__init__(formula, unit, name, roundoff, float_point, rounded)
        self._inderect_formula = None
        self._inderect = None

    def _extract_variables(self) -> List[Values]:
        vars = []

        def collect_variable(form: Expr):
            if isinstance(form, (Values, Variable)):
                if form not in vars:
                    vars.append(form)
            elif hasattr(form, 'args'):
                for argument in form.args:
                    collect_variable(argument)

        collect_variable(self._formula)
        print(123, vars)
        return vars

    def _calculate_inderect(self):
        terms = []
        print(321, self._formula)
        for var in self.variables:
            print(f"{var=}")
            if isinstance(var, Values) and var.absolute is not None:
                partial = diff(self._formula)
                error_var = var.absolute.to_variable() 
                
                term = (partial * error_var) ** 2
                print(f"\n{var=}\n{var.to_variable()=}\n{partial=}\n{error_var=}\n{term=}\n")
                terms.append(term)
                
        print(terms)
        
        if not terms:
            self._inderect_formula = Float(0)
        else:
            self._inderect_formula = sqrt(Add(*terms))

        # Создаём Calculation для погрешности
        self._inderect = Calculation(
            formula=self._inderect_formula,
            unit=self._unit,
            name=string_russian_to_tex(fr"\Delta {self._name}"),
            roundoff=self._roundoff,
            float_point=self._float_point,
            rounded=self._rounded
        )
        
        print(f"{self._inderect.variables=}")

        # === ПОДСТАНОВКА ===
        sub = {}

        # 1. Основные переменные (t → 10.6)
        print(123, self.variables)
        for v in self.variables:
            sub[v] = v.round_value() if self._rounded else v.value

        # 2. Погрешности (Δt → 0.3)
        for v in self.variables:
            if isinstance(v, Values) and v.absolute is not None:
                err_var = v.absolute.to_variable()
                sub[err_var] = v.absolute.value  # значение погрешности

        # Применяем подстановку
        temp = self._inderect_formula.subs(sub)
        error_value = float(temp.evalf())

        self._inderect._value = error_value
        self._inderect.check_values = True

    @property
    def error(self) -> Calculation:
        if self._inderect is None:
            self._calculate_inderect()
        return self._inderect