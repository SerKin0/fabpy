from models.constants import students_coefficient

def rounding(number: float, roundoff: int) -> str:
    return f"{number:.{roundoff}f}"

# Получение коэффицента Стьюдента
def student(alpha: float, n: int) -> int:
    if alpha in students_coefficient.keys():
        values = students_coefficient.get(alpha)
        return values.get(n)
    return 1

def string_russian_to_tex(string: str, command: str = "text") -> str:
    """ Преобразует строку в формат, подходящий для импорта в формулу LaTeX """
    def iscyrilic(symbol: str) -> bool:
        return symbol in "абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
    
    if string.startswith(r"\text") and string.endswith("}"):
        if string[5] == "{" and string[-1] == "}":
            return string

    result = ""
    cur = 0
    while cur < len(string):
        if string[cur:cur+5] == r"\text" and cur+5 < len(string) and string[cur+5] == "{":
            brace_count = 1
            end_pos = cur + 6 
            while end_pos < len(string) and brace_count > 0:
                if string[end_pos] == "{":
                    brace_count += 1
                elif string[end_pos] == "}":
                    brace_count -= 1
                end_pos += 1
            
            result += string[cur:end_pos]
            cur = end_pos
            continue
        
        if not iscyrilic(string[cur]):
            result += string[cur]
            cur += 1
        else:
            start = cur
            while cur < len(string) and iscyrilic(string[cur]):
                cur += 1
            cyrillic_text = string[start:cur]
            
            result += fr"\{command}{{{cyrillic_text}}}"
    
    return result
    