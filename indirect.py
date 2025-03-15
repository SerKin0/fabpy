from math import sqrt
from dataclasses import dataclass
import sympy as sp

from fabpy.constants import students_coefficient
from fabpy.utils import rounding, student


class IndetectError:
    def __init__(self, data: dict[tuple | list], name: str = 't', roundoff: int = 1, floating_point: str = ','):
        
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
        pass

    def latex(self):
        pass
    