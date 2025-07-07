# tests/conftest.py
"""
Configuration file for pytest.
This allows sharing fixtures between test files when using pytest.
"""

import pytest
import io
import base64
from PIL import Image

@pytest.fixture
def test_image():
    """Create a small test image for testing."""
    return Image.new('RGB', (100, 100), color='blue')

@pytest.fixture
def test_data_url():
    """Create a data URL from a test image."""
    img = Image.new('RGB', (10, 10), color='red')
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"

@pytest.fixture
def sample_session():
    """Create a sample session for testing."""
    return {
        "prompt": "A test prompt",
        "image_description": "Description of test image",
        "chat": [{"role": "user", "content": "I see a red ball"}, {"role": "assistant", "content": "Good observation!"}],
        "key_details": ["red ball", "blue sky", "green grass"],
        "identified_details": ["red ball"],
        "used_hints": ["Look at the top of the image"],
        "difficulty": "Simple",
        "autism_level": "Level 1",
        "age": "5",
        "attempt_limit": 3,
        "attempt_count": 1,
        "details_threshold": 0.7,
        "image_style": "Cartoon"
    }

@pytest.fixture
def sample_checklist():
    """Create a sample checklist for testing."""
    return [
        {"detail": "red ball", "identified": True, "id": 0},
        {"detail": "blue sky", "identified": False, "id": 1},
        {"detail": "green grass", "identified": False, "id": 2}
    ]
