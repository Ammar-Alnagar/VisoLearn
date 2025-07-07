import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API keys
HF_TOKEN = os.environ.get("HF_TOKEN")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

BFL_API_KEY=os.environ.get("BFL_API_KEY")

# Configure difficulty levels
DIFFICULTY_LEVELS = ["Very Simple", "Simple", "Moderate", "Detailed", "Very Detailed"]

# Default treatment plans based on autism level
DEFAULT_TREATMENT_PLANS = {
    "Level 1": "Develop social communication skills and manage specific interests while maintaining independence.",
    "Level 2": "Focus on structured learning environments with visual supports and consistent routines.",
    "Level 3": "Provide highly structured support with simplified visual information and sensory-appropriate environments."
}

# Available image styles
IMAGE_STYLES = ["Realistic", "Illustration", "Cartoon", "Watercolor", "3D Rendering"]

# Default session settings
DEFAULT_SESSION = {
    "prompt": None,
    "image": None,
    "image_description": None,
    "chat": [],
    "treatment_plan": "",
    "topic_focus": "",
    "key_details": [],
    "identified_details": [],
    "used_hints": [],
    "difficulty": "Very Simple",
    "age": "3",
    "autism_level": "Level 1",
    "attempt_limit": 3,
    "attempt_count": 0,
    "details_threshold": 0.7,
    "image_style": "Realistic"
}
