from setuptools import setup

setup(
    name="clocks",
    version="1.0.0",
    install_requires=["slideshow"],
    entry_points={"slideshow": ["clocks = hookimpl"]},
    py_modules=["hookimpl"]
)