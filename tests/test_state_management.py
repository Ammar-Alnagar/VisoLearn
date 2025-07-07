# tests/test_state_management.py

import unittest
from unittest.mock import patch, MagicMock
from PIL import Image

from utils.state_management import (
    generate_image_and_reset_chat,
    chat_respond,
    update_sessions
)

class TestStateManagement(unittest.TestCase):
    """Test suite for state management functionality."""

    @patch('utils.state_management.generate_image_fn')
    @patch('utils.state_management.generate_prompt_from_options')
    @patch('utils.state_management.generate_detailed_description')
    @patch('utils.state_management.extract_key_details')
    def test_generate_image_and_reset_chat(self,
                                          mock_extract_details,
                                          mock_gen_desc,
                                          mock_gen_prompt,
                                          mock_gen_img):
        """Test generating a new image and resetting the chat state."""
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
        self.assertEqual(new_active_session["age"], "5")
        self.assertEqual(new_active_session["autism_level"], "Level 1")
        self.assertEqual(new_active_session["topic_focus"], "animals")
        self.assertEqual(new_active_session["treatment_plan"], "Test plan")
        self.assertEqual(new_active_session["attempt_limit"], 3)
        self.assertEqual(new_active_session["details_threshold"], 0.7)
        self.assertEqual(new_active_session["image_style"], "Realistic")

    @patch('utils.state_management.compare_details_chat_fn')
    @patch('utils.state_management.parse_evaluation')
    def test_chat_respond_basic(self, mock_parse_eval, mock_compare_details):
        """Test basic chat response without advancing."""
        # Setup mocks
        mock_compare_details.return_value = "Raw evaluation response"
        mock_parse_eval.return_value = (
            "Good job!", "Simple", False, ["detail 1"], 70
        )

        # Setup test data
        user_message = "I see a red ball"
        active_session = {
            "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVQI12P4//8/AAX+Av7czFnnAAAAAElFTkSuQmCC",
            "image_description": "An image with a red ball",
            "chat": [],
            "key_details": ["red ball", "blue sky"],
            "identified_details": [],
            "difficulty": "Simple",
            "attempt_count": 0,
            "attempt_limit": 3
        }
        saved_sessions = []
        checklist = [
            {"detail": "red ball", "identified": False, "id": 0},
            {"detail": "blue sky", "identified": False, "id": 1}
        ]

        # Call the function
        result = chat_respond(user_message, active_session, saved_sessions, checklist)
        _, updated_chat, _, updated_session, updated_checklist, _ = result

        # Verify results
        self.assertEqual(len(updated_chat), 2)  # User message and response
        self.assertEqual(updated_chat[0], {"role": "user", "content": "I see a red ball"})
        self.assertEqual(updated_chat[1], {"role": "assistant", "content": "Good job!"})
        self.assertEqual(updated_session["identified_details"], ["detail 1"])
        self.assertTrue(updated_checklist[0]["identified"])  # red ball
        self.assertFalse(updated_checklist[1]["identified"])  # blue sky

    @patch('utils.state_management.compare_details_chat_fn')
    @patch('utils.state_management.parse_evaluation')
    @patch('utils.state_management.generate_image_fn')
    @patch('utils.state_management.generate_prompt_from_options')
    @patch('utils.state_management.generate_detailed_description')
    @patch('utils.state_management.extract_key_details')
    def test_chat_respond_with_advancement(self,
                                          mock_extract_details,
                                          mock_gen_desc,
                                          mock_gen_prompt,
                                          mock_gen_img,
                                          mock_parse_eval,
                                          mock_compare_details):
        """Test chat response that triggers advancement to new difficulty."""
        # Setup mocks for evaluation
        mock_compare_details.return_value = "Raw evaluation response"
        mock_parse_eval.return_value = (
            "Great job!", "Moderate", True, ["red ball", "blue sky"], 90
        )

        # Setup mocks for new image generation
        mock_gen_prompt.return_value = "A new prompt for moderate difficulty"
        mock_image = Image.new('RGB', (100, 100), color='green')
        mock_gen_img.return_value = mock_image
        mock_gen_desc.return_value = "Description of the new image"
        mock_extract_details.return_value = ["detail A", "detail B", "detail C"]

        # Setup test data
        user_message = "I see a red ball and blue sky"
        active_session = {
            "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVQI12P4//8/AAX+Av7czFnnAAAAAElFTkSuQmCC",
            "image_description": "An image with a red ball and blue sky",
            "chat": [],
            "key_details": ["red ball", "blue sky"],
            "identified_details": [],
            "difficulty": "Simple",
            "attempt_count": 0,
            "attempt_limit": 3,
            "age": "5",
            "autism_level": "Level 1",
            "topic_focus": "Colors",
            "treatment_plan": "Test plan",
            "details_threshold": 0.7,
            "image_style": "Cartoon"
        }
        saved_sessions = []
        checklist = [
            {"detail": "red ball", "identified": False, "id": 0},
            {"detail": "blue sky", "identified": False, "id": 1}
        ]

        # Call the function
        result = chat_respond(user_message, active_session, saved_sessions, checklist)
        _, updated_chat, new_sessions, new_session, new_checklist, _ = result

        # Verify results
        self.assertEqual(len(new_sessions), 1)  # The old session should be saved
        self.assertEqual(new_sessions[0]["difficulty"], "Simple")  # Old session difficulty
        self.assertEqual(new_session["difficulty"], "Moderate")  # New session difficulty
        self.assertEqual(len(new_checklist), 3)  # New details count
        self.assertEqual(new_checklist[0]["detail"], "detail A")
        self.assertEqual(new_session["key_details"], ["detail A", "detail B", "detail C"])
        self.assertEqual(new_session["attempt_count"], 0)  # Reset attempt count
        self.assertEqual(new_session["image_style"], "Cartoon")  # Keep style

        # Verify advancement message in chat
        self.assertEqual(len(updated_chat), 1)
        self.assertTrue("advanced" in updated_chat[0][1].lower() or
                       "congratulations" in updated_chat[0][1].lower())

    @patch('utils.state_management.generate_image_fn')
    @patch('utils.state_management.generate_prompt_from_options')
    def test_generate_image_and_reset_chat_failure(self, mock_gen_prompt, mock_gen_img):
        """Test that generate_image_and_reset_chat returns 5 values when image generation fails."""
        # Setup mocks
        mock_gen_prompt.return_value = "A test prompt"
        mock_gen_img.return_value = None  # Simulate image generation failure

        # Test parameters
        age = "5"
        autism_level = "Level 1"
        topic_focus = "animals"
        treatment_plan = "Test plan"
        attempt_limit = "3"
        details_threshold = "70"
        active_session = {"chat": [{"role": "assistant", "content": "Welcome!"}]}
        saved_sessions = []
        image_style = "Realistic"

        # Call the function
        result = generate_image_and_reset_chat(
            age, autism_level, topic_focus, treatment_plan, attempt_limit,
            details_threshold, active_session, saved_sessions, image_style
        )

        # Verify exactly 5 return values
        self.assertEqual(len(result), 5)
        image, new_active_session, new_sessions, checklist, chat_history = result

        # Verify error case values
        self.assertIsNone(image)
        self.assertEqual(new_active_session, active_session)
        self.assertEqual(new_sessions, saved_sessions)
        self.assertEqual(checklist, [])
        self.assertEqual(chat_history, [{"role": "assistant", "content": "Welcome!"}])  # Should return existing chat

    def test_update_sessions(self):
        """Test updating session list with active session."""
        # Test with empty active session
        saved_sessions = [{"prompt": "Session 1"}, {"prompt": "Session 2"}]
        active_session = {}

        result = update_sessions(saved_sessions, active_session)
        self.assertEqual(len(result), 2)

        # Test with valid active session
        active_session = {"prompt": "Active session"}
        result = update_sessions(saved_sessions, active_session)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[2]["prompt"], "Active session")


if __name__ == '__main__':
    unittest.main()
