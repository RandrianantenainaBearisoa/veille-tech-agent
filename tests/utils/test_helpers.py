import builtins
from pathlib import Path
from unittest.mock import MagicMock

from src.utils import helpers as helpers_module
from src.utils.helpers import get_feed_topics, read_yaml


def test_yaml_normal(monkeypatch):
    fake_file = MagicMock()
    fake_file.read.return_value = {"key": "value"}

    fake_file.__enter__.return_value = fake_file
    fake_file.__exit__.return_value = False

    class MockYaml:
        @classmethod
        def safe_load(cls, stream):
            return stream

    def mock_open(file: Path, mode: str):
        return fake_file

    monkeypatch.setattr(helpers_module, "yaml", MockYaml)
    monkeypatch.setattr(builtins, "open", mock_open)

    result = read_yaml(Path("this/is/a/file/path"))

    assert result == fake_file


def test_yaml_error(monkeypatch):
    fake_file = MagicMock()
    fake_file.read.return_value = {"key": "value"}

    fake_file.__enter__.return_value = fake_file
    fake_file.__exit__.return_value = False

    class MockYaml:
        @classmethod
        def safe_load(cls, stream):
            return stream

    def mock_open(file: Path, mode: str):
        print(0 / 0)
        return fake_file

    monkeypatch.setattr(helpers_module, "yaml", MockYaml)
    monkeypatch.setattr(builtins, "open", mock_open)

    result = read_yaml(Path("this/is/a/file/path"))

    assert result == {}


def test_get_feed_topics(monkeypatch):
    expected_result = {"rss_list": [{"key": "value"}]}

    def mock_read_yaml(filepath: Path):
        return expected_result

    monkeypatch.setattr(helpers_module, "read_yaml", mock_read_yaml)

    result = get_feed_topics()
    assert result == [{"key": "value"}]


def test_get_feed_topics_error(monkeypatch):
    expected_result = {"rss_lists": [{"key": "value"}]}

    def mock_read_yaml(filepath: Path):
        return expected_result

    monkeypatch.setattr(helpers_module, "read_yaml", mock_read_yaml)

    result = get_feed_topics()
    assert result == []