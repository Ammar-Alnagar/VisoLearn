# tests/test_image_generation.py

import os
import unittest
from unittest.mock import patch, MagicMock
import base64
import io
from PIL import Image

from models.image_generation import generate_image_fn, global_image_data_url, global_image_prompt

class TestImageGeneration(unittest.TestCase):
    """Test suite for image generation functionality."""

    @patch('models.image_generation.InferenceClient')
    def test_generate_image_success(self, mock_client):
        """Test successful image generation with valid prompt."""
        # Create a mock PIL image
        mock_image = Image.new('RGB', (512, 512), color='red')
        mock_client_instance = MagicMock()
        mock_client_instance.text_to_image.return_value = mock_image
        mock_client.return_value = mock_client_instance

        # Test the function
        result = generate_image_fn("A test prompt")

        # Verify the function called the API correctly
        mock_client_instance.text_to_image.assert_called_once()
        self.assertEqual(result, mock_image)
        self.assertIsNotNone(global_image_data_url)
        self.assertEqual(global_image_prompt, "A test prompt")

    @patch('models.image_generation.InferenceClient')
    def test_generate_image_with_parameters(self, mock_client):
        """Test image generation with custom parameters."""
        mock_image = Image.new('RGB', (512, 512), color='blue')
        mock_client_instance = MagicMock()
        mock_client_instance.text_to_image.return_value = mock_image
        mock_client.return_value = mock_client_instance

        result = generate_image_fn(
            "A detailed prompt",
            guidance_scale=5.0,
            negative_prompt="bad quality",
            num_inference_steps=30
        )

        # Verify custom parameters were passed
        mock_client_instance.text_to_image.assert_called_once_with(
            "A detailed prompt",
            model="stabilityai/stable-diffusion-3.5-large-turbo",
            guidance_scale=5.0,
            negative_prompt="bad quality",
            num_inference_steps=30
        )
        self.assertEqual(result, mock_image)

    @patch('models.image_generation.InferenceClient')
    def test_generate_image_error(self, mock_client):
        """Test error handling during image generation."""
        # Setup mock to raise an exception
        mock_client_instance = MagicMock()
        mock_client_instance.text_to_image.side_effect = Exception("API Error")
        mock_client.return_value = mock_client_instance

        # Test the function
        result = generate_image_fn("A test prompt")

        # Verify the result is None when an error occurs
        self.assertIsNone(result)

    @patch('models.image_generation.InferenceClient')
    def test_empty_prompt_handling(self, mock_client):
        """Test handling of empty prompts."""
        mock_image = Image.new('RGB', (512, 512), color='white')
        mock_client_instance = MagicMock()
        mock_client_instance.text_to_image.return_value = mock_image
        mock_client.return_value = mock_client_instance

        # Test with empty prompt
        result = generate_image_fn("")

        # Should still call the API with the empty string
        mock_client_instance.text_to_image.assert_called_once()
        self.assertEqual(result, mock_image)


if __name__ == '__main__':
    unittest.main()
