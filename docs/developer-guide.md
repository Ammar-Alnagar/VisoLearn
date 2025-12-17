# 👨‍💻 Developer Guide

## 📋 Overview

This document provides comprehensive guidance for developers who want to contribute to or extend the VisoLearn-2 platform. It covers setup, development workflow, coding standards, testing, and contribution guidelines.

## 🚀 Getting Started

### Prerequisites

Before setting up the development environment, ensure you have the following installed:

- **Python**: Version 3.8 or higher (3.10+ recommended)
- **Git**: Version control system
- **Package Manager**: pip (usually comes with Python)
- **API Accounts**: 
  - OpenAI account for GPT-4 and DALL-E access
  - Google account for Google Generative AI access
  - Hugging Face account (optional)

### Development Environment Setup

```bash
# 1. Clone the repository
git clone https://github.com/your-username/VisoLearn-2.git
cd VisoLearn-2

# 2. Create virtual environment
python -m venv venv-dev
source venv-dev/bin/activate  # On Windows: venv-dev\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install development dependencies
pip install -r requirements-dev.txt

# 5. Install package in development mode
pip install -e .

# 6. Create development configuration
cp .env.example .env.dev
# Edit .env.dev with your development API keys

# 7. Set up pre-commit hooks (optional but recommended)
pip install pre-commit
pre-commit install
```

### Environment Configuration

Create a `.env` file in the project root with the following variables:

```bash
# API Keys - Required for full functionality
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
HF_TOKEN=your_huggingface_token_here
BFL_API_KEY=your_blue_foundation_api_key_here

# Application Settings
DEBUG_MODE=True
SERVER_HOST=localhost
SERVER_PORT=7860

# Session Settings
MAX_SESSIONS=10
SESSION_TIMEOUT_MINUTES=30
IMAGE_CACHE_SIZE=100

# Google Drive Integration (optional)
GOOGLE_DRIVE_SYNC=False
```

## 🏗️ Project Structure

```
VisoLearn-2/
├── app.py                 # Main application entry point
├── config.py             # Configuration management
├── requirements.txt      # Production dependencies
├── requirements-dev.txt  # Development dependencies
├── .env.example         # Example environment file
├── .gitignore           # Git ignore patterns
├── docs/                # Documentation files
│   ├── index.md         # Main documentation
│   ├── api-reference.md # API documentation
│   ├── ui-components.md # UI component documentation
│   ├── ai-models.md     # AI model documentation
│   ├── utilities.md     # Utility functions documentation
│   ├── configuration.md # Configuration documentation
│   └── user-journey.md  # User journey documentation
├── models/              # AI model integration modules
│   ├── image_generation.py
│   ├── story_generation.py
│   ├── prompt_generation.py
│   ├── evaluation.py
│   └── backup_image_generation.py
├── ui/                  # User interface components
│   ├── interface.py     # Main UI implementation
│   ├── __init__.py
│   └── Compumacy-Logo-Trans2.png
├── utils/               # Utility functions
│   ├── state_management.py
│   ├── file_operations.py
│   ├── local_storage.py
│   ├── visualization.py
│   └── __init__.py
├── static/              # Static assets
├── tests/               # Test files
├── Sessions History/    # Session data storage
├── __init__.py          # Package initialization
└── README.md           # Project overview
```

## 🧪 Development Workflow

### 1. Branch Strategy

Follow the Git Flow branching model:

- `main`: Production-ready code
- `develop`: Integration branch for features
- `feature/*`: Individual feature branches
- `release/*`: Release preparation branches
- `hotfix/*`: Critical bug fixes

```bash
# Create a feature branch
git checkout -b feature/your-feature-name develop

# Create a hotfix branch
git checkout -b hotfix/critical-fix main
```

### 2. Coding Standards

#### Python Code Style
- Follow PEP 8 style guide
- Use 4 spaces for indentation
- Maximum line length of 88 characters
- Use descriptive variable and function names
- Include docstrings for all public functions

```python
def process_user_input(user_input: str, difficulty_level: str) -> dict:
    """
    Process user input and generate appropriate response.
    
    Args:
        user_input: Raw input from user
        difficulty_level: Current difficulty level setting
    
    Returns:
        Processed response with evaluation and feedback
    """
    # Function implementation here
    pass
```

#### Type Hints
Use type hints consistently for better code documentation and IDE support:

```python
from typing import Dict, List, Optional, Union

def analyze_session_data(
    session_id: str, 
    analytics_data: List[Dict[str, Union[int, str]]]
) -> Optional[Dict[str, float]]:
    # Implementation
    pass
```

#### Error Handling
Always implement proper error handling with logging:

```python
import logging

def safe_api_call(api_function, *args, **kwargs):
    """Safely execute an API call with error handling."""
    try:
        result = api_function(*args, **kwargs)
        logging.info(f"API call successful: {api_function.__name__}")
        return result
    except Exception as e:
        logging.error(f"API call failed: {e}")
        return {"error": str(e), "success": False}
```

### 3. Documentation Standards

