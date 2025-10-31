from math import sqrt
from models.constants import students_coefficient, mul_symbol_default, name_default, float_point_defualt
from models.utils import rounding, student


class ErrorCalculation:
    """Базовый класс для вычисления различных типов погрешностей."""
    
    def __init__(self, 
                 name: str = name_default,
                 unit: str = '', 
                 roundoff: int = 1, 
                 floating_point: str = float_point_defualt,
                 rounded: bool = False):
        """Инициализирует базовый объект для вычисления погрешностей.

        Args:
            name (str): Имя переменной (по умолчанию default_name)
            unit (str): Единица измерения
            roundoff (int): Количество знаков после запятой (по умолчанию 1)
            floating_point (str): Разделитель десятичной части (по умолчанию ',')
            rounded (bool): Использовать округленные значения (по умолчанию False)
        """
        self._name = name
        self._unit = unit
        self._roundoff = roundoff
        self._floating_point = floating_point
        self._rounded = rounded

        # LaTeX представления
        self.latex_name = str()
        self.latex_general = str()
        self.latex_values = str()
        self.latex_result = str()

        self._value = 0.0  # Значение погрешности

        self.check_values = False  # Флаг проверки вычислений
        self.check_latex = False   # Флаг проверки LaTeX

    @property
    def value(self) -> float:
        """Возвращает значение погрешности."""
        if not self.check_values:
            self.calculation()
        return self._value

    def round_value(self, rounding_value: int = None) -> float:
        """Возвращает округленное значение погрешности."""
        return round(self.value, rounding_value if rounding_value else self._roundoff)

    def calculation(self) -> None:
        """Метод для вычисления погрешности. Должен быть переопределен в дочерних классах."""
        raise NotImplementedError("Метод calculation() должен быть реализован в дочернем классе")

    def build(self) -> None:
        """Метод для построения LaTeX-представления. Должен быть переопределен в дочерних классах."""
        raise NotImplementedError("Метод build() должен быть реализован в дочернем классе")

    def latex(self, print_name: bool = True, print_general: bool = True, 
              print_values: bool = True, print_result: bool = True) -> str:
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

    def _format_unit(self, value: float) -> str:
        """Форматирует значение с единицей измерения для LaTeX."""
        formatted_value = rounding(value, self._roundoff)
        if self._unit:
            return fr"{formatted_value} \, \mathrm{{ {self._unit} }}".replace('.', self._floating_point)
        return str(formatted_value).replace('.', self._floating_point)


class StandardDeviation(ErrorCalculation):
    def __init__(self, values: list, name: str = name_default, unit: str = '', roundoff: int = 1,
                 float_point: str = float_point_defualt, rounded: bool = True):
        super.__init__(name, unit, roundoff, float_point, rounded)

        self._values = values
        self._average_value = 0.
        self._n = 0

    def calculation(self) -> float:
        self._n = len(self._values)

        if self._n == 0:
            self._average_value = 0
            self._value = 0
        else:
            self._average_value = sum(self._values) / len(self._n) 

            if self._rounded:
                self._average_value = round(self._average_value, self._roundoff)

            self._value = sqrt(sum([(self._average_value - value)**2 for value in self._values])) / (self._n * (self._n - 1))

        self.check_values = True
        self.build()

        return self._value
    
    def build(self) -> None:
        if not self.check_values:
            raise ValueError("Значения для формул отстутсвуют.")
        
        self.latex_name = fr"S_{{ {self._name} }}"

        self.latex_general = fr""
        return super().build()