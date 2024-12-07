from setuptools import setup


setup(
    name="loadImgE621",
    version="1.0.0",
    install_requires=["slideshow"],
    entry_points={"slideshow": ["loadImgE621 = loadimge_hookimpl"]},
    py_modules=["loadimge_hookimpl","loadereconfig","imgeloader","py621"],
    
)