from setuptools import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='StanleyWedding',
    version='1.0.0',
    description='Python web application for uploading and displaying event photographs.',
    long_description=long_description,
    url='https://github.ncsu.edu/jwstanl3/stanley_wedding',
    license='Apache-2.0'
)