#### Function Documentation
All functions should have comprehensive docstrings:

```python
def generate_educational_image(
    description: str, 
    style: str = "cartoon", 
    difficulty: str = "simple"
) -> Dict[str, Union[str, bool]]:
    """
    Generate an educational image based on description and parameters.
    
    This function creates AI-generated images that are appropriate for 
    autism education, with considerations for visual processing strengths.
    
    Args:
        description: Descriptive text for image generation
        style: Visual style (default: "cartoon")
        difficulty: Complexity level (default: "simple")
    
    Returns:
        Dictionary containing image URL and metadata
        
    Raises:
        ValueError: If description is empty or invalid parameters
        
    Example:
        >>> result = generate_educational_image("a happy child learning")
        >>> print(result['url'])
        "https://example.com/image.png"
    """
    # Implementation here
    pass
```

#### Module Documentation
Each module should include a module-level docstring:

```python
"""
Image Generation Module for VisoLearn-2

This module handles the creation of educational images using AI models,
with special consideration for autism-friendly visual processing.

The module includes:
- AI model integration (OpenAI, Google, etc.)
- Image validation and quality assessment
- Autism-specific visual design considerations
- Error handling and fallback mechanisms

Key functions:
- generate_educational_image(): Main image generation function
- validate_image_quality(): Quality assessment
- apply_autism_friendly_filters(): Visual adjustments
"""
```

## 🧪 Testing Strategy

### Test Structure

Tests are organized by functionality:

```
tests/
├── test_image_generation.py     # Image generation tests
├── test_story_generation.py     # Story generation tests
├── test_evaluation.py          # Evaluation system tests
├── test_file_operations.py     # File operations tests
├── test_integration.py         # Integration tests
├── test_ui_components.py       # UI component tests
└── test_comprehensive.py       # Full system tests
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run tests with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/test_image_generation.py

# Run tests with verbose output
pytest tests/ -v

# Run tests and stop on first failure
pytest tests/ -x
```

### Test Writing Guidelines

#### Unit Tests
Test individual functions and components:

```python
import pytest
from models.evaluation import evaluate_response

def test_evaluate_response_accuracy():
    """Test that evaluation returns correct accuracy scores."""
    user_input = "A red apple on a table"
    expected_details = ["red", "apple", "table"]
    difficulty = "simple"
    
    result = evaluate_response(user_input, expected_details, difficulty)
    
    assert 'accuracy' in result
    assert 0 <= result['accuracy'] <= 100
    assert 'feedback' in result

def test_evaluate_response_empty_input():
    """Test evaluation with empty user input."""
    result = evaluate_response("", ["apple"], "simple")
    assert result['accuracy'] == 0
    assert len(result['identified_details']) == 0
```

#### Integration Tests
Test interactions between components:

```python
def test_image_generation_complete_flow():
    """Test complete image generation flow."""
    from models.image_generation import generate_image
    from models.prompt_generation import generate_image_prompt
    
    # Generate a prompt
    prompt = generate_image_prompt(
        description="educational image",
        style="cartoon",
        difficulty="simple"
    )
    
    # Generate image
    result = generate_image(prompt, "cartoon", "simple")
    
    # Assert successful generation
    assert result is not None
    assert 'url' in result or 'error' not in result
```

#### Performance Tests
Test performance under load:

```python
import time

def test_performance_multiple_simultaneous_requests():
    """Test performance with multiple simultaneous requests."""
    import threading
    
    def generate_image_thread():
        # Generate image and measure time
        start = time.time()
        generate_image("test prompt", "cartoon", "simple")
        return time.time() - start
    
    # Start multiple threads
    threads = []
    for _ in range(5):
        thread = threading.Thread(target=generate_image_thread)
        threads.append(thread)
        thread.start()
    
    # Wait for all to complete
    for thread in threads:
        thread.join()
```

## 🔧 Development Tools

### Code Quality Tools

#### Linting and Formatting
```bash
# Format code with black
black src/

# Check code style with flake8
flake8 src/

# Type checking with mypy
mypy src/
```

#### Pre-commit Hooks
Add the following to `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/flake8
    rev: 4.0.1
    hooks:
      - id: flake8
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v0.950
    hooks:
      - id: mypy
```

### Debugging

#### Debug Mode
Enable debug mode by setting `DEBUG_MODE=True` in your `.env` file:

```python
# Enable additional logging in debug mode
import os
DEBUG_MODE = os.environ.get('DEBUG_MODE', 'False').lower() == 'true'

if DEBUG_MODE:
    import logging
    logging.basicConfig(level=logging.DEBUG)
```

#### Debugging Tips
- Use `print()` statements for quick debugging
- Utilize Python debugger (`pdb`) for complex issues
- Enable detailed logging for API calls
- Use browser developer tools for UI issues

## 🚀 Building and Deployment

### Local Development Server

```bash
# Start the development server
python app.py

# The application will be available at:
# http://localhost:7860
```

### Production Build

