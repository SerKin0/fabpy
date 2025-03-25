from fabpy.constants import students_coefficient

def rounding(number: float, roundoff: int) -> str:
    return f"{number:.{roundoff}f}"

# Получение коэффицента Стьюдента
def student(alpha: float, n: int) -> int:
    if alpha in students_coefficient.keys():
        values = students_coefficient.get(alpha)
        return values.get(n)
    return None