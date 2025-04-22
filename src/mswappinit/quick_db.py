import os
import typing
from pathlib import Path

from pickledb import PickleDB

from mswappinit import log


def pickle_base(data_dir: Path) -> PickleDB:
    """Initialize a pickledb instance for quick and dirty persistence."""
    data_dir.mkdir(parents=True, exist_ok=True)
    path = data_dir / "quick_db.json"
    db = PickleDB(path)
    return db


def initialize_production_quick_db() -> PickleDB:
    """Initialize quick_db for the production environment."""
    from mswappinit import project

    if not project.data:
        raise ImportError("project.data not defined in .env")
    data_dir = typing.cast(Path, project.data)
    return pickle_base(data_dir)


# Main initialization
if os.getenv("MSWAPPINIT_TESTING") is None:
    quick_db = initialize_production_quick_db()
else:
    log.warning("quick_db not initialized in testing mode")
