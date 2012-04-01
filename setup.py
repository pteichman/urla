#!/usr/bin/env python

# Require setuptools. See http://pypi.python.org/pypi/setuptools for
# installation instructions, or run the ez_setup script found at
# http://peak.telecommunity.com/dist/ez_setup.py
from setuptools import setup, find_packages

setup(
    name = "urla",
    version = "0.9.0",
    author = "Peter Teichman",
    author_email = "peter@teichman.org",
    packages = ["urla"],
    test_suite = "tests",
    install_requires = ["argparse==1.2.1", "Whoosh==2.0.0"],
    classifiers = [
    ],
    entry_points = {
        "console_scripts" : [
            "urla = urla.control:main"
        ]
    }
)
