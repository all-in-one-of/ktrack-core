import os

import pytest
import six
import valideer
from mock import mock, MagicMock
from valideer import ValidationError

from kttk.config import config_manager

BUILTIN_SOPEN = "builtins.open" if six.PY3 else "__builtin__.open"


@pytest.fixture
def folder_in_env():
    os.environ[config_manager.KTRACK_TEMPLATE_DIR] = "test_dir"
    yield
    os.environ.pop(config_manager.KTRACK_TEMPLATE_DIR)


def test_get_config_folder_default():
    # test default case, this would be config folder in ktrack module
    folder = config_manager.get_config_folder()
    folder = folder.replace("\\", "/")
    assert folder.endswith("kttk/config")


def test_get_config_folder_with_env(folder_in_env):
    # test if enviroment variable override is correctly # todo add integration tests for this
    folder = config_manager.get_config_folder()
    assert folder == "test_dir"


def test_load_file_no_file():
    # test trying to load a config file which does not exist
    with mock.patch("os.path.exists") as mock_path_exists:
        mock_path_exists.return_value = False

        with pytest.raises(config_manager.InvalidConfigException):
            config_manager.load_file("blabla")


def test_load_file_no_validator():
    # tests loading a existing file with no validator
    with mock.patch("os.path.exists") as mock_path_exists:
        mock_path_exists.return_value = True
        with mock.patch(BUILTIN_SOPEN) as mock_file:
            with mock.patch("yaml.load") as mock_yml_load:
                mock_yml_load.return_value = {"db": "path"}

                data = config_manager.load_file("blabla")
                assert data == mock_yml_load.return_value


def test_load_file_validator_valid():
    # tests loading a existing file with validator and data is valid
    with mock.patch("os.path.exists") as mock_path_exists:
        mock_path_exists.return_value = True
        with mock.patch(BUILTIN_SOPEN) as mock_file:
            with mock.patch("yaml.load") as mock_yml_load:
                mock_yml_load.return_value = {"db": "path"}

                mock_validator = MagicMock()
                mock_validator.return_value = True, "reason"
                data = config_manager.load_file("blabla", mock_validator)

                assert data == mock_yml_load.return_value
                assert mock_validator.called


def test_load_file_validator_invalid():
    # tests loading a existing file with validator and data is invalid

    with mock.patch("os.path.exists") as mock_path_exists:
        mock_path_exists.return_value = True
        with mock.patch(BUILTIN_SOPEN) as mock_file:
            with mock.patch("yaml.load") as mock_yml_load:
                mock_yml_load.return_value = {"db": "path"}

                mock_validator = MagicMock()
                mock_validator.return_value = False, "reason"

                with pytest.raises(config_manager.InvalidConfigException):
                    data = config_manager.load_file("blabla", mock_validator)


def test_validate_schema():
    # create a simple test schema
    test_schema = valideer.Mapping(
        key_schema=valideer.String, value_schema=valideer.String
    )

    result, message = config_manager.validate_schema({"1": "1"}, test_schema)
    assert result
    assert message == ""

    result, message = config_manager.validate_schema({1: 1}, test_schema)
    assert result == False
    assert isinstance(message, str)
    assert len(message) > 0


def test_general_data_schema():
    # test valid
    assert config_manager.general_data_schema.validate(
        {"test": "test"}
    )  # would raise ValidationError if invalid

    with pytest.raises(valideer.ValidationError):
        config_manager.general_data_schema.validate({"test": []})


def test_load_general_data():
    with mock.patch("kttk.config.config_manager.load_file") as mock_load_data:
        config_manager._load_general_data()
        mock_load_data.assert_called()


def test_get_value_with_data():
    with mock.patch(
        "kttk.config.config_manager._general_data", {"test": "test"}
    ) as mock_data:
        assert config_manager.get_value("test") == "test"


def test_get_value_no_data():
    with mock.patch("kttk.config.config_manager._general_data", None) as mock_data:
        with mock.patch("kttk.config.config_manager._load_general_data") as mock_load:
            mock_load.return_value = {"test": "test"}
            assert config_manager.get_value("test") == "test"
