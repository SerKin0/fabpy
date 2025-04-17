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
    """
    def __init__(self, 
                 name: str, 
                 values: list | float | int | tuple, 
                 delta: float,  
                 unit: str = None,
                 roundoff: int = 1, 
                 alpha: float = 0.95, 
                 use_instrumental_error: bool = True,
                 use_random_error: bool = True,
                 rounded: bool = False):
        """Инициализирует объект Values с экспериментальными данными и параметрами обработки.

        Args:
            name (str): Имя переменной для использования в формулах (например, "V", "I")
            values (list | float | int | tuple): Экспериментальные данные (список, число или кортеж)
            delta (float): Погрешность измерительного прибора в тех же единицах, что и измерения
            roundoff (int, optional): Количество знаков после запятой для округления. По умолчанию 1
            alpha (float, optional): Уровень доверия для доверительного интервала. По умолчанию 0.95
            use_instrumental_error (bool, optional): Использовать приборную погрешность. По умолчанию True
            use_random_error (bool, optional): Использовать случайную погрешность. По умолчанию True
            rounded (bool, optional): Использовать округленные значения. По умолчанию False

        Raises:
            TypeError: Если values не является списком, кортежем или числом
            ValueError: Если values пуст или содержит нечисловые значения
        """
        self.name = name
        self.unit = unit
        # Преобразование входных данных в список
        if isinstance(values, (float, int)):
            self._values = [values]
        else:
            self._values = list(values)
        self.roundoff = roundoff
        self.delta = delta
        self.alpha = alpha
        self.use_instrumental_error = use_instrumental_error 
        self.use_random_error = use_random_error
        self.rounded = rounded

        # Символы для математических выражений
        self.symbol = Symbol(name)
        self.error_name = fr"\Delta {{ {name} }}"
        self.error_symbol = Symbol(self.error_name)

        # Инициализация объектов погрешностей
        self._standard_deviation = None
        self._random_error = None
        self._instrumental_error = None
        self._absolute_error = None

        self.calculate_errors()

    @property
    def values(self) -> list:
        """Возвращает список экспериментальных значений."""
        return self._values

    def calculate_errors(self) -> None:
        """Вычисляет все типы погрешностей для данных."""
        self._standard_deviation = StandardDeviation(
            values=self._values, name=self.name, roundoff=self.roundoff, unit=self.unit, rounded=self.rounded
        )

        # Расчет случайной погрешности (только если больше одного значения)
        self._random_error = RandomError(
            values=self._values, name=self.name, roundoff=self.roundoff, unit=self.unit,
            standard_deviation=self._standard_deviation, rounded=self.rounded
        ) if self.use_random_error and len(self._values) > 1 else RandomError(
            values=self._values, name=self.name, roundoff=self.roundoff,
            standard_deviation=self._standard_deviation, rounded=self.rounded
        )

        # Расчет приборной погрешности (если используется)
        self._instrumental_error = InstrumentalError(
            delta=self.delta, alpha=self.alpha, name=self.name, unit=self.unit,
            roundoff=self.roundoff, rounded=self.rounded
        ) if self.use_instrumental_error else None

        self._absolute_error = AbsoluteError(
            random_error=self._random_error, instrumental_error=self._instrumental_error,
            name=self.name, roundoff=self.roundoff, rounded=self.rounded, unit=self.unit
        )

    @property
    def value(self) -> float:
        """Возвращает среднее значение измерений."""
        return mean(self._values) if self._values else 0.0
    
    @property
    def standard_deviation(self) -> StandardDeviation:
        """Возвращает объект стандартного отклонения."""
        if self._standard_deviation is None:
            self.calculate_errors()
        return self._standard_deviation
    
    @property
    def random_error(self) -> RandomError:
        """Возвращает объект случайной погрешности."""
        if self._random_error is None:
            self.calculate_errors()
        return self._random_error
    
    @property
    def instrumental_error(self) -> InstrumentalError:
        """Возвращает объект приборной погрешности."""
        if self._instrumental_error is None:
            self.calculate_errors()
        return self._instrumental_error
    
    @property
    def absolute_error(self) -> AbsoluteError:
        """Возвращает объект абсолютной погрешности."""
        if self._absolute_error is None:
            self.calculate_errors()
        return self._absolute_error
    
    def round_value(self, rounding: int = None) -> float:
        """Возвращает округленное среднее значение."""
        return round(mean(self._values), rounding if rounding is not None else self.roundoff)
    
    @property
    def error(self) -> float:
        """Возвращает значение абсолютной погрешности."""
        return self.absolute_error.value if self.absolute_error else 0.0
    
    def round_error(self, rounding: int = None) -> float:
        """Возвращает округленное значение абсолютной погрешности."""
        return round(self.error, self.roundoff if rounding is None else rounding)
    
    @property
    def sp(self) -> Symbol:
        """Возвращает SymPy символ переменной."""
        return self.symbol
    
    @property
    def spe(self) -> Symbol:
        """Возвращает SymPy символ погрешности переменной."""
        return self.error_symbol


class Formula:
    """Класс для вычисления значения формулы и построения её LaTeX-представления."""
    def __init__(self,
                 formula: Expr,
                 data: list[Values],
                 unit: str = None,
                 name: str = 't',
                 roundoff: int = 1, 
                 floating_point: str = ',',
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
        self.formula = formula
        self.data = data
        self.unit = unit
        self.name = name
        self.roundoff = roundoff
        self.floating_point = floating_point
        self.rounded = rounded

        self.symbol = Symbol(name)
        self.error_name = fr"\Delta {{ {name} }}"
        self.error_symbol = Symbol(self.error_name)

        # LaTeX представления
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
    def indetect_error(self) -> IndetectError:
        """Возвращает объект косвенной погрешности."""
        if self._indetect_error is None:
            self._indetect_error = IndetectError(
                self.formula, self.data, self.name, roundoff=self.roundoff, unit=self.unit,
                floating_point=self.floating_point, rounded=self.rounded
            )
        return self._indetect_error

    @property
    def value(self) -> float:
        """Возвращает вычисленное значение формулы."""
        if self._value is None:
            self.calculation()
        return self._value
    
    @property
    def error(self) -> float:
        """Возращает значение косвенной погрешности. """
        return self.indetect_error.value
    
    def round_value(self, rounding: int = None) -> float:
        """Возращает округленное значение формулы."""
        return round(self.value, self.roundoff if rounding is None else rounding)
    
    def round_error(self, rounding: int = None) -> float:
        """Возращает округленное значение косвенной погреншности."""
        return round(self.error, self.roundoff if rounding is None else rounding)

    def calculation(self) -> float:
        """Вычисляет значение формулы, подставляя данные."""
        temp = self.formula
        # Подстановка значений переменных
        temp = temp.subs({var.sp: var.round_value() if self.rounded else var.value for var in self.data})
        self._value = float(temp.evalf())
        self.check_values = True
        return self._value
    
    def build(self) -> None:
        """Строит LaTeX-представление формулы."""
        if not self.check_values:
            self.calculation()
        
        self.latex_name = self.name
        self.latex_general = latex(self.formula)

        expr = self.formula.copy()
        # Подстановка округленных значений в выражение
        for var in self.data:
            symbol_value = Symbol(fr"{var.round_value() if self.rounded else var.value} \, {var.unit}")
            expr = expr.subs(var.sp, symbol_value)
        
        latex_str = latex(expr)
        # Очистка LaTeX от лишнего форматирования чисел
        latex_str = re.sub(r'\\mathit\{(\d+)\}', r'\1', latex_str)
        latex_str = re.sub(r'\\mathrm\{(\d+)\}', r'\1', latex_str)

        self.latex_values = latex_str.replace('.', self.floating_point)
        self.latex_result = fr"{rounding(self.value, self.roundoff)} \, \mathrm{{ {self.unit} }}".replace('.', self.floating_point)

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
    
    @property
    def sp(self) -> Symbol:
        """Возвращает SymPy символ переменной."""
        return self.symbol
    
    @property
    def spe(self) -> Symbol:
        """Возвращает SymPy символ погрешности переменной."""
        return self.error_symbol