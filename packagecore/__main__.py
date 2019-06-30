#!/usr/bin/python3
##
# @file main.py
# @brief The main function.
# @author Dominique LaSalle <packagecore@solidlake.com>
# Copyright 2017-2019, Solid Lake LLC
# @version 1
# @date 2017-07-03


import sys
import os
import argparse

from .configfile import YAMLConfigFile
from .packager import Packager
from .distributions import DATA


BIN_NAME = "packagecore"

# pylint: disable=redefined-builtin


class ShowDistributionsAction(argparse.Action):
    def __init__(self,
                 option_strings,
                 dest=None,
                 default=None,
                 help=None):
        super(ShowDistributionsAction, self).__init__(
            option_strings=option_strings,
            dest=dest,
            default=default,
            nargs=0,
            help=help)

    def __call__(self, parser, namespace, values, option_string=None):
        print("Available distributions to use as targets in the 'packages' section:")
        for distname in DATA:
            print("\t%s" % distname)
        parser.exit()


class ParseCommaSeparatedListAction(argparse.Action):
    def __init__(self,
                 option_strings,
                 dest,
                 nargs=None,
                 **kwargs):
        if nargs is not None:
            raise ValueError("nargs not allowed")
        super(ParseCommaSeparatedListAction, self).__init__(
            option_strings,
            dest=dest,
            **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        try:
            assert isinstance(values, str)
        except AssertionError:
            raise TypeError("%s is not a string" % values)
        args = values.split(",")
        setattr(namespace, self.dest, args)


class AddEnvironmentVariableAction(argparse.Action):
    def __init__(self,
                 option_strings,
                 dest,
                 nargs=None,
                 **kwargs):
        if nargs is not None:
            raise ValueError("nargs not allowed")
        super(AddEnvironmentVariableAction, self).__init__(
            option_strings,
            dest=dest,
            **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        try:
            assert isinstance(values, str)
        except AssertionError:
            raise TypeError("%s is not a string" % values)
        args = values.split(sep="=", maxsplit=1)
        if not hasattr(namespace, self.dest) or not getattr(namespace, self.dest):
            setattr(namespace, self.dest, {})
        env = getattr(namespace, self.dest)
        env[args[0]] = args[1]


def getVersion():
    import pkg_resources
    versionBytes = pkg_resources.resource_string(__name__, "VERSION")
    version = versionBytes.decode("utf8").strip()
    return version


def main():
    # defaults
    release = 1
    configFilename = "packagecore.yaml"
    outputdir = "./"

    packageCoreVersion = getVersion()

    usage = "usage: %(prog)s [options] <version> [<release>]"
    parser = argparse.ArgumentParser(usage=usage)

    # we set the default to None here, so we can check if it has been, otherwise
    # we'll just assume they're looking for the default in the -C option
    parser.add_argument("-c", "--config", dest="configfile",
                        metavar="<yaml file>",
                        default=None, help="The path to the yaml configuration "
                        "file. Defaults to %s." % configFilename)

    parser.add_argument("-C", "--src", dest="sourceDir",
                        metavar="<source dir>",
                        default="./", help="The source directory to build. "
                        "Defaults to '%(default)s'.")

    parser.add_argument("-p", "--package", "--packages", dest="distributions",
                        metavar="<distribution names>", default=None,
                        type=str, action=ParseCommaSeparatedListAction,
                        help="Instead of building all packages in a configuration file, build "
                        "packages for specific distributions (comma-separated list).")

    parser.add_argument("-o", "--outputdir", dest="outputdir",
                        metavar="<output directory>", default=outputdir,
                        help="The directory to "
                        "put generated packages into. If the directory does not exist, it "
                        "will be created. Defaults to %(default)s.")

    parser.add_argument("-d", "--distributions", action=ShowDistributionsAction,
                        dest="showdistributions", help="Show a list of available Linux "
                        "distributions to use as targets in the 'packages' section.",
                        default=False)

    parser.add_argument("-v", "--version", dest="showversion", action="version",
                        version=getVersion(),
                        help="Display the current version.", default=False)
    parser.add_argument("-e", "--environment", dest="environment",
                        action=AddEnvironmentVariableAction,
                        help="Pass environment variables into the containers"
                        " where the packages are built.", default=None)

    # parameters
    parser.add_argument("version",
                        help="The version of the package to generate (e.g., 1.2.3)")
    parser.add_argument("release", nargs="?", type=int,
                        help="The release number of the package to generate (e.g., 2)."
                        " Defaults to '%(default)s'.", default=1)

    args = parser.parse_args()

    print("args: {%s}" % args)
    if args.configfile is None:
        args.configfile = os.path.join(args.sourceDir, configFilename)

    if not args.version:
        print("Must supply a version string.", file=sys.stderr)
        parser.print_help(file=sys.stderr)
        return -1

    version = args.version
    release = args.release
    print("Building with %s %s." % (BIN_NAME, packageCoreVersion))
    print("Building version '%s' release '%d'." % (version, release))

    # if we're using the default configFilename assume we mean in the source
    # directory
    conf = YAMLConfigFile(args.configfile)

    packager = Packager(conf=conf.getData(), srcDir=args.sourceDir,
                        outputDir=args.outputdir,
                        version=version, release=release,
                        distributions=args.distributions,
                        environment=args.environment)

    print("This program is licensed under the GPLv2, a copy of which is ")
    print("included with this software package.")

    if packager.run():
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
