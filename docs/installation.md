# 🛠️ Installation and Setup Guide

## 📋 Overview

This guide provides comprehensive instructions for installing, configuring, and setting up VisoLearn-2 for development, testing, and production environments.

## 📦 System Requirements

### Minimum Requirements
- **Operating System**: Windows 10+, macOS 10.14+, Ubuntu 18.04+
- **Python**: 3.8+ (3.10+ recommended)
- **RAM**: 4GB (8GB recommended)
- **Storage**: 2GB (5GB for full usage)
- **Internet**: 10 Mbps+ (for AI API calls)

### Recommended Requirements
- **Operating System**: Windows 11, macOS 12+, Ubuntu 22.04+
- **Python**: 3.11+
- **RAM**: 16GB
- **Storage**: SSD with 10GB+ free space
- **Internet**: 50 Mbps+ broadband
- **GPU**: CUDA-compatible (optional for enhanced performance)

## 🐍 Python Installation

### Install Python

**Windows:**
1. Download Python from https://www.python.org/downloads/
2. Run the installer
3. Check "Add Python to PATH" during installation
4. Complete the installation

**macOS:**
```bash
# Using Homebrew
brew install python

# Verify installation
python3 --version
```

**Linux (Ubuntu/Debian):**
```bash
# Update package list
sudo apt update

# Install Python and dependencies
sudo apt install python3 python3-pip python3-venv

# Verify installation
python3 --version
pip3 --version
```

### Set Up Virtual Environment

```bash
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

## 📥 Project Setup

### Clone the Repository

```bash
# Clone the VisoLearn-2 repository
git clone https://github.com/visolearn/visolearn-2.git

# Navigate to the project directory
cd visolearn-2
```

### Install Dependencies

```bash
# Install required Python packages
pip install -r requirements.txt

# Install additional dependencies for development
pip install -r requirements-dev.txt
```

### Verify Installation

```bash
# Check that all dependencies are installed
pip list

# Run a quick test
python -c "import app; print('VisoLearn-2 imported successfully')"
```

## 🔑 API Configuration

### Set Up API Keys

VisoLearn-2 requires API keys for OpenAI, Google, and other services.

#### Option 1: Environment Variables

Create a `.env` file in the project root:

```bash
# Create .env file
touch .env

# Edit the file
nano .env
```

Add your API keys:

```env
# OpenAI API Key
OPENAI_API_KEY=your_openai_api_key_here

# Google API Key
GOOGLE_API_KEY=your_google_api_key_here

# Hugging Face Token
HF_TOKEN=your_huggingface_token_here

# Blue Foundation API Key
BFL_API_KEY=your_blue_foundation_api_key_here

# Debug mode (optional)
DEBUG_MODE=True
```

#### Option 2: Direct Configuration

Edit `config.py` and add your API keys directly:

```python
# config.py
OPENAI_API_KEY = "your_openai_api_key_here"
GOOGLE_API_KEY = "your_google_api_key_here"
HF_TOKEN = "your_huggingface_token_here"
BFL_API_KEY = "your_blue_foundation_api_key_here"
DEBUG_MODE = True
```

### API Key Security

**Best Practices:**
- Never commit API keys to version control
- Use environment variables for production
- Implement key rotation policies
- Monitor API usage regularly

## 🚀 Running VisoLearn-2

### Development Mode

```bash
# Run the application in development mode
python app.py

# The application will be available at http://localhost:7860
```

### Production Mode

```bash
# Install additional production dependencies
pip install gunicorn

# Run with production server
gunicorn -w 4 -b 0.0.0.0:7860 app:main

# For better performance, use:
gunicorn -w 8 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:7860 app:main
```

### Docker Deployment (Optional)

```bash
# Build Docker image
docker build -t visolearn-2 .

# Run Docker container
docker run -p 7860:7860 --env-file .env visolearn-2

# For production with proper configuration
docker run -d -p 7860:7860 \
  --env-file .env \
  --name visolearn-2 \
  --restart unless-stopped \
  visolearn-2
```

## 🧪 Testing Setup

### Install Test Dependencies

```bash
# Install testing packages
pip install pytest pytest-cov pytest-mock
```

### Run Tests

```bash
# Run all tests
pytest tests/

# Run tests with coverage
pytest --cov=./ --cov-report=html tests/

# Run specific test module
pytest tests/test_image_generation.py

