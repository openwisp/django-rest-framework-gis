from setuptools import setup, find_packages
from setuptools.command.test import test

from rest_framework_gis import get_version


setup(
    name='djangorestframework-gis',
    version=get_version(),
    license='BSD',
    author='Douglas Meehan',
    author_email='dmeehan@gmail.com',
    description='Geographic add-ons for Django Rest Framework',
    url='https://github.com/djangonauts/django-rest-framework-gis',
    download_url='https://github.com/djangonauts/django-rest-framework-gis/releases',
    platforms=['Platform Indipendent'],
    keywords=['django', 'rest-framework', 'gis', 'geojson'],
    packages=find_packages(exclude=['tests', 'tests.*']),
    install_requires=[
        "djangorestframework>=2.2.2"
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Topic :: Internet :: WWW/HTTP',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Framework :: Django',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ]
)
