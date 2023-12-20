# test_utils.py

import pytest
from unittest.mock import MagicMock
from aiogram import types
from modules.config import ADMIN_USER_ID
from modules.utils import (
    reply_text,
    reply_video,
    reply_photo,
    reply_audio,
    reply_voice,
    reply_file,
    remove_file_safe,
    get_file_size_mb,
    is_link,
    admin_required,
    escape_md,
)


class TestUtils:

    def test_remove_file_safe_existing(self, tmp_path):
        file_path = tmp_path / "test_file.txt"
        file_path.touch()

        remove_file_safe(str(file_path))
        assert not file_path.exists()

    def test_remove_file_safe_nonexistent(self, tmp_path):
        file_path = tmp_path / "nonexistent_file.txt"

        remove_file_safe(str(file_path))  # Should not raise an error

    def test_get_file_size_mb(self, tmp_path):
        file_path = tmp_path / "test_file.txt"
        file_contents = b'a' * 1024  # Creating a file of 1KB
        file_path.write_bytes(file_contents)

        # Approximately 1KB in MB
        assert get_file_size_mb(str(file_path)) == 0.0009765625

    def test_is_link(self):
        assert is_link("https://example.com") is True
        assert is_link("http://example.com") is True
        assert is_link("ftp://example.com") is False
        assert is_link("example.com") is False

    def test_escape_md(self):
        assert escape_md("Some *text* _here_") == "Some \\*text\\* \\_here\\_"
        assert escape_md("No special characters") == "No special characters"
