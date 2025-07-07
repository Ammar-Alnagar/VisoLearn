# tests/test_config.py

import unittest
import importlib.util
import os

class TestConfig(unittest.TestCase):
    """Test the configuration settings."""

    def setUp(self):
        """Set up the test by loading the config module."""
        # Dynamically load the config module
        spec = importlib.util.spec_from_file_location("config", "config.py")
        self.config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.config)

    def test_difficulty_levels(self):
        """Test that difficulty levels are properly defined."""
        self.assertTrue(hasattr(self.config, 'DIFFICULTY_LEVELS'))
        self.assertIsInstance(self.config.DIFFICULTY_LEVELS, list)
        self.assertTrue(len(self.config.DIFFICULTY_LEVELS) >= 3)
        self.assertIn("Very Simple", self.config.DIFFICULTY_LEVELS)
        self.assertIn("Simple", self.config.DIFFICULTY_LEVELS)

    def test_image_styles(self):
        """Test that image styles are properly defined."""
        self.assertTrue(hasattr(self.config, 'IMAGE_STYLES'))
        self.assertIsInstance(self.config.IMAGE_STYLES, list)
        self.assertTrue(len(self.config.IMAGE_STYLES) >= 3)
        self.assertIn("Realistic", self.config.IMAGE_STYLES)
        self.assertIn("Cartoon", self.config.IMAGE_STYLES)

    def test_default_treatment_plans(self):
        """Test that default treatment plans are properly defined."""
        self.assertTrue(hasattr(self.config, 'DEFAULT_TREATMENT_PLANS'))
        self.assertIsInstance(self.config.DEFAULT_TREATMENT_PLANS, dict)
        self.assertIn("Level 1", self.config.DEFAULT_TREATMENT_PLANS)
        self.assertIn("Level 2", self.config.DEFAULT_TREATMENT_PLANS)
        self.assertIn("Level 3", self.config.DEFAULT_TREATMENT_PLANS)

    def test_default_session(self):
        """Test that the default session is properly defined."""
        self.assertTrue(hasattr(self.config, 'DEFAULT_SESSION'))
        self.assertIsInstance(self.config.DEFAULT_SESSION, dict)

    def test_api_keys_config(self):
        """Test API key configuration."""
        # Check if the API keys are loaded from environment variables
        self.assertTrue(hasattr(self.config, 'HF_TOKEN'))
        self.assertTrue(hasattr(self.config, 'GOOGLE_API_KEY'))

        # If testing in a CI environment where env vars might be set:
        if os.environ.get('CI') != 'true':
            # Only check format in non-CI environments
            if self.config.HF_TOKEN:
                self.assertNotEqual(self.config.HF_TOKEN, '<your-hf-token>')
            if self.config.GOOGLE_API_KEY:
                self.assertNotEqual(self.config.GOOGLE_API_KEY, '<your-gemini-api-key>')


if __name__ == '__main__':
    unittest.main()
