from math import sqrt
from sympy import Expr, Symbol, sqrt, diff, Add, latex
import re

from fabpy.constants import students_coefficient
from fabpy.utils import rounding, student

class IndetectError:
    """
    Класс для вычисления погрешности измерений по формуле косвенной ошибки.
    
    Args:
        formula (Expr): Символьная формула для вычисления (SymPy выражение)
        data (list): Список объектов измеряемых величин с их значениями и погрешностями
        name (str): Название вычисляемой величины (по умолчанию 't')
        roundoff (int): Количество знаков после запятой для округления (по умолчанию 1)
        floating_point (str): Символ разделителя десятичной части (по умолчанию ',')
        rounded (bool): Использовать округленные значения (по умолчанию False)
    """
    def __init__(self, 
                 formula: Expr, 
                 data: list, 
                 name: str = 't', 
                 unit: str = None,
                 roundoff: int = 1, 
                 floating_point: str = ',', 
                 rounded: bool = False):
        self.formula = formula
        self.data = data
        self.name = name
        self.unit = unit
        self.roundoff = roundoff
        self.floating_point = floating_point
        self.rounded = rounded

        # LaTeX представления результатов
        self.latex_name = str()
        self.latex_general = str()
        self.latex_values = str()
        self.latex_result = str()

        self.error_formula = Expr()  # Формула погрешности

        self._value = None  # Кэшированное значение результата

        self.check_values = False  # Флаг проверки вычислений
        self.check_latex = False   # Флаг проверки LaTeX

    @property
    def value(self) -> float:
        """Возвращает вычисленное значение погрешности."""
        if self._value is None:
            self.calculation()
        return self._value
    
    def round_value(self, rounding: int = None) -> float:
        """Возвращает округленное значение погрешности."""
        if self._value is None:
            self.calculation()
        return round(self._value, rounding if rounding else self.roundoff)
    
    def calculation(self) -> float:
        """Вычисляет погрешность по формуле косвенной ошибки."""
        elements = []
        # Собираем слагаемые для формулы погрешности
        for var in self.data:
            if var.error != 0:
                elements.append(diff(self.formula, var.sp)**2 * var.spe**2)
        
        # Формируем итоговую формулу погрешности
        self.error_formula = sqrt(Add(*elements))
        temp = self.error_formula.copy()
        
        # Подставляем значения в формулу
        for var in self.data:
            temp = temp.subs(var.sp, var.round_value() if self.rounded else var.value)
            if var.error != 0:
                temp = temp.subs(var.spe, var.round_error() if self.rounded else var.error)
        
        self._value = float(temp.evalf())
        return self._value
    
    def build(self) -> None:
        """Строит LaTeX представление вычислений."""
        from sympy import Pow, latex, Symbol
        import re

        if not self.check_values:
            self.calculation()

        self.latex_name = fr"\Delta{{ {self.name} }}"
        self.latex_general = latex(self.error_formula)
        
        expr = self.error_formula
        for var in self.data:
            parenthesized = r"( {{ {value} }} \, \mathrm{{ {unit} }} )"
            content = r"{{ {value} }} \, \mathrm{{ {unit} }}"

            # Проверяем, находится ли переменная в степени
            is_in_power = any(
                isinstance(node, Pow) and var.sp in node.args
                for node in expr.atoms(Pow)
            )
            
            # Формируем значение переменной
            value_str = rounding(var.round_value() if self.rounded else var.value, var.roundoff)
            # Добавляем скобки, если переменная в степени
            if is_in_power:
                value_str = parenthesized.format(value=value_str, unit=var.unit)
            else:
                value_str = content.format(value=value_str, unit=var.unit)
            
            # Формируем пары для подстановки значений
            subs_pairs = [
                (var.sp, Symbol(value_str))
            ]
            if var.error != 0:
                error_str = rounding(var.round_error() if self.rounded else var.error, var.roundoff)
                # Погрешность также может быть в степени, проверяем
                is_error_in_power = any(
                    isinstance(node, Pow) and var.spe in node.args
                    for node in expr.atoms(Pow)
                )

                if is_error_in_power:
                    error_str = parenthesized.format(value=error_str, unit=var.unit)
                else:
                    error_str = content.format(value=error_str, unit=var.unit)
                subs_pairs.append(
                    (var.spe, Symbol(error_str))
                )
            
            expr = expr.subs(subs_pairs)

        latex_str = latex(expr, mul_symbol=r'\cdot')
        # Убираем лишнее форматирование чисел
        latex_str = re.sub(r'\\mathit\{(\d+)\}', r'\1', latex_str)
        latex_str = re.sub(r'\\mathrm\{(\d+)\}', r'\1', latex_str)

        self.latex_values = latex_str.replace('.', self.floating_point)
        self.check_latex = True
    
    def latex(self, 
              print_name: bool = True, 
              print_general: bool = True, 
              print_values: bool = True, 
              print_result: bool = True) -> str:
        """
        Возвращает LaTeX представление вычислений.
        
        Args:
            print_name (bool): Включать имя величины
            print_general (bool): Включать общую формулу
            print_values (bool): Включать формулу с подставленными значениями
            print_result (bool): Включать числовой результат
            
        Returns:
            str: LaTeX строка с выбранными компонентами
        """
        if not self.check_latex:    
            self.build()

        resulting_formula = []
        # Собираем требуемые части LaTeX представления
        if print_name:
            resulting_formula.append(self.latex_name)
        if print_general:
            resulting_formula.append(self.latex_general)
        if print_values:
            resulting_formula.append(self.latex_values)
        if print_result:
            resulting_formula.append(self.latex_result)

        return " = ".join(resulting_formula)