# tests/test_file_operations.py

import unittest
from unittest.mock import patch, mock_open, MagicMock
import base64
import io
import json
from PIL import Image

from utils.file_operations import (
    save_image_from_data_url,
    save_all_session_images,
    save_session_log
)


class TestFileOperations(unittest.TestCase):
    """Test suite for file operation functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a small test image and convert to data URL
        self.test_image = Image.new('RGB', (10, 10), color='red')
        buffer = io.BytesIO()
        self.test_image.save(buffer, format="PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode()
        self.test_data_url = f"data:image/png;base64,{img_str}"

    @patch('builtins.open', new_callable=mock_open)
    def test_save_image_from_data_url(self, mock_file):
        """Test saving an image from a data URL."""
        # Call the function
        result = save_image_from_data_url(self.test_data_url, "test.png")

        # Verify the file was "saved"
        self.assertTrue(result)
        mock_file.assert_called_once_with("test.png", "wb")

        # Test with invalid data URL
        result = save_image_from_data_url("not-a-data-url", "test.png")
        self.assertFalse(result)

        # Test with empty data URL
        result = save_image_from_data_url("", "test.png")
        self.assertFalse(result)

    @patch('utils.file_operations.os.makedirs')
    @patch('utils.file_operations.save_image_from_data_url')
    @patch('utils.file_operations.datetime')
    def test_save_all_session_images(self, mock_datetime, mock_save_image, mock_makedirs):
        """Test saving all session images."""
        # Setup mocks
        mock_datetime.datetime.now.return_value.strftime.return_value = "20230101_120000"
        mock_save_image.return_value = True

        # Setup test data
        saved_sessions = [
            {"image": self.test_data_url, "prompt": "Session 1"},
            {"image": self.test_data_url, "prompt": "Session 2"},
            {"image": "not-an-image", "prompt": "Session 3"}  # Should be skipped
        ]

        active_session = {"image": self.test_data_url, "prompt": "Active session"}

        # Call the function
        result = save_all_session_images(saved_sessions, active_session)

        # Verify results
        mock_makedirs.assert_called_once()
        self.assertEqual(mock_save_image.call_count, 3)  # 2 from saved + 1 active
        self.assertIn("Successfully saved 3 images", result)

    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    @patch('utils.file_operations.datetime')
    def test_save_session_log(self, mock_datetime, mock_json_dump, mock_file):
        """Test saving session logs to a JSON file."""
        # Setup mocks
        mock_datetime.datetime.now.return_value.strftime.return_value = "20230101_120000"

        # Setup test data
        saved_sessions = [
            {"prompt": "Session 1", "image": self.test_data_url},
            {"prompt": "Session 2", "image": self.test_data_url}
        ]

        active_session = {"prompt": "Active session", "image": self.test_data_url}

        # Call the function
        result = save_session_log(saved_sessions, active_session)

        # Verify results
        mock_file.assert_called_once_with("session_log_20230101_120000.json", "w", encoding="utf-8")
        mock_json_dump.assert_called_once()

        # Verify that image data URLs are removed in the saved JSON
        call_args = mock_json_dump.call_args[0]
        saved_data = call_args[0]

        # Check first argument (data to save)
        self.assertEqual(len(saved_data), 3)  # 2 saved + 1 active
        for session in saved_data:
            self.assertIn("prompt", session)
            self.assertEqual(session["image"], "[IMAGE_DATA_REMOVED]")

        # Verify success message
        self.assertIn("Session log saved to:", result)

    @patch('builtins.open')
    @patch('json.dump')
    def test_save_session_log_error(self, mock_json_dump, mock_file):
        """Test error handling when saving session logs."""
        # Setup mock to raise an exception
        mock_file.side_effect = PermissionError("Cannot write file")

        # Setup test data
        saved_sessions = [{"prompt": "Session 1"}]
        active_session = {"prompt": "Active session"}

        # Call the function
        result = save_session_log(saved_sessions, active_session)

        # Verify error message
        self.assertIn("Error saving session log", result)
        self.assertIn("Cannot write file", result)


if __name__ == '__main__':
    unittest.main()
