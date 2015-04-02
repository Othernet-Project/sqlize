import os
from setuptools import setup, find_packages

import sqlize


def read(fname):
    """ Return content of specified file """
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='sqlize',
    version=sqlize.__version__,
    author='Outernet Inc',
    author_email='branko@outernet.is',
    description='Lightweight SQL query builder',
    license='BSD',
    keywords='sql query builder',
    url='https://github.com/Outernet-project/sqlize',
    packages=find_packages(),
    long_description=read('README.rst'),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Topic :: Utilities',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
    ],
)
