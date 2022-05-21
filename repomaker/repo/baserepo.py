#!/usr/bin/env python3
import os
import shutil
import sys
from pathlib import Path

from .. import run
from .. import log


class RepoError(Exception):
    """Repo Exception"""


class BaseRepo(object):
    """
    """
    VCS = "baserepo"

    def __init__(self, path, parent=None, logger=None, **kwargs):
        # path to repo (relative to parent path)
        self.path = path

        # full URL of the repo
        self.url = ""

        # Log instance for repo operations (default is silent logger)
        self.log = logger or log.Log(level=-1)

        # parent repo of this repo (if any)
        self.parent = parent

        super().__init__(**kwargs)

    def __str__(self):
        s = f"<{self.__class__.__name__}:{self.path}"
        for k in ('rev', 'branch', 'url'):
            v = self.__dict__[k]
            if v:
                s += f" {k}={v}"
        return s + ">"

    def __repr__(self):
        return self.__str__()

    def __lt__(self, other):
        """Support sorting of class objects"""
        return self.path < other.path

    @classmethod
    def create_from_clone(cls, url_base, name, branch=None, args=None):
        """
        Clone repo from `url_base/name` and return Repo instance from the clone

        :param url_base: git base URL
        :param name: repo name/path
        :param branch: branch or tag to checkout
        :param args: additional git clone args
        """
        raise NotImplementedError()


    ###########################################################################
    # VCS admin operations
    ###########################################################################

    def _get_cmdline(self, cmdline):
        """
        Return complete commandline string suitable for the repo engine/type

        :param cmdline:
        :return:
        """
        raise NotImplementedError()

    def run_shell_command(self, cmdline, assert_ok=True):
        """
        Run shell command in repo

        :param cmdline: shell command
        :param assert_ok:
        """
        exitcode, out, err = run.cmd_run(cmdline, cwd=self.path, logger=self.log)

        if assert_ok and exitcode != 0:
            self.log.error(f"run_shell_command('{cmdline}') failed with exitcode {exitcode}:")
            self.log.error(err)
            exit(1)

        return out

    def run_command(self, cmdline, assert_ok=True):
        """
        Run VCS command with cmdline

        :param cmdline: shell command
        :param assert_ok:
        """
        cmdline = self._get_cmdline(cmdline)

        exitcode, out, err = run.cmd_run(cmdline, logger=self.log)

        if assert_ok and exitcode != 0:
            self.log.error(f"run_command('{cmdline}') failed with exitcode {exitcode}:")
            self.log.error(err)
            exit(1)

        return out.rstrip()

    def delete_on_disk(self):
        """
        Delete everything from disk (if it is safe)
        """
        if not os.path.exists(self.path):
            return True

        items = os.listdir(self.path)
        if items:
            repo_meta_dir = os.path.join(self.path, f".{self.VCS}")
            if os.path.exists(repo_meta_dir) and self.is_dirty():
                self.log.verb(f"NOT deleting dirty {self.VCS} repo at {self.path}")
                return False

        self.log.verb(f"deleting {self.VCS} repo at {self.path}")
        shutil.rmtree(self.path)
        return True


    ###########################################################################
    # VCS state operation
    ###########################################################################

    def checkout(self, ref=None):
        """
        Switch repo branch

        :param ref:     Revision to update to (None for tip)
        :return:        self
        """
        raise NotImplementedError()


    ###########################################################################
    # VCS query operations
    ###########################################################################

    def get_current_branch(self):
        """
        Return name of current branch
        """
        return NotImplementedError()

    def is_dirty(self):
        raise NotImplemented()


    ###########################################################################
    # VCS change operations
    # All these methods return an instance of the class itself
    ###########################################################################

    def init(self):
        """
        Create repo directory and initialize repo

        :return: self
        """
        raise NotImplementedError()

    def file_add(self, filepath, from_file=None, text=None, force=False):
        """
        Add file to staging area, ready to commit

        :param filepath: file path in repo
        :param from_file: copy this file and use that as file contents
        :param text: use this text as file contents
        :param force: True to overwrite existing file
        :return: self
        """
        raise NotImplementedError()

    def file_remove(self, filepath):
        """
        Remove file (for next commit)

        :param filepath: file path in repo
        :return: self
        """
        raise NotImplementedError()

    def commit(self, message, addremove=False):
        """
        Commit in single-threaded mode

        :param message:   Message for the commit
        :param addremove: True to automatically add/remove files
        :return: self
        """
        raise NotImplementedError()

    def tag(self, name, message=None, ref=None):
        """
        Tag a commit

        :param name:     Tag name
        :param message:  Tag commit message (default is same as `name`)
        :param ref:      Revision to tag (None for HEAD)
        :return: self
        """
        raise NotImplementedError()

    def branch_create(self, name):
        """
        Create branch

        :param name:     Tag name
        :return: self
        """
        raise NotImplementedError()

    def branch_move(self, name):
        """
        Rename branch

        :param name:     Tag name
        :return: self
        """
        raise NotImplementedError()
