from math import sqrt
from dataclasses import dataclass

from fabpy.constants import students_coefficient
from fabpy.utils import rounding, student


class StandardDeviation:
    def __init__(self, values: list, name: str = 't', roundoff: int = 1, floating_point: str = ','):
        self.values = values
        self.name = name
        self.roundoff = roundoff
        self.floating_point = floating_point

        self.latex_name = str()
        self.latex_general = str()
        self.latex_values = str()
        self.latex_result = str()

        self.average_value = float()
        self.n = int()
        self._result = float()

        self.check_values = False
        self.check_latex = False

    @property
    def result(self) -> float:
        if not self.check_values:
            self.calculation()
        return self._result

    @result.setter
    def result(self, value):
        self._result = value

    def calculation(self) -> None:
        try:
            self.average_value = sum(self.values) / len(self.values)
            self.n = len(self.values)
            self._result = sqrt(sum([(self.average_value - var)**2 for var in self.values]) / (self.n * (self.n - 1)))
            self.check_values = True

            self.build()
        except ZeroDivisionError:
            raise ZeroDivisionError("The length of the list is zero")

    def build(self) -> None:
        if not self.check_values:
            raise ValueError("You can't create formula components because the required numeric values are missing. Try correcting the input data and restarting the calculation function.")
        else:
            self.latex_name = fr"S_{{ {self.name} }}"

            self.latex_general = fr"\sqrt{{\frac{{ \sum_{{ i=1 }}^{{n}} (\overline{{ {self.name} }} - {{ {self.name} }}_{{i}})^2}}{{ n(n-1) }}}}"
            
            temp_sum = " + ".join([fr"({rounding(self.average_value, self.roundoff)} - {rounding(var, self.roundoff)})^2" for var in self.values])
            self.latex_values = fr"\sqrt{{ \frac{{ {temp_sum} }}{{ {self.n} \, ({self.n} - 1) }} }}".replace('.', self.floating_point)
            
            self.latex_result = rounding(self.result, self.roundoff).replace('.', self.floating_point)
            self.check_latex = True

    def latex(self, print_name: bool = True, print_general: bool = True, print_values: bool = True, print_result: bool = True) -> str:
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
    def __init__(self, values: list, standard_deviation: float | StandardDeviation, alpha: float = 0.95, name: str = 't', roundoff: int = 1, floating_point: str = ','):
        self.values = values
        self.alpha = alpha
        self.name = name
        self.roundoff = roundoff
        self.floating_point = floating_point

        if isinstance(standard_deviation, StandardDeviation):
            self.standard_deviation = standard_deviation.result  # Используем свойство result
        elif isinstance(standard_deviation, (float, int)):
            self.standard_deviation = float(standard_deviation)
        else:
            raise TypeError("standard_deviation must be either a float or an instance of StandardDeviation")

        self.latex_name = str()
        self.latex_general = str()
        self.latex_values = str()
        self.latex_result = str()

        self.student_t = float()
        self.n = int()
        self._result = float()

        self.check_values = False
        self.check_latex = False

    @property
    def result(self) -> float:
        if not self.check_values:
            self.calculation()
        return self._result

    @result.setter
    def result(self, value):
        self._result = value

    def calculation(self) -> None:
        self.n = len(self.values)
        self.student_t = student(self.alpha, self.n - 1)

        if not self.student_t:
            raise ValueError(f"There is no definition of the value for such parameters (alpha = {self.alpha}, n = {self.n}).")
        
        self._result = self.student_t * self.standard_deviation
        self.check_values = True

        self.build()

    def build(self) -> None:
        if not self.check_values:
            raise ValueError("You can't create formula components because the required numeric values are missing. Try correcting the input data and restarting the calculation function.")
        else:
            self.latex_name = fr"\Delta \, {{ {self.name} }}_{{\text{{сл}}}}"

            self.latex_general = fr"t_{{ {self.alpha}, \, n-1 }} \cdot S_{{ {self.name}, \, n }}".replace('.', self.floating_point)
            
            self.latex_values = fr"{rounding(self.student_t, self.roundoff)} \cdot {rounding(self.standard_deviation, self.roundoff)}".replace('.', self.floating_point)
            
            self.latex_result = rounding(self._result, self.roundoff).replace('.', self.floating_point)
            self.check_latex = True

    def latex(self, print_name: bool = True, print_general: bool = True, print_values: bool = True, print_result: bool = True) -> str:
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
    def __init__(self, delta: float, alpha: float = 0.95, name: str = 't', roundoff: int = 1, floating_point: str = ','):
        self.delta = delta
        self.alpha = alpha
        self.name = name
        self.roundoff = roundoff
        self.floating_point = floating_point

        self.latex_name = str()
        self.latex_general = str()
        self.latex_values = str()
        self.latex_result = str()

        self.student_t = float()
        self._result = float()

        self.check_values = False
        self.check_latex = False

    @property
    def result(self) -> float:
        if not self.check_values:
            self.calculation()
        return self._result

    def calculation(self) -> None:
        self.student_t = student(self.alpha, float('inf'))

        self._result = self.student_t * self.delta / 3
        self.check_values = True

        self.build()

    def build(self) -> None:
        if not self.check_values:
            raise ValueError("You can't create formula components because the required numeric values are missing. Try correcting the input data and restarting the calculation function.")
        else:
            self.latex_name = fr"\Delta \, {{ {self.name} }}_{{\text{{пр}}}}"

            self.latex_general = fr"t_{{ {self.alpha}, \, \infty }} \cdot \frac{{ \delta_{{ {self.name} }} }}{{ 3 }}".replace('.', self.floating_point)
            
            self.latex_values = fr"{self.student_t} \cdot \frac{{ {self.delta} }}{{ 3 }}".replace('.', self.floating_point)
            
            self.latex_result = rounding(self._result, self.roundoff).replace('.', self.floating_point)
            self.check_latex = True

    def latex(self, print_name: bool = True, print_general: bool = True, print_values: bool = True, print_result: bool = True) -> str:
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
    def __init__(self, random_error: float | RandomError = None, instrumental_error: float | InstrumentalError = None, name: str = 't', roundoff: int = 1, floating_point: str = ','):
        self.name = name
        self.roundoff = roundoff
        self.floating_point = floating_point

        if isinstance(random_error, RandomError):
            self.random_error = random_error.result  # Используем свойство result
        elif isinstance(random_error, (float, int)):
            self.random_error = float(random_error)
        else:
            raise TypeError("Random Error Type Error.")

        if instrumental_error is None:
            self.instrumental_error = 0
        elif isinstance(instrumental_error, InstrumentalError):
            self.instrumental_error = instrumental_error.result  # Используем свойство result
        elif isinstance(instrumental_error, (float, int)):
            self.instrumental_error = float(instrumental_error)
        else:
            raise TypeError("Instrumental Error Type Error.")
        
        self.latex_name = str()
        self.latex_general = str()
        self.latex_values = str()
        self.latex_result = str()

        self._result = float()

        self.check_values = False
        self.check_latex = False

    @property
    def result(self) -> float:
        if not self.check_values:
            self.calculation()
        return self._result

    def calculation(self) -> None:
        self._result = sqrt(self.instrumental_error**2 + self.random_error**2)
        self.check_values = True

        self.build()

    def build(self) -> None:
        if not self.check_values:
            raise ValueError("You can't create formula components because the required numeric values are missing. Try correcting the input data and restarting the calculation function.")
        else:
            self.latex_name = fr"\Delta \, {{ {self.name} }}"

            self.latex_general = fr"\sqrt{{ {{ \Delta {{ {self.name} }}_{{\text{{сл}}}} }}^2 + {{ \Delta {{ {self.name} }}_{{\text{{пр}}}} }}^2 }}".replace('.', self.floating_point)
            
            self.latex_values = fr"\sqrt{{ {{ {rounding(self.random_error, self.roundoff)} }}^2 + {{ {rounding(self.instrumental_error, self.roundoff)} }}^2 }}".replace('.', self.floating_point)
            
            self.latex_result = rounding(self._result, self.roundoff).replace('.', self.floating_point)
            self.check_latex = True

    def latex(self, print_name: bool = True, print_general: bool = True, print_values: bool = True, print_result: bool = True) -> str:
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