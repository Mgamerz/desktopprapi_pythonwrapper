#!/usr/bin/env python
import os
import re
from setuptools import setup

MODULE_NAME = 'DesktopprApi'

README = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()
VERSION = re.search("__version__ = '([^']+)'",
                    open('{0}.py'.format(MODULE_NAME)).read()).group(1)

setup(name=MODULE_NAME,
      author='Michael Perez',
      author_email='developer.mgamerzproductions@gmail.com',
      classifiers=['Intended Audience :: Developers',
                   'License :: OSI Approved :: GPL v3',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Programming Language :: Python :: 3.3'],
      description='API Wrapper for the Desktoppr.co web site',
      install_requires=['requests>=1.0.2', 'setuptools'],
      license='GPL v3',
      long_description=README,
      py_modules=[MODULE_NAME, 'DesktopprTester'],
      test_suite='DesktopprTester',
      url='https://github.com/mgamerz/desktopprapi_pythonwrapper',
      version=VERSION)
