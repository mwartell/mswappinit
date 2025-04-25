"""
mswappinit - convenience wrappers for development configuration

https://github.com/mwartell/mswappinit
"""

import datetime
import io
import os
import sys
import typing
from pathlib import Path

import loguru
from dotenv import dotenv_values, load_dotenv

# we explicitly don't import the quick_db module here so that it is not autoloaded
#     import mswappinit.quick_db to use it

__all__ = [
    "project",
    "log",
]


class ProjectConfiguration:
    def __init__(self, testing_mock: str | None = None):
        # we want the variables in the os environment and in a dict
        if testing_mock:
            load_dotenv(stream=io.StringIO(testing_mock))
            env = dotenv_values(stream=io.StringIO(testing_mock))
        else:
            load_dotenv()
            env = dotenv_values()

        if "PROJECT_NAME" not in env or not env["PROJECT_NAME"]:
            raise ImportError(f"{__name__} requires a PROJECT_NAME in .env")

        self.name = env["PROJECT_NAME"].lower()

        prefix = env["PROJECT_NAME"].upper() + "_"

        project = {}
        for k, v in env.items():
            if k.startswith(prefix):
                project_key = k[len(prefix) :].lower()
                project[project_key] = _uptype(v)
        self.env = project

    def __getattr__(self, name) -> str | int | float | bool | Path:
        if name in self.env:
            return self.env[name]
        raise AttributeError(f"no attribute {name} in {self.name} config")

    def __contains__(self, name) -> bool:
        return name in self.env

    def __str__(self) -> str:
        return f"ProjectConfiguration<{self.name}: {self.env}>"


def _uptype(value):
    """return an up-cast type, if possible, for value"""

    for conversion in [int, float]:
        try:
            return conversion(value)
        except ValueError:
            pass

    if value.lower() in ["true", "false"]:
        return value.lower() == "true"

    if value.startswith("/"):
        return Path(value)

    return value


if os.getenv("MSWAPPINIT_TESTING") is None:
    project = ProjectConfiguration()
else:
    print("MSWAPPINIT_TESTING is set, project is dummy")
    project = ProjectConfiguration(
        testing_mock="PROJECT_NAME=test\nTEST_DATA=/tmp\nTEST_LOG=/tmp\n"
    )


def build_logger():
    logger = loguru.logger
    logger.remove()
    fmt = (
        r"<i>{time}</i> "
        r"<level>{level: <8}</level> "
        r"{file.path}:{line} "
        r"<lvl>{message}</lvl>"
    )
    logger.add(sys.stderr, format=fmt, colorize=True, backtrace=True, diagnose=True)

    log_dir = typing.cast(Path, project.log)
    log_dir.mkdir(parents=True, exist_ok=True)
    date = datetime.datetime.now().strftime("%Y-%m-%d")
    path = log_dir / f"{project.name}-{date}.log"

    logger.add(path, format=fmt, backtrace=True, diagnose=True)
    return logger


"""log is the exported loguru instance for the project
    usage:
        from mswappinit import log
        log.info("hello world")
"""


log = build_logger()
