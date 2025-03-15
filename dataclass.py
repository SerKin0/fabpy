from fabpy import InstrumentalError, RandomError, StandardDeviation, AbsoluteError


class Values:
    def __init__(self, 
                 name: str, 
                 values: list, 
                 delta: float, 
                 absolute_error=None, 
                 roundoff: int = 1, 
                 alpha: float = 0.95, 
                 use_instrumental_error: bool = True):
        self.name = name
        self.values = values
        self.roundoff = roundoff
        self.absolute_error = absolute_error
        self.delta = delta
        self.alpha = alpha
        self.use_instrumental_error = use_instrumental_error 

    @property
    def value(self):
        return sum(self.values) / len(self.values) if self.values else 0
    
    @property
    def error(self):
        if self.absolute_error is None:
            # Вычисляем стандартное отклонение
            self.standard_deviation = StandardDeviation(values=self.values, name=self.name, roundoff=self.roundoff)
            # print(f"{self.standard_deviation.result=}")

            # Вычисляем случайную погрешность
            self.random_error = RandomError(values=self.values, name=self.name, roundoff=self.roundoff, standard_deviation=self.standard_deviation)
            # print(f"{self.random_error.result=}")

            # Вычисляем приборную погрешность, если use_instrumental_error=True
            if self.use_instrumental_error:
                self.instrumental_error = InstrumentalError(delta=self.delta, alpha=self.alpha, name=self.name, roundoff=self.roundoff)
            else:
                self.instrumental_error = None  # Приборная погрешность не учитывается
            # print(f"{self.instrumental_error.result=}")

            # Вычисляем абсолютную погрешность
            self.absolute_error = AbsoluteError(random_error=self.random_error, instrumental_error=self.instrumental_error, name=self.name, roundoff=self.roundoff)
            # print(f"{self.absolute_error.result=}")

        return self.absolute_error.result