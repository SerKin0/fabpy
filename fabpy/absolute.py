from math import sqrt
from dataclasses import dataclass

from fabpy.constants import students_coefficient, mul_symbol
from fabpy.utils import rounding, student


class StandardDeviation:
    """Класс для вычисления стандартного отклонения набора значений."""
    def __init__(self, 
                 values: list, 
                 name: str = 't',
                 unit: str = '', 
                 roundoff: int = 1, 
                 floating_point: str = ',',
                 rounded: bool = False):
        """Инициализирует объект StandardDeviation.

        Args:
            values (list): Список измеренных значений
            name (str): Имя переменной (по умолчанию 't')
            roundoff (int): Количество знаков после запятой (по умолчанию 1)
            floating_point (str): Разделитель десятичной части (по умолчанию ',')
            rounded (bool): Использовать округленные значения (по умолчанию False)
        """
        self.values = values
        self.name = name
        self.unit = unit
        self.roundoff = roundoff
        self.floating_point = floating_point
        self.rounded = rounded

        # LaTeX представления
        self.latex_name = str()
        self.latex_general = str()
        self.latex_values = str()
        self.latex_result = str()

        self.average_value = 0.0  # Среднее значение
        self.n = 0  # Количество измерений
        self._value = 0.0  # Значение стандартного отклонения

        self.check_values = False  # Флаг проверки вычислений
        self.check_latex = False   # Флаг проверки LaTeX

    @property
    def value(self) -> float:
        """Возвращает значение стандартного отклонения."""
        if not self.check_values:
            self.calculation()
        return self._value

    def round_value(self, rounding: int = None) -> float:
        """Возвращает округленное значение стандартного отклонения."""
        return round(self.value, rounding if rounding else self.roundoff)

    def calculation(self) -> None:
        """Вычисляет стандартное отклонение."""
        self.n = len(self.values)
        self.average_value = sum(self.values) / self.n if self.n > 0 else 0

        if self.rounded:
            self.average_value = round(self.average_value, self.roundoff)

        # Стандартное отклонение для выборки
        if self.n > 1:
            self._value = sqrt(sum([(self.average_value - var)**2 for var in self.values]) / (self.n * (self.n - 1)))
        else:
            self._value = 0  # Для одного значения

        self.check_values = True
        self.build()

    def build(self) -> None:
        """Строит LaTeX-представление стандартного отклонения."""
        if not self.check_values:
            raise ValueError("You can't create formula components because the required numeric values are missing.")
        
        self.latex_name = fr"S_{{ {self.name} }}"
        self.latex_general = fr"\sqrt{{\frac{{ \sum_{{ i=1 }}^{{n}} (\overline{{ {self.name} }} - {{ {self.name} }}_{{i}})^2}}{{ n(n-1) }}}}"
        
        if self.n > 1:
            # Формируем сумму разностей в квадрате
            temp_sum = " + ".join([fr"({rounding(self.average_value, self.roundoff)} \, \mathrm{{ {self.unit} }} - {rounding(var, self.roundoff)} \, \mathrm{{ {self.unit} }})^2" for var in self.values])
            self.latex_values = fr"\sqrt{{ \frac{{ {temp_sum} }}{{ {self.n} \, ({self.n} - 1) }} }}".replace('.', self.floating_point)
        else:
            self.latex_values = "0"
        
        self.latex_result = fr"{rounding(self._value, self.roundoff)} \, \mathrm{{ {self.unit} }}".replace('.', self.floating_point)
        self.check_latex = True

    def latex(self, print_name: bool = True, print_general: bool = True, print_values: bool = True, print_result: bool = True) -> str:
        """Возвращает LaTeX-представление вычислений.

        Args:
            print_name (bool): Включать имя
            print_general (bool): Включать общую формулу
            print_values (bool): Включать формулу с подставленными значениями
            print_result (bool): Включать результат
        """
        if not self.check_latex:
            self.calculation()            
        
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


