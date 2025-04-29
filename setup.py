from setuptools import setup, find_packages

setup(
    name='med2img',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'pydicom',
        'Pillow'
    ],
    entry_points={
        'console_scripts': [
            'med2img=med2img.cli:main'
        ]
    }
)