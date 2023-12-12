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

    @pytest.mark.asyncio
    async def test_reply_text(self):
        chat = types.Chat(
            id=12345,  # Replace with a valid chat ID
            type="private",  # Replace with a valid chat type (e.g., 'private')
        )

        message = types.Message(
            message_id=123,  # Replace with a valid message ID
            date=1234567890,  # Replace with a valid date
            chat=chat,  # Replace with a valid types.Chat instance
        )
        message.reply = MagicMock()

        await reply_text(message, "Test message")
        message.reply.assert_called_with("Test message")

    @pytest.mark.asyncio
    async def test_reply_video(self):
        message = types.Message()
        message.reply_video = MagicMock()

        await reply_video(message, "test_video.mp4")
        message.reply_video.assert_called()

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

    @pytest.mark.asyncio
    async def test_admin_required(self):
        async def test_func(message):
            return "Test function called"

        admin_message = types.Message()
        admin_message.from_user.id = int(ADMIN_USER_ID)

        non_admin_message = types.Message()
        non_admin_message.from_user.id = int(ADMIN_USER_ID) + 1

        wrapped_test_func = admin_required(test_func)

        result_admin = await wrapped_test_func(admin_message)
        result_non_admin = await wrapped_test_func(non_admin_message)

        assert result_admin == "Test function called"
        assert result_non_admin is None

    @pytest.mark.asyncio
    async def test_reply_photo(self):
        message = types.Message()
        message.reply_photo = MagicMock()

        await reply_photo(message, "test_photo.jpg")
        message.reply_photo.assert_called()

    @pytest.mark.asyncio
    async def test_reply_audio(self):
        message = types.Message()
        message.reply_audio = MagicMock()

        await reply_audio(message, "test_audio.mp3")
        message.reply_audio.assert_called()

    @pytest.mark.asyncio
    async def test_reply_voice(self):
        message = types.Message()
        message.reply = MagicMock()
        message.reply_voice = MagicMock()

        await reply_voice(message, "test_voice.ogg", "Voice message")
        message.reply.assert_called_with("Voice message")
        message.reply_voice.assert_called()

    @pytest.mark.asyncio
    async def test_reply_file(self):
        message = types.Message()
        message.reply_document = MagicMock()

        await reply_file(message, "test_document.pdf")
        message.reply_document.assert_called()

    def test_escape_md(self):
        assert escape_md("Some *text* _here_") == "Some \\*text\\* \\_here\\_"
        assert escape_md("No special characters") == "No special characters"
