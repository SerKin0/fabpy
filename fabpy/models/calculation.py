from sympy import Expr, Symbol, latex
from models.constants import name_default, mul_symbol_default, float_point_defualt, name_default
from models.utils import rounding, string_russian_to_tex
from typing import List
import re

from sympy import Symbol
from typing import Union
from models.utils import string_russian_to_tex
from models.models import Variable

class Calculation:
    """Класс для вычисления значения формулы и построения её LaTeX-представления."""
    def __init__(self,
                 formula: Expr,
                 unit: str = '',
                 name: str = name_default,
                 roundoff: int = 1, 
                 floating_point: str = float_point_defualt,
                 rounded: bool = False):
        
        self._formula = formula
        self._unit = string_russian_to_tex(unit)
        self._name = string_russian_to_tex(name)
        self._roundoff = roundoff
        self._float_point = floating_point
        self._rounded = rounded

        self.symbol = Symbol(name)
        self.error_name = fr"\Delta {name}"
        self.error_symbol = Symbol(self.error_name)

        # LaTeX представления
        self.latex_name = str()
        self.latex_general = str()
        self.latex_values = str()
        self.latex_result = str()

        self._variables = self._extract_variables()

        self._value = None
        self.check_values = False
        self.check_latex = False

        self.calculation()

    def _extract_variables(self) -> Variable:
        vars = []

        def collect_variable(form: Expr):
            if type(form) is Variable:
                vars.append(form)
            elif hasattr(form, 'args'):
                for argument in form.args:
                    collect_variable(argument)

        collect_variable(self._formula)
        return vars

    @property
    def variables(self) -> List[Variable]:
        if not self._variables:
            self._variables = self._extract_variables()
        return self._variables

    @property
    def value(self) -> float:
        if self._value is None:
            self.calculation()
        return self._value

    def round_value(self, rounding: int = None) -> float:
        return round(self.value, self._roundoff if rounding is None else rounding)
    
    def calculation(self) -> float:
        temp = self._formula
        sub = {}
        
        for var in self.variables:
            if self._rounded:
                sub[var] = var.round_value()
            else:
                sub[var] = var.value

        temp = temp.subs(sub)
        self._value = float(temp.evalf())
        self.check_values = True
        return self._value
    
    def build(self) -> None:
        if not self.check_values:
            self.calculation()
        
        self.latex_name = self._name
        self.latex_general = latex(self._formula)

        expr = self._formula.copy()

        def format_value_unit(value: str, unit: str) -> str:
            string = value.replace('.', self._float_point)
            if unit:
                string += fr"~\mathrm{{ {unit} }}"
            return string

        for var in self.variables:
            value_str = (rounding(var.value, var.roundoff)).replace('.', self._float_point)
            symbol_replace = format_value_unit(value_str, var.unit)
            temp_symbol = Symbol(symbol_replace)
            expr = expr.subs(var, temp_symbol)
        
        latex_str = latex(expr, mul_symbol=mul_symbol_default)
        latex_str = re.sub(r'\\mathit\{(\d+)\}', r'\1', latex_str)
        latex_str = re.sub(r'\\mathrm\{(\d+)\}', r'\1', latex_str)

        self.latex_values = latex_str.replace('.', self._float_point)

        result_value_str = rounding(self.value, self._roundoff)
        self.latex_result = format_value_unit(result_value_str, self._unit)
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
    
    def __str__(self):
        return f"{self._name} {self._formula}"