#!/usr/bin/env python3

PACKAGENAME = "packagecore"

from setuptools import setup, find_packages

import os

with open("%s/VERSION" % PACKAGENAME, "r") as versionFile:
  version = versionFile.read().strip()

readmePath = os.path.join(os.path.abspath(os.path.dirname(__file__)), "README.md")
with open(readmePath, "r") as readmeFile:
  readme = readmeFile.read()

setup(
  name=PACKAGENAME,
  description="Utility for building Linux packages for multiple " \
      "distributions.",
  long_description=readme,
  long_description_content_type="text/markdown",
  author="Dominique LaSalle",
  author_email="packagecore@solidlake.com",
  url="https://github.com/bytepackager/packagecore",
  license="GPL2",
  install_requires="pyyaml",
  python_requires=">=3.0",
  version=version,
  packages=find_packages(),
  test_suite=PACKAGENAME,
  include_package_data=True,
  entry_points={
    "console_scripts": [
      "%s = %s.__main__:main" % (PACKAGENAME, PACKAGENAME)
    ]
  })
