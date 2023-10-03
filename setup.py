from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in hr_services/__init__.py
from hr_services import __version__ as version

setup(
	name="hr_services",
	version=version,
	description="HR Additional Services",
	author="Elite Resources",
	author_email="usamanaveed9263@gmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
