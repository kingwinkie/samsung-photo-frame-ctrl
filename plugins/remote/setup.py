from setuptools import setup, find_packages

PLUGINNAME : str = "REMOTE"

setup(
    name=PLUGINNAME,
    version="1.0.0",
    install_requires=["slideshow"],
    entry_points={"slideshow": [f"{PLUGINNAME} = {PLUGINNAME}_hookimpl"]},
    py_modules=[PLUGINNAME,"<CLASSFILE>"],
    packages=find_packages()
)