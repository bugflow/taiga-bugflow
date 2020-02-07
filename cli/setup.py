from setuptools import setup

setup(
    name='taiga-bugflow',
    version='0.1',
    py_modules=['taiga-bugflow'],
    install_requires=[
        'Click'
    ],
    entry_points='''
        [console_scripts]
        taiga-bugflow=taiga_bugflow:cli 
    ''',
)
