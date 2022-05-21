#!/usr/bin/env python3
"""
Log class and console coloring
"""
import enum
import os
import sys


class Ansi:
    """

    """
    reset, bold, dim, italic, under, inv = "", "", "", "", "", ""

    class fg:
        black, red, green, yellow, blue, magenta, cyan, white = "", "", "", "", "", "", "", ""
        iblack, ired, igreen, iyellow, iblue, imagenta, icyan, iwhite = "", "", "", "", "", "", "", ""

    class bg(fg):
        pass

    class fg8:
        orange0, orange1, orange2, orange3 = "", "", "", ""
        pink0,   pink1,   pink2,   pink3   = "", "", "", ""
        purple0, purple1, purple2, purple3 = "", "", "", ""

    class style:
        note = "fg.iyellow"
        info = "fg.white bold"
        norm = ""
        verb = "fg.white"
        debug = "fg.icyan"
        trace = "fg.cyan italic"
        warn = "fg.iyellow"
        error = "fg.ired"
        tip = "fg.yellow"
        shell = "fg.igreen"
        lite = "fg.white bold"

    _initialized = False

    @staticmethod
    def enable(force=False):
        """
        Call this method to enable/disable ANSI colors.
        By default, all `Ansi.fg` and `Ansi.reset` etc. are empty strings.
        After calling this function, they will have proper ANSI escape values

        :param force: True to force use of colors
        """
        Ansi._initialized = True

        # dicts are ordered by default from Python 3.6
        # and thus this code will only work with Python 3.6+
        if not (force or (sys.stdout.isatty() and os.name != 'nt')):
            return

        # codes for foreground
        # black, red, green, yellow, blue, magenta, cyan, white
        # and same colors in intense version
        codes = iter([
            30, 31, 32, 33, 34, 35, 36, 37,
            90, 91, 92, 93, 94, 95, 96, 97])
        for k in Ansi.fg.__dict__.keys():
            if not k.startswith("__"):
                code = next(codes)
                setattr(Ansi.fg, k, f"\033[{code}m")
                setattr(Ansi.bg, k, f"\033[{code + 10}m")

        # codes for reset, bold, din, italic, under, inv
        codes = iter([
            0, 1, 2, 3, 4, 7])
        for k in Ansi.__dict__.keys():
            if type(Ansi.__dict__[k]) == str and not k.startswith("__"):
                code = next(codes)
                setattr(Ansi, k, f"\033[{code}m")

        # codes for 8-bit ANSI foreground colors
        codes = iter([
            130, 166, 172, 208,  # orange
            199, 207, 213, 219,  # pink
             93, 129,  99, 141,  # purple
        ])
        for k in Ansi.fg8.__dict__.keys():
            if not k.startswith("__"):
                code = next(codes)
                setattr(Ansi.fg8, k, f"\033[38:5:{code}m")

        # expand the colors into the Ansi.style attributes
        for k,v in Ansi.style.__dict__.items():
            if type(Ansi.style.__dict__[k]) == str and not k.startswith("__"):
                names = v.split(" ")
                s = ""
                for name in names:
                    if not name:
                        continue
                    if name.startswith("fg."):
                        s += Ansi.fg.__dict__[name[3:]]
                    else:
                        s += Ansi.__dict__[name]
                setattr(Ansi.style, k, s)


class Log(object):
    """
    Log() can be instanced globally or as a member of the main class
    """

    class Level(enum.IntEnum):
        Note = -1
        Info = 0
        Verbose = 1
        Debug = 2
        Trace = 3
        Crazy = 4

    def __init__(self, level=0, with_progress=False, with_tips=True, with_shell=True):
        self.level = level
        self.with_progress = with_progress
        # True to show user tips
        self.enable_tips = with_tips
        # True to show shell commands
        self.enable_shell = with_shell

        # initialize ANSI colors if user forgot to do so
        if not Ansi._initialized:
            Ansi.enable()

    def note(self, s, level=-1):
        """Log notice message that is more noteworthy than `info`"""
        if self.level >= level:
            print(f"{Ansi.style.note}{s}{Ansi.reset}")

    def info(self, s, level=0):
        """Log normal info message colorized specially"""
        if self.level >= level:
            print(f"{Ansi.style.info}{s}{Ansi.reset}")

    def norm(self, s, level=0):
        """Log normal info message (usaully neutral/white color)"""
        if self.level >= level:
            print(f"{Ansi.style.norm}{s}{Ansi.reset}")

    def verb(self, s, level=1):
        """Log message at verbose level (more detail)"""
        if self.level >= level:
            print(f"{Ansi.style.verb}{s}{Ansi.reset}")

    def debug(self, s, level=2):
        """Log message at debug level (lots of detail)"""
        if self.level >= level:
            print(f"{Ansi.style.debug}{s}{Ansi.reset}")

    def trace(self, s, level=3):
        """Log message at trace level (tons of detail)"""
        if self.level >= level:
            print(f"{Ansi.style.trace}{s}{Ansi.reset}")

    def error(self, s):
        print(f"{Ansi.style.error}ERROR: {s}{Ansi.reset}", file=sys.stderr)

    def warn(self, s):
        print(f"{Ansi.style.warn}WARNING: {s}{Ansi.reset}", file=sys.stderr)

    def lite(self, s, level=0):
        if self.level >= level:
            print(f"{Ansi.style.lite}{s}{Ansi.reset}")

    def tip(self, s):
        if self.enable_tips:
            print(f"{Ansi.style.tip}Tip: {s}{Ansi.reset}")

    def shell(self, s):
        if self.enable_shell:
            print(f"{Ansi.style.shell}{s}{Ansi.reset}")
