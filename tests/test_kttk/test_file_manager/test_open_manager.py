import pytest
from mock import MagicMock

from kttk.context import Context
from kttk.file_manager.create_new_manager import CreateNewManager
from kttk.file_manager.open_manager import OpenManager


@pytest.fixture
def open_manager(populated_context):
    manager = OpenManager(MagicMock(), MagicMock(), populated_context)
    manager._helper = MagicMock()
    return manager


def test_open_no_scene_no_unsaved_changes(open_manager):
    """
    Opens a scene when no scene is currently open with no unsaved changes
    """
    open_manager._engine.current_file_path.return_value = None
    open_manager._engine.has_unsaved_changes.return_value = False

    open_manager._open_scene = MagicMock()

    open_manager.do_it(MagicMock())

    assert open_manager._open_scene.called


def test_open_no_scene_unsaved_changes_save_changes_canceled(open_manager):
    """
    Opens a scene when no scene is currently open with unsaved changes and user canceles
    """
    open_manager._engine.current_file_path.return_value = None
    open_manager._engine.has_unsaved_changes.return_value = True
    open_manager._view_callback_provider.ask_for_save.return_value = "cancel"

    open_manager._open_scene = MagicMock()

    open_manager.do_it(MagicMock())

    assert not open_manager._open_scene.called
    assert not open_manager._engine.save.called


def test_open_no_scene_unsaved_changes_save_changes(open_manager):
    """
    Opens a scene when no scene is currently open with unsaved changes which are saved
    """
    open_manager._engine.current_file_path.return_value = None
    open_manager._engine.has_unsaved_changes.return_value = True
    open_manager._view_callback_provider.ask_for_save.return_value = True

    open_manager._open_scene = MagicMock()

    open_manager.do_it(MagicMock())

    assert open_manager._open_scene.called
    assert open_manager._engine.save.called


def test_open_no_scene_unsaved_changes_no_save(open_manager):
    """
    Opens a scene when no scene is currently open with unsaved changes which are not saved
    """
    open_manager._engine.current_file_path.return_value = None
    open_manager._engine.has_unsaved_changes.return_value = True
    open_manager._view_callback_provider.ask_for_save.return_value = False

    open_manager._open_scene = MagicMock()

    open_manager.do_it(MagicMock())

    assert open_manager._open_scene.called
    assert not open_manager._engine.save.called


def test_open_scene_unsaved_changes_no_save(open_manager):
    """
    Opens a scene when a scene is currently open with unsaved changes which are not saved
    """
    open_manager._engine.current_file_path.return_value = "some_path"
    open_manager._engine.has_unsaved_changes.return_value = True
    open_manager._view_callback_provider.ask_for_save.return_value = False

    open_manager._open_scene = MagicMock()

    open_manager.do_it(MagicMock())

    assert open_manager._open_scene.called
    assert not open_manager._engine.save.called


def test_open_scene_unsaved_changes_save(open_manager):
    """
    Opens a scene when a scene is currently open with unsaved changes which are  saved
    """
    open_manager._engine.current_file_path.return_value = "some_path"
    open_manager._engine.has_unsaved_changes.return_value = True
    open_manager._view_callback_provider.ask_for_save.return_value = True

    open_manager._open_scene = MagicMock()

    open_manager.do_it(MagicMock())

    assert open_manager._open_scene.called
    assert open_manager._engine.save.called


def test_open_scene_already_open_no_reload(open_manager):
    """
    Opens a scene when the scene is already open, no reload is performed
    """
    open_manager._engine.current_file_path.return_value = "some_path"
    open_manager._view_callback_provider.ask_for_reload.return_value = False

    open_manager._open_scene = MagicMock()

    open_manager.do_it({"path": "some_path"})

    assert not open_manager._open_scene.called


def test_open_scene_already_open_do_reload(open_manager):
    """
    Opens a scene when the scene is already open, reload is performed
    """
    open_manager._engine.current_file_path.return_value = "some_path"
    open_manager._view_callback_provider.ask_for_reload.return_value = True

    open_manager._open_scene = MagicMock()

    open_manager.do_it({"path": "some_path"})

    assert open_manager._open_scene.called


def test_open_scene_already_open_reload_cancel(open_manager):
    """
    Opens a scene when the scene is already open, reload is canceled
    """
    open_manager._engine.current_file_path.return_value = "some_path"
    open_manager._view_callback_provider.ask_for_reload.return_value = "cancel"

    open_manager._open_scene = MagicMock()

    open_manager.do_it({"path": "some_path"})

    assert not open_manager._open_scene.called
