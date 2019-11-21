from setuptools import setup, find_packages

setup(
    name="pyfinmod",
    version="0.2",
    description="Financial modelling in Python",
    url="https://github.com/smirnov-am/pyfinmod",
    author="Alexey Smirnov",
    author_email="msc.smirnov.am@gmail.com",
    license="MIT",
    scripts=[],
    install_requires=[
        "pandas>=0.23.4",
        "python-dateutil>=2.7.5",
        "scipy>=1.1.0",
        "requests>=2.21.0",
        "tables>=3.4.4",
    ],
    packages=find_packages(),
    data_files=[("", [])],
)
