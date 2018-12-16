from setuptools import setup, find_packages

setup(name='pyfinmod',
      version='0.0.1',
      description='Financial modelling in Python',
      url='https://github.com/smirnov-am/pyfinmod',
      author='Alexey Smirnov',
      author_email='msc.smirnov.am@gmail.com',
      license='MIT',
      scripts=[],
      install_requires=['pandas',
                        'python-dateutil',
                        'scipy'],
      packages=find_packages(),
      data_files=[('', [])])
