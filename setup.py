from setuptools import find_packages
from setuptools import setup


setup(
    name="slideshow",
    version="1.0.0",
    install_requires="pluggy>=0.3,<1.0",
    entry_points={"console_scripts": ["slideshow = slideshow", "txt2img = txt2img", "showimage = showimage"]},
    packages=find_packages()
)