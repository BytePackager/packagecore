##
# @file buildvariables.py
# @brief Collection of environment variables set during build.
# @author Dominique LaSalle <packagecore@solidlake.com>
# Copyright 2017-2019, Solid Lake LLC
# @version 1
# @date 2017-05-15


DESTDIR_KEY = "BP_DESTDIR"
SOURCEDIR_KEY = "BP_SOURCEDIR"


class BuildVariables:
    ##
    # @brief Create a new set of environment variables for building.
    #
    # @param destDir The directory to treat as root during installation.
    # @param sourceDir The directory containing the source files.
    #
    # @return New BuildVariables object.
    def __init__(self, destDir, sourceDir):
        self._destDir = destDir
        self._sourceDir = sourceDir

    ##
    # @brief Write environment variables to a file.
    #
    # @param out The file-like object to write to.
    #
    # @return None
    def write(self, out):
        for key, value in self.generate().items():
            out.write("%s=\"%s\"\n" % (key, value))

    ##
    # @brief Generate a dictionary of the variables.
    #
    # @return The generated dictionary.
    def generate(self):
        return {
            DESTDIR_KEY: self._destDir,
            SOURCEDIR_KEY: self._sourceDir
        }
