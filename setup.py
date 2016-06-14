#!/usr/bin/env python3

import os, re

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

try:
    import jasmin_django_utils.__version__ as version
except ImportError:
    # If we get an import error, find the version string manually
    version = "unknown"
    with open(os.path.join(here, 'jasmin_django_utils', '__init__.py')) as f:
        for line in f:
            match = re.search('__version__ *= *[\'"](?P<version>.+)[\'"]', line)
            if match:
                version = match.group('version')
                break

with open(os.path.join(here, 'README.md')) as f:
    README = f.read()

requires = [
    'django',
]

if __name__ == "__main__":

    setup(
        name = 'jasmin-django-utils',
        version = version,
        description = 'Django utilities used by JASMIN apps',
        long_description = README,
        classifiers = [
            "Programming Language :: Python",
            "Framework :: Django",
        ],
        author = 'Matt Pryor',
        author_email = 'matt.pryor@stfc.ac.uk',
        url = 'http://www.jasmin.ac.uk',
        keywords = 'web django jasmin utilities utils enumfield crossdb',
        packages = find_packages(),
        include_package_data = True,
        zip_safe = False,
        install_requires = requires,
        tests_require = requires,
        test_suite = "jasmin_django_utils.test",
    )
