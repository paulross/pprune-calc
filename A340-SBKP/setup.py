from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import sys
import setuptools

__version__ = '0.0.1'

# Building: MACOSX_DEPLOYMENT_TARGET=10.9 python setup.py build_ext -f --inplace
# Testing: PYTHONPATH=. pytest --benchmark-name=long --benchmark-sort=name --benchmark-save=benchmark_00 --benchmark-warmup=on tests/unit/
# --benchmark-warmup=on is slow as it does about 10000 warmup iterations.
# Benchmark data in .benchmarks


test_requirements = [
    'pytest',
    'hypothesis',
]

setup(
    name='A340-SBKP',
    version=__version__,
    author='Paul Ross',
    author_email='apaulross@gmail.com',
    url='https://github.com/paulross/pprune-calc/A340-SBKP',
    packages=setuptools.find_packages('.'),
    package_dir={'' : '.'},
    description='Video analysis',
    long_description='',
    # ext_modules=ext_modules,
    install_requires=['numpy',],
    tests_require=test_requirements,
    # cmdclass={'build_ext': BuildExt},
    zip_safe=False,
)
