# FabPy

 Библиотека на Python для вычисления и оформления погрешностей в LaTeX в физических лабораторных работах.

# Установка 

Вы можете использовать для установки pip:

```pip install fabpy```

# Использование
## Среднеквадратичное отклонение, случайная, приборная и абсолютная погрешности

`fabpy` может использоваться в различных средах программирования, однако рекомендуется использовать Jupiter Notebook или Jupyter Lab.

```python
import fabpy as fb
```

Допустим что у вас некоторые измерения времени `t = [21.5, 22.1, 21.9]` с погрешностью прибора измерения $\Delta t = 0,2 \,с$. Занесем эти данные в объект `Values`:

```python
import fabpy as fb

t = fb.Values(name='t', values=[21.5, 22.1, 21.9], delta=0.2)
```

---
Объект `Values` имеет такие параметры как:

- `name` - имя переменной, которое будет использоваться в формулах LaTeX;
- `values` - значения измерений, может принимать как множество значений (*list, tuple*), так и одно значение (*int, float*);

*Учитывайте*, что при создании объекта с одним значением ($n = 1$), случайная погрешность (`RandomError`) будет равно **0**, т.к. при расчете среднеквадратичного отклонения (`StandardError`), знаменатель равен 0;

$$S_t = \sqrt{\frac{\sum_{i=1}^{n} (\overline{t} - t_i)^2}{n(n-1)}}$$

- `delta` - погрешность измерительного прибора в тех же единицах, что и измерения;
- `roundoff` - количество знаков после запятой для округления;
- `alpha` - доверительный коэффициент для расчета доверительного интервала. По умолчанию 0.95;
- `use_instrumental_error` - использовать ли при расчетах абсолютной погрешности приборную погрешность;
- `use_random_error` - использовать ли при расчетах абсолютной погрешности случайную погрешность;
- `rounded` - использовать при расчетах округленные значения (по `roundoff`) или точные значения;
---

После создания объекта класса, можно и получить необходимые данные.

```python
from fabpy.dataclass import Values

t = Values(name='t', values=[21.5, 22.1, 21.9], delta=0.2)

# Получение точного значения СРЕДНЕКВАДРАТИЧНОГО ОТКЛОНЕНИЯ 
print(t.standard_deviation.value)
>>> 0.17638342073763963
# Получение округленного значения СРЕДНЕКВАДРАТИЧНОГО ОТКЛОНЕНИЯ
print(t.standard_deviation.round_value())
>>> 0.2
# Получение формулы вычисления LaTeX
print(t.standard_deviation.latex())
>>> S_{ t } = \sqrt{\frac{ \sum_{ i=1 }^{n} (\overline{ t } - { t }_{i})^2}{ n(n-1) }} = \sqrt{\frac{ (21,8 - 21,5)^2 + (21,8 - 22,1)^2 + (21,8 - 21,9)^2 }{ 3 \, (3 - 1) } } = 0,2

print(t.random_error.value)
>>> 0.7589778594340633
print(t.random_error.round_value())
>>> 0.8
print(t.random_error.latex())
>>> \Delta \, { t }_{\text{сл}} = t_{ 0,95, \, n-1 } \cdot S_{ t, \, n } = 4,303 \cdot 0,2 = 0,8

print(t.instrumental_error.value)
>>> 0.13066666666666668
print(t.instrumental_error.round_value())
>>> 0.1
print(t.instrumental_error.latex())
>>> \Delta \, { t }_{\text{пр}} = t_{ 0,95, \, \infty } \cdot \frac{ \delta_{ t } }{ 3 } = 1,96 \cdot \frac{ 0,2 }{ 3 } = 0,1

print(t.absolute_error.value)
>>> 0.7701436027708667
print(t.absolute_error.round_value())
>>> 0.8
print(t.absolute_error.latex())
>>> \Delta \, { t } = \sqrt{ { \Delta { t }_{\text{сл}} }^2 + { \Delta { t }_{\text{пр}} }^2 } = \sqrt{ { 0,8 }^2 + { 0,1 }^2 } = 0,8
```

В результате получаете как серию точных и округленных значений, так и формулы вычисления.

Однако, если посторонний человек посмотрит такие формулы, у него могут возникнуть сомнения в верности вычисления. Это связано с тем, что при вычислении используются точные значения. Если вы хотите, чтобы в вычислениях участвовали значения округленные, нужно установить параметр класса `Values(rounded=True)`:

