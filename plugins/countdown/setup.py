from setuptools import setup, find_packages

PLUGINNAME : str = "COUNTDOWN"

setup(
    name=PLUGINNAME,
    version="1.0.0",
    install_requires=["slideshow"],
    entry_points={"slideshow": [f"{PLUGINNAME} = {PLUGINNAME}_hookimpl"]},
    packages=find_packages()
)