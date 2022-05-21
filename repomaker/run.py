import subprocess
import sys


def cmd_run(cmd: str, cwd=None, assert_ok=False, logger=None):
    """
    Run `cmd` in directory `cwd` and return complete result

    The command is printed/logged if log.verbose >= 1.

    :param cmd: command to run
    :param cwd: directory in which to run the command
    :param assert_ok:
    :param logger:
    :return:
    """
    if logger:
        logger.shell(cmd)

    # Using universal_newlines=True converts the output to a string instead of a byte array
    # Python 3.7 has the more intuitive text=True instead of universal_newlines
    proc = subprocess.run(cmd, shell=True, cwd=cwd,
                       universal_newlines=True, encoding="utf8",
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if assert_ok and proc.returncode != 0:
        if logger:
            logger.error(proc.stderr)
        else:
            print(proc.stderr, file=sys.stderr)
        exit(1)

    return proc.returncode, proc.stdout, proc.stderr


def cmd_run_get_output(cmd: str, cwd=None, logger=None, splitlines=False):
    """
    Run `cmd` in directory `cwd` and return output stripped for newline

    If `splitlines` is True, multiline output is expected and output will be a
    list of lines (without newline character)

    :param cmd: command to run
    :param cwd: directory in which to run the command
    :param logger:
    :param splitlines: True to return lines as a list
    :return:
    """
    exitcode, out, err = cmd_run(cmd, cwd=cwd, logger=logger, assert_ok=True)

    if splitlines:
        return out.splitlines()

    return out.strip()