```python
from fabpy.dataclass import Values

t = Values(name='t', values=[21.5, 22.1, 21.9], delta=0.2, rounded=True)

print(t.absolute_error.value)
>>> 0.9055385138137417
print(t.absolute_error.round_value())
>>> 0.9
print(t.absolute_error.latex())
>>> \Delta \, { t } = \sqrt{ { \Delta { t }_{\text{сл}} }^2 + { \Delta { t }_{\text{пр}} }^2 } = \sqrt{ { 0,9 }^2 + { 0,1 }^2 } = 0,9
```
$$\Delta \, { t } = \sqrt{ { \Delta { t }_{\text{сл}} }^2 + { \Delta { t }_{\text{пр}} }^2 } = \sqrt{ { 0,9 }^2 + { 0,1 }^2 } = 0,9$$

## Косвенная погрешность

В качестве примера, возьму формулу для вычисления момента инерции из лабораторной работы "Матяник Обребека".

$$J = \frac{mgr^2(t_2 - t_1)^2}{h\left(1 - \frac{t_2}{t_1}\right)^2 + h'} - mr^2$$

Для начала заводим все данные в объект `Values`:

```python
from fabpy import Values, Formula

# Создаем переменные эксперементальных измерений и констант
_R = [18.7, 18.7, 18.7]
_m = 190
_r = 1.75
_h = 150
_g = 980
_t_1 = [11.6, 11.1, 11.7]
_t_2 = [21.5, 22.1, 21.9]
_h__prime = [127.5, 127.5, 127.0]

# Создаем объекты Values
R = Values(name=f'R', values=_R, delta=0.1, rounded=True)
m = Values(name=f'm', values=_m, delta=0.5, use_random_error=False, rounded=True)
g = Values(name=f'g', values=_g, delta=0., use_instrumental_error=False, use_random_error=False, rounded=True)
r = Values(name=f"r", values=_r, delta=0.005, use_random_error=False, roundoff=3, rounded=True)
t_1 = Values(name=f"t_{{1}}", values=_t_1, delta=0.2, rounded=True)
t_2 = Values(name=f"t_{{2}}", values=_t_2, delta=0.2, rounded=True)
h = Values(name=f"h", values=_h, delta=0.1, use_random_error=False, rounded=True)
h__prime = Values(name=f"h'", values=_h__prime, delta=0.1, rounded=True)
```

Теперь нужно записать изначальную формулу, по которой будем считать ее значение и косвенную погрешность. Для этого создаем любую переменную и записываем формулу на подобии с библиотекой `sympy`, добавляя к переменным данных `.sp`, означающая что используется в качестве объекта `sympy`.

После чего заносим формулу и данные в объект `Formula`.


```python
J = (m * g * r**2 * (t_2 - t_1)**2) / (h * (1 - t_2/t_1)**2 + h__prime) - m * r**2

f = Formula(J, [h__prime, R, m, g, r, t_1, t_2, h], 'J', rounded=True)
```

---
Объект Formula имеет следующие параметры:

- `formula` - символьное выражение (тип *sympy.Expr*), представляющее формулу для вычисления;
- `data` - список объектов `Values`, содержащих измеренные значения и их погрешности;
- `name` - имя переменной, которое будет использоваться в формулах LaTeX (по умолчанию 't');
- `roundoff` - количество знаков после запятой для округления (по умолчанию 1);
- `floating_point` - символ разделителя десятичной части в LaTeX-выводе (по умолчанию ',');
- `rounded` - использовать при расчетах округленные (по roundoff) или точные значения (по умолчанию False).
---

Теперь выведим формулу LaTeX:
```python
print(f.latex())
print(f.value)
print(f.round_value())

>>> J = \frac{g m r^{2} \left(- t_{1} + t_{2}\right)^{2}}{h \left(1 - \frac{t_{2}}{t_{1}}\right)^{2} + h'} - m r^{2} = \frac{1,75^{2} \cdot 190 \cdot 980 \left(- 11,5 + 21,8\right)^{2}}{127,3 + 150 \left(1 - \frac{21,8}{11,5}\right)^{2}} - 1,75^{2} \cdot 190 = 243721,
>>> 243721.156186329
>>> 243721.2

print(f.indetect_error.latex())
print(f.indetect_error.value)
print(f.indetect_error.round_value())

>>> \Delta{ J } = \sqrt{\frac{\Delta { h }^{2} g^{2} m^{2} r^{4} \left(1 - \frac{t_{2}}{t_{1}}\right)^{4} \left(- t_{1} + t_{2}\right)^{4}}{\left(h \left(1 - \frac{t_{2}}{t_{1}}\right)^{2} + h'\right)^{4}} + \frac{\Delta { h' }^{2} g^{2} m^{2} r^{4} \left(- t_{1} + t_{2}\right)^{4}}{\left(h \left(1 - \frac{t_{2}}{t_{1}}\right)^{2} + h'\right)^{4}} + \Delta { m }^{2} \left(\frac{g r^{2} \left(- t_{1} + t_{2}\right)^{2}}{h \left(1 - \frac{t_{2}}{t_{1}}\right)^{2} + h'} - r^{2}\right)^{2} + \Delta { r }^{2} \left(\frac{2 g m r \left(- t_{1} + t_{2}\right)^{2}}{h \left(1 - \frac{t_{2}}{t_{1}}\right)^{2} + h'} - 2 m r\right)^{2} + \Delta { t_{1} }^{2} \left(- \frac{2 g h m r^{2} t_{2} \left(1 - \frac{t_{2}}{t_{1}}\right) \left(- t_{1} + t_{2}\right)^{2}}{t_{1}^{2} \left(h \left(1 - \frac{t_{2}}{t_{1}}\right)^{2} + h'\right)^{2}} + \frac{g m r^{2} \left(2 t_{1} - 2 t_{2}\right)}{h \left(1 - \frac{t_{2}}{t_{1}}\right)^{2} + h'}\right)^{2} + \Delta { t_{2} }^{2} \left(\frac{2 g h m r^{2} \left(1 - \frac{t_{2}}{t_{1}}\right) \left(- t_{1} + t_{2}\right)^{2}}{t_{1} \left(h \left(1 - \frac{t_{2}}{t_{1}}\right)^{2} + h'\right)^{2}} + \frac{g m r^{2} \left(- 2 t_{1} + 2 t_{2}\right)}{h \left(1 - \frac{t_{2}}{t_{1}}\right)^{2} + h'}\right)^{2}} = \sqrt{0,003^{2} \left(\frac{2 \cdot 1,750 \cdot 190,0 \cdot 980,0 \left(- 11,5 + 21,8\right)^{2}}{127,3 + 150,0 \left(1 - \frac{21,8}{11,5}\right)^{2}} - 2 \cdot 1,750 \cdot 190,0\right)^{2} + \frac{0,1^{2} \cdot 1,750^{4} \cdot 190,0^{2} \cdot 980,0^{2} \left(1 - \frac{21,8}{11,5}\right)^{4} \left(- 11,5 + 21,8\right)^{4}}{\left(127,3 + 150,0 \left(1 - \frac{21,8}{11,5}\right)^{2}\right)^{4}} + 0,3^{2} \left(\frac{1,750^{2} \cdot 980,0 \left(- 11,5 + 21,8\right)^{2}}{127,3 + 150,0 \left(1 - \frac{21,8}{11,5}\right)^{2}} - 1,750^{2}\right)^{2} + \frac{0,9^{2} \cdot 1,750^{4} \cdot 190,0^{2} \cdot 980,0^{2} \left(- 11,5 + 21,8\right)^{4}}{\left(127,3 + 150,0 \left(1 - \frac{21,8}{11,5}\right)^{2}\right)^{4}} + 0,9^{2} \left(\frac{1,750^{2} \cdot 190,0 \cdot 980,0 \left(- 2 \cdot 11,5 + 2 \cdot 21,8\right)}{127,3 + 150,0 \left(1 - \frac{21,8}{11,5}\right)^{2}} + \frac{2 \cdot 1,750^{2} \cdot 150,0 \cdot 190,0 \cdot 980,0 \left(1 - \frac{21,8}{11,5}\right) \left(- 11,5 + 21,8\right)^{2}}{11,5 \left(127,3 + 150,0 \left(1 - \frac{21,8}{11,5}\right)^{2}\right)^{2}}\right)^{2} + 0,9^{2} \left(\frac{1,750^{2} \cdot 190,0 \cdot 980,0 \left(2 \cdot 11,5 - 2 \cdot 21,8\right)}{127,3 + 150,0 \left(1 - \frac{21,8}{11,5}\right)^{2}} - \frac{2 \cdot 1,750^{2} \cdot 150,0 \cdot 190,0 \cdot 21,8 \cdot 980,0 \left(1 - \frac{21,8}{11,5}\right) \left(- 11,5 + 21,8\right)^{2}}{11,5^{2} \left(127,3 + 150,0 \left(1 - \frac{21,8}{11,5}\right)^{2}\right)^{2}}\right)^{2}} = 22241,4
>>> 22241.44380543627
>>> 22241.4
```

$$J = \frac{g m r^{2} \left(- t_{1} + t_{2}\right)^{2}}{h \left(1 - \frac{t_{2}}{t_{1}}\right)^{2} + h'} - m r^{2} = \frac{1,75^{2} \cdot 190 \cdot 980 \left(- 11,5 + 21,8\right)^{2}}{127,3 + 150 \left(1 - \frac{21,8}{11,5}\right)^{2}} - 1,75^{2} \cdot 190 = 243721$$

$$\Delta{ J } = \sqrt{\frac{\Delta { h }^{2} g^{2} m^{2} r^{4} \left(1 - \frac{t_{2}}{t_{1}}\right)^{4} \left(- t_{1} + t_{2}\right)^{4}}{\left(h \left(1 - \frac{t_{2}}{t_{1}}\right)^{2} + h'\right)^{4}} + \frac{\Delta { h' }^{2} g^{2} m^{2} r^{4} \left(- t_{1} + t_{2}\right)^{4}}{\left(h \left(1 - \frac{t_{2}}{t_{1}}\right)^{2} + h'\right)^{4}} + \Delta { m }^{2} \left(\frac{g r^{2} \left(- t_{1} + t_{2}\right)^{2}}{h \left(1 - \frac{t_{2}}{t_{1}}\right)^{2} + h'} - r^{2}\right)^{2} + \Delta { r }^{2} \left(\frac{2 g m r \left(- t_{1} + t_{2}\right)^{2}}{h \left(1 - \frac{t_{2}}{t_{1}}\right)^{2} + h'} - 2 m r\right)^{2} + \Delta { t_{1} }^{2} \left(- \frac{2 g h m r^{2} t_{2} \left(1 - \frac{t_{2}}{t_{1}}\right) \left(- t_{1} + t_{2}\right)^{2}}{t_{1}^{2} \left(h \left(1 - \frac{t_{2}}{t_{1}}\right)^{2} + h'\right)^{2}} + \frac{g m r^{2} \left(2 t_{1} - 2 t_{2}\right)}{h \left(1 - \frac{t_{2}}{t_{1}}\right)^{2} + h'}\right)^{2} + \Delta { t_{2} }^{2} \left(\frac{2 g h m r^{2} \left(1 - \frac{t_{2}}{t_{1}}\right) \left(- t_{1} + t_{2}\right)^{2}}{t_{1} \left(h \left(1 - \frac{t_{2}}{t_{1}}\right)^{2} + h'\right)^{2}} + \frac{g m r^{2} \left(- 2 t_{1} + 2 t_{2}\right)}{h \left(1 - \frac{t_{2}}{t_{1}}\right)^{2} + h'}\right)^{2}} = \sqrt{0,003^{2} \left(\frac{2 \cdot 1,750 \cdot 190,0 \cdot 980,0 \left(- 11,5 + 21,8\right)^{2}}{127,3 + 150,0 \left(1 - \frac{21,8}{11,5}\right)^{2}} - 2 \cdot 1,750 \cdot 190,0\right)^{2} + \frac{0,1^{2} \cdot 1,750^{4} \cdot 190,0^{2} \cdot 980,0^{2} \left(1 - \frac{21,8}{11,5}\right)^{4} \left(- 11,5 + 21,8\right)^{4}}{\left(127,3 + 150,0 \left(1 - \frac{21,8}{11,5}\right)^{2}\right)^{4}} + 0,3^{2} \left(\frac{1,750^{2} \cdot 980,0 \left(- 11,5 + 21,8\right)^{2}}{127,3 + 150,0 \left(1 - \frac{21,8}{11,5}\right)^{2}} - 1,750^{2}\right)^{2} + \frac{0,9^{2} \cdot 1,750^{4} \cdot 190,0^{2} \cdot 980,0^{2} \left(- 11,5 + 21,8\right)^{4}}{\left(127,3 + 150,0 \left(1 - \frac{21,8}{11,5}\right)^{2}\right)^{4}} + 0,9^{2} \left(\frac{1,750^{2} \cdot 190,0 \cdot 980,0 \left(- 2 \cdot 11,5 + 2 \cdot 21,8\right)}{127,3 + 150,0 \left(1 - \frac{21,8}{11,5}\right)^{2}} + \frac{2 \cdot 1,750^{2} \cdot 150,0 \cdot 190,0 \cdot 980,0 \left(1 - \frac{21,8}{11,5}\right) \left(- 11,5 + 21,8\right)^{2}}{11,5 \left(127,3 + 150,0 \left(1 - \frac{21,8}{11,5}\right)^{2}\right)^{2}}\right)^{2} + 0,9^{2} \left(\frac{1,750^{2} \cdot 190,0 \cdot 980,0 \left(2 \cdot 11,5 - 2 \cdot 21,8\right)}{127,3 + 150,0 \left(1 - \frac{21,8}{11,5}\right)^{2}} - \frac{2 \cdot 1,750^{2} \cdot 150,0 \cdot 190,0 \cdot 21,8 \cdot 980,0 \left(1 - \frac{21,8}{11,5}\right) \left(- 11,5 + 21,8\right)^{2}}{11,5^{2} \left(127,3 + 150,0 \left(1 - \frac{21,8}{11,5}\right)^{2}\right)^{2}}\right)^{2}} = 22241,4$$