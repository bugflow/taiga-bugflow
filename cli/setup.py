from setuptools import setup

setup(
    name='tiaga-bugflow',
    version='0.1',
    py_modules=['tiaga-bugflow'],
    install_requires=[
        'Click'
    ],
    entry_points='''
        [console_scripts]
        tiaga-bugflow=tiaga_bugflow:cli 
    ''',
)
