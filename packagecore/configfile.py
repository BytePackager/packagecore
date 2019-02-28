##
# @file configfile.py
# @brief Parse for the YAML config files.
# @author Dominique LaSalle <packagecore@solidlake.com>
# Copyright 2017-2019, Solid Lake LLC
# @version 1
# @date 2017-07-03


import yaml


class YAMLConfigFile:
    def __init__(self, filename):
        with open(filename, "r") as yamlfile:
            self._data = yaml.load(yamlfile.read())

    def getData(self):
        return self._data.copy()
