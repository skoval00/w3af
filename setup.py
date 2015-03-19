# coding: utf-8

from setuptools import setup, find_packages
from glob import glob


setup(
    name='w3af_console',
    version=file('w3af/core/data/constants/version.txt').read().strip(),
    packages=find_packages(
        exclude=[
            'w3af.core.ui.gui',
            'w3af.core.ui.gui.*',
            'w3af.core.ui.tests.gui',
            'w3af.core.ui.tests.gui.*',
        ],
    ),
    data_files=[
        ('profiles', glob('profiles/*.pw3af')),
        ('examples', glob('scripts/*.w3af')),
        ('doc', glob('doc/[A-Z]*')),
    ],
    scripts=['w3af_console'],
    include_package_data=True,
    setup_requires = [ "setuptools_git>=0.3", ],

)
