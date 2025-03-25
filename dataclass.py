from statistics import mean
from sympy import Symbol, Expr, latex
import re

from fabpy.absolute import StandardDeviation, RandomError, InstrumentalError, AbsoluteError
from fabpy.utils import rounding
from fabpy.indirect import IndetectError


class Values:
    def __init__(self, 
                 name: str, 
                 values: list | float | int | tuple, 
                 delta: float,  
                 roundoff: int = 1, 
                 alpha: float = 0.95, 
                 use_instrumental_error: bool = True,
                 use_random_error: bool = True,
                 rounded: bool = False):
        """Класс для представления и обработки экспериментальных данных с расчетом погрешностей.

        Предоставляет функциональность для хранения измеренных значений, вычисления различных типов погрешностей (случайной, приборной, абсолютной), а также символьное представление переменной для использования в формулах.

        Args:
            name (str): Имя переменной, которая будет использоваться при посдтановках в формулах
            values (list | float | int | tuple): Эксперементальные значения полученные при измерениях
            delta (float): Погрешность прибора измерения. Единицы измерения должны быть такими же, что и у измерений
            roundoff (int, optional): . Defaults to 1.
            alpha (float, optional): _description_. Defaults to 0.95.
            use_instrumental_error (bool, optional):  Использовать ли при вычислении абсолютной погрешности приборную погрешность. Defaults to True.
            use_random_error (bool, optional): Использовать ли при вычислении абсолютной погрешности случайную погрешность. Defaults to True.
            rounded (bool, optional): _description_. Defaults to False.
        """
        self.name = name
        if isinstance(values, (float, int)):
            self._values = list(values)
        else:
            self._values = values
        self.roundoff = roundoff
        self.delta = delta
        self.alpha = alpha
        self.use_instrumental_error = use_instrumental_error 
        self.use_random_error = use_random_error
        self.rounded = rounded

        # Создаем SymPy-символ для использования в выражениях
        self.symbol = Symbol(name)
        self.error_name = fr"\Delta {{ {name} }}"
        self.error_symbol = Symbol(self.error_name)

        # Инициализируем атрибуты
        self.standard_deviation = None
        self.random_error = None
        self.instrumental_error = None
        self.absolute_error = None

        # Вычисляем все значения при создании объекта
        self._calculate_errors()

    @property
    def values(self):
        """Getter для values."""
        return self._values

    def _calculate_errors(self):
        """Метод для вычисления всех погрешностей и отклонений."""
        # Вычисляем стандартное отклонение
        self.standard_deviation = StandardDeviation(values=self._values, name=self.name, roundoff=self.roundoff)

        # Вычисляем случайную погрешность, если она используется
        if self.use_random_error:
            self.random_error = RandomError(values=self._values, name=self.name, roundoff=self.roundoff, standard_deviation=self.standard_deviation)
        else:
            self.random_error = None

        # Вычисляем приборную погрешность, если она используется
        if self.use_instrumental_error:
            self.instrumental_error = InstrumentalError(delta=self.delta, alpha=self.alpha, name=self.name, roundoff=self.roundoff)
        else:
            self.instrumental_error = None

        # Вычисляем абсолютную погрешность
        self.absolute_error = AbsoluteError(random_error=self.random_error, instrumental_error=self.instrumental_error, name=self.name, roundoff=self.roundoff)

    @property
    def value(self) -> float:
        """Среднее значение."""
        return mean(self._values) if self._values else 0.
    
    def round_value(self, rounding: int = None) -> float:
        return round(mean(self._values), self.roundoff if rounding is None else rounding)
    
    @property
    def error(self):
        """Возвращает результат абсолютной погрешности."""
        return self.absolute_error.result if self.absolute_error else 0
    
    def round_error(self, rounding: int = None) -> float:
        return round(self.error, self.roundoff if rounding is None else rounding)
    
    @property
    def sp(self):
        """Возвращает SymPy-объект: символ переменной"""
        return self.symbol
    
    @property
    def spe(self):
        """Возращает SymPy-объект: символ погрешности переменной"""
        return self.error_symbol
    

class Formula:
    def __init__(self,
                 formula: Expr,
                 data: list[Values],
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

        self._value = None

        self._indetect_error = None

        self.check_values = False
        self.check_latex = False

        self.calculation()

    @property
    def indetect_error(self):
        if self._indetect_error is None:
            self._indetect_error = IndetectError(self.formula, self.data, self.name, )
        return self._indetect_error

    @property
    def value(self):
        if self._value is None:
            self.calculation()
        return self._value

    def calculation(self):
        temp = None
        for var in self.data:
            temp = self.formula.subs({var.name: var.round_value() for var in self.data})
        self._value = float(temp.evalf())
        self.check_values = True
        return self._value
    
    def build(self) -> None:
        if not self.check_values:
            self.calculation()
        
        self.latex_name = self.name

        self.latex_general = latex(self.formula)

        expr = self.formula.copy()
        for var in self.data:
            symbol_value = Symbol(str(var.round_value()))
            expr = expr.subs(var.sp, symbol_value)

        latex_str = latex(expr)

        latex_str = re.sub(r'\\mathit\{(\d+)\}', r'\1', latex_str)
        latex_str = re.sub(r'\\mathrm\{(\d+)\}', r'\1', latex_str)

        self.latex_values = latex_str.replace('.', self.floating_point)

        self.latex_result = rounding(self.value, self.roundoff).replace('.', self.floating_point)

        self.check_latex = True

    
    def latex(self, print_name: bool = True, print_general: bool = True, print_values: bool = True, print_result: bool = True) -> str:
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


