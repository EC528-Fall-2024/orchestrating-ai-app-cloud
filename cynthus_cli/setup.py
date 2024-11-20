import setuptools
from distutils.core import setup

setup(
    name='cynthus',
    version='1.0.0',
    description='Cynthus - A CLI for AI Application Deployment on the Cloud',
    author='Ryan Darrow, Krishna Patel, Thai Nguyen, Zhaowen Gu, Harlan Jones, Jialin Sui',
    author_email='darrowry@bu.edu',
    packages=['cynthus'],
    entry_points={
        'console_scripts': ['cynthus=cynthus.commands:cli_entry_point'],
    },
    install_requires=[
        'requests',
        'kaggle',
        'pyrebase',
        'firebase_auth'
    ],
)
