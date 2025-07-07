# tests/test_integration.py

import unittest
from unittest.mock import patch, MagicMock
import io
import base64
from PIL import Image
import gradio as gr

from app import main
from models.image_generation import generate_image_fn
from models.evaluation import generate_detailed_description, extract_key_details
from utils.state_management import generate_image_and_reset_chat, chat_respond

class TestEndToEndFlow(unittest.TestCase):
    """Test end-to-end integration flows."""

    @patch('models.image_generation.InferenceClient')
    @patch('models.evaluation.GenerativeModel')
    @patch('models.prompt_generation.GenerativeModel')
    def test_generate_image_flow(self, mock_prompt_model, mock_eval_model, mock_inference):
        """Test the complete image generation flow."""
        # Setup mocks
        # 1. Prompt generation
        prompt_model_instance = MagicMock()
        prompt_response = MagicMock()
        prompt_response.text = "A detailed test prompt for image generation"
        prompt_model_instance.generate_content.return_value = prompt_response
        mock_prompt_model.return_value = prompt_model_instance

        # 2. Image generation
        mock_image = Image.new('RGB', (512, 512), color='blue')
        inference_instance = MagicMock()
        inference_instance.text_to_image.return_value = mock_image
        mock_inference.return_value = inference_instance

        # 3. Image description
        eval_model_instance = MagicMock()
        description_response = MagicMock()
        description_response.text = "This is a description of the test image."
        details_response = MagicMock()
        details_response.text = '["detail 1", "detail 2", "detail 3"]'

        # Configure the mock to return different responses for different calls
        eval_model_instance.generate_content.side_effect = [
            description_response,  # First call - generate description
            details_response       # Second call - extract details
        ]
        mock_eval_model.return_value = eval_model_instance

        # Execute the flow
        # Parameters for image generation
        age = "6"
        autism_level = "Level 1"
        topic_focus = "animals"
        treatment_plan = "Test treatment plan"
        attempt_limit = "3"
        details_threshold = "70"
        active_session = {}
        saved_sessions = []
        image_style = "Cartoon"

        image, new_session, new_saved_sessions, checklist, chat_history = generate_image_and_reset_chat(
            age, autism_level, topic_focus, treatment_plan, attempt_limit,
            details_threshold, active_session, saved_sessions, image_style
        )

        # Verify the full flow executed correctly
        # 1. Check prompt generation
        prompt_model_instance.generate_content.assert_called_once()

        # 2. Check image generation
        inference_instance.text_to_image.assert_called_once_with(
            "A detailed test prompt for image generation",
            model="stabilityai/stable-diffusion-3.5-large-turbo",
            guidance_scale=4.0,
            negative_prompt="blurry, distorted, low quality, pixelated, poorly drawn, deformed, unfinished, sketchy, cartoon, blur",
            num_inference_steps=50
        )

        # 3. Check image description and details extraction
        self.assertEqual(eval_model_instance.generate_content.call_count, 2)

        # 4. Check session creation
        self.assertEqual(new_session["prompt"], "A detailed test prompt for image generation")
        self.assertEqual(new_session["image_description"], "This is a description of the test image.")
        self.assertEqual(new_session["key_details"], ["detail 1", "detail 2", "detail 3"])
        self.assertEqual(new_session["age"], "6")
        self.assertEqual(new_session["autism_level"], "Level 1")
        self.assertEqual(new_session["topic_focus"], "animals")
        self.assertEqual(new_session["attempt_limit"], 3)

        # 5. Check checklist creation
        self.assertEqual(len(checklist), 3)
        self.assertEqual(checklist[0]["detail"], "detail 1")
        self.assertFalse(checklist[0]["identified"])

    @patch('utils.state_management.compare_details_chat_fn')
    @patch('utils.state_management.parse_evaluation')
    def test_chat_interaction_flow(self, mock_parse_eval, mock_compare_details):
        """Test the chat interaction flow."""
        # Create a test image for the session
        test_image = Image.new('RGB', (100, 100), color='red')
        buffer = io.BytesIO()
        test_image.save(buffer, format="PNG")
        img_bytes = buffer.getvalue()
        test_data_url = f"data:image/png;base64,{base64.b64encode(img_bytes).decode()}"

        # Setup mocks
        mock_compare_details.return_value = "Raw evaluation response"
        mock_parse_eval.return_value = (
            "Good observation! Yes, there is a red ball in the image.",
            "Simple",
            False,
            ["red ball"],
            80
        )

        # Create test session and checklist
        active_session = {
            "prompt": "A test prompt",
            "image": test_data_url,
            "image_description": "An image with a red ball and blue sky",
            "chat": [],
            "key_details": ["red ball", "blue sky", "green grass"],
            "identified_details": [],
            "used_hints": [],
            "difficulty": "Simple",
            "autism_level": "Level 1",
            "age": "5",
            "attempt_limit": 3,
            "attempt_count": 0,
            "details_threshold": 0.7
        }

        saved_sessions = []

        checklist = [
            {"detail": "red ball", "identified": False, "id": 0},
            {"detail": "blue sky", "identified": False, "id": 1},
            {"detail": "green grass", "identified": False, "id": 2}
        ]

        # Execute chat flow
        user_message = "I see a red ball"
        _, updated_chat, new_saved_sessions, updated_session, updated_checklist, _ = chat_respond(
            user_message, active_session, saved_sessions, checklist
        )

        # Verify the flow executed correctly
        # 1. Check evaluation was called
        mock_compare_details.assert_called_once()

        # 2. Check chat was updated
        self.assertEqual(len(updated_chat), 2)
        self.assertEqual(updated_chat[0], {"role": "user", "content": "I see a red ball"})
        self.assertEqual(updated_chat[1], {"role": "assistant", "content": "Good observation! Yes, there is a red ball in the image."})

        # 3. Check identified details were updated
        self.assertEqual(updated_session["identified_details"], ["red ball"])

        # 4. Check checklist was updated
        self.assertTrue(updated_checklist[0]["identified"])  # red ball
        self.assertFalse(updated_checklist[1]["identified"])  # blue sky
        self.assertFalse(updated_checklist[2]["identified"])  # green grass

        # 5. No advancement should have occurred
        self.assertEqual(updated_session["difficulty"], "Simple")
        self.assertEqual(len(new_saved_sessions), 0)


if __name__ == '__main__':
    unittest.main()
