from setuptools import setup, find_packages
from setuptools.command.test import test

from rest_framework_gis import get_version


class TestCommand(test):
    def run(self):
        from tests.runtests import runtests
        runtests()


setup(
    name='djangorestframework-gis',
    version=get_version(),
    url='https://github.com/dmeehan/django-rest-framework-gis',
    license='BSD',
    author='Douglas Meehan',
    author_email='dmeehan@gmail.com',
    description='Geographic add-ons for Django Rest Framework',
    packages=find_packages(exclude=['tests', 'tests.*']),
    install_requires=[
        "djangorestframework>=2.2.2",
        "django-filter>=0.7",
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP',
    ],
    cmdclass={"test": TestCommand},
)