# Run tests with verbose output
pytest -v tests/
```

### Test Configuration

Create a `pytest.ini` file for test configuration:

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = --tb=short -v
```

## 📁 File Structure Setup

### Session Storage

```bash
# Create sessions directory
mkdir -p "Sessions History"

# Set proper permissions
chmod 755 "Sessions History"
```

### Static Files

```bash
# Create static files directory
mkdir -p static

# Copy static assets
cp -r static/templates static/
cp static/styles.css static/
```

## 🔧 Configuration Options

### Application Configuration

Edit `config.py` to customize application behavior:

```python
# Session timeout (minutes)
SESSION_TIMEOUT = 30

# Maximum session history
MAX_SESSION_HISTORY = 100

# Image generation settings
DEFAULT_IMAGE_SIZE = "1024x1024"
DEFAULT_IMAGE_STYLE = "cartoon"

# Analytics settings
ENABLE_ANALYTICS = True
ANALYTICS_INTERVAL = 60  # seconds
```

### Environment Variables

```bash
# Set environment variables (Linux/macOS)
export OPENAI_API_KEY="your_key_here"
export GOOGLE_API_KEY="your_key_here"
export DEBUG_MODE=True

# Set environment variables (Windows)
set OPENAI_API_KEY=your_key_here
set GOOGLE_API_KEY=your_key_here
set DEBUG_MODE=True
```

## 🌐 Network Configuration

### Firewall Settings