class RandomError:
    """Класс для вычисления случайной погрешности на основе стандартного отклонения."""
    def __init__(self, 
                 values: list, 
                 standard_deviation: StandardDeviation, 
                 alpha: float = 0.95, 
                 unit: str = '',
                 name: str = 't', 
                 roundoff: int = 1, 
                 floating_point: str = ',',
                 rounded: bool = False):
        """Инициализирует объект RandomError.

        Args:
            values (list): Список измеренных значений
            standard_deviation (StandardDeviation): Объект стандартного отклонения
            alpha (float): Уровень доверия (по умолчанию 0.95)
            name (str): Имя переменной (по умолчанию 't')
            roundoff (int): Количество знаков после запятой (по умолчанию 1)
            floating_point (str): Разделитель десятичной части (по умолчанию ',')
            rounded (bool): Использовать округленные значения (по умолчанию False)
        """
        self.values = values
        self.alpha = alpha
        self.unit = unit
        self.name = name
        self.roundoff = roundoff
        self.floating_point = floating_point
        self.rounded = rounded
        self.standard_deviation = standard_deviation

        # LaTeX представления
        self.latex_name = str()
        self.latex_general = str()
        self.latex_values = str()
        self.latex_result = str()

        self.student_t = 0.0  # Коэффициент Стьюдента
        self.standard_deviation_value = 0.0  # Значение стандартного отклонения
        self.n = 0  # Количество измерений
        self._value = 0.0  # Значение случайной погрешности

        self.check_values = False
        self.check_latex = False

    @property
    def value(self) -> float:
        """Возвращает значение случайной погрешности."""
        if not self.check_values:
            self.calculation()
        return self._value
    
    def round_value(self, rounding: int = None) -> float:
        """Возвращает округленное значение случайной погрешности."""
        return round(self.value, rounding if rounding else self.roundoff)

    def calculation(self) -> None:
        """Вычисляет случайную погрешность."""
        self.n = len(self.values)
        self.student_t = student(self.alpha, self.n - 1) if self.n > 1 else 0

        if self.n > 1:
            if not self.student_t:
                raise ValueError(f"No definition for student_t with alpha={self.alpha}, n={self.n}")
            self.standard_deviation_value = self.standard_deviation.round_value() if self.rounded else self.standard_deviation.value
            self._value = self.student_t * self.standard_deviation_value
        else:
            self._value = 0  # Для одного значения

        self.check_values = True
        self.build()

    def build(self) -> None:
        """Строит LaTeX-представление случайной погрешности."""
        if not self.check_values:
            raise ValueError("You can't create formula components because the required numeric values are missing.")
        
        self.latex_name = fr"\Delta \, {{ {self.name} }}_{{\text{{сл}}}}"
        self.latex_general = fr"t_{{ {self.alpha}, \, n-1 }} \{mul_symbol} S_{{ {self.name}, \, n }}"
        
        if self.n > 1:
            self.latex_values = fr"{self.student_t} \{mul_symbol} {rounding(self.standard_deviation.value, self.roundoff)} \, \mathrm{{ {self.unit} }}".replace('.', self.floating_point)
        else:
            self.latex_values = "0"
        
        self.latex_result = fr"{rounding(self._value, self.roundoff)} \, \mathrm {{ {self.unit} }}".replace('.', self.floating_point)
        self.check_latex = True

    def latex(self, print_name: bool = True, print_general: bool = True, print_values: bool = True, print_result: bool = True) -> str:
        """Возвращает LaTeX-представление вычислений."""
        if not self.check_latex:
            self.calculation()            
        
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


class InstrumentalError:
    """Класс для вычисления приборной погрешности."""
    def __init__(self, 
                 delta: float, 
                 alpha: float = 0.95, 
                 name: str = 't', 
                 unit: str = '',
                 roundoff: int = 1, 
                 floating_point: str = ',',
                 rounded: bool = False):
        """Инициализирует объект InstrumentalError.

        Args:
            delta (float): Погрешность прибора
            alpha (float): Уровень доверия (по умолчанию 0.95)
            name (str): Имя переменной (по умолчанию 't')
            roundoff (int): Количество знаков после запятой (по умолчанию 1)
            floating_point (str): Разделитель десятичной части (по умолчанию ',')
            rounded (bool): Использовать округленные значения (по умолчанию False)
        """
        self.delta = delta
        self.alpha = alpha
        self.name = name
        self.unit = unit
        self.roundoff = roundoff
        self.floating_point = floating_point
        self.rounded = rounded

        # LaTeX представления
        self.latex_name = str()
        self.latex_general = str()
        self.latex_values = str()
        self.latex_result = str()

        self.student_t = 0.0  # Коэффициент Стьюдента для бесконечной выборки
        self._value = 0.0  # Значение приборной погрешности

        self.check_values = False
        self.check_latex = False

    @property
    def value(self) -> float:
        """Возвращает значение приборной погрешности."""
        if not self.check_values:
            self.calculation()
        return self._value
    
    def round_value(self, rounding: int = None) -> float:
        """Возвращает округленное значение приборной погрешности."""
        return round(self.value, rounding if rounding else self.roundoff)

    def calculation(self) -> None:
        """Вычисляет приборную погрешность."""
        self.student_t = student(self.alpha, float('inf'))
        self._value = self.student_t * self.delta / 3
        self.check_values = True
        self.build()

    def build(self) -> None:
        """Строит LaTeX-представление приборной погрешности."""
        if not self.check_values:
            raise ValueError("You can't create formula components because the required numeric values are missing.")
        
        self.latex_name = fr"\Delta \, {{ {self.name} }}_{{\text{{пр}}}}"
        self.latex_general = fr"t_{{ {self.alpha}, \, \infty }} \{mul_symbol} \frac{{ \delta_{{ {self.name} }} }}{{ 3 }}"
        self.latex_values = fr"{self.student_t} \{mul_symbol} \frac{{ {self.delta} \, \mathrm{{ {self.unit} }} }}{{ 3 }}".replace('.', self.floating_point)
        self.latex_result = fr"{rounding(self._value, self.roundoff)} \, \mathrm{{ {self.unit} }}".replace('.', self.floating_point)
        self.check_latex = True

    def latex(self, print_name: bool = True, print_general: bool = True, print_values: bool = True, print_result: bool = True) -> str:
        """Возвращает LaTeX-представление вычислений."""
        if not self.check_latex:
            self.calculation()            
        
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


