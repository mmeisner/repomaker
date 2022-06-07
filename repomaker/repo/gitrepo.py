#!/usr/bin/env python3
import os
import shutil
from pathlib import Path

from .baserepo import BaseRepo, RepoError
from .. import run


class GitRepo(BaseRepo):
    """
    Git repo class.
    """
    VCS = "git"

    USER_NAME = "Ada Lovelace"
    USER_EMAIL = "ada@unito.it"

    @classmethod
    def create_from_clone(cls, url_base, name, branch=None, args=None, logger=None):
        # [--recurse-submodules[=<pathspec>]] [--[no-]shallow-submodules]
        # --branch <name>
        args = f"{args} " if args else ""
        branch = f"--branch {branch} " if branch else ""
        cmd = f"git clone {branch}{args}{url_base}/{name}"
        repo = cls(name, logger=logger)
        run.cmd_run(cmd, logger=logger, assert_ok=True)
        return repo


    ###########################################################################
    # VCS admin operations
    ###########################################################################

    def _get_cmdline(self, cmdline):
        return f"git -C {self.path} {cmdline}"

    def config_read(self, key):
        """
        Read git config value from local repo

        :param key: Config key to read, e.g. 'user.email'
        :return: Value of config key
        """
        out = self.run_command(f"config {key}", assert_ok=False)
        return out.strip()

    def config_write(self, key, value):
        """
        Write local repo git config with key `key` with `value`

        :param key: Config key to write, e.g. 'user.email'
        :param value: Value of config key
        """
        self.run_command(f"config {key} '{value}'")

    def config_write_user(self, user_name=None, user_email=None, force=False):
        """
        If git repo config does not contain 'user.name' then write
        'user.name' and 'user.email' config.

        If no `user_name` or `user_email` are provided, dummy defaults
        will be used.

        User name and email must have a value for "git commit" to succeed.

        :param user_name: User name
        :param user_email: User email
        :param force: Force writing of config even if it already has a value
        """
        if force or not self.config_read("user.name"):
            if not user_name:
                user_name = GitRepo.USER_NAME
            self.config_write("user.name", user_name)

            if not user_email:
                user_email = GitRepo.USER_EMAIL
            self.config_write("user.email", user_email)


    ###########################################################################
    # VCS query operations
    ###########################################################################

    def get_current_branch(self):
        return self.run_command(f"branch --show-current")


    ###########################################################################
    # VCS state operation
    ###########################################################################

    def checkout(self, ref=None):
        self.run_command(f"checkout {ref}")
        return self


    ###########################################################################
    # VCS change operations
    ###########################################################################

    def init(self):
        """
        Initialize git repo and set user.name and user.email to default values.

        :return: self
        """
        # git 2.28 has:
        #     git init --initial-branch=main
        # or
        #     git init -b main
        path = Path(self.path)
        if not path.is_dir():
            path.mkdir()

        self.run_command("init")

        # ensure there is a username and email
        self.config_write_user()

        return self

    def file_add(self, filepath, srcfile=None, text=None, force=False):
        """
        Add file with relative path `filepath` to the index.

        File is created with verbatim contents `text` or is copied from
        existing file located at `copy_from`.

        If file already exists in the repo, RepoError is raised, unless force
        is True.

        :param filepath: Relative path of file inside the repo
        :param srcfile: Path to file to copy from
        :param text: Text to write to file
        :param force: Overwrite existing file
        :return: self
        """
        actualpath = Path(self.path) / filepath
        if not force and actualpath.exists():
            raise RepoError(f"{actualpath} already exists")

        if text and srcfile:
            raise RepoError("`text` and `copy_from` are mutually exclusive")

        if not actualpath.parent.is_dir():
            actualpath.parent.mkdir(parents=True)

        if force and actualpath.is_file():
            actualpath.unlink()

        if srcfile:
            shutil.copyfile(srcfile, actualpath)
        elif text:
            open(actualpath, "w").write(text)
        else:
            text = f"some text in {filepath}"

        self.run_command(f"add {filepath}")
        return self

    def file_remove(self, filepath):
        self.run_command(f"rm {filepath}")
        return self

    def commit(self, message=None, addremove=False, verify=False):
        if addremove:
            self.run_command("add -A")

        # optionally bypass pre-commit and commit-msg hooks
        arg_verify = "" if verify else "--no-verify "

        self.run_command(f"commit {arg_verify}-m '{message}'")
        return self

    def tag(self, name, message=None, ref=None):
        if not ref:
            ref = "HEAD"
        message = message if message else name
        cmd = f"tag -a {name} -m '{message}' {ref}"
        self.run_command(cmd)
        return self

    def branch_create(self, name):
        self.run_command(f"checkout -b {name}")
        return self

    def branch_move(self, name):
        self.run_command(f"branch -M {name}")
        return self
