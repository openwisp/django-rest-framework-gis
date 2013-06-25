from setuptools import setup, find_packages

from rest_framework_gis import __version__

setup(
    name='django-rest-framework-gis',
    version=__version__,
    url='https://github.com/dmeehan/django-rest-framework-gis',
    license='',
    author='Douglas Meehan',
    author_email='dmeehan@gmail.com',
    description='Geographic add-ons for Django Rest Framework',
    packages=find_packages()
)
