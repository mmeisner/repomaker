# repomaker

`repomaker` is a small Python library that is used to create git repositories
programmatically. The API is simple and intuitive.

Also included is a `GitRepoServer` class which can start and stop a
`git daemon` process that serves git repos.

The library can be used from Python unit tests or if you just need to automate
some git procedures from a Python script.

The library has only been tested on Linux. It uses the native `git` command
to do its work.