class AbsoluteError:
    """Класс для вычисления полной абсолютной погрешности."""
    def __init__(self, 
                 random_error: RandomError, 
                 instrumental_error: InstrumentalError, 
                 name: str = 't', 
                 unit: str = '',
                 roundoff: int = 1, 
                 floating_point: str = ',',
                 rounded: bool = False):
        """Инициализирует объект AbsoluteError.

        Args:
            random_error (RandomError): Объект случайной погрешности
            instrumental_error (InstrumentalError): Объект приборной погрешности
            name (str): Имя переменной (по умолчанию 't')
            roundoff (int): Количество знаков после запятой (по умолчанию 1)
            floating_point (str): Разделитель десятичной части (по умолчанию ',')
            rounded (bool): Использовать округленные значения (по умолчанию False)
        """
        self.name = name
        self.roundoff = roundoff
        self.unit = unit 
        self.floating_point = floating_point
        self.rounded = rounded
        
        self.instrumental_error = instrumental_error
        self.random_error = random_error
        
        # LaTeX представления
        self.latex_name = str()
        self.latex_general = str()
        self.latex_values = str()
        self.latex_result = str()

        self._value = 0.0  # Значение абсолютной погрешности

        self.check_values = False
        self.check_latex = False

    @property
    def value(self) -> float:
        """Возвращает значение абсолютной погрешности."""
        if not self.check_values:
            self.calculation()
        return self._value
    
    def round_value(self, rounding: int = None) -> float:
        """Возвращает округленное значение абсолютной погрешности."""
        return round(self.value, rounding if rounding else self.roundoff)

    def calculation(self) -> None:
        """Вычисляет абсолютную погрешность как корень суммы квадратов."""
        random_error_value = (self.random_error.round_value() if self.rounded else self.random_error.value) if self.random_error else 0
        instrumental_error_value = (self.instrumental_error.round_value() if self.rounded else self.instrumental_error.value) if self.instrumental_error else 0
        self._value = sqrt(instrumental_error_value**2 + random_error_value**2)
        self.check_values = True
        self.build()

    def build(self) -> None:
        """Строит LaTeX-представление абсолютной погрешности."""
        if not self.check_values:
            self.calculation()

        self.latex_name = fr"\Delta \, {{ {self.name} }}"
        self.latex_general = fr"\sqrt{{ {{ \Delta {{ {self.name} }}_{{\text{{сл}}}} }}^2 + {{ \Delta {{ {self.name} }}_{{\text{{пр}}}} }}^2 }}"
        
        random_value = rounding(self.random_error.value, self.roundoff) if self.random_error else "0"
        instr_value = rounding(self.instrumental_error.value, self.roundoff) if self.instrumental_error else "0"
        self.latex_values = fr"\sqrt{{ ({{ {random_value} }} \, \mathrm{{ {self.unit} }})^2 + ({{ {instr_value} }} \, \mathrm{{ {self.unit} }})^2 }}".replace('.', self.floating_point)
        
        self.latex_result = fr"{rounding(self._value, self.roundoff)} \, \mathrm{{ {self.unit} }}".replace('.', self.floating_point)
        self.check_latex = True

    def latex(self, print_name: bool = True, print_general: bool = True, print_values: bool = True, print_result: bool = True) -> str:
        """Возвращает LaTeX-представление вычислений."""
        if not self.check_latex:
            self.calculation()            
        
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