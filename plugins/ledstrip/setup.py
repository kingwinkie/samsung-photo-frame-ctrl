from setuptools import setup


setup(
    name="ledstrip",
    version="1.0.0",
    install_requires=["slideshow"],
    entry_points={"slideshow": ["ledstrip = ledstrip_hookimpl"]},
    py_modules=["ledstrip_hookimpl","sender","ledconfig"],
    
)