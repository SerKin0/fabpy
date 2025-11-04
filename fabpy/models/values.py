from sympy import sqrt, Float
from typing import Optional, Union

from models.utils import student
from models.calculation import Calculation
from models.models import Variable
from models.constants import name_default


class Values(Variable):
    def __init__(self, name: str = name_default, values: Union[list, tuple, float, int] = 0., 
                 error: Optional[float] = None, unit: str = "", roundoff: int = 1, rounded: bool = True, 
                 float_point: str = ',', alpha: float = 0.95, delta: float = 0):
        super().__init__(name, values, unit, roundoff, rounded, float_point)
        self._error = self.__format_error(error)
        self._alpha = alpha
        self._delta = delta

        self._standart_deviation = None
        self._random = None
        self._instrumental = None
        self._absolute = None

    def __format_error(self, error: float, type_error: str = None) -> Calculation:
        if error is None:
            return None
        
        # Исправлено: создаем Calculation напрямую с числовым значением
        temp_name = fr"\Delta {self.name}_\text{{ {type_error} }}" if type_error is not None else fr"\Delta {self.name}"
        return Calculation(
            name=temp_name, 
            formula=Float(error),  # передаем число напрямую
            unit=self.unit, 
            rounded=self.rounded, 
            roundoff=self.roundoff, 
            float_point=self.float_point
        )

    @property
    def error(self) -> Calculation:
        if self._error is None:
            return self.__format_error(self._error)
        else:
            return self._error
        
    @error.setter
    def error(self, new_error: float = None) -> None:
        self._error = self.__format_error(new_error)

    @property
    def standart_deviation(self) -> Calculation:
        if self._standart_deviation is None:
            n = len(self._values)
            vars = []
            for index, value in enumerate(self._values):
                vars.append(Variable(fr" {{ {self._name} }}_{{ {index+1} }}", values=value, unit=self.unit, 
                                roundoff=self.roundoff, rounded=self.rounded, float_point=self.float_point))
            
            average_value = Variable(name=fr"\overline{{ {self._name} }}", values=sum(self._values) / n, unit=self.unit, roundoff=self.roundoff, rounded=self.rounded)
            numerical = sum([(value - average_value)**2 for value in vars])

            self._standart_deviation = Calculation(formula=sqrt(numerical / n), unit=self.unit, name=fr"S_{{ {self.name} }}", roundoff=self.roundoff, rounded=self.rounded, float_point=self.float_point)

        return self._standart_deviation
    
    @property
    def random(self) -> Calculation:
        if self._random is None:
            t = Variable(fr't_{{ {self._alpha},~n }}', values=student(alpha=self._alpha, n=len(self._values)), roundoff=2)
            S = Variable(name=self.standart_deviation._name, values=self.standart_deviation.value, unit=self.standart_deviation._unit, roundoff=self.standart_deviation._roundoff, rounded=self.standart_deviation._rounded)
            self._random = Calculation(t * S,unit=self.unit, name=fr'\Delta {{ {self.name} }}_{{ \text{{сл}} }}', roundoff=self.roundoff, rounded=self.rounded, float_point=self.float_point)
        return self._random
        
    @random.setter
    def random(self, new_random) -> None:
        self._random = self.__format_error(new_random)

    @property
    def instrumental(self) -> Calculation:
        if self._instrumental is None:
            t = Variable(fr't_{{ {self._alpha},~\infty }}', values=student(alpha=self._alpha, n=float('inf')), roundoff=2)
            delta = Variable(fr"\delta_{{ {self.name} }}", values=self._delta, unit=self.unit, roundoff=self.roundoff, rounded=self.rounded, float_point=self.float_point)
            self._instrumental = Calculation(t * delta / 3, unit=self.unit, name=fr'\Delta {{ {self.name} }}_{{ \text{{пр}} }}', roundoff=self.roundoff, rounded=self.rounded, float_point=self.float_point)
        return self._instrumental
    
    @instrumental.setter
    def instrumental(self, new_instrumental: float) -> None:
        self._instrumental = self.__format_error(new_instrumental, "пр")
        # Сбрасываем абсолютную погрешность для пересчета
        self._absolute = None

    @property
    def absolute(self) -> Calculation:
        if self._absolute is None:
            error_random = Variable(name=self.random._name, values=self.random.value, unit=self.random._unit, roundoff=self.random._roundoff, rounded=self.random._rounded)
            error_instrumental = Variable(name=self.instrumental._name, values=self.instrumental.value, unit=self.instrumental._unit, roundoff=self.instrumental._roundoff, rounded=self.instrumental._rounded)
            self._absolute =Calculation(sqrt(error_instrumental**2 + error_random**2), unit=self.unit, name=fr'\Delta {self.name}', roundoff=self.roundoff, rounded=self.rounded, float_point=self.float_point)
        return self._absolute