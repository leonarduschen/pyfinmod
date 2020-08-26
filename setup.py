from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="pyfinmod",
    version="0.2",
    description="Financial modelling in Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/leonarduschen/pyfinmod",
    author="Alexey Smirnov",
    author_email="msc.smirnov.am@gmail.com",
    maintainer="leonarduschen",
    maintainer_email="leonardus.chen@gmail.com",
    license="MIT",
    scripts=[],
    install_requires=[
        "pandas>=0.23.4",
        "python-dateutil>=2.7.5",
        "scipy>=1.1.0",
        "requests>=2.21.0",
        "tables>=3.4.4",
    ],
    tests_require=["pytest"],
    setup_requires=['pytest-runner'],
    include_package_data=True,
    packages=find_packages(exclude=('tests', 'docs')),
    data_files=[("", [])],
)
