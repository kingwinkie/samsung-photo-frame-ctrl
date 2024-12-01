from setuptools import setup


setup(
    name="loadImgUrl",
    version="1.0.0",
    install_requires=["slideshow"],
    entry_points={"slideshow": ["loadImgUrl = loadimgurl_hookimpl"]},
    py_modules=["loadimgurl_hookimpl","loaderconfig","imgurlloader"],
    
)