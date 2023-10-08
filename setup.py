from setuptools import setup, find_packages

setup(
    name='emulsion',
    version='0.1.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'click',
    ],
    entry_points={
        'console_scripts': [
            'emulsion = emulsion:cli',
        ],
    },
)
