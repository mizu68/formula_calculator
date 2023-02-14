from setuptools import setup, find_packages
import codecs
from formula_calculator import __version__ as ver

def read_install_requires():
    with codecs.open('requirements.txt', 'r', encoding='utf-8') as f:
        res = f.readlines()
    res = list(map(lambda s: s.replace('\n', ''), res))
    return res

setup(
    name="formula_calculator",
    version=ver,
    packages=find_packages(),
    install_requires=read_install_requires(),
    python_requires='>=3.6',
    description="交易与衍生品部自研公式计算器",
    package_data={'': ['*.*']},
)