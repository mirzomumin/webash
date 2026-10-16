from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from src.core.base.container import ContainerManager, get_linux_username


@pytest.mark.parametrize(
    "username,first_name,last_name,expected",
    [
        ("Anonymous", "Anonym", None, "anonymous"),
        (None, "x' ; sh ; '", None, "xsh"),
        (None, "123_John", None, "john"),
        (None, "Мирзо", "O'Neil", "oneil"),
        (None, None, None, "user"),
    ],
)
def test_get_linux_username(username, first_name, last_name, expected):
    user = SimpleNamespace(
        username=username, first_name=first_name, last_name=last_name
    )
    assert get_linux_username(user) == expected


def test_create_passes_username_as_argument():
    user = SimpleNamespace(
        id=uuid4(), username=None, first_name="x'; sh; '", last_name=None
    )
    docker_client = MagicMock()

    ContainerManager().create(user=user, docker_client=docker_client)

    kwargs = docker_client.containers.run.call_args.kwargs
    assert kwargs["entrypoint"] == [
        "sh",
        "-c",
        'adduser -D "$1" && su "$1" -c sh',
        "sh",
        "xsh",
    ]
    assert kwargs["working_dir"] == "/home/xsh"
    assert "command" not in kwargs
