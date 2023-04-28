from setuptools import setup, find_packages
from os.path import join, dirname

setup(
    name='MyPythonFinance',
    version='1.0',
    packages=['Mdf_downloader'],
    long_description=open(join(dirname(__file__), 'README.txt')).read(),
)