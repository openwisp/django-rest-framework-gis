#!/usr/bin/env python
import os
import sys

from setuptools import find_packages, setup

from rest_framework_gis import get_version

if sys.argv[-1] == 'publish':
    os.system("python setup.py sdist bdist_wheel")
    os.system("twine upload -s dist/*")
    os.system("rm -rf dist build")
    args = {'version': get_version()}
    print("You probably want to also tag the version now:")
    print("  git tag -a %(version)s -m 'version %(version)s'" % args)
    print("  git push --tags")
    sys.exit()

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
    install_requires=['djangorestframework'],
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
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3 :: Only',
    ],
    project_urls={
        'Bug Reports': 'https://github.com/openwisp/django-rest-framework-gis/issues',
        'Continuous Integration': 'https://travis-ci.org/openwisp/django-rest-framework-gis',
        'Mailing List': 'https://groups.google.com/forum/#!forum/django-rest-framework-gis',
        'Code Coverage': 'https://coveralls.io/github/openwisp/django-rest-framework-gis',
        'Source Code': 'https://github.com/openwisp/django-rest-framework-gis',
    },
)
