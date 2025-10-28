

class ErrorModel:
    def __init__(self, name: str = "t", values: list|tuple|float|int = 0., 
                 error: float|int = None, unit: str = "", roundoff: int = 1,
                 rounded: bool = True, float_point: str = ','):
        """ Модель класса для оброботки погрешностей полученных данных

        Args:
            name (str, optional): Имя переменной, которое будет участвовать в формулах (допускается оформление в стиле LaTeX). Defaults to "t".
            values (list | tuple | float | int, optional): Значение или значения переменной. Defaults to 0..
            error (float | int, optional): Если программа не должна сама вычислять данные по формулам, вы можете задать нужное значение. Defaults to None.
            unit (str, optional): Единицы измерения величины (допускается оформление в стиле LaTeX). Defaults to "".
            roundoff (int, optional): Количество цифр после запятой. Defaults to 1.
            rounded (bool, optional): При вычислениях округлять значение переменной до значащей цифры. Defaults to True.
            float_point (str, optional): Символ плавающей точки. Defaults to ','.
        """

        self._name = name
        
        if values in (list, tuple):
            self._values = values
        elif values in (int, float):
            self._values = [values]
        else:
            self._values = []
            raise ValueError(f"Параметр 'values' может быть только (list, tuple, float, int), а не {type(values)}.")
        
        self._error = error
        self._unit = unit
        self._roundoff = roundoff
        self._float_point = float_point

        # Среднее арифметическое значение
        self.average_value = None

    @property
    def name(self) -> str:
        """Возращает имя переменной."""
        return self._name
    
    def name(self, name: str) -> None:
        """Изменение значения переменной 'name'."""
        if name is None:
            self._name = ""
        else:
            self._name = name
    
    @property
    def values(self) -> list:
        return self._values