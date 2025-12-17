# 📚 Technical Reference Documentation

## 🎯 Overview

This document provides comprehensive technical documentation for all modules, functions, classes, and components in the VisoLearn-2 system. It serves as a detailed reference for developers, maintainers, and advanced users.

## 🏗️ Module Documentation

### 📁 Models Module

The `models/` directory contains the core AI and business logic components of VisoLearn-2.

#### 🖼️ `image_generation.py`

**Purpose:** Handles image generation using Google Imagen 4.0 Ultra API and provides image processing utilities.

**Key Functions:**

```python
def generate_image_fn(selected_prompt, model="models/imagen-4.0-ultra-generate-preview-06-06", output_path=None)
```

**Parameters:**
- `selected_prompt` (str): Text description for image generation
- `model` (str): Imagen model identifier (default: Google Imagen 4.0 Ultra)
- `output_path` (str, optional): File path to save generated image

**Returns:** PIL.Image.Image or None

**Global Variables:**
- `global_image_data_url`: Stores the data URL of the generated image
- `global_image_prompt`: Stores the prompt used for generation
- `global_image_description`: Stores user-provided image description

**Error Handling:**
- Validates API key availability from environment variables or config
- Handles image generation failures gracefully
- Provides meaningful error messages

**Usage Example:**
```python
from models.image_generation import generate_image_fn

# Generate an image with a specific prompt
image = generate_image_fn("A happy child playing with colorful blocks")
if image:
    image.show()  # Display the generated image
```

#### ✅ `evaluation.py`

**Purpose:** Implements the evaluation engine for assessing user descriptions and providing feedback.

**Key Functions:**

```python
def evaluate_description(user_description, expected_details, difficulty_level=1)
```

**Parameters:**
- `user_description` (str): User-provided description of the image
- `expected_details` (list): List of key details that should be mentioned
- `difficulty_level` (int): Current difficulty level (1-5)

**Returns:** dict containing evaluation results with keys:
- `score` (float): Overall evaluation score (0-1)
- `feedback` (str): Constructive feedback for the user
- `missing_details` (list): Details not mentioned by user
- `correct_details` (list): Details correctly identified

**Evaluation Algorithm:**
1. Semantic analysis using Google Gemini
2. Detail matching against expected elements
3. Language complexity assessment
4. Therapeutic goal alignment check

**Usage Example:**
```python
from models.evaluation import evaluate_description

result = evaluate_description(
    "I see a boy with blue shirt playing with red blocks",
    ["boy", "blue shirt", "red blocks", "table", "smiling"],
    difficulty_level=2
)

print(f"Score: {result['score']}")
print(f"Feedback: {result['feedback']}")
```

#### 📖 `story_generation.py`

**Purpose:** Manages the comic story generation process including narrative creation and panel management.

**Key Functions:**

```python
def generate_story_prompt(characters, setting, theme, num_panels=4)
```

**Parameters:**
- `characters` (list): List of character descriptions
- `setting` (str): Story setting/location
- `theme` (str): Story theme or lesson
- `num_panels` (int): Number of comic panels (default: 4)

**Returns:** dict containing:
- `story_prompt` (str): Complete story generation prompt
- `panel_prompts` (list): Individual prompts for each panel
- `character_descriptions` (dict): Detailed character info

**Story Generation Process:**
1. Character development and consistency checks
2. Narrative structure creation
3. Panel-by-panel scene breakdown
4. Visual continuity planning

**Usage Example:**
```python
from models.story_generation import generate_story_prompt

story_data = generate_story_prompt(
    characters=["boy with autism", "supportive teacher"],
    setting="classroom",
    theme="overcoming challenges",
    num_panels=6
)
```

#### 💬 `prompt_generation.py`

**Purpose:** Creates contextual prompts for image generation based on user profile and learning objectives.

**Key Functions:**

```python
def generate_contextual_prompt(age, autism_level, topic, difficulty=1)
```

**Parameters:**
- `age` (int): User's age
- `autism_level` (int): Autism support level (1-3)
- `topic` (str): Learning topic/interest area
- `difficulty` (int): Current difficulty level

**Returns:** str - Complete image generation prompt

**Prompt Generation Logic:**
- Age-appropriate language and concepts
- Autism-level specific visual complexity
- Topic-relevant content selection
- Difficulty-based detail requirements

