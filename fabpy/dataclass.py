from statistics import mean
from sympy import Symbol, Expr, latex
import re

from fabpy.absolute import StandardDeviation, RandomError, InstrumentalError, AbsoluteError
from fabpy.utils import rounding
from fabpy.indirect import IndetectError


class Values:
    """Класс для представления и обработки экспериментальных данных с расчетом погрешностей.

    Предоставляет функциональность для:
    - Хранения измеренных значений
    - Вычисления различных типов погрешностей (случайной, приборной, абсолютной)
    - Символьного представления переменной для использования в формулах
    - Округления результатов согласно заданной точности
    - Генерации LaTeX-представления переменных и погрешностей

    Attributes:
        name (str): Имя переменной для использования в формулах
        _values (list[float]): Список экспериментальных значений
        roundoff (int): Количество знаков после запятой для округления
        delta (float): Погрешность измерительного прибора (в тех же единицах, что и измерения)
        alpha (float): Уровень доверия (по умолчанию 0.95)
        use_instrumental_error (bool): Флаг использования приборной погрешности
        use_random_error (bool): Флаг использования случайной погрешности
        rounded (bool): Флаг округления результатов
        symbol (Symbol): SymPy символ переменной
        error_name (str): Имя символа погрешности в LaTeX нотации
        error_symbol (Symbol): SymPy символ погрешности переменной
        standard_deviation (StandardDeviation): Объект стандартного отклонения
        random_error (RandomError): Объект случайной погрешности (если используется)
        instrumental_error (InstrumentalError): Объект приборной погрешности (если используется)
        absolute_error (AbsoluteError): Объект абсолютной погрешности

    Methods:
        _calculate_errors(): Вычисляет все типы погрешностей
        round_value(rounding=None): Возвращает округленное среднее значение
        round_error(rounding=None): Возвращает округленную абсолютную погрешность

    Properties:
        values: Возвращает список экспериментальных значений
        value: Возвращает среднее значение
        error: Возвращает абсолютную погрешность
        sp: Возвращает SymPy символ переменной
        spe: Возвращает SymPy символ погрешности переменной
    """
    def __init__(self, 
                 name: str, 
                 values: list | float | int | tuple, 
                 delta: float,  
                 roundoff: int = 1, 
                 alpha: float = 0.95, 
                 use_instrumental_error: bool = True,
                 use_random_error: bool = True,
                 rounded: bool = False):
        """Инициализирует объект Values с экспериментальными данными и параметрами обработки.

        Args:
            name (str): Имя переменной для использования в формулах (например, "V", "I")
            values (list | float | int | tuple): Экспериментальные данные. Может быть:
                - списком значений
                - одиночным числом (будет преобразовано в список)
                - кортежем значений
            delta (float): Погрешность измерительного прибора в тех же единицах, что и измерения
            roundoff (int, optional): Количество знаков после запятой для округления. По умолчанию 1.
            alpha (float, optional): Уровень доверия для расчета доверительного интервала. По умолчанию 0.95.
            use_instrumental_error (bool, optional): Использовать ли приборную погрешность при расчете. 
                По умолчанию True.
            use_random_error (bool, optional): Использовать ли случайную погрешность при расчете. 
                По умолчанию True.
            rounded (bool, optional): Производить ли округление результатов. По умолчанию False.

        Raises:
            TypeError: Если values не является списком, кортежем или числом
            ValueError: Если values пуст или содержит нечисловые значения
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
        self._standard_deviation = None
        self._random_error = None
        self._instrumental_error = None
        self._absolute_error = None

        # Вычисляем все значения при создании объекта
        self.calculate_errors()

    @property
    def values(self):
        """Getter для values."""
        return self._values

    def calculate_errors(self):
        """Метод для вычисления всех погрешностей и отклонений."""
        # Если  
        if len(self.values) > 1:
            # Вычисляем стандартное отклонение
            self._standard_deviation = StandardDeviation(values=self._values, name=self.name, roundoff=self.roundoff)

            # Вычисляем случайную погрешность, если она используется
            if self.use_random_error:
                self._random_error = RandomError(values=self._values, name=self.name, roundoff=self.roundoff, standard_deviation=self._standard_deviation)
            else:
                self._random_error = None
        else:
            pass

        # Вычисляем приборную погрешность, если она используется
        if self.use_instrumental_error:
            self._instrumental_error = InstrumentalError(delta=self.delta, alpha=self.alpha, name=self.name, roundoff=self.roundoff)
        else:
            self._instrumental_error = None

        # Вычисляем абсолютную погрешность
        self._absolute_error = AbsoluteError(random_error=self._random_error, instrumental_error=self._instrumental_error, name=self.name, roundoff=self.roundoff)

    @property
    def value(self) -> float:
        """Среднее значение."""
        return mean(self._values) if self._values else 0.
    
    @property
    def standard_deviation(self) -> StandardDeviation:
        if self._standard_deviation is None:
            self.calculate_errors()
        return self._standard_deviation
    
    @property
    def random_error(self) -> RandomError:
        if self._random_error is None:
            self.calculate_errors()
        return self._random_error
    
    @property
    def instrumental_error(self) -> InstrumentalError:
        if self._instrumental_error is None:
            self.calculate_errors()
        return self._instrumental_error
    
    @property
    def absolute_error(self) -> AbsoluteError:
        if self._absolute_error is None:
            self.calculate_errors()
        return self._absolute_error
    
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
            self._indetect_error = IndetectError(self.formula, self.data, self.name, roundoff=self.roundoff, floating_point=self.floating_point, rounded=self.rounded)
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


