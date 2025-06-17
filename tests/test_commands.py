from mustiolo.models.command import CommandGroup, CommandModel
from mustiolo.exception import CommandDuplicate, CommandMissingMenuMessage, ParameterMissingType

import pytest


def test_command_group():
    group = CommandGroup("test_group", "This is a test group")
    assert group._name == "test_group"
    assert group._menu == "This is a test group"
    assert group._usage == ""
    assert len(group.get_commands().keys()) == 0



def test_command_group_with_commands():

    def test_command():
        """
        <menu>Test command</menu>
        """
        pass
    
    group = CommandGroup("test_group", "This is a test group")
    group.register_command(fn=test_command, name="test_command", alias="", menu="This is a test command")
    assert group.has_command("test_command")
    assert isinstance(group.get_command("test_command"), CommandModel)
    assert len(group.get_commands().keys()) == 1


def test_command_group_with_subgroups():
    
    def test_command():
        """
        <menu>Test command</menu>
        """
        pass

    group = CommandGroup("test_group", "This is a test group")
    subgroup = CommandGroup("test_subgroup", "This is a test subgroup")
    group.add_command_group(subgroup)
    subgroup.register_command(fn=test_command, name="test_command", alias="", menu="This is a test command")
    assert group.has_command("test_subgroup")
    assert isinstance(group.get_command("test_subgroup"), CommandGroup)
    assert len(group.get_commands().keys()) == 1
    assert len(subgroup.get_commands().keys()) == 1


def test_command_group_with_duplicate_commands():
    
    def test_command():
        """
        <menu>Test command</menu>
        """
        pass

    def test_command2():
        """
        <menu>Test command</menu>
        """
        pass

    group = CommandGroup("test_group", "This is a test group")
    group.register_command(fn=test_command, name="test_command", alias="", menu="This is a test command")
    with pytest.raises(CommandDuplicate) as e:
        group.register_command(test_command2, "test_command", "This is a test command")
        assert str(e) == "CommandDuplicate: test_command is already defined in file <string> at line 0"

    assert len(group.get_commands().keys()) == 1


def test_command_group_with_missing_parameter_type():

    def test_command(name):
        """
        <menu>Test command</menu>
        """
        pass

    group = CommandGroup("test_group", "This is a test group")
    with pytest.raises(ParameterMissingType) as e:
        group.register_command(test_command)
        assert str(e) == "Function 'test_command' at '0' has a parameter without type"



def test_command_group_with_menu_in_docstring():
    def test_command():
        """
        <menu>Test command</menu>
        """
        pass

    group = CommandGroup("test_group", "This is a test group")
    group.register_command(test_command)
    assert group.get_command("test_command").menu == "Test command"
    assert group.get_command("test_command").usage == "Test command"



def test_command_group_with_menu_and_usage_in_docstring():
    def test_command():
        """
        <menu>Menu</menu>
        <usage>Usage</usage>
        """
        pass

    group = CommandGroup("test_group", "This is a test group")
    group.register_command(test_command)
    assert group.get_command("test_command").menu == "Menu"
    assert group.get_command("test_command").usage == "Usage"


def test_command_group_with_empty_docstring():
    def test_command():
        pass

    group = CommandGroup("test_group", "This is a test group")
    with pytest.raises(CommandMissingMenuMessage):
        group.register_command(test_command)
