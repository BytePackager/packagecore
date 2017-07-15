#!/usr/bin/env python3


from setuptools import setup, find_packages

with open("VERSION", "r") as versionFile:
  version = versionFile.read().strip()

setup(
  name="packagecore",
  description="Utility for building Linux packages for multiple " \
      "distributions.",
  author="Dominique LaSalle",
  author_email="dominique@bytepackager.com",
  url="https://github.com/bytepackager/packagecore",
  license="GPL2",
  install_requires="pyyaml",
  python_requires=">=3.0",
  version=version,
  packages=find_packages(),
  test_suite="packagecore",
  include_package_data=True,
  package_data={"": "packagecore/VERSION"},
  entry_points={
    "console_scripts": [
      "packagecore = packagecore.__main__:main"
    ]
  })
