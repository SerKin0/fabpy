from math import sqrt
from dataclasses import dataclass

from constants import students_coefficient, student
from utils import rounding

@dataclass
class TempStandardDeviation:
    average_value: float
    length: int
    result: float


@dataclass
class TempRandomError:
    alpha: float
    student_factor: float
    standard_deviation: float
    result: float

@dataclass
class TempIntsrumentalError:
    alpha: float
    delta: float
    student_factor: float
    result: float  


@dataclass
class TempAbsoluteError:
    intsrumental_error: float
    random_error: float
    result: float


class Fallibility:
    def __init__(self, data: list[float], roundoff: int = 0, name_variable: str = 't', floating_point: str = ','):
        self.data = data
        self.roundoff = roundoff
        self.name_variable = name_variable
        self.floating_point = floating_point
        
        # Переменные хранящие значения
        self.standard_deviation = float()
        self.random_error = float()
        self.intsrumental_error = float()
        self.absolute_error = float()

        # Переменные хранящие формулы LaTeX
        self.standard_deviation_latex = str()
        self.random_error_latex = str()
        self.intsrumental_error_latex = str()
        self.absolute_error_latex = str()

        # Вспомогательные значения
        self.temp_standard_deviation = None
        self.temp_random_error = None
        self.temp_intsrumental_error = None
        self.temp_absolute_error = None

    def calculation_standard_deviation(self):
        try:
            length = len(self.data)
            average_value = sum(self.data) / length
            numerator = sum([(average_value - value)**2 for value in self.data])
            denominator = length * (length - 1)
            
            self.standard_deviation = sqrt(numerator / denominator)
            self.temp_standard_deviation = TempStandardDeviation(average_value=average_value, length=length, result=self.standard_deviation)
            return self.standard_deviation
        except ZeroDivisionError:
            raise ZeroDivisionError("The value in the denominator is zero when calculating the standard deviation.")

    def writing_standard_deviation(self,
                                   print_start: bool = True,
                                   print_general_view: bool = True,
                                   print_calculation: bool = True, 
                                   print_result: bool = True):
        if not self.temp_standard_deviation:
            raise TypeError("The values of 'standard_deviation' were not processed")
        else:
            average_value = self.temp_standard_deviation.average_value
            length = self.temp_standard_deviation.length
            res = self.temp_standard_deviation.result
            
        string = r"\sqrt{{\frac{{{0}}}{{{1}}}}}" 
        general = fr"\sqrt{{\frac{{\sum_{{i=1}}^{{n}}(\overline{{{{{self.name_variable}}}}} - {{{self.name_variable}}}_i)^2}}{{n}}}}" 
        numerator = " + ".join([f"({rounding(average_value, self.roundoff)} - {rounding(value, self.roundoff)})^2" for value in self.data])
        denominator = fr"{length} ({length} - 1)"
        result = rounding(res, self.roundoff)

        temp_print = []
        if print_start:
            temp_print.append(f"S_{{{self.name_variable}}}")
        if print_general_view:
            temp_print.append(general)
        if print_calculation:
            temp_print.append(f"{string.format(numerator, denominator)}")
        if print_result:
            temp_print.append(result)

        self.standard_deviation_latex = " = ".join(temp_print).replace('.', self.floating_point)
        return self.standard_deviation_latex

    def calculation_random_error(self, alpha: float = 0.95):
        student_factor = student(alpha, len(self.data) - 1)
        standard_deviation = self.standard_deviation
        
        self.random_error = student_factor * standard_deviation
        self.temp_random_error = TempRandomError(student_factor=student_factor, standard_deviation=standard_deviation, result=self.random_error, alpha=alpha)
        return self.random_error

    def writing_random_error(self,
                             print_start: bool = True,
                             print_general_view: bool = True,
                             print_calculation: bool = True, 
                             print_result: bool = True):
        alpha = self.temp_random_error.alpha
        student_factor = self.temp_random_error.student_factor
        standard_deviation = rounding(self.temp_random_error.standard_deviation, self.roundoff)
        result = rounding(self.temp_random_error.result, self.roundoff)
        
        string = r"{0} \cdot {1}"
        general = fr"t_{{{alpha}, \, n - 1}} \cdot S_{{{{{self.name_variable}}}, n}}"

        temp_print = []
        if print_start:
            temp_print.append(fr"\Delta {{{self.name_variable}}}_{{\text{{сл}}}}")
        if print_general_view:
            temp_print.append(general)
        if print_calculation:
            temp_print.append(f"{string.format(self.temp_random_error.student_factor, standard_deviation)}")
        if print_result:
            temp_print.append(result)

        self.random_error_latex = " = ".join(temp_print).replace('.', self.floating_point)
        return self.random_error_latex

    def calculation_intsrumental_error(self, delta: float, alpha: float = 0.95):
        student_factor = student(alpha, float('inf'))
        
        self.intsrumental_error = student_factor * delta / 3
        self.temp_intsrumental_error = TempIntsrumentalError(alpha=alpha, delta=delta, result=self.intsrumental_error, student_factor=student_factor)
        return self.intsrumental_error

    def writing_intsrumental_error(self,
                             print_start: bool = True,
                             print_general_view: bool = True,
                             print_calculation: bool = True, 
                             print_result: bool = True):
        alpha = self.temp_intsrumental_error.alpha
        delta = rounding(self.temp_intsrumental_error.delta, self.roundoff)
        result = rounding(self.temp_intsrumental_error.result, self.roundoff)
        student_factor = self.temp_intsrumental_error.student_factor
        
        string = r"{0} \cdot \frac{{{1}}}{{3}}"
        general = fr"t_{{{alpha}, \, n}} \cdot \frac{{\delta_{{{self.name_variable}}}}}{{3}}"

        temp_print = []
        if print_start:
            temp_print.append(fr"\Delta {{{self.name_variable}}}_{{\text{{пр}}}}")
        if print_general_view:
            temp_print.append(general)
        if print_calculation:
            temp_print.append(f"{string.format(student_factor, delta)}")
        if print_result:
            temp_print.append(result)

        self.intsrumental_error_latex = " = ".join(temp_print).replace('.', self.floating_point)
        return self.intsrumental_error_latex

    def calculation_absolute_error(self):        
        self.absolute_error = sqrt(self.intsrumental_error ** 2 + self.random_error ** 2)
        self.temp_absolute_error = TempAbsoluteError(intsrumental_error=self.intsrumental_error, random_error=self.random_error, result=self.absolute_error)
        return self.absolute_error

    def writing_absolute_error(self,
                             print_start: bool = True,
                             print_general_view: bool = True,
                             print_calculation: bool = True, 
                             print_result: bool = True):
        random_error = rounding(self.temp_absolute_error.random_error, self.roundoff)
        intsrumental_error = rounding(self.temp_absolute_error.intsrumental_error, self.roundoff)
        result = rounding(self.temp_absolute_error.result, self.roundoff)
        
        string = r"\sqrt{{{0}^2 + {1}^2}}"
        general = fr"\sqrt{{\left({{{self.name_variable}}}_{{\text{{сл}}}}\right)^2 + \left({{{self.name_variable}}}_{{\text{{пр}}}}\right)^2}}"

        temp_print = []
        if print_start:
            temp_print.append(fr"\Delta {self.name_variable}")
        if print_general_view:
            temp_print.append(general)
        if print_calculation:
            temp_print.append(f"{string.format(random_error, intsrumental_error)}")
        if print_result:
            temp_print.append(result)

        self.absolute_error_latex = " = ".join(temp_print).replace('.', self.floating_point)
        return self.absolute_error_latex

        