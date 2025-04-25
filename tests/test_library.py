import os

import pytest

"""these test the inner functionality of the mswappinit library.
we skip the outer behavior because the auto-initialization
needs support files in the working directory."""

# Set the MSWAPPINIT_TESTING flag as an environment variable
os.environ["MSWAPPINIT_TESTING"] = "1"


def test_log():
    """Test the logging functionality."""
    from mswappinit import log

    assert log is not None, "Log should be initialized"
    assert hasattr(log, "info"), "Log should have an info method"
    assert hasattr(log, "debug"), "Log should have a debug method"
    assert hasattr(log, "error"), "Log should have an error method"


def test_project(tmp_path):
    """Test the project configuration."""
    from mswappinit import ProjectConfiguration

    mock = f"PROJECT_NAME=test\nTEST_DATA={tmp_path}\nTEST_TOKEN=123456"
    env = ProjectConfiguration(testing_mock=mock)

    assert env is not None, "Project should be initialized"
    # assert env.name == "test", "Project name should be 'test'"
    assert env.name == "test", "Project name should be 'test'"
    assert env.data == tmp_path, "Project data should match the temporary directory"
    assert env.token == 123456
    with pytest.raises(AttributeError):
        _ = env.non_existent_attribute


def test_quickdb(tmp_path):
    """Test the quick database functionality."""
    from mswappinit.quick_db import pickle_base

    db = pickle_base(tmp_path)
    assert db is not None, "Database should be initialized"
    assert db.location == f"{tmp_path}/quick_db.json", (
        "Database path should match the temporary directory"
    )

    with db:
        db.set("key", "value")

    assert db["key"] == "value", "Database should return the correct value for the key"
