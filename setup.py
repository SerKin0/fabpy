from setuptools import setup, find_packages

setup(
    name="fabpy",
    version="0.2",
    packages=find_packages(),
    description="Подобии библиотеки на Python для вычисления и оформления погрешностей в LaTeX для физических лабораторных работ.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="SerKin0",
    author_email="sergey.skor007@gmail.com",
    url="https://github.com/SerKin0/fabpy",
    install_requires=[
        "numpy>=1.21.0",  # Если нужны другие зависимости
        "sympy>=1.9",     # Добавляем sympy (минимальная версия 1.9)
    ],
    python_requires=">=3.6",
)