# tests/test_interface.py

import unittest
from unittest.mock import patch, MagicMock
import gradio as gr

from ui.interface import create_interface

class TestInterface(unittest.TestCase):
    """Test suite for the Gradio interface."""

    @patch('ui.interface.gr.Blocks')
    def test_create_interface(self, mock_blocks):
        """Test that the interface is created with all components."""
        # Setup mocks
        mock_blocks_instance = MagicMock()
        mock_blocks.return_value = mock_blocks_instance

        # Mock the context manager behavior
        mock_blocks_instance.__enter__.return_value = mock_blocks_instance

        # Call the function
        interface = create_interface()

        # Verify the interface was created
        self.assertEqual(interface, mock_blocks_instance)

        # Verify all the components were added (check method calls)
        # This is a simplified check - in a real test we might verify more details
        mock_blocks_instance.launch.assert_not_called()  # Should not be called yet

    @patch('ui.interface.gr')
    def test_interface_components(self, mock_gr):
        """Test that all required components are created in the interface."""
        # Setup complex mocks to track component creation
        component_tracker = {}

        def track_component(component_type, **kwargs):
            if component_type not in component_tracker:
                component_tracker[component_type] = []
            component_tracker[component_type].append(kwargs)
            mock_component = MagicMock()
            # Make methods return the mock itself for chaining
            mock_component.change.return_value = mock_component
            mock_component.click.return_value = mock_component
            mock_component.submit.return_value = mock_component
            return mock_component

        # Mock all relevant gr components to track their creation
        mock_gr.Blocks.return_value.__enter__.return_value = MagicMock()
        mock_gr.Column.return_value.__enter__.return_value = MagicMock()
        mock_gr.Row.return_value.__enter__.return_value = MagicMock()

        mock_gr.Markdown.side_effect = lambda **kwargs: track_component("Markdown", **kwargs)
        mock_gr.Textbox.side_effect = lambda **kwargs: track_component("Textbox", **kwargs)
        mock_gr.Dropdown.side_effect = lambda **kwargs: track_component("Dropdown", **kwargs)
        mock_gr.Number.side_effect = lambda **kwargs: track_component("Number", **kwargs)
        mock_gr.Slider.side_effect = lambda **kwargs: track_component("Slider", **kwargs)
        mock_gr.Button.side_effect = lambda **kwargs: track_component("Button", **kwargs)
        mock_gr.Image.side_effect = lambda **kwargs: track_component("Image", **kwargs)
        mock_gr.Chatbot.side_effect = lambda **kwargs: track_component("Chatbot", **kwargs)
        mock_gr.HTML.side_effect = lambda **kwargs: track_component("HTML", **kwargs)
        mock_gr.JSON.side_effect = lambda **kwargs: track_component("JSON", **kwargs)
        mock_gr.State.side_effect = lambda **kwargs: track_component("State", **kwargs)

        # Call the function
        create_interface()

        # Verify essential components were created
        self.assertIn("State", component_tracker)  # Should create state components
        self.assertIn("Button", component_tracker)  # Should create buttons
        self.assertIn("Textbox", component_tracker)  # Should create textboxes
        self.assertIn("Dropdown", component_tracker)  # Should create dropdowns
        self.assertIn("Image", component_tracker)  # Should create image display
        self.assertIn("Chatbot", component_tracker)  # Should create chatbot

        # Check for specific buttons
        button_labels = [kwargs.get('value', '') for kwargs in component_tracker.get("Button", [])]
        self.assertTrue(any("Generate Image" in str(label) for label in button_labels))

        # Check for specific dropdowns
        dropdown_labels = [kwargs.get('label', '') for kwargs in component_tracker.get("Dropdown", [])]
        self.assertTrue(any("Autism Level" in str(label) for label in dropdown_labels))
        self.assertTrue(any("Image Style" in str(label) for label in dropdown_labels))


if __name__ == '__main__':
    unittest.main()
