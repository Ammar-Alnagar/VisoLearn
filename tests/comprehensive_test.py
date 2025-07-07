import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import base64
import io
from PIL import Image
import numpy as np

# Add the parent directory to sys.path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.image_generation import generate_image_fn
from models.evaluation import generate_detailed_description, extract_key_details, compare_details_chat_fn, parse_evaluation
from models.prompt_generation import generate_prompt_from_options
from utils.state_management import generate_image_and_reset_chat, chat_respond, update_sessions
from utils.visualization import update_difficulty_label, update_checklist_html, update_progress_html
from utils.file_operations import save_image_from_data_url, save_all_session_images, save_session_log


class TestImageGeneration(unittest.TestCase):
    """Test the image generation functionality."""

    @patch('models.image_generation.InferenceClient')
    def test_generate_image_success(self, mock_client):
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

    @patch('models.image_generation.InferenceClient')
    def test_generate_image_error(self, mock_client):
        # Setup mock to raise an exception
        mock_client_instance = MagicMock()
        mock_client_instance.text_to_image.side_effect = Exception("API Error")
        mock_client.return_value = mock_client_instance

        # Test the function
        result = generate_image_fn("A test prompt")

        # Verify the result is None when an error occurs
        self.assertIsNone(result)


class TestEvaluation(unittest.TestCase):
    """Test the image evaluation and description functionality."""

    @patch('models.evaluation.GenerativeModel')
    def test_generate_detailed_description(self, mock_model):
        # Setup mock
        mock_model_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "This is a detailed description of the image."
        mock_model_instance.generate_content.return_value = mock_response
        mock_model.return_value = mock_model_instance

        # Create a test image
        test_image = Image.new('RGB', (100, 100), color='blue')

        # Call the function
        result = generate_detailed_description(test_image, "test prompt", "Simple", "animals")

        # Verify result
        self.assertEqual(result, "This is a detailed description of the image.")
        mock_model_instance.generate_content.assert_called_once()

    @patch('models.evaluation.GenerativeModel')
    def test_extract_key_details(self, mock_model):
        # Setup mock
        mock_model_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.text = '["detail 1", "detail 2", "detail 3"]'
        mock_model_instance.generate_content.return_value = mock_response
        mock_model.return_value = mock_model_instance

        # Create a test image
        test_image = Image.new('RGB', (100, 100), color='green')

        # Call the function
        result = extract_key_details(test_image, "test prompt", "animals")

        # Verify result contains extracted details
        self.assertIn("detail 1", result)
        self.assertIn("detail 2", result)
        self.assertIn("detail 3", result)

    def test_parse_evaluation_json(self):
        # Test with valid JSON
        eval_text = '{"feedback": "Good job!", "newly_identified_details": ["detail 1", "detail 2"], "hint": "Look for colors", "score": 75, "advance_difficulty": false}'
        active_session = {"identified_details": [], "key_details": ["detail 1", "detail 2", "detail 3"], "difficulty": "Simple", "used_hints": []}

        feedback, difficulty, should_advance, newly_identified, score = parse_evaluation(eval_text, active_session)

        self.assertEqual(feedback, "Good job!")
        self.assertEqual(difficulty, "Simple")
        self.assertEqual(newly_identified, ["detail 1", "detail 2"])
        self.assertEqual(score, 75)
        self.assertFalse(should_advance)


class TestPromptGeneration(unittest.TestCase):
    """Test prompt generation functionality."""

    @patch('models.prompt_generation.GenerativeModel')
    def test_generate_prompt_from_options(self, mock_model):
        # Setup mock
        mock_model_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "A detailed prompt for image generation"
        mock_model_instance.generate_content.return_value = mock_response
        mock_model.return_value = mock_model_instance

        # Call the function
        result = generate_prompt_from_options("Simple", "5", "Level 1", "animals", "Focus on social skills", "Realistic")

        # Verify result
        self.assertEqual(result, "A detailed prompt for image generation")
        mock_model_instance.generate_content.assert_called_once()


class TestStateManagement(unittest.TestCase):
    """Test state management functionality."""

    @patch('utils.state_management.generate_image_fn')
    @patch('utils.state_management.generate_prompt_from_options')
    @patch('utils.state_management.generate_detailed_description')
    @patch('utils.state_management.extract_key_details')
    def test_generate_image_and_reset_chat(self, mock_extract_details, mock_gen_desc, mock_gen_prompt, mock_gen_img):
        # Setup mocks
        mock_gen_prompt.return_value = "A test prompt"
        mock_image = Image.new('RGB', (100, 100), color='purple')
        mock_gen_img.return_value = mock_image
        mock_gen_desc.return_value = "Description of the image"
        mock_extract_details.return_value = ["detail 1", "detail 2"]

        # Test parameters
        age = "5"
        autism_level = "Level 1"
        topic_focus = "animals"
        treatment_plan = "Test plan"
        attempt_limit = "3"
        details_threshold = "70"
        active_session = {}
        saved_sessions = []
        image_style = "Realistic"

        # Call the function
        image, new_active_session, new_sessions, checklist, chat_history = generate_image_and_reset_chat(
            age, autism_level, topic_focus, treatment_plan, attempt_limit,
            details_threshold, active_session, saved_sessions, image_style
        )

        # Verify the function created a proper new session
        self.assertEqual(image, mock_image)
        self.assertEqual(new_active_session["prompt"], "A test prompt")
        self.assertEqual(new_active_session["image_description"], "Description of the image")
        self.assertEqual(new_active_session["key_details"], ["detail 1", "detail 2"])
        self.assertEqual(len(checklist), 2)
        self.assertEqual(checklist[0]["detail"], "detail 1")


class TestVisualization(unittest.TestCase):
    """Test visualization helper functions."""

    def test_update_difficulty_label(self):
        # Test with a session that has a difficulty
        session = {"difficulty": "Challenging"}
        result = update_difficulty_label(session)
        self.assertEqual(result, "**Current Difficulty:** Challenging")

        # Test with a session that has no difficulty
        session = {}
        result = update_difficulty_label(session)
        self.assertEqual(result, "**Current Difficulty:** Very Simple")

    def test_update_checklist_html(self):
        # Test with empty checklist
        result = update_checklist_html([])
        self.assertIn("Generate an image to see details to identify", result)

        # Test with populated checklist
        checklist = [
            {"detail": "red ball", "identified": True, "id": 1},
            {"detail": "blue sky", "identified": False, "id": 2}
        ]
        result = update_checklist_html(checklist)
        self.assertIn("red ball", result)
        self.assertIn("blue sky", result)
        self.assertIn("identified", result)
        self.assertIn("not-identified", result)


class TestFileOperations(unittest.TestCase):
    """Test file operation functionality."""

    @patch('builtins.open')
    def test_save_image_from_data_url(self, mock_open):
        # Create a small test image and convert to data URL
        img = Image.new('RGB', (10, 10), color='red')
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode()
        data_url = f"data:image/png;base64,{img_str}"

        # Call the function
        result = save_image_from_data_url(data_url, "test.png")

        # Verify the file was "saved"
        self.assertTrue(result)
        mock_open.assert_called_once_with("test.png", "wb")


if __name__ == '__main__':
    unittest.main()
