from setuptools import setup

PLUGIN_NAME = "DUMMYFRAME"

setup(
    name="dummyFrame",
    version="1.0.0",
    install_requires=["slideshow"],
    entry_points={"slideshow": ["dummyFrame = dummyframe_hookimpl"]},
    py_modules=["dummyframe_hookimpl"],
    
)