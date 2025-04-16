"""
mswappinit - convenience wrappers for development configuration

https://github.com/mwartell/mswappinit
"""

import io
import os
import sys
from pathlib import Path

from dotenv import dotenv_values, load_dotenv
from loguru import logger

"""log is the exported loguru instance for the project
    usage:
        from mswappinit import log
        log.info("hello world")
"""
log = logger
log.remove()
log.add(
    sys.stderr,
    # msw isn't fond of ISO timestamps during development
    format="{elapsed} {function} {file}:{line} - <level>{message}</level>",
)
log.debug("msw logger initialized")


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

        self.project_name = env["PROJECT_NAME"]

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
        raise AttributeError(f"no attribute {name} in {self.project_name} config")

    def __contains__(self, name) -> bool:
        return name in self.env

    def __str__(self) -> str:
        return f"ProjectConfiguration<{self.project_name}: {self.env}>"


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
    log.debug(project)
else:
    log.warning("MSWAPPINIT_TESTING is set, project is dummy")
    project = ProjectConfiguration(testing_mock="PROJECT_NAME=test\nTEST_DATA=/tmp")
