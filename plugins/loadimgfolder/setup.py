from setuptools import setup


setup(
    name="loadImgFolder",
    version="1.0.0",
    install_requires=["slideshow"],
    entry_points={"slideshow": ["loadImgFolder = loadimgfolder_hookimpl"]},
    py_modules=["loadimgfolder_hookimpl","loaderconfig","imgfolderloader"],
    
)