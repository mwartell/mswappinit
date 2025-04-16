import os
import typing
from pathlib import Path

from pickledb import PickleDB

from mswappinit import log


def pickle_base(data_dir: Path) -> PickleDB:
    """initialize a pickledb instance for quick and dirty persistence"""

    data_dir.mkdir(parents=True, exist_ok=True)
    path = data_dir / "quick_db.json"
    db = PickleDB(path)
    log.info(f"quick_db initialized at {path}")
    return db


if os.getenv("MSWAPPINIT_TESTING") is None:
    from mswappinit import project

    try:
        assert project.data, "project.data not defined"
        data_dir = typing.cast(Path, project.data)
        quick_db = pickle_base(data_dir)
    except AssertionError as e:
        log.warning(f"quick_db not initialized: {e}")
else:
    from mswappinit import ProjectConfiguration

    mock = "PROJECT_NAME=test\nTEST_DATA=/tmp\nTEST_TOKEN=123456"
    project = ProjectConfiguration(mock=mock)
    log.warning("MSWAPPINIT_TESTING is set, quick_db will not be initialized")
