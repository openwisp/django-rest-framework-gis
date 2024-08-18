#!/usr/bin/env python
import os

from setuptools import find_packages, setup

from rest_framework_gis import get_version

here = os.path.abspath(os.path.dirname(__file__))

# Get the long description from the README file
with open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='djangorestframework-gis',
    version=get_version(),
    license='BSD',
    author='Douglas Meehan',
    author_email='django-rest-framework-gis@googlegroups.com',
    description='Geographic add-ons for Django Rest Framework',
    long_description=long_description,
    url='https://github.com/openwisp/django-rest-framework-gis',
    download_url='https://github.com/openwisp/django-rest-framework-gis/releases',
    platforms=['Platform Indipendent'],
    keywords=['django', 'rest-framework', 'gis', 'geojson'],
    packages=find_packages(exclude=['tests', 'tests.*']),
    install_requires=['djangorestframework>=3.12,<3.16', 'django-filter>=23.5,<25.0'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Topic :: Internet :: WWW/HTTP',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Framework :: Django',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3 :: Only',
    ],
    project_urls={
        'Bug Reports': 'https://github.com/openwisp/django-rest-framework-gis/issues',
        'Continuous Integration': (
            'https://github.com/openwisp/django-rest-framework-gis/actions?'
            'query=workflow%3A%22Django+Rest+Framework+Gis+CI+Build%22'
        ),
        'Mailing List': 'https://groups.google.com/forum/#!forum/django-rest-framework-gis',
        'Code Coverage': 'https://coveralls.io/github/openwisp/django-rest-framework-gis',
        'Source Code': 'https://github.com/openwisp/django-rest-framework-gis',
    },
)
