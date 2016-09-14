# -*- coding: utf-8 -*-

from setuptools import setup, find_packages, Extension
#from disutils.core import Extension


with open('README.md') as f:
    readme = f.read()


setup(
    name='partitionengine',
    version='0.0.1',
    description='Package for Export Import Template Engine',
    long_description=readme,
    author='Preethi PY',
    author_email='preethi.py@gmail.com',
    packages=find_packages(exclude=('tests', 'docs')),
    #ext_modules=[Extension('log', ['partitionengine/logs/console.log'])],
    platforms=['any'],
    entry_points={
              'console_scripts': [
                  'partitionengine = partitionengine.Console:main',                  
              ],              
          },
)

