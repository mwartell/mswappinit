"""
mswappinit - convenience wrappers for development configuration

https://github.com/mwartell/mswappinit
"""

import io
import os
import sys
from pathlib import Path

from dotenv import dotenv_values
from loguru import logger

"""log is the exported loguru instance for the project
    usage:
        from mswappinit import log
        log.info("hello world")
"""
logger.remove()
logger.add(
    # msw isn't wild about timestamps during development
    sys.stderr,
    format="{elapsed} {function} {file}:{line} - <level>{message}</level>",
)
logger.info("msw logger initialized")

log = logger


class ProjectConfiguration:
    def __init__(self, mock: str | None = None):
        # TODO: the configuration is not exported to the environment, should it be?
        if mock:
            env = dotenv_values(stream=io.StringIO(mock))
        else:
            env = dotenv_values()

        assert "PROJECT_NAME" in env, "PROJECT_NAME not found in dotenv file"
        assert env["PROJECT_NAME"], "PROJECT_NAME must not be empty"
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
    log.warning("MSWAPPINIT_TESTING is set, project is uninitialized")
    project = ProjectConfiguration(mock="PROJECT_NAME=test")
