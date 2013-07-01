from setuptools import setup, find_packages

from rest_framework_gis import __version__

setup(
    name='djangorestframework-gis',
    version=__version__,
    url='https://github.com/dmeehan/django-rest-framework-gis',
    license='BSD',
    author='Douglas Meehan',
    author_email='dmeehan@gmail.com',
    description='Geographic add-ons for Django Rest Framework',
    packages=find_packages(),
    install_requires=[
        "djangorestframework>=2.2.2"
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
    ]
)
