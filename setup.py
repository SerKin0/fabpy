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
    install_requires=[],  # Зависимости (например, "requests >= 2.25.1")
    python_requires=">=3.6",
)