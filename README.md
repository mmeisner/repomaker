# repomaker

`repomaker` is a small Python library that is used to create git repositories
programmatically. The API is simple and intuitive.

Also included is a `GitRepoServer` class which can start and stop a
`git daemon` process that serves git repos.

The library can be used from Python unit tests or if you just need to automate
some git procedures from a Python script.

The library has only been tested on Linux. It uses the native `git` command
to do its work.

See the `example.py` file for an example of how to use the `GitRepo` and
`GitRepoServer` classes.

If `example.py` is executed, it will print all the git commands it executes.

## Similar projects

With a quick search I found only two other similar projects, although I am
sure there must be more?

* [GitPython](https://github.com/gitpython-developers/GitPython)
  *GitPython is a python library used to interact with Git repositories*.
  This is a huge Python library that also includes a full-blown implementation
  of the git object model in Python.
* [fixtures-git](https://opendev.org/x/fixtures-git) *A git fixture using the
  fixtures API for writing tests for tools that use git*.
  There are no usage examples for this module, so I am unsure about exactly
  what this is.