**Usage Example:**
```python
from models.prompt_generation import generate_contextual_prompt

prompt = generate_contextual_prompt(
    age=8,
    autism_level=2,
    topic="animals",
    difficulty=3
)
```

### 📁 Utils Module

The `utils/` directory contains utility functions and helper modules.

#### 💾 `file_operations.py`

**Purpose:** Handles all file system operations including session management and data persistence.

**Key Functions:**

```python
def save_session_data(session_id, data, session_type="image_description")
```

**Parameters:**
- `session_id` (str): Unique session identifier
- `data` (dict): Session data to save
- `session_type` (str): Type of session (image_description, story, etc.)

**Returns:** bool - Success status

**File Structure:**
```
Sessions History/
├── {session_id}/
│   ├── images/
│   │   └── session_0.png
│   ├── metadata.json
│   └── sessions.json
```

**Usage Example:**
```python
from utils.file_operations import save_session_data

session_data = {
    "user_id": "user123",
    "timestamp": "2024-01-15T10:30:00",
    "images": ["image1.png"],
    "descriptions": ["A boy playing with blocks"]
}

save_session_data("session_20240115", session_data)
```

#### 🔄 `state_management.py`

**Purpose:** Manages application state and session data during runtime.

**Key Functions:**

```python
def get_current_session()
def update_session_state(key, value)
def reset_session()
```

**State Management Features:**
- Session persistence across interface interactions
- Temporary data storage
- State validation and cleanup
- Multi-session support

**Usage Example:**
```python
from utils.state_management import get_current_session, update_session_state

# Get current session data
session = get_current_session()

# Update session state
update_session_state("current_image", "image123.png")
```

#### 📊 `visualization.py`

**Purpose:** Generates visual representations of progress and analytics data.

**Key Functions:**

```python
def generate_progress_chart(session_data)
def create_skill_development_heatmap(user_data)
```

**Visualization Types:**
- Progress charts and graphs
- Skill development heatmaps
- Engagement timelines
- Achievement visualizations

**Usage Example:**
```python
from utils.visualization import generate_progress_chart

# Generate a progress chart for display
chart_image = generate_progress_chart(session_data)
chart_image.save("progress_chart.png")
```

### 📁 UI Module

The `ui/` directory contains user interface components.

#### 🎨 `interface.py`

**Purpose:** Main Gradio interface implementation with all interactive components.

**Key Components:**

```python
def create_interface()
```

**Interface Sections:**
- Image Description Practice Module
- Comic Story Generator Module
- Analytics Dashboard
- Settings and Configuration
- User Profile Management

**UI Features:**
- Autism-friendly design patterns
- High-contrast color schemes
- Reduced visual clutter
- Consistent navigation

**Usage Example:**
```python
from ui.interface import create_interface

# Create and launch the interface
demo = create_interface()
demo.launch()
```

## 🔧 Configuration Management

### 📄 `config.py`

**Purpose:** Centralized configuration management for API keys and application settings.

**Configuration Variables:**
- `OPENAI_API_KEY`: OpenAI API key
- `GOOGLE_API_KEY`: Google API key
- `HF_TOKEN`: Hugging Face token
- `BFL_API_KEY`: Blue Foundation API key
- `DEBUG_MODE`: Debug flag
- `SESSION_TIMEOUT`: Session timeout duration

**Configuration Loading:**
1. Environment variables (highest priority)
2. Config file settings
3. Default values

**Usage Example:**
```python
import config

# Access configuration values
api_key = config.OPENAI_API_KEY
debug_mode = config.DEBUG_MODE
```

## 🚀 Main Application

### 📄 `app.py`

**Purpose:** Main application entry point and initialization.

**Key Functions:**

```python
def main()
```

**Initialization Process:**
1. Configure Google API client
2. Initialize Gradio interface
3. Set up server configuration
4. Launch web application

**Usage Example:**
```python
# Run the application
python app.py
```

## 🧪 Testing Framework

### 📁 `tests/`

**Test Structure:**
- Unit tests for individual functions
- Integration tests for module interactions
- End-to-end tests for complete workflows
- Performance tests for system behavior

**Test Coverage:**
- 85%+ code coverage target
- Comprehensive error case testing
- Edge case validation
- Regression test suite

**Running Tests:**
```bash
# Run all tests
python -m pytest tests/

# Run specific test module
python -m pytest tests/test_image_generation.py
```

## 📊 Data Structures

### Session Data Structure

```json
{
  "session_id": "unique_identifier",
  "user_id": "user_identifier",
  "timestamp": "ISO_8601_timestamp",
  "session_type": "image_description|story|comic",
  "metadata": {
    "age": 8,
    "autism_level": 2,
    "topic": "animals",
    "difficulty_level": 3
  },
  "images": [
    {
      "image_id": "image_001",
      "prompt": "detailed_image_prompt",
      "path": "images/image_001.png",
      "generated_at": "timestamp",
      "descriptions": [
        {
          "description": "user_description_text",
          "timestamp": "timestamp",
          "evaluation": {
            "score": 0.85,
            "feedback": "feedback_text",
            "missing_details": ["detail1", "detail2"],
            "correct_details": ["detail3", "detail4"]
          }
        }
      ]
    }
  ],
  "progress": {
    "current_level": 3,
    "completion_rate": 0.75,
    "skills_developed": ["visual_analysis", "descriptive_language"]
  }
}
```

### User Profile Structure

```json
{
  "user_id": "unique_identifier",
  "name": "user_name",
  "age": 8,
  "autism_level": 2,
  "preferences": {
    "image_style": "cartoon",
    "difficulty_progression": "automatic",
    "language": "english",
    "theme": "light"
  },
  "progress": {
    "image_description": {
      "current_level": 3,
      "sessions_completed": 15,
      "average_score": 0.82
    },
    "story_comprehension": {
      "current_level": 2,
      "sessions_completed": 8,
      "average_score": 0.78
    }
  },
  "achievements": [
    {
      "achievement_id": "first_session",
      "unlocked_at": "timestamp",
      "description": "Completed first learning session"
    }
  ]
}
```

## 🔄 API Integration Patterns

### OpenAI API Integration

**Best Practices:**
- API key management via environment variables
- Error handling and retry logic
- Rate limiting awareness
- Response validation

**Integration Example:**
```python
import openai
from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

try:
    response = openai.Image.create(
        prompt="A happy child playing with blocks",
        n=1,
        size="1024x1024"
    )
    image_url = response['data'][0]['url']
except openai.error.OpenAIError as e:
    # Handle API errors gracefully
    print(f"OpenAI API error: {e}")
```

### Google Gemini Integration

**Best Practices:**
- Context management for multi-turn conversations
- Token usage monitoring
- Response formatting and validation
- Error recovery strategies

**Integration Example:**
```python
from google.generativeai import configure, GenerativeModel

configure(api_key=config.GOOGLE_API_KEY)
model = GenerativeModel('gemini-pro')

try:
    response = model.generate_content(
        "Evaluate this description: 'A boy with blue shirt playing with red blocks'"
    )
    evaluation = response.text
except Exception as e:
    # Handle Google API errors
    print(f"Google API error: {e}")
```

## 📈 Performance Optimization Techniques

### Caching Strategies

**Image Caching:**
- Store generated images locally
- Implement cache invalidation policies
- Use thumbnails for previews

**API Response Caching:**
- Cache frequent API responses
- Implement TTL (Time-To-Live) policies
- Monitor cache hit rates

### Asynchronous Processing

**Background Tasks:**
- Image generation queues
- Analytics processing
- Cloud synchronization
- Data backup operations

**Parallel Processing:**
- Multi-threaded operations
- Concurrent API calls
- Batch processing capabilities

## 🔒 Security Best Practices

### API Key Management

**Security Measures:**
- Never commit API keys to version control
- Use environment variables for sensitive data
- Implement key rotation policies
- Monitor API usage patterns

### Data Protection

**Security Features:**
- Data encryption for sensitive information
- Secure authentication mechanisms
- Input validation and sanitization
- Privacy-preserving analytics

## 🤝 Extensibility Patterns

### Plugin Architecture

**Extension Points:**
- Custom evaluation algorithms
- Additional image styles
- New therapeutic modules
- Enhanced analytics features

**Plugin Interface:**
```python
class EvaluationPlugin:
    def evaluate(self, user_description, expected_details):
        """Evaluate user description and return feedback"""
        pass
    
    def get_name(self):
        """Return plugin name"""
        pass
    
    def get_version(self):
        """Return plugin version"""
        pass
```

