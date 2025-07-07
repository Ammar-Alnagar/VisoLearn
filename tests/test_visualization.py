# tests/test_visualization.py

import unittest
from unittest.mock import patch

from utils.visualization import (
    update_difficulty_label,
    update_checklist_html,
    update_progress_html,
    update_attempt_counter
)

class TestVisualization(unittest.TestCase):
    """Test suite for visualization helper functions."""

    def test_update_difficulty_label(self):
        """Test generating difficulty label HTML."""
        # Test with a session that has a difficulty
        session = {"difficulty": "Challenging"}
        result = update_difficulty_label(session)
        self.assertEqual(result, "**Current Difficulty:** Challenging")

        # Test with a session that has no difficulty
        session = {}
        result = update_difficulty_label(session)
        self.assertEqual(result, "**Current Difficulty:** Very Simple")

    def test_update_checklist_html(self):
        """Test generating checklist HTML."""
        # Test with empty checklist
        result = update_checklist_html([])
        self.assertIn("Generate an image to see details to identify", result)

        # Test with populated checklist
        checklist = [
            {"detail": "red ball", "identified": True, "id": 1},
            {"detail": "blue sky", "identified": False, "id": 2}
        ]
        result = update_checklist_html(checklist)

        # Check content
        self.assertIn("red ball", result)
        self.assertIn("blue sky", result)
        self.assertIn("identified", result)
        self.assertIn("not-identified", result)

        # Check styling
        self.assertIn("background-color: #1e4620", result)  # Identified item
        self.assertIn("background-color: #222222", result)  # Not identified item
        self.assertIn("✅", result)  # Checkmark
        self.assertIn("❌", result)  # X mark

    def test_update_progress_html(self):
        """Test generating progress HTML."""
        # Test with empty checklist
        result = update_progress_html([], {})
        self.assertIn("No active session", result)

        # Test with checklist and session
        checklist = [
            {"detail": "item 1", "identified": True, "id": 0},
            {"detail": "item 2", "identified": True, "id": 1},
            {"detail": "item 3", "identified": False, "id": 2},
            {"detail": "item 4", "identified": False, "id": 3}
        ]

        session = {"details_threshold": 0.75}
        result = update_progress_html(checklist, session)

        # Check content
        self.assertIn("Progress: 2 / 4 details", result)
        self.assertIn("width: 50%", result)  # Progress bar width
        self.assertIn("Need to identify at least 3 details", result)  # Threshold info

        # Test passing threshold
        checklist = [
            {"detail": "item 1", "identified": True, "id": 0},
            {"detail": "item 2", "identified": True, "id": 1},
            {"detail": "item 3", "identified": True, "id": 2},
            {"detail": "item 4", "identified": False, "id": 3}
        ]

        result = update_progress_html(checklist, session)
        self.assertIn("Threshold reached", result)

    def test_update_attempt_counter(self):
        """Test generating attempt counter HTML."""
        # Test with default values
        session = {}
        result = update_attempt_counter(session)
        self.assertIn("Attempts: 0/3", result)

        # Test with custom values
        session = {"attempt_count": 2, "attempt_limit": 5}
        result = update_attempt_counter(session)
        self.assertIn("Attempts: 2/5", result)


if __name__ == '__main__':
    unittest.main()
