from setuptools import setup, find_packages

setup(
    name="pywfd",
    version="1.1.7",
    description="A library to handle wfd in python.",
    install_requires=["numpy", "pandas", "dlchord"],
    author="anime-song",
    url="https://github.com/anime-song/wfdload",
    license="MIT",
    packages=["pywfd"],
)