### Configuration Extensibility

**Customization Options:**
- Module-specific configuration
- Feature flags and toggles
- Environment-based settings
- User preference overrides

## 📚 Error Handling and Debugging

### Error Handling Patterns

**Common Error Types:**
- API connection failures
- Invalid user input
- Resource limitations
- Permission issues

**Error Handling Example:**
```python
try:
    # Risky operation
    result = generate_image(prompt)
    
    if not result:
        raise ValueError("Image generation failed")
        
except APIError as e:
    # Handle API-specific errors
    log_error(f"API Error: {e}")
    show_user_message("Temporary service issue. Please try again.")
    
except ValueError as e:
    # Handle validation errors
    log_error(f"Validation Error: {e}")
    show_user_message("Please check your input and try again.")
    
except Exception as e:
    # Handle unexpected errors
    log_error(f"Unexpected Error: {e}", level="critical")
    show_user_message("An unexpected error occurred. Please contact support.")
```

### Debugging Techniques

**Debugging Tools:**
- Comprehensive logging system
- Debug mode with verbose output
- Performance profiling
- Memory usage monitoring

**Debugging Example:**
```python
import logging
from config import DEBUG_MODE

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if DEBUG_MODE else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Debug logging
def complex_function():
    logger.debug("Starting complex function")
    try:
        # Function logic
        logger.info("Function completed successfully")
    except Exception as e:
        logger.error(f"Function failed: {e}", exc_info=True)
```

## 📊 Analytics and Monitoring

### Analytics Collection

**Tracked Metrics:**
- Session duration and engagement
- Response accuracy and completeness
- Progress through difficulty levels
- Skill development trends
- Therapeutic goal achievement

**Analytics Structure:**
```json
{
  "analytics_id": "unique_identifier",
  "session_id": "related_session",
  "user_id": "user_identifier",
  "timestamp": "ISO_8601_timestamp",
  "metrics": {
    "engagement": {
      "duration_seconds": 360,
      "interactions": 15,
      "completion_rate": 0.85
    },
    "performance": {
      "average_score": 0.78,
      "improvement_rate": 0.12,
      "skill_development": ["visual_analysis", "narrative_comprehension"]
    },
    "technical": {
      "api_calls": 8,
      "processing_time_ms": 4500,
      "errors": 0
    }
  }
}
```

### Monitoring System

**Monitoring Features:**
- Real-time performance metrics
- Error rate tracking
- Resource utilization monitoring
- User activity logging

**Alerting System:**
- Threshold-based alerts
- Anomaly detection
- Performance degradation warnings
- Error rate spikes

## 🎯 Future Development Roadmap

### Architecture Evolution

**Planned Enhancements:**
- Microservices architecture
- Containerization with Docker
- Kubernetes orchestration
- Serverless function integration
- Enhanced caching layers
- Advanced monitoring systems

### Performance Improvements

**Optimization Targets:**
- Reduced API response times
- Enhanced caching strategies
- Improved resource utilization
- Better error recovery
- Enhanced scalability

### Feature Expansion

**Upcoming Features:**
- Multi-language support expansion
- Enhanced accessibility options
- Advanced therapeutic modules
- Mobile application versions
- Integration with educational platforms

## 📚 Additional Resources

### Documentation Structure

```
docs/
├── index.md                  # Main documentation hub
├── technical-architecture.md # System architecture overview
├── technical-reference.md    # Detailed module documentation (this file)
├── ai-models.md              # AI model documentation
├── api-reference.md          # API integration guide
├── utilities.md              # Utility functions reference
├── installation.md           # Installation instructions
├── usage.md                  # User guide and examples
└── contributing.md           # Contribution guidelines
```

### Getting Help

**Support Channels:**
- GitHub Issues: Bug reports and feature requests
- Discussion Forum: Community support and ideas
- Documentation: Comprehensive guides and tutorials
- Email Support: Direct assistance from the team

**Debugging Resources:**
- Error code reference
- Troubleshooting guide
- Performance tuning tips
- Common issues and solutions

This technical reference provides a comprehensive guide to the VisoLearn-2 system architecture, modules, and development patterns. For specific implementation details, refer to the individual module documentation and source code comments.