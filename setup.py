from setuptools import find_packages, setup

setup(
    name='rosmaster_lib',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        'pyserial>=3.4',
        'rplidar-roboticia>=1.0.0',
        'opencv-python>=4.5',
        'numpy>=1.19',
        'openni>=2.3.0',
    ],
    python_requires='>=3.6',
)
