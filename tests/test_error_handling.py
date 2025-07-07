# tests/test_error_handling.py

import unittest
from unittest.mock import patch, MagicMock
import io
import base64
from PIL import Image

from models.image_generation import generate_image_fn
from models.evaluation import generate_detailed_description, extract_key_details
from utils.file_operations import save_image_from_data_url

class TestErrorHandling(unittest.TestCase):
    """Test error handling in various components."""

    def test_image_generation_error_handling(self):
        """Test error handling in image generation function."""
        with patch('models.image_generation.InferenceClient') as mock_client:
            # Setup mock to raise different types of exceptions
            mock_client_instance = MagicMock()

            # Case 1: API Error
            mock_client_instance.text_to_image.side_effect = Exception("API Error")
            mock_client.return_value = mock_client_instance
            result = generate_image_fn("A test prompt")
            self.assertIsNone(result)

            # Case 2: Connection Error
            mock_client_instance.text_to_image.side_effect = ConnectionError("Network failure")
            result = generate_image_fn("A test prompt")
            self.assertIsNone(result)

            # Case 3: Value Error
            mock_client_instance.text_to_image.side_effect = ValueError("Invalid parameter")
            result = generate_image_fn("A test prompt")
            self.assertIsNone(result)

    def test_evaluation_error_handling(self):
        """Test error handling in evaluation functions."""
        # Create a test image
        test_image = Image.new('RGB', (10, 10), color='red')

        # Case 1: Error in generate_detailed_description
        with patch('models.evaluation.GenerativeModel') as mock_model:
            mock_model_instance = MagicMock()
            mock_model_instance.generate_content.side_effect = Exception("API Error")
            mock_model.return_value = mock_model_instance

            result = generate_detailed_description(
                test_image, "test prompt", "Simple", "animals"
            )
            self.assertTrue(result.startswith("Error processing image"))

        # Case 2: Error in extract_key_details
        with patch('models.evaluation.GenerativeModel') as mock_model:
            mock_model_instance = MagicMock()
            mock_model_instance.generate_content.side_effect = Exception("API Error")
            mock_model.return_value = mock_model_instance

            result = extract_key_details(test_image, "test prompt", "animals")
            self.assertIn("Error processing image", result)

    def test_invalid_image_handling(self):
        """Test handling of invalid images."""
        # Case 1: None image
        with patch('models.evaluation.GenerativeModel') as mock_model:
            result = generate_detailed_description(None, "test prompt", "Simple", "animals")
            self.assertTrue(result.startswith("Error: No image provided"))
            # Verify model was not called
            mock_model.assert_not_called()

        # Case 2: Invalid data URL
        invalid_data_url = "data:image/png;base64,INVALID_BASE64"
        result = save_image_from_data_url(invalid_data_url, "test.png")
        self.assertFalse(result)

        # Case 3: Non-image data URL
        non_image_data_url = "data:text/plain;base64,SGVsbG8gV29ybGQ="  # "Hello World" in base64
        with patch('models.evaluation.GenerativeModel') as mock_model:
            result = generate_detailed_description(
                non_image_data_url, "test prompt", "Simple", "animals"
            )
            self.assertTrue("Error" in result)

    def test_malformed_json_handling(self):
        """Test handling of malformed JSON in evaluation responses."""
        from models.evaluation import parse_evaluation

        # Create an active session
        active_session = {
            "identified_details": [],
            "key_details": ["detail 1", "detail 2"],
            "difficulty": "Simple",
            "used_hints": []
        }

        # Case 1: Completely invalid JSON
        eval_text = "This is not JSON at all"
        feedback, difficulty, should_advance, newly_identified, score = parse_evaluation(
            eval_text, active_session
        )
        self.assertTrue(len(feedback) > 0)  # Should have some default feedback
        self.assertEqual(difficulty, "Simple")  # Should keep current difficulty
        self.assertFalse(should_advance)
        self.assertEqual(newly_identified, [])
        self.assertEqual(score, 0)

        # Case 2: Partial JSON with missing fields
        eval_text = '{"feedback": "Good job!"}'  # Missing other fields
        feedback, difficulty, should_advance, newly_identified, score = parse_evaluation(
            eval_text, active_session
        )
        self.assertEqual(feedback, "Good job!")
        self.assertEqual(difficulty, "Simple")
        self.assertFalse(should_advance)
        self.assertEqual(newly_identified, [])
        self.assertEqual(score, 0)

        # Case 3: JSON with incorrect value types
        eval_text = '{"feedback": "Good job!", "newly_identified_details": "not a list", "score": "not a number", "advance_difficulty": "not a boolean"}'
        feedback, difficulty, should_advance, newly_identified, score = parse_evaluation(
            eval_text, active_session
        )
        self.assertEqual(feedback, "Good job!")
        self.assertEqual(difficulty, "Simple")
        self.assertFalse(should_advance)
        self.assertIn(type(newly_identified), (list, tuple))  # Should be a list-like object
        self.assertEqual(score, 0)


if __name__ == '__main__':
    unittest.main()
