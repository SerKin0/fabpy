from math import sqrt
from dataclasses import dataclass
import sympy as sp

from fabpy.constants import students_coefficient
from fabpy.utils import rounding, student
from fabpy.dataclass import Values

class IndetectError:
    def __init__(self, data: dict[Values], name: str = 't', roundoff: int = 1, floating_point: str = ','):
        self.data = data
        self.name = name
        self.roundoff = roundoff
        self.floating_point = floating_point

        self.latex_name = str()
        self.latex_general = str()
        self.latex_values = str()
        self.latex_result = str()

        self.result = float()

        self.check_values = False
        self.check_latex = False

    def calculation(self):
        pass

    def build(self):
        if not self.check_values:
            raise ValueError("You can't create formula components because the required numeric values are missing. Try correcting the input data and restarting the calculation function.")
        else:
            self.latex_name = fr"\Delta{{ {self.name} }}"

            self.latex_general = fr" "
            
            self.latex_values = fr" ".replace('.', self.floating_point)
            
            self.latex_result = rounding(self.result, self.roundoff).replace('.', self.floating_point)
            self.check_latex = True

    def latex(self):
        pass
    