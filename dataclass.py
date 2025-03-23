from fabpy import InstrumentalError, RandomError, StandardDeviation, AbsoluteError
from statistics import mean
from sympy import Symbol

class Values:
    def __init__(self, 
                 name: str, 
                 values: list, 
                 delta: float,  
                 roundoff: int = 1, 
                 alpha: float = 0.95, 
                 use_instrumental_error: bool = True,
                 use_random_error: bool = True):
        self.name = name
        self._values = values  # Приватный атрибут для хранения значений
        self.roundoff = roundoff
        self.delta = delta
        self.alpha = alpha
        self.use_instrumental_error = use_instrumental_error 
        self.use_random_error = use_random_error

        # Создаем SymPy-символ для использования в выражениях
        self.symbol = Symbol(name)
        self.error_symbol = Symbol(fr"\Delta {{ {name} }}")

        # Инициализируем атрибуты
        self.standard_deviation = None
        self.random_error = None
        self.instrumental_error = None
        self.absolute_error = None

        # Вычисляем все значения при создании объекта
        self._calculate_errors()

    @property
    def values(self):
        """Getter для values."""
        return self._values

    def _calculate_errors(self):
        """Метод для вычисления всех погрешностей и отклонений."""
        # Вычисляем стандартное отклонение
        self.standard_deviation = StandardDeviation(values=self._values, name=self.name, roundoff=self.roundoff)

        # Вычисляем случайную погрешность, если она используется
        if self.use_random_error:
            self.random_error = RandomError(values=self._values, name=self.name, roundoff=self.roundoff, standard_deviation=self.standard_deviation)
        else:
            self.random_error = None

        # Вычисляем приборную погрешность, если она используется
        if self.use_instrumental_error:
            self.instrumental_error = InstrumentalError(delta=self.delta, alpha=self.alpha, name=self.name, roundoff=self.roundoff)
        else:
            self.instrumental_error = None

        # Вычисляем абсолютную погрешность
        self.absolute_error = AbsoluteError(random_error=self.random_error, instrumental_error=self.instrumental_error, name=self.name, roundoff=self.roundoff)

    @property
    def value(self) -> float:
        """Среднее значение."""
        return mean(self._values) if self._values else 0.
    
    def round_value(self, rounding: int = None) -> float:
        return round(mean(self._values), self.roundoff if rounding is None else rounding)
    
    @property
    def error(self):
        """Возвращает результат абсолютной погрешности."""
        return self.absolute_error.result if self.absolute_error else 0
    
    @property
    def sp(self):
        """Возвращает SymPy-объект: символ переменной"""
        return self.symbol
    
    @property
    def spe(self):
        """Возращает SymPy-объект: символ погрешности переменной"""
        return self.error_symbol
    