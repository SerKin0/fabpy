from math import sqrt
from sympy import Expr, Symbol, sqrt, diff, Add, latex
import re

from fabpy.constants import students_coefficient
from fabpy.utils import rounding, student

class IndetectError:
    def __init__(self, 
                 formula: Expr, 
                 data: list, 
                 name: str = 't', 
                 roundoff: int = 1, 
                 floating_point: str = ',',
                 rounded: bool = False):
        self.formula = formula
        self.data = data
        self.name = name
        self.roundoff = roundoff
        self.floating_point = floating_point
        self.rounded = rounded

        self.latex_name = str()
        self.latex_general = str()
        self.latex_values = str()
        self.latex_result = str()

        self.error_formula = Expr

        self._value = None

        self.check_values = False
        self.check_latex = False

    @property
    def value(self) -> float:
        if self._value is None:
            self.calculation()
        return self._value
    
    def round_value(self, rounding: int = None) -> float:
        if self._value is None:
            self.calculation()
        return round(self._value, rounding if rounding else self.roundoff)
    
    def calculation(self) -> float:
        elements = []
        for var in self.data:
            if var.error != 0:
                elements.append(diff(self.formula, var.sp)**2 * var.spe**2)
        self.error_formula = sqrt(Add(*elements))
        temp = self.error_formula.copy()
        for var in self.data:
            temp = temp.subs(var.sp, var.round_value() if self.rounded else var.value)
            if var.error != 0:
                temp = temp.subs(var.spe, var.round_error() if self.rounded else var.error)
        
        self._value = float(temp.evalf())
        return self._value
    
    def build(self) -> None:
        if not self.check_values:
            self.calculation()

        self.latex_name = fr"\Delta{{ {self.name} }}"
        self.latex_general = latex(self.error_formula)
        
        expr = self.error_formula
        for var in self.data:
            # Создаем подстановки как пары (старый, новый)
            subs_pairs = [
                (var.sp, Symbol(str(var.round_value() if self.rounded else var.value)))
            ]
            if var.error != 0:
                subs_pairs.append(
                    (var.spe, Symbol(str(var.round_error() if self.rounded else var.error)))
                )
            
            # Применяем подстановки
            expr = expr.subs(subs_pairs)

        latex_str = latex(expr)

        latex_str = re.sub(r'\\mathit\{(\d+)\}', r'\1', latex_str)
        latex_str = re.sub(r'\\mathrm\{(\d+)\}', r'\1', latex_str)

        self.latex_values = latex_str.replace('.', self.floating_point)
        
        self.latex_result = rounding(self._value, self.roundoff).replace('.', self.floating_point)

        self.check_latex = True
    
    def latex(self, 
              print_name: bool = True, 
              print_general: bool = True, 
              print_values: bool = True, 
              print_result: bool = True) -> str:    
        if not self.check_latex:    
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
