from setuptools import find_packages, setup

setup(
    name='rosmaster_lib',
    version='1.0.0',
    packages=find_packages(),
    install_requires=['pyserial>=3.4'],
    python_requires='>=3.6',
)
