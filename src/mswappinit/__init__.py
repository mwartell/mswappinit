"""
mswconfig - convenience wrappers for development configuration

This library provides three application bootstrap utilites
1. project - a configuration dotenv loader that makes nice parameter accessors
2. log - a logger that is pleasing to the author
3. quick_db - a pickledb instance for quick and dirty persistence

dotenv is used to load environment variables from a file named .env
these could be something like: `AWS_PROFILE=cluster` and these
will all be loaded into the environment as expected.

this module provides convenience attribute access to project specific
variables that are loaded from the dotenv file. A PROJECT_NAME must
be defined and then all other variables of the form {PROJECT_NAME}_{VAR}
can be accessed as attributes of the project object.

For example, if the PROJECT_NAME is "rag" and the dotenv file contains
`RAG_DATA=/path/to/data` then the value of `project.data` will be the
Path object `/path/to/data`.

For convenience, the values are upcast to the most likely type. For example,
if the value is "true" or "false" it will be converted to a boolean. If the
value is a number it will be converted to an int or float. If the value starts
with a "/" it will be converted to a Path object. Otherwise, it will be
returned as a string.
"""

import io
import sys
from pathlib import Path
from typing import cast

from dotenv import dotenv_values
from loguru import logger
from pickledb import PickleDB

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

logger.info("msw logger initiallized")

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


def pickle_base(data_dir: Path) -> PickleDB:
    """initialize a pickledb instance for quick and dirty persistence"""

    data_dir.mkdir(parents=True, exist_ok=True)
    path = data_dir / "quick_db.json"
    db = PickleDB(path)
    log.info(f"quickdb initialized at {path}")
    return db


"""quick_db is the exported pickledb instance for quick and dirty persistence.
   It will be None if projects.data is not defined. Using it as a context
   manager will automatically save the database to the file.
   usage:
         from mswappinit import quick_db

         with quick_db:
            quick_db.set("key", "value")

         assert quick_db["key"] == "value"
"""
if globals().get("MSWAPPINIT_TESTING") is None:
    try:
        project = ProjectConfiguration()
        log.debug(project)
        data_dir = cast(Path, project.data)  # noqa: unbound-local
        quick_db = pickle_base(data_dir)
    except AssertionError as e:
        log.warning(f"quick_db not initialized: {e}")
else:
    log.warning(
        "mswappinit is being tested, project and quick_db will not be initialized"
    )
