#!/usr/bin/env python3

import os

from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, "README.md")) as f:
    README = f.read()

if __name__ == "__main__":
    setup(
        name="jasmin-django-utils",
        setup_requires=["setuptools_scm"],
        use_scm_version=True,
        description="Django utilities used by JASMIN apps.",
        long_description=README,
        classifiers=[
            "Programming Language :: Python",
            "Framework :: Django",
        ],
        author="Matt Pryor",
        author_email="matt.pryor@stfc.ac.uk",
        url="https://github.com/cedadev/jasmin-django-utils",
        keywords="web django jasmin utilities utils enumfield crossdb settings appsettings",
        packages=find_packages(),
        include_package_data=True,
        zip_safe=False,
        install_requires=["django"],
        extras_require={
            "api": [
                "djangorestframework",
                "django-oauth-toolkit",
            ],
        },
    )
