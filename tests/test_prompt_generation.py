# tests/test_prompt_generation.py

import unittest
from unittest.mock import patch, MagicMock

from models.prompt_generation import generate_prompt_from_options
import config

class TestPromptGeneration(unittest.TestCase):
    """Test suite for prompt generation functionality."""

    @patch('models.prompt_generation.GenerativeModel')
    def test_generate_prompt_from_options(self, mock_model):
        """Test generating a prompt with various options."""
        # Setup mock
        mock_model_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "A detailed prompt for image generation"
        mock_model_instance.generate_content.return_value = mock_response
        mock_model.return_value = mock_model_instance

        # Call the function with all parameters
        result = generate_prompt_from_options(
            "Simple", "5", "Level 1", "animals",
            "Focus on social skills", "Realistic"
        )

        # Verify result
        self.assertEqual(result, "A detailed prompt for image generation")
        mock_model_instance.generate_content.assert_called_once()

        # Verify the prompt includes style information
        call_args = mock_model_instance.generate_content.call_args[0][0]
        self.assertIn("Realistic", call_args)

    @patch('models.prompt_generation.GenerativeModel')
    def test_generate_prompt_default_treatment_plan(self, mock_model):
        """Test prompt generation with default treatment plan."""
        mock_model_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "A prompt with default treatment plan"
        mock_model_instance.generate_content.return_value = mock_response
        mock_model.return_value = mock_model_instance

        # Call without treatment plan
        result = generate_prompt_from_options(
            "Moderate", "7", "Level 2", "emotions", "", "Cartoon"
        )

        self.assertEqual(result, "A prompt with default treatment plan")

        # Verify default treatment plan was used
        call_args = mock_model_instance.generate_content.call_args[0][0]
        default_plan = config.DEFAULT_TREATMENT_PLANS["Level 2"]
        self.assertIn(default_plan, call_args)
        self.assertIn("Cartoon", call_args)

    @patch('models.prompt_generation.GenerativeModel')
    def test_generate_prompt_different_styles(self, mock_model):
        """Test prompt generation with different image styles."""
        mock_model_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Style-specific prompt"
        mock_model_instance.generate_content.return_value = mock_response
        mock_model.return_value = mock_model_instance

        # Test each style
        styles = ["Illustration", "Cartoon", "Watercolor", "3D Rendering"]

        for style in styles:
            result = generate_prompt_from_options(
                "Simple", "5", "Level 1", "animals",
                "Focus on social skills", style
            )

            self.assertEqual(result, "Style-specific prompt")
            call_args = mock_model_instance.generate_content.call_args[0][0]
            self.assertIn(style, call_args)


if __name__ == '__main__':
    unittest.main()
