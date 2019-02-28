##
# @file configparser.py
# @brief Class for turning dictionary config into set of builds.
# @author Dominique LaSalle <packagecore@solidlake.com>
# Copyright 2017-2019, Solid Lake LLC
# @version 1
# @date 2017-07-16


from .builddata import BuildData


def _stringifyCommands(cmds):
    if isinstance(cmds, list):
        cmds = "\n".join(cmds)
    elif isinstance(cmds, str):
        pass
    else:
        raise TypeError("Expected commands to be a string or list. Not '%s'." %
                        type(cmds))
    return cmds

# Will need to refactor this someday so that pylint doesn't have to be disabled
# pylint: disable=too-many-locals,too-many-branches


def parse(conf, version, release):
    builds = {}

    # set globals
    projectPreCompileCommands = ""
    projectCompileCommands = ""
    projectInstallCommands = ""
    projectPostInstallCommands = ""
    projectTestInstallCommands = ""
    if "commands" in conf:
        commands = conf["commands"]
        if "precompile" in commands:
            projectPreCompileCommands = _stringifyCommands(
                commands["precompile"])
        if "compile" in commands:
            projectCompileCommands = _stringifyCommands(
                commands["compile"])
        if "install" in commands:
            projectInstallCommands = _stringifyCommands(
                commands["install"])
        if "postinstall" in commands:
            projectPostInstallCommands = \
                _stringifyCommands(commands["postinstall"])
        if "testinstall" in commands:
            projectTestInstallCommands = \
                _stringifyCommands(commands["testinstall"])

    # parse packages
    for osName, data in conf["packages"].items():

        # set package specific commnds
        preCompileCommands = projectPreCompileCommands
        compileCommands = projectCompileCommands
        installCommands = projectInstallCommands
        postInstallCommands = projectPostInstallCommands
        testInstallCommands = projectTestInstallCommands
        if not data is None and "commands" in data:
            commands = data["commands"]
            if "precompile" in commands:
                projectPreCompileCommands = \
                    _stringifyCommands(commands["precompile"])
            if "compile" in commands:
                compileCommands = _stringifyCommands(commands["compile"])
            if "install" in commands:
                installCommands = _stringifyCommands(commands["install"])
            if "postinstall" in commands:
                postInstallCommands = _stringifyCommands(
                    commands["postinstall"])
            if "testinstall" in commands:
                testInstallCommands = _stringifyCommands(
                    commands["testinstall"])

        # construct it with the required fields
        buildData = BuildData(
            name=conf["name"],
            version=version,
            releaseNum=release,
            osName=osName,
            preCompileCommands=preCompileCommands,
            compileCommands=compileCommands,
            installCommands=installCommands,
            postInstallCommands=postInstallCommands,
            testInstallCommands=testInstallCommands)

        # set metadata fields
        if "maintainer" in conf:
            buildData.maintainer = conf["maintainer"]
        if "license" in conf:
            buildData.license = conf["license"]
        if "homepage" in conf:
            buildData.homepage = conf["homepage"]
        if "summary" in conf:
            buildData.summary = conf["summary"]

        # set dependencies
        if "builddeps" in data:
            buildData.buildDeps = data["builddeps"]
        if "deps" in data:
            buildData.runDeps = data["deps"]
        if "container" in data:
            buildData.container = data["container"]

        builds[buildData.osName] = buildData

    return builds
