import setuptools
from distutils.core import setup

setup(
    name='cynthus',
    version='1.0.0',
    description='Command Line Interface for Cynthus',
    author='Ryan Darrow',
    author_email='darrowry@bu.edu',
    packages=['cynthus'],
    entry_points={
        'console_scripts': ['cynthus=cynthus.commands:cli_entry_point'],
    },
    install_requires=[
        'requests',
    ],
)