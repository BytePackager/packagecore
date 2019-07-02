The packagecore Command
=======================

The `packagecore` command is the most common route for invoking PackageCore and
building packages.

Generally, it will be invoked from inside of the source code to be built as:
```
packagecore "$(cat VERSION)"
```

Doing so will cause it to load a configuration from `packagecore.yaml` in the
same directory.

The syntax for its use is:

```
packagecore [options] <version> [<release number>]
```

Where `<version>` is the current version of your software, and
`<release number>` is the current release for that version of your software. 


Options
-------

You change the default behavior of the command using the following
flags/options:

* `-c <yaml file>, --config=<yaml file>`:

  The path to the yaml configuration file. Defaults to
  `packagecore.yaml`.

* `-C <source dir>, --src=<source dir>`:

  The source directory to build. Defaults to './'.

* `-p <distribution list>, --package=<distribution list>, --packages=<distribution list>`:
  Instead of building all packages in a configuration
  file, build package for a specific set of distributions in a comma delimited
  list (e.g., `--packages=ubuntu18.04,fedora29`).

* `-o <output directory>, --outputdir=<output directory>`:
  The directory to put generated packages into. If the
  directory does not exist, it will be created. Defaults
  to ./.

* `-e <variable name>=<variable value>`:
  Add the given environment variable to the executed docker containers. May be
  specified multiple times to provide multiple environment variables.


You can also get a list of distribution that packages can currently be built
for via:
```
packagecore -d 
```
