#Create Setup.py file to make the module installable
from setuptools import setup, find_packages


setup(
    name = "nipo",
    version = "0.1",
    author = "Mcflyhalf",
    author_email = "mcflyhalf@live.com",
    description = ("An application of facial recognition in classroom attendance monitoring"),
    keywords = "facial recognition classroom attendance",
    packages= find_packages(),
)