```bash
# Create a production build
pip install -r requirements.txt

# Run the application with production settings
DEBUG_MODE=False python app.py
```

### Docker Deployment (Optional)

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 7860

CMD ["python", "app.py"]
```

```bash
# Build Docker image
docker build -t visolearn .

# Run container
docker run -p 7860:7860 --env-file .env visolearn
```

## 🧪 Quality Assurance

### Code Review Checklist

Before submitting a pull request, ensure:

- [ ] Code follows PEP 8 style guidelines
- [ ] Type hints are included where appropriate
- [ ] Comprehensive docstrings are provided
- [ ] Tests are written and passing
- [ ] Error handling is implemented
- [ ] Performance considerations are addressed
- [ ] Security best practices are followed
- [ ] Accessibility considerations are implemented
- [ ] Documentation is updated

### Testing Requirements

- Unit test coverage should be >= 80%
- Integration tests should cover main workflows
- Performance tests for critical paths
- Error condition tests

### Code Quality Metrics

- Maintain high code readability
- Limit function complexity
- Ensure proper error handling
- Follow security best practices

## 💡 Best Practices

### For AI Model Integration
- Always implement fallback mechanisms
- Include proper error handling for API calls
- Validate and sanitize all outputs
- Monitor API usage and costs
- Implement rate limiting appropriately

### For Accessibility
- Follow WCAG 2.1 guidelines
- Provide alternative text for images
- Ensure keyboard navigation works
- Use sufficient color contrast
- Support screen readers

### For Performance
- Implement caching for expensive operations
- Use lazy loading where appropriate
- Optimize image sizes and formats
- Minimize external API calls
- Consider database indexing

## 🤝 Contributing

### How to Contribute

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes**
4. **Add tests** for your changes
5. **Run all tests** to ensure everything passes
6. **Commit your changes**: `git commit -m 'Add amazing feature'`
7. **Push to the branch**: `git push origin feature/amazing-feature`
8. **Open a pull request**

### Pull Request Guidelines

- Keep pull requests focused on a single feature or bug fix
- Include a clear, descriptive title and description
- Add relevant tests
- Update documentation as needed
- Ensure all tests pass
- Follow the project's code style

### Issue Reporting

When creating an issue, please include:

- **Clear title** describing the issue
- **Steps to reproduce** the problem
- **Expected behavior**
- **Actual behavior**
- **Environment information** (Python version, OS, etc.)
- **Any relevant screenshots or error messages**

## 📊 Development Analytics

### Monitoring Development Metrics

Track these key metrics during development:

- Code coverage percentage
- Build time
- Test execution time
- Performance benchmarks
- Security scan results

### Performance Benchmarks

```python
import time
import pytest

def benchmark_image_generation():
    """Benchmark image generation performance."""
    start_time = time.time()
    
    # Generate multiple images
    for i in range(10):
        generate_image(f"test image {i}", "cartoon", "simple")
    
    end_time = time.time()
    avg_time = (end_time - start_time) / 10
    
    print(f"Average image generation time: {avg_time:.2f}s")
    assert avg_time < 15.0  # Should generate in under 15 seconds
```

## 🛠️ Troubleshooting

### Common Development Issues

**Issue: API Keys Not Working**
- Verify API keys are correctly set in `.env` file
- Check API key permissions and quotas
- Ensure no extra whitespace in the key

**Issue: Tests Failing**
- Run tests individually to isolate the problem
- Check for dependency conflicts
- Verify test data and mocks

**Issue: Performance Problems**
- Use profiling tools to identify bottlenecks
- Check API call frequency and caching
- Monitor resource usage

### Debugging Commands

```bash
# Check environment variables
python -c "import os; print(os.environ.get('OPENAI_API_KEY', 'Not set'))"

# Test API connectivity
python -c "import openai; openai.api_key='your-key'; print(openai.Model.list())"

# Run with detailed logging
DEBUG_MODE=true python app.py
```

## 📚 Additional Resources

### Learning Resources
- [Python Documentation](https://docs.python.org/)
- [Gradio Documentation](https://gradio.app/docs/)
- [OpenAI API Reference](https://platform.openai.com/docs/)
- [Google Generative AI](https://ai.google.dev/)
- [PEP 8 Style Guide](https://pep8.org/)

### Development Tools
- [VS Code](https://code.visualstudio.com/) - Recommended IDE
- [PyCharm](https://www.jetbrains.com/pycharm/) - Alternative IDE
- [Git](https://git-scm.com/) - Version control
- [Docker](https://www.docker.com/) - Containerization

### Community Resources
- [Python Discord](https://pythondiscord.com/) - Python community
- [OpenAI Community](https://community.openai.com/) - AI development
- [Gradio Community](https://discord.gg/feTf9x3ZSB) - UI framework

## 📞 Support

For development support:
- Check the existing documentation in the `docs/` folder
- Review the issue tracker for similar problems
- Open a new issue if you can't find a solution
- Contact the maintainers through GitHub

This guide should help you get started with developing and contributing to VisoLearn-2. Happy coding!