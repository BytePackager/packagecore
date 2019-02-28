##
# @file scriptfile.py
# @brief Functions for generating script files.
# @author Dominique LaSalle <packagecore@solidlake.com>
# Copyright 2017-2019, Solid Lake LLC
# @version 1
# @date 2017-05-21


import os


##
# @brief Open a file like object with executable permissions.
#
# @param filename The name of the file to open.
#
# @return The open file object.
def __open(filename):
    return os.fdopen(os.open(filename, os.O_WRONLY | os.O_CREAT, 0o755), "w")


##
# @brief Create a shell script on the filesystem.
#
# @param filename The name of the script.
# @param cmds The commands to be execute.
# @param env Environment variables to set in the script.
#
# @return None
def generateScript(filename, cmds, env=None):
    if env is None:
        env = {}
    with __open(filename) as scriptFile:
        scriptFile.write("#!/bin/bash -e\n")
        scriptFile.write("\n")
        for key, value in env.items():
            scriptFile.write("%s=\"%s\"\n" % (key, value))
        scriptFile.write("\n")
        scriptFile.write(cmds)
        scriptFile.write("\n")
