from setuptools import find_packages, setup

setup(
    name='rosmaster_lib',
    author='Biorobotics Lab - Clement Joseph under faculty mentor, Dr.Alfredo Weitzenfeld. Based on Rosmaster_Lib and other packages for Rosmaster Robot by Yahboom Team',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'rosmaster_lib': ['openni2/**'],
    },
    install_requires=[
        'pyserial>=3.4',
        'rplidar-roboticia>=0.9.5',
        'opencv-python>=4.5',
        'numpy>=1.19',
        'openni>=2.3.0',
    ],
    python_requires='>=3.6',
)
