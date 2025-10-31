from sympy import Expr, Symbol, latex
from models.constants import name_default, mul_symbol_default, float_point_defualt, name_default
from models.utils import rounding
from models.values import Variable
from typing import List
import re

class Calculation:
    """Класс для вычисления значения формулы и построения её LaTeX-представления."""
    def __init__(self,
                 formula: Expr,
                 unit: str = '',
                 name: str = name_default,
                 roundoff: int = 1, 
                 floating_point: str = float_point_defualt,
                 rounded: bool = False):
        """Инициализирует объект Formula для вычисления и представления формулы.

        Args:
            formula (Expr): SymPy выражение формулы
            data (list[Values]): Список объектов Values с измерениями
            name (str): Имя результата (по умолчанию 't')
            roundoff (int): Количество знаков после запятой (по умолчанию 1)
            floating_point (str): Разделитель десятичной части (по умолчанию ',')
            rounded (bool): Использовать округленные значения (по умолчанию False)
        """
        self._formula = formula
        self._unit = unit
        self._name = name
        self._roundoff = roundoff
        self._float_point = floating_point
        self._rounded = rounded

        self.symbol = Symbol(name)
        self.error_name = fr"\Delta {{ {name} }}"
        self.error_symbol = Symbol(self.error_name)

        # LaTeX представления
        self.latex_name = str()
        self.latex_general = str()
        self.latex_values = str()
        self.latex_result = str()

        self._variables = self._extract_variables()

        self._value = None
        self._indetect_error = None

        self.check_values = False
        self.check_latex = False

        self.calculation()

    def _extract_variables(self) -> List[Variable]:
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
    def variables(self) -> list[Variable]:
        if not self._variables:
            self._variables = self._extract_variables()
        return self._variables

    @property
    def value(self) -> float:
        """Возвращает вычисленное значение формулы."""
        if self._value is None:
            self.calculation()
        return self._value

    def round_value(self, rounding: int = None) -> float:
        """Возращает округленное значение формулы."""
        return round(self.value, self.roundoff if rounding is None else rounding)
    
    def calculation(self) -> float:
        """Вычисляет значение формулы, подставляя данные."""
        temp = self._formula
        # Подстановка значений переменных

        sub = {}
        print(self.variables)
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
        """Строит LaTeX-представление формулы."""
        if not self.check_values:
            self.calculation()
        
        self.latex_name = self._name
        self.latex_general = latex(self._formula)

        expr = self._formula.copy()
        # Подстановка округленных значений в выражение

        def format_value_unit(value: str, unit: str) -> str:
            string = value.replace('.', self._float_point)
            if unit:
                string += fr"~\mathrm{{ {unit} }}"
            return string

        for var in self.variables:
            value_to_show = var.round_value() if self._rounded else var.value
            value_str = str(value_to_show).replace('.', self._float_point)

            symbol_replace = format_value_unit(value_str, var.unit)

            temp_symbol = Symbol(symbol_replace)
            expr = expr.subs(var, temp_symbol)
        
        latex_str = latex(expr, mul_symbol=mul_symbol_default)
        # Очистка LaTeX от лишнего форматирования чисел
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
        """Возвращает LaTeX-представление формулы.

        Args:
            print_name (bool): Включать имя
            print_general (bool): Включать общую формулу
            print_values (bool): Включать формулу с подставленными значениями
            print_result (bool): Включать результат

        Returns:
            str: LaTeX-строка с выбранными компонентами
        """
        if not self.check_latex:
            self.build()            
        
        resulting_formula = []
        # Сборка требуемых компонентов LaTeX
        if print_name:
            resulting_formula.append(self.latex_name)
        if print_general:
            resulting_formula.append(self.latex_general)
        if print_values:
            resulting_formula.append(self.latex_values)
        if print_result:
            resulting_formula.append(self.latex_result)

        return " = ".join(resulting_formula)