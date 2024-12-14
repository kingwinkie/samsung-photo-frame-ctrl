from setuptools import setup


setup(
    name="loadImgArtsy",
    version="1.0.0",
    install_requires=["slideshow"],
    entry_points={"slideshow": ["loadImgArtsy = loadimga_hookimpl"]},
    py_modules=["loadimga_hookimpl","imgaloader"]
    
)