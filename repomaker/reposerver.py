"""
Functions to start a repo server (git daemon) as a background process
"""
import atexit
import os
import shlex
import shutil
import time
import subprocess
from pathlib import Path

from . import run


class RepoServerError(Exception):
    """RepoServer exception"""


class RepoServer(object):
    """
    This class can start a repo server (e.g. git daemon) that users
    can clone/push from/to and other operations
    """

    # The name of the VCS for this repo server class (overridden in subclass)
    VCS = None

    # The base URL of this repo server class (overridden in subclass)
    URL_BASE = None

    def __init__(self, work_dir, logger=None, logfile=None):
        """
        Create new server object

        :param work_dir:  Directory to start process from
        :param logger:    Log instance to use for logging from this class
        :param logfile:   Path of server's logfile
        """
        self.work_dir = work_dir

        if not logfile:
            logfile = Path(work_dir) / f"{self.VCS}-server.log"
        self.logfile = logfile

        self.log = logger
        
        # Directory of the repo (tree)
        self.root_dir = work_dir

        # Server process commandline (initialized in subclass)
        self.cmdline = None

        # Server process instance
        self.process = None

        atexit.register(self.stop)
        self.log.info(f"{self} created, logging to {self.logfile}")

    def __str__(self):
        return f"<{self.__class__.__name__} dir={self.work_dir}>"

    def delete_repos(self):
        """
        Delete all repos on server
        """
        self.log.info(f"{self} deleting all repos")
        shutil.rmtree(self.root_dir, ignore_errors=True)

    def atinit(self):
        """
        Prepare server launch (one-time setup)
        """
        self.log.info(f"makedirs {self.root_dir}")
        if not os.path.isdir(self.root_dir):
            os.makedirs(self.root_dir)

        # create and delete contents of the server logfile
        open(self.logfile, "w").close()

    def start(self):
        """
        Start the background process
        """
        self.log.info(f"starting server in {self.work_dir} with cmdline:\n  {self.cmdline}")
        self.atinit()

        args = shlex.split(self.cmdline)
        with open(self.logfile, "a") as logfile:
            self.process = subprocess.Popen(args, stdout=logfile, stderr=logfile, cwd=self.work_dir, shell=False)
            self.log.info(f"started server (pid={self.process.pid}) serving repos from {self.root_dir}")
        self.wait_until_ready()

    def wait_until_ready(self, timeout=None):
        """
        Wait for the repo server to become responsive
        """
        return NotImplementedError()

    def stop(self):
        """
        Terminate the background repo server process
        """
        if self.process and self.process.poll() is None:
            self.log.info(f"killing server pid {self.process.pid}")
            self.process.terminate()
            self.process.wait()
            self.process = None

    def restart(self):
        """
        Terminate the start the background repo server process
        """
        if self.process:
            self.stop()
        self.log.info("=" * 60)
        self.start()

    def repo_exists(self, path):
        """
        Return true is repo `path` exists on server

        :param path: repo path (relative to server root)
        :return: True if repo `path` exists on this server
        """
        raise NotImplemented()


class GitRepoServer(RepoServer):
    """
    Git specific implementation of RepoServer
    """
    VCS = "git"

    def __init__(self, work_dir, logger=None, logfile=None):
        super().__init__(work_dir, logger=logger, logfile=logfile)

        # Standard port is 9418
        self.port = 9418

        GitRepoServer.URL_BASE = f"git://localhost"

        self.cmdline = \
            f"git daemon --reuseaddr --port={self.port} --export-all --verbose --enable=receive-pack" + \
            f" --base-path=."

    def wait_until_ready(self, timeout=2):
        # create an empty dummy repository that we can use for connection test
        dummy_repo_name = "dummy-repo.git"
        repo_dir = Path(self.root_dir) / f"{dummy_repo_name}"
        if not repo_dir.is_dir():
            repo_dir.mkdir(parents=True)
            cmd = f"git --git-dir={repo_dir}/.git init --bare"
            run.cmd_run(cmd, cwd=self.root_dir, assert_ok=True)

        self.log.info(f"{self.VCS} server wait_until_ready()")

        time_started = time.time()
        deadline = time_started + timeout
        while time.time() < deadline:
            if self.repo_exists(dummy_repo_name):
                break
            time.sleep(0.1)

        if self.process.poll() is None:
            elapsed = time.time() - time_started
            self.log.info(f"Connected to {self.VCS} server in {elapsed:.1f}s")
        else:
            self.log.error("Oops, server exited. Here is the tail of the logfile:")
            out = run.cmd_run_get_output(f"tail {self.logfile}")
            print(out)
            raise RepoServerError("Oops, cannot connect to reposerver process")

    def repo_exists(self, path):
        # return quickly if directory doesn't exist
        repo_dir = Path(self.root_dir) / path
        if not repo_dir.is_dir():
            return False

        # then make a proper request to make sure all is fine
        url = f"{self.URL_BASE}/{path}"
        cmd = f"git ls-remote --heads {url}"
        exitcode, _, _ = run.cmd_run(cmd)
        return exitcode == 0