```bash
# Allow traffic on port 7860 (default)
sudo ufw allow 7860/tcp

# For production, you may need additional ports
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

### Reverse Proxy Setup (Nginx)

```nginx
server {
    listen 80;
    server_name visolearn.example.com;

    location / {
        proxy_pass http://localhost:7860;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## 📊 Monitoring Setup

### Logging Configuration

```python
# Configure logging in your application
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('visolearn.log'),
        logging.StreamHandler()
    ]
)
```

### Performance Monitoring

```bash
# Install monitoring tools
pip install psutil prometheus-client

# Add monitoring endpoints to your application
```

## 🔄 Update and Maintenance

### Updating Dependencies

```bash
# Update all Python packages
pip list --outdated
pip install --upgrade -r requirements.txt

# Update specific package
pip install --upgrade package-name
```

### Version Control

```bash
# Check current version
git tag

# Update to latest version
git pull origin main

# Check for changes
git status
```

## 🛡️ Security Configuration

### API Key Protection

```bash
# Add .env to .gitignore
echo ".env" >> .gitignore

# Set file permissions
chmod 600 .env
```

### SSL/TLS Configuration

```bash
# Generate self-signed certificate (development only)
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365

# Use with your application
python app.py --ssl-keyfile key.pem --ssl-certfile cert.pem
```

## 📚 Troubleshooting

### Common Installation Issues

**Python Version Issues:**
```bash
# Check Python version
python --version

# Install specific Python version
pyenv install 3.11.0
pyenv global 3.11.0
```

**Dependency Conflicts:**
```bash
# Create clean virtual environment
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**API Connection Problems:**
```bash
# Test API connectivity
curl https://api.openai.com/v1/models -H "Authorization: Bearer YOUR_API_KEY"

# Check network connectivity
ping api.openai.com
```

### Debugging Tips

```bash
# Run in debug mode
python app.py --debug

# Enable verbose logging
export LOG_LEVEL=DEBUG
python app.py

# Check logs
tail -f visolearn.log
```

## 🎯 Deployment Checklist

### Pre-Deployment Checklist

- [ ] All API keys configured
- [ ] Environment variables set correctly
- [ ] Dependencies installed
- [ ] Tests passing
- [ ] Configuration files updated
- [ ] Backup of existing data
- [ ] Monitoring configured
- [ ] Security settings verified

### Post-Deployment Checklist

- [ ] Application accessible
- [ ] API endpoints working
- [ ] Error logging functional
- [ ] Performance monitoring active
- [ ] Backup system verified
- [ ] Security audit completed

## 📈 Performance Optimization

### Caching Configuration

```python
# Configure caching in your application
from functools import lru_cache

@lru_cache(maxsize=128)
def cached_function(arg1, arg2):
    # Function implementation
    pass
```

### Database Optimization

```bash
# For SQLite databases
sqlite3 database.db "VACUUM;"
sqlite3 database.db "ANALYZE;"
```

## 🌍 Internationalization Setup

### Language Configuration

```python
# Configure supported languages
SUPPORTED_LANGUAGES = [
    'en',  # English
    'es',  # Spanish
    'fr',  # French
    'de',  # German
    'zh'   # Chinese
]
```

### Localization Files

```bash
# Create localization directory
mkdir -p locales

# Generate translation files
pybabel extract -o locales/messages.pot .
pybabel init -i locales/messages.pot -d locales -l es
```

## 📱 Mobile Configuration

### Responsive Design Testing

```bash
# Test responsive design
python app.py

# Open in browser and use device emulator
# Chrome: F12 > Device Toolbar
# Firefox: F12 > Responsive Design Mode
```

### Mobile-Specific Settings

```python
# Configure mobile-specific settings
MOBILE_SETTINGS = {
    'touch_target_size': '48px',
    'font_size': '16px',
    'button_size': 'large',
    'spacing': 'increased'
}
```

## 🤖 AI Model Configuration

### Model Selection

```python
# Configure AI model preferences
AI_MODEL_CONFIG = {
    'image_generation': {
        'primary': 'dall-e-3',
        'fallback': 'dall-e-2',
        'quality': 'hd'
    },
    'text_generation': {
        'primary': 'gpt-4',
        'fallback': 'gpt-3.5-turbo',
        'temperature': 0.7
    },
    'evaluation': {
        'primary': 'gemini-pro',
        'fallback': 'gpt-4',
        'strictness': 'moderate'
    }
}
```

### Model Performance Tuning

```python
# Optimize model parameters
MODEL_PARAMETERS = {
    'image_generation': {
        'size': '1024x1024',
        'quality': 'standard',
        'style': 'natural'
    },
    'text_generation': {
        'max_tokens': 500,
        'temperature': 0.7,
        'top_p': 1.0,
        'frequency_penalty': 0.5,
        'presence_penalty': 0.5
    }
}
```

## 📊 Analytics Configuration

### Data Collection Setup

```python
# Configure analytics collection
ANALYTICS_CONFIG = {
    'enabled': True,
    'interval': 60,  # seconds
    'retention_days': 30,
    'anonymize_data': True,
    'track_performance': True,
    'track_errors': True
}
```

### Reporting Configuration

```python
# Configure reporting options
REPORTING_CONFIG = {
    'daily_reports': True,
    'weekly_summary': True,
    'email_notifications': False,
    'dashboard_updates': True,
    'export_formats': ['pdf', 'csv', 'json']
}
```

## 🔒 Privacy Configuration

### Data Protection Settings

```python
# Configure privacy settings
PRIVACY_CONFIG = {
    'data_encryption': True,
    'anonymize_user_data': True,
    'retention_policy': '30_days',
    'gdpr_compliance': True,
    'coppa_compliance': True,
    'data_export_enabled': True
}
```

### Consent Management

```python
# Configure consent management
CONSENT_CONFIG = {
    'require_consent': True,
    'consent_expiry': '1_year',
    'consent_reminder': '30_days',
    'consent_logging': True,
    'consent_withdrawal': True
}
```

## 📚 Additional Resources

### Documentation Links
- **Official Documentation**: https://visolearn.org/docs
- **API Reference**: https://visolearn.org/api
- **Developer Guide**: https://visolearn.org/developers
- **Community Forum**: https://community.visolearn.org

### Support Channels
- **GitHub Issues**: https://github.com/visolearn/visolearn-2/issues
- **Email Support**: support@visolearn.org
- **Live Chat**: https://visolearn.org/support
- **Knowledge Base**: https://visolearn.org/help

### Learning Resources
- **Tutorials**: https://visolearn.org/tutorials
- **Video Guides**: https://visolearn.org/videos
- **Webinars**: https://visolearn.org/webinars
- **FAQ**: https://visolearn.org/faq

## 🎯 Next Steps

After completing the installation:

1. **Run the application**: `python app.py`
2. **Access the interface**: http://localhost:7860
3. **Explore features**: Try the image description and story modules
4. **Review documentation**: Check the user guide for detailed usage
5. **Join the community**: Connect with other users and developers

## 📞 Getting Help

If you encounter any issues during installation:

1. **Check the troubleshooting section** above
2. **Review the FAQ** for common questions
3. **Search the knowledge base** for solutions
4. **Ask in the community forum** for assistance
5. **Contact support** for urgent issues

This installation guide provides comprehensive instructions for setting up VisoLearn-2 in various environments. For specific configuration needs or advanced setups, refer to the technical documentation or contact our support team.