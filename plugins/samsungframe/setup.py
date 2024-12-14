from setuptools import setup


setup(
    name="samsungFrame",
    version="1.0.0",
    install_requires=["slideshow"],
    entry_points={"slideshow": ["samsungFrame = samsungframe_hookimpl"]},
    py_modules=["samsungframe_hookimpl"],
    
)