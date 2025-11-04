from sympy import Symbol, sqrt, Sum
from typing import Dict, List, Optional, Union
from models.utils import rounding, string_russian_to_tex
import numpy as np
from models.calculation import Calculation
from models.models import Variable

class Values(Variable):
    def __init__(self, name = "t", values = 0, error: Optional[float] = None, unit: str = "", roundoff = 1, rounded = True, float_point = ','):
        super().__init__(name, values, unit, roundoff, rounded, float_point)

    @property
    def standart_deviation(self):
        n = len(self._values)
        vars = []
        print(self._values)
        for index, value in enumerate(self._values):
            vars.append(Variable(fr"{{ {self._name} }}_{{ {index+1} }}", values=value, unit=self.unit, 
                              roundoff=self.roundoff, rounded=self.rounded, float_point=self.float_point))
        
        average_value = Variable(name=fr"\overline{{ {self._name} }}", values=sum(self._values) / n, unit=self.unit, roundoff=self.roundoff, rounded=self.rounded)
        print(vars)
        numerical = sum([(value - average_value)**2 for value in vars])
        print(numerical)
        return Calculation(formula=sqrt(numerical / (n * (n - 1))), unit=self.unit, name=fr"S_{{ {self.name} }}", roundoff=self.roundoff, rounded=self.rounded, floating_point=self.float_point)
    
    @property
    def random(self):
        pass