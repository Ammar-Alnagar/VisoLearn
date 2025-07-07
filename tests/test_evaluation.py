# tests/test_evaluation.py

import unittest
from unittest.mock import patch, MagicMock
import base64
import io
import json
from PIL import Image

from models.evaluation import (
    generate_detailed_description,
    extract_key_details,
    compare_details_chat_fn,
    parse_evaluation,
    update_checklist
)

class TestEvaluation(unittest.TestCase):
    """Test suite for image evaluation and description functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a small test image
        self.test_image = Image.new('RGB', (100, 100), color='blue')
        # Create a data URL
        buffer = io.BytesIO()
        self.test_image.save(buffer, format="PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode()
        self.test_data_url = f"data:image/png;base64,{img_str}"

    @patch('models.evaluation.GenerativeModel')
    def test_generate_detailed_description(self, mock_model):
        """Test generating a detailed description from an image."""
        # Setup mock
        mock_model_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "This is a detailed description of the image."
        mock_model_instance.generate_content.return_value = mock_response
        mock_model.return_value = mock_model_instance

        # Test with PIL Image
        result = generate_detailed_description(
            self.test_image, "test prompt", "Simple", "animals"
        )
        # Verify result
        self.assertEqual(result, "This is a detailed description of the image.")
        mock_model_instance.generate_content.assert_called_once()

        # Reset mock
        mock_model_instance.reset_mock()

        # Test with data URL
        result = generate_detailed_description(
            self.test_data_url, "test prompt", "Simple", "animals"
        )
        # Verify result
        self.assertEqual(result, "This is a detailed description of the image.")
        mock_model_instance.generate_content.assert_called_once()

    @patch('models.evaluation.GenerativeModel')
    def test_generate_detailed_description_error(self, mock_model):
        """Test error handling in description generation."""
        # Setup mock to raise an exception
        mock_model_instance = MagicMock()
        mock_model_instance.generate_content.side_effect = Exception("API Error")
        mock_model.return_value = mock_model_instance

        # Call the function
        result = generate_detailed_description(
            self.test_image, "test prompt", "Simple", "animals"
        )

        # Verify error message is returned
        self.assertTrue(result.startswith("Error processing image"))

    @patch('models.evaluation.GenerativeModel')
    def test_extract_key_details(self, mock_model):
        """Test extracting key details from an image."""
        # Setup mock with JSON response
        mock_model_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.text = '["detail 1", "detail 2", "detail 3"]'
        mock_model_instance.generate_content.return_value = mock_response
        mock_model.return_value = mock_model_instance

        # Call the function
        result = extract_key_details(self.test_image, "test prompt", "animals")

        # Verify result contains extracted details
        self.assertIn("detail 1", result)
        self.assertIn("detail 2", result)
        self.assertIn("detail 3", result)

        # Test with non-JSON response
        mock_response.text = "- detail 1\n- detail 2\n- detail 3"
        result = extract_key_details(self.test_image, "test prompt", "animals")

        # Verify fallback parsing works
        self.assertTrue(isinstance(result, list))
        self.assertTrue(len(result) > 0)

    def test_parse_evaluation_json(self):
        """Test parsing evaluation response in JSON format."""
        # Test with valid JSON
        eval_text = '{"feedback": "Good job!", "newly_identified_details": ["detail 1", "detail 2"], "hint": "Look for colors", "score": 75, "advance_difficulty": false}'
        active_session = {
            "identified_details": [],
            "key_details": ["detail 1", "detail 2", "detail 3"],
            "difficulty": "Simple",
            "used_hints": []
        }

        feedback, difficulty, should_advance, newly_identified, score = parse_evaluation(eval_text, active_session)

        self.assertEqual(feedback, "Good job!")
        self.assertEqual(difficulty, "Simple")
        self.assertEqual(newly_identified, ["detail 1", "detail 2"])
        self.assertEqual(score, 75)
        self.assertFalse(should_advance)

    def test_parse_evaluation_malformed_json(self):
        """Test parsing evaluation with malformed JSON."""
        # Test with malformed JSON
        eval_text = 'feedback: "Good job!", newly_identified_details: ["detail 1", "detail 2"], hint: "Look for colors", score: 75, advance_difficulty: false'
        active_session = {
            "identified_details": [],
            "key_details": ["detail 1", "detail 2", "detail 3"],
            "difficulty": "Simple",
            "used_hints": []
        }

        feedback, difficulty, should_advance, newly_identified, score = parse_evaluation(eval_text, active_session)

        # Should still extract values
        self.assertTrue(len(feedback) > 0)
        self.assertEqual(difficulty, "Simple")
        self.assertTrue(isinstance(newly_identified, list))

    def test_update_checklist(self):
        """Test updating the checklist with newly identified details."""
        checklist = [
            {"detail": "red ball", "identified": False, "id": 0},
            {"detail": "blue sky", "identified": False, "id": 1},
            {"detail": "green tree", "identified": True, "id": 2},
            {"detail": "yellow sun", "identified": False, "id": 3}
        ]

        newly_identified = ["the blue sky", "sun that is yellow"]
        key_details = ["red ball", "blue sky", "green tree", "yellow sun"]

        updated_checklist = update_checklist(checklist, newly_identified, key_details)

        # Check that the right items were marked as identified
        self.assertFalse(updated_checklist[0]["identified"])  # red ball
        self.assertTrue(updated_checklist[1]["identified"])   # blue sky
        self.assertTrue(updated_checklist[2]["identified"])   # green tree (already was)
        self.assertTrue(updated_checklist[3]["identified"])   # yellow sun


if __name__ == '__main__':
    unittest.main()
