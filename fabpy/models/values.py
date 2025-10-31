from sympy import Symbol
from typing import Dict, List, Optional, Union

class Variable(Symbol):
    def __new__(cls, name: str, **kwargs):
        obj = Symbol.__new__(cls, name)
        return obj

    def __init__(self, name: str = "t", values: Union[list, tuple, float, int] = 0., 
                 error: Optional[Union[float, int]] = None, unit: str = "", 
                 roundoff: int = 1, rounded: bool = True, float_point: str = ','):
        
        # Вызываем __init__ родителя (Symbol)
        super().__init__()
        
        # Обработка значений
        self._name = name

        if isinstance(values, (list, tuple)):
            self._values = list(values)
        elif isinstance(values, (int, float)):
            self._values = [values]
        else:
            self._values = []
            raise ValueError(f"Параметр 'values' может быть только (list, tuple, float, int), а не {type(values)}.")
        
        self._error = error
        self._unit = unit
        self._roundoff = roundoff
        self._rounded = rounded
        self._float_point = float_point

        # Вычисляем среднее значение
        self.average_value = self._calculate_average()

    @property
    def name(self) -> str:
        """Возращает имя переменной"""
        return self._name
    
    @property
    def unit(self) -> str:
        """Возращает строку с единицами измерения величины"""
        return self._unit
    
    @property
    def roundoff(self) -> int:
        """Возращает количество цифр после плавающей запятой"""
        return self._roundoff
    
    @property
    def rounded(self) -> bool:
        """Возращает флаг о необходимости округления значения в формулах"""
        return self._rounded
    
    @property
    def float_point(self) -> str:
        """Возращает символ плавающей точки"""
        return self._float_point
    
    @name.setter
    def name(self, new_name: str) -> None:
        """Изменяет имя переменной на новое"""
        if not new_name:
            self._name = "t"
        else:
            self._name = new_name
    
    @unit.setter
    def unit(self, new_unit: str) -> None:
        """Изменяем единицы измерения переменной"""
        if not new_unit:
            self._unit = ''
        else:
            self._unit = new_unit

    @roundoff.setter
    def roundoff(self, new_roundoff: int) -> None:
        """Изменяем количество цифр после плавающей точки"""
        if not new_roundoff:
            self._roundoff = 1
        else:
            self._roundoff = new_roundoff

    @rounded.setter
    def rounded(self, new_rounded: bool) -> None:
        """Изменяем параметр округления значения в формулах"""
        if not new_rounded:
            self._rounded = True
        else:
            self._rounded = new_rounded

    @float_point.setter
    def float_point(self, new_float_point: str) -> None:
        """Изменяем символ плавающей точки"""
        if (not new_float_point) or (new_float_point == ''):
            self._float_point = ','
        else:
            self._float_point = new_float_point


    def _calculate_average(self) -> float:
        """Вычисляет среднее арифметическое значение"""
        if not self._values:
            return 0.0
        return sum(self._values) / len(self._values)


    @property
    def value(self) -> float:
        """Возвращает среднее значение как основное значение переменной"""
        return self.average_value
    

    @property
    def error(self) -> float:
        """Возращает абсолютную погрешность"""
        if type(self._error) is float:
            return self._error
        

    
    def __repr__(self) -> str:
        return f"Variable('{self.name}', value={self.value}, error={self.error}, unit='{self.unit}')"