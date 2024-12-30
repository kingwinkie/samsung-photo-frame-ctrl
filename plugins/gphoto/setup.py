from setuptools import setup, find_packages

PLUGINNAME : str = "GPHOTO"

setup(
    name=PLUGINNAME,
    version="1.0.0",
    install_requires=["slideshow"],
    entry_points={"slideshow": [f"{PLUGINNAME} = {PLUGINNAME}_hookimpl"]},
    py_modules=[PLUGINNAME,"gpapi"],
    packages=find_packages()
)