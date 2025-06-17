from mustiolo.cli import MenuGroup
import pytest


def test_menu_group_with_reserved_name():
    with pytest.raises(Exception) as e:
        group = MenuGroup("?", "This is a test group")
        assert str(e) == "CommandReserved: ? is a reserved command name"
        assert group.name == "?"

def test_menu_group_with_reserved_command():

    group = MenuGroup("test_group", "This is a test group")

    with pytest.raises(Exception):
        @group.command("exit", "This is a test command")
        def command_exit():
            pass

    assert len(group.get_group().get_commands().keys()) == 0
