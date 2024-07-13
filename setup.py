# Minimal setup.py. Extend as needed.
from setuptools import setup, find_namespace_packages

setup(name = 'cocotbext-apb3',
      version = '0.1',
      packages = find_namespace_packages(include=['cocotbext.amba_bus','cocotbext.sram']),
      install_requires = ['cocotb'],
      python_requires = '>=3.8',
      classifiers = [
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)",
        "Framework :: cocotb"])
