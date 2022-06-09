#!/usr/bin/env python3
# Example of using repomaker classes GitRepo and GitRepoServer
# tags: git repo test

__author__ = "Mads Meisner-Jensen"
import os
import argparse
import shutil

from repomaker import GitRepo, GitRepoServer, Log


# default logger instance for repo operations
# (prints git command that is executed)
log = Log(level=1)


def make_repo_abc(server_root, name, logger=log):
    """
    Example of how to create a repo programmatically
    """
    # create some repo on the server
    path = f"{server_root}/{name}"

    r = GitRepo(path, logger=logger).init()
    r.config_write_user(force=True)
    r.file_add("a", text="this is a file"). \
        commit(message="first commit"). \
        branch_move("main"). \
        file_add("b", text="another file"). \
        commit(message="next commit"). \
        file_remove("a"). \
        commit(message="third commit", addremove=True). \
        tag("1.0.0"). \
        branch_create("bugfix"). \
        file_add("b", text="modified text", force=True). \
        commit(message="bugfixed file b"). \
        checkout("main")

    user_name = r.config_read("user.name")
    print(f"user.name = {user_name}")

    return r


def example_testcase():
    """
    Example showing how to use repomaker in a testcase.
    In the steps below, "TEST" means what the test framework does
    and "PROG" means what the program under test does.

    - TEST: create some initial repos
    - TEST: start a git server of those repos
    - PROG: perform some actions towards git server and verify result
    - TEST: change repos on the server
    - PROG: perform some more actions towards git server and verify result
    - etc.
    """
    server_log = Log(level=1)
    server_root = "/tmp/reposerver"
    server = GitRepoServer(server_root, logger=server_log)
    server.delete_repos()
    server.start()

    name = "abc"
    # make a repo on the server
    repo = make_repo_abc(server.root_dir, name=name)
    # Get the full reflog of the created repo
    reflog = repo.reflog()

    # Now clone the repo from the server into /tmp
    os.chdir("/tmp")
    shutil.rmtree(name, ignore_errors=True)

    r = GitRepo.create_from_clone(server.URL_BASE, name, logger=log)
    log.info(f"cwd = {os.getcwd()}")
    branch_name = r.get_current_branch()
    print(f"current branch = {branch_name}")

    # Checkout bugfix branch
    r.checkout("bugfix")
    branch_name = r.get_current_branch()
    print(f"current branch = {branch_name}")

    # Print the reflog of the original server repo
    # It can be used to locate specific commit hashes
    log.info("reflog of repo:")
    for e in reflog:
        print(e)

    # Here we locate the commit(s) having "bugfixed" in the commit message
    log.info("finding the 'bugfix' commit entry in reflog of repo:")
    entries = r.reflog_find_substr(reflog, "subject", "bugfixed")
    for e in entries:
        print(e)

def parser_create():
    description = f"""\
Run example of how to use GitRepo and GitRepoServer classes
"""
    parser = argparse.ArgumentParser(
        description=description, formatter_class=argparse.RawDescriptionHelpFormatter)

    return parser


def main():
    parser = parser_create()
    opt = parser.parse_args()

    example_testcase()


if __name__ == "__main__":
    main()
