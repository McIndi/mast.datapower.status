# -*- coding: utf-8 -*-
import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "mast.datapower.status",
    version = "2.0.1",
    author = "Clifford Bressette",
    author_email = "cliffordbressette@mcindi.com",
    description = ("A utility to help manage users and groups for IBM DataPower"),
    license = "GPLv3",
    keywords = "DataPower user group account rbm",
    url = "http://github.com/mcindi/mast.datapower.accounts",
    namespace_packages=["mast", "mast.datapower"],
    packages=['mast', "mast.datapower", 'mast.datapower.status'],
    entry_points = {
        'mast_web_plugin': [
            'status = mast.datapower.status:WebPlugin'
        ]
    },
    package_data={
        "mast.datapower.status": ["docroot/*"]
    },
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Topic :: Utilities",
        "License :: OSI Approved :: GPLv3",
    ],
)

