from math import sqrt
from sympy import Expr, Symbol, sqrt, diff, Add, latex
import re

from dataclasses import dataclass
from fabpy.constants import students_coefficient
from fabpy.utils import rounding, student
from fabpy.dataclass import Values


class IndetectError:
    def __init__(self, formula: Expr,  data: list[Values], name: str = 't', roundoff: int = 1, floating_point: str = ','):
        self.formula = formula
        self.data = data
        self.name = name
        self.roundoff = roundoff
        self.floating_point = floating_point

        self.error_formula = None

        self.latex_name = str()
        self.latex_general = str()
        self.latex_values = str()
        self.latex_result = str()

        self.result = float()
        self.error = float()

        self.check_values = False
        self.check_latex = False

    def calculation(self) -> float:
        """Вычисление значения функции по средним значениям функции"""
        temp = None
        for var in self.data:
            temp = self.formula.subs({var.name: var.round_value() for var in self.data})
        self.result = temp
        return float(self.result)     

    def error_calculation(self):
        elements = []
        temp = None
        for var in self.data:
            if var.error != 0:
                elements.append(diff(self.formula, var.sp)**2 * var.spe**2)
        self.error_formula = sqrt(Add(*elements))
        
        # Подставляем значения переменных и их погрешностей
        temp = self.error_formula
        for var in self.data:
            temp = temp.subs(var.sp, var.round_value())
            if var.error != 0:
                temp = temp.subs(var.spe, var.error)
        
        self.error = float(temp.evalf())
        return self.error
            

    def build(self):
        if self.check_values:
            raise ValueError("You can't create formula components because the required numeric values are missing. Try correcting the input data and restarting the calculation function.")
        else:
            self.latex_name = fr"\Delta{{ {self.name} }}"

            self.latex_general = latex(self.error_formula)
            
            expr = self.error_formula.copy()
            for var in self.data:
                symbol_value = Symbol(str(var.round_value()))
                expr = expr.subs(var.sp, symbol_value)
                if var.error != 0:
                    symbol_error_value = Symbol(str(var.round_error()))
                    expr = expr.subs(var.spe, symbol_error_value)

            latex_str = latex(expr)

            latex_str = re.sub(r'\\mathit\{(\d+)\}', r'\1', latex_str)
            latex_str = re.sub(r'\\mathrm\{(\d+)\}', r'\1', latex_str)

            self.latex_values = latex_str.replace('.', self.floating_point)
            
            self.latex_result = rounding(self.error, self.roundoff).replace('.', self.floating_point)

            self.check_latex = True

    def latex(self, print_name: bool = True, print_general: bool = True, print_values: bool = True, print_result: bool = True) -> str:        
        self.build()
        resulting_formula = []

        if print_name:
            resulting_formula.append(self.latex_name)
        if print_general:
            resulting_formula.append(self.latex_general)
        if print_values:
            resulting_formula.append(self.latex_values)
        if print_result:
            resulting_formula.append(self.latex_result)

        return " = ".join(resulting_formula)
    