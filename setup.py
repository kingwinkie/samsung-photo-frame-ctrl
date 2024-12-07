from setuptools import find_packages
from setuptools import setup


setup(
    name="slideshow",
    version="1.0.0",
    install_requires="pluggy>=0.3,<1.0",
    entry_points={"console_scripts": ["eggsample=eggsample.host:main"]},
    packages=find_packages()
)