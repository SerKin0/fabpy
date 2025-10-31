from math import sqrt
from models.constants import students_coefficient, mul_symbol
from models.utils import rounding, student


class ErrorCalculation:
    """Базовый класс для вычисления различных типов погрешностей."""
    
    def __init__(self, 
                 name: str = 't',
                 unit: str = '', 
                 roundoff: int = 1, 
                 floating_point: str = ',',
                 rounded: bool = False):
        """Инициализирует базовый объект для вычисления погрешностей.

        Args:
            name (str): Имя переменной (по умолчанию 't')
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


# class ErrorModel:
#     def __init__(self, name: str = "t", values: list|tuple|float|int = 0., 
#                  error: float|int = None, unit: str = "", roundoff: int = 1,
#                  rounded: bool = True, float_point: str = ','):
#         """ Модель класса для оброботки погрешностей полученных данных

#         Args:
#             name (str, optional): Имя переменной, которое будет участвовать в формулах (допускается оформление в стиле LaTeX). Defaults to "t".
#             values (list | tuple | float | int, optional): Значение или значения переменной. Defaults to 0..
#             error (float | int, optional): Если программа не должна сама вычислять данные по формулам, вы можете задать нужное значение. Defaults to None.
#             unit (str, optional): Единицы измерения величины (допускается оформление в стиле LaTeX). Defaults to "".
#             roundoff (int, optional): Количество цифр после запятой. Defaults to 1.
#             rounded (bool, optional): При вычислениях округлять значение переменной до значащей цифры. Defaults to True.
#             float_point (str, optional): Символ плавающей точки. Defaults to ','.
#         """

#         self._name = name
        
#         if values in (list, tuple):
#             self._values = values
#         elif values in (int, float):
#             self._values = [values]
#         else:
#             self._values = []
#             raise ValueError(f"Параметр 'values' может быть только (list, tuple, float, int), а не {type(values)}.")
        
#         self._error = error
#         self._unit = unit
#         self._roundoff = roundoff
#         self._float_point = float_point

#         # Среднее арифметическое значение
#         self.average_value = None

#     @property
#     def name(self) -> str:
#         """Возращает имя переменной."""
#         return self._name
    
#     def name(self, name: str) -> None:
#         """Изменение значения переменной 'name'."""
#         if name is None:
#             self._name = ""
#         else:
#             self._name = name
    
#     @property
#     def values(self) -> list:
#         return self._values