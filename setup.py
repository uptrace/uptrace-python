import os

import setuptools


PACKAGE_INFO = {}
with open(os.path.join("src", "uptrace", "version.py")) as f:
    exec(f.read(), PACKAGE_INFO)

setuptools.setup(version=PACKAGE_INFO["__version__"])
