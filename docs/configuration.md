# ⚙️ Configuration and Settings Documentation

## 📋 Overview

This document provides comprehensive documentation for the configuration system, settings management, and application configuration in VisoLearn-2. It covers environment variables, configuration files, default values, and how the system manages different settings.

## 🏗️ Configuration Architecture

### Configuration Layers

```
VisoLearn-2 Configuration System
├── Environment Variables (highest priority)
├── .env Configuration File
├── config.py Settings
├── User Preferences
└── Default Values (lowest priority)
```

### Configuration Components

**Main Configuration File:** `config.py`
- API keys management
- System settings
- Default values
- Difficulty levels
- Image styles
- Session defaults

**Environment Configuration:** `.env`
- Secure API key storage
- Application settings
- Database configurations
- Debug modes

## 📁 Configuration Files

### Main Configuration (config.py)

```python
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API keys
HF_TOKEN = os.environ.get("HF_TOKEN")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
BFL_API_KEY = os.environ.get("BFL_API_KEY")

# Configure difficulty levels
DIFFICULTY_LEVELS = ["Very Simple", "Simple", Moderate", "Detailed", "Very Detailed"]

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
```

### Environment Configuration (.env)

```bash
# API Keys - Keep these secure!
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
HF_TOKEN=your_huggingface_token_here
BFL_API_KEY=your_blue_foundation_api_key_here

# Application Settings
DEBUG_MODE=False
SERVER_HOST=0.0.0.0
SERVER_PORT=7860

# Session Settings
MAX_SESSIONS=10
SESSION_TIMEOUT_MINUTES=30
IMAGE_CACHE_SIZE=100

# Google Drive Integration
GOOGLE_DRIVE_SYNC=True
GOOGLE_DRIVE_FOLDER_NAME=VisoLearn-Sessions
```

## 🔐 Security Configuration

### API Key Management

#### Secure Storage
```python
# config.py - Proper API key handling
import os
from dotenv import load_dotenv

load_dotenv()  # Load from .env file

class APIConfig:
    """Configuration for API keys and connections"""
    
    @staticmethod
    def get_openai_key():
        """Get OpenAI API key from environment"""
        key = os.environ.get("OPENAI_API_KEY")
        if not key:
            raise ValueError("OpenAI API key not found in environment variables")
        return key
    
    @staticmethod
    def get_google_key():
        """Get Google API key from environment"""
        key = os.environ.get("GOOGLE_API_KEY")
        if not key:
            raise ValueError("Google API key not found in environment variables")
        return key
    
    @staticmethod
    def get_all_keys():
        """Get all API keys safely"""
        return {
            'openai': os.environ.get("OPENAI_API_KEY"),
            'google': os.environ.get("GOOGLE_API_KEY"),
            'hf': os.environ.get("HF_TOKEN"),
            'bfl': os.environ.get("BFL_API_KEY")
        }
```

#### Environment Security
```python
# secure_config.py
import os
import logging
from pathlib import Path

def validate_environment_security():
    """
    Validate that the environment is properly configured and secure
    """
    issues = []
    
    # Check for required environment variables
    required_vars = ['OPENAI_API_KEY', 'GOOGLE_API_KEY']
    for var in required_vars:
        if not os.environ.get(var):
            issues.append(f"Missing required environment variable: {var}")
    
    # Check .env file permissions
    env_path = Path('.env')
    if env_path.exists():
        # On Unix systems, check file permissions
        if os.name != 'nt':  # Not Windows
            file_perms = env_path.stat().st_mode
            if file_perms & 0o007:  # Group or others have permissions
                issues.append(".env file has insecure permissions (others can read)")
    
    # Check for debug mode
    debug_mode = os.environ.get('DEBUG_MODE', 'False').lower() == 'true'
    if debug_mode:
        issues.append("DEBUG_MODE is enabled - turn off in production")
    
    return issues

def load_secure_config():
    """
    Load configuration with security validation
    """
    from dotenv import load_dotenv
    load_dotenv()  # Load environment variables
    
    security_issues = validate_environment_security()
    if security_issues:
        for issue in security_issues:
            logging.warning(f"Security Issue: {issue}")
    
    return True
```

## ⚙️ Application Settings

### System Configuration Manager

```python
import json
import os
from pathlib import Path
from typing import Any, Dict

class SystemConfig:
    """
    Manage system-wide application settings
    """
    
    def __init__(self, config_file="system_config.json"):
        self.config_file = Path(config_file)
        self.settings = self._load_settings()
    
    def _load_settings(self) -> Dict[str, Any]:
        """Load settings from file or use defaults"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        else:
            return self._get_default_settings()
    
    def _get_default_settings(self) -> Dict[str, Any]:
        """Get default system settings"""
        return {
            "app_name": "VisoLearn-2",
            "version": "2.0.0",
            "debug_mode": False,
            "log_level": "INFO",
            "session_timeout": 1800,  # 30 minutes in seconds
            "image_cache_size": 100,
            "max_concurrent_users": 10,
            "api_rate_limits": {
                "openai": 60,  # requests per minute
                "google": 1000,  # units per minute
                "image_generation": 10  # per minute
            },
            "ui_settings": {
                "theme": "default",
                "high_contrast_mode": False,
                "font_size": 16,
                "reduce_motion": False
            },
            "data_privacy": {
                "data_retention_days": 365,
                "anonymize_user_data": True,
                "allow_cloud_sync": True
            }
        }
    
    def get_setting(self, key: str, default: Any = None):
        """Get a specific setting value"""
        keys = key.split('.')
        value = self.settings
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set_setting(self, key: str, value: Any) -> bool:
        """Set a specific setting value"""
        keys = key.split('.')
        current = self.settings
        
        for k in keys[:-1]:
            if k not in current or not isinstance(current[k], dict):
                current[k] = {}
            current = current[k]
        
        current[keys[-1]] = value
        return self.save_settings()
    
    def save_settings(self) -> bool:
        """Save settings to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    def reset_to_defaults(self) -> bool:
        """Reset all settings to defaults"""
        self.settings = self._get_default_settings()
        return self.save_settings()
    
    def validate_settings(self) -> Dict[str, list]:
        """Validate settings and return any issues"""
        issues = {}
        
        # Validate ranges
        if not 1 <= self.get_setting("session_timeout", 1800) <= 7200:
            issues["session_timeout"] = ["Timeout must be between 1 and 120 minutes"]
        
        if not 1 <= self.get_setting("image_cache_size", 100) <= 1000:
            issues["image_cache_size"] = ["Cache size must be between 1 and 1000"]
        
        if not 1 <= self.get_setting("max_concurrent_users", 10) <= 100:
            issues["max_concurrent_users"] = ["Max users must be between 1 and 100"]
        
        return issues
```

### User Configuration

```python
import json
import os
from pathlib import Path
from typing import Any, Dict

class UserConfig:
    """
    Manage user-specific configuration settings
    """
    
    def __init__(self, user_id: str, base_dir: str = "user_configs"):
        self.user_id = user_id
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
        self.config_file = self.base_dir / f"{user_id}_config.json"
        self.settings = self._load_user_settings()
    
    def _load_user_settings(self) -> Dict[str, Any]:
        """Load user-specific settings from file or use defaults"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        else:
            return self._get_default_user_settings()
    
    def _get_default_user_settings(self) -> Dict[str, Any]:
        """Get default user settings"""
        return {
            "user_id": self.user_id,
            "preferences": {
                "difficulty_level": "Simple",
                "image_style": "Cartoon",
                "age": 5,
                "autism_level": "Level 1",
                "treatment_plan": "Default Plan",
                "topic_focus": "General"
            },
            "ui_settings": {
                "theme": "default",
                "high_contrast": False,
                "font_size": 16,
                "reduce_motion": False
            },
            "notification_settings": {
                "email": True,
                "progress_reports": True,
                "achievement_alerts": True
            },
            "privacy_settings": {
                "data_sharing": False,
                "cloud_sync": True,
                "analytics": True
            }
        }
    
    def get_preference(self, key: str, default: Any = None):
        """Get a user preference value"""
        keys = key.split('.')
        value = self.settings.get('preferences', {})
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set_preference(self, key: str, value: Any) -> bool:
        """Set a user preference"""
        if 'preferences' not in self.settings:
            self.settings['preferences'] = {}
        
        keys = key.split('.')
        current = self.settings['preferences']
        
        for k in keys[:-1]:
            if k not in current or not isinstance(current[k], dict):
                current[k] = {}
            current = current[k]
        
        current[keys[-1]] = value
        return self.save_settings()
    
    def update_preferences(self, preferences: Dict[str, Any]) -> bool:
        """Update multiple preferences at once"""
        if 'preferences' not in self.settings:
            self.settings['preferences'] = {}
        
        self.settings['preferences'].update(preferences)
        return self.save_settings()
    
    def save_settings(self) -> bool:
        """Save user settings to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving user settings: {e}")
            return False
    
    def reset_preferences(self) -> bool:
        """Reset user preferences to defaults"""
        self.settings['preferences'] = self._get_default_user_settings()['preferences']
        return self.save_settings()
```

## 🎨 UI Configuration

### Theme and Display Settings

```python
class ThemeConfig:
    """
    Manage UI theme and display configuration
    """
    
    # Default theme configurations
    THEMES = {
        "default": {
            "primary_color": "#4F8BF9",
            "secondary_color": "#5ECC62",
            "background_color": "#F8FAFC",
            "text_color": "#1E293B",
            "accent_color": "#F59E0B",
            "border_radius": "8px",
            "font_family": "Open Sans, sans-serif",
            "font_size_base": "16px"
        },
        "high_contrast": {
            "primary_color": "#000000",
            "secondary_color": "#FFFFFF",
            "background_color": "#FFFFFF",
            "text_color": "#000000",
            "accent_color": "#FF0000",
            "border_radius": "4px",
            "font_family": "Arial, sans-serif",
            "font_size_base": "18px"
        },
        "dyslexic_friendly": {
            "primary_color": "#4A90E2",
            "secondary_color": "#7ED321",
            "background_color": "#F6F6F6",
            "text_color": "#333333",
            "accent_color": "#F5A623",
            "border_radius": "6px",
            "font_family": "OpenDyslexic, Arial, sans-serif",
            "font_size_base": "17px"
        }
    }
    
    def __init__(self):
        self.current_theme = "default"
    
    def get_theme_config(self, theme_name: str = None) -> Dict[str, str]:
        """Get theme configuration"""
        theme = theme_name or self.current_theme
        return self.THEMES.get(theme, self.THEMES["default"])
    
    def set_theme(self, theme_name: str) -> bool:
        """Set the current theme"""
        if theme_name in self.THEMES:
            self.current_theme = theme_name
            return True
        return False
    
    def generate_css_variables(self, theme_name: str = None) -> str:
        """Generate CSS variables for the theme"""
        theme = self.get_theme_config(theme_name)
        
        css_vars = []
        for key, value in theme.items():
            css_key = key.replace('_', '-')
            css_vars.append(f"  --{css_key}: {value};")
        
        return ":root {\n" + "\n".join(css_vars) + "\n}"
    
    def validate_theme(self, theme_name: str) -> bool:
        """Validate if theme exists"""
        return theme_name in self.THEMES
    
    def get_available_themes(self) -> list:
        """Get list of available themes"""
        return list(self.THEMES.keys())
```

### Accessibility Configuration

```python
class AccessibilityConfig:
    """
    Manage accessibility settings for users with autism
    """
    
    def __init__(self):
        self.settings = {
            "high_contrast_mode": False,
            "reduce_motion": False,
            "screen_reader_friendly": True,
            "font_enlargement": 1.0,  # Multiplier
            "color_filter": "none",  # none, protanopia, deuteranopia, tritanopia
            "input_delay": 0,  # milliseconds for input processing delay
            "visual_feedback": True,
            "audio_feedback": False,
            "simplified_ui": False
        }
    
    def get_accessibility_settings(self) -> Dict[str, Any]:
        """Get current accessibility settings"""
        return self.settings.copy()
    
    def update_accessibility_settings(self, new_settings: Dict[str, Any]) -> bool:
        """Update accessibility settings"""
        valid_keys = set(self.settings.keys())
        for key, value in new_settings.items():
            if key in valid_keys:
                # Validate values where needed
                if key == "font_enlargement":
                    if isinstance(value, (int, float)) and 0.5 <= value <= 3.0:
                        self.settings[key] = value
                    else:
                        return False
                elif key == "input_delay":
                    if isinstance(value, int) and 0 <= value <= 5000:
                        self.settings[key] = value
                    else:
                        return False
                else:
                    self.settings[key] = value
        
        return True
    
    def get_css_accessibility_rules(self) -> str:
        """Generate CSS rules for accessibility features"""
        rules = []
        
        if self.settings["high_contrast_mode"]:
            rules.append("""
            * {
                background-color: white !important;
                color: black !important;
                border: 2px solid black !important;
            }
            """)
        
        if self.settings["reduce_motion"]:
            rules.append("""
            * {
                animation-duration: 0.01ms !important;
                animation-iteration-count: 1 !important;
                transition-duration: 0.01ms !important;
            }
            """)
        
        if self.settings["font_enlargement"] != 1.0:
            multiplier = self.settings["font_enlargement"]
            rules.append(f"""
            body {{
                font-size: calc(16px * {multiplier}) !important;
                line-height: calc(1.5 * {multiplier}) !important;
            }}
            """)
        
        if self.settings["simplified_ui"]:
            rules.append("""
            .complex-element, .advanced-feature {
                display: none !important;
            }
            """)
        
        return "\n".join(rules)
```

## 🌐 API Configuration

### API Connection Settings

```python
import time
from typing import Dict, Any

class APIConfig:
    """
    Manage API connection settings and configurations
    """
    
    def __init__(self):
        self.settings = {
            "openai": {
                "api_key": None,
                "base_url": "https://api.openai.com/v1",
                "model": "gpt-4-vision-preview",
                "image_model": "dall-e-3",
                "temperature": 0.7,
                "max_tokens": 1000,
                "timeout": 30,
                "retry_attempts": 3,
                "rate_limit": 60  # requests per minute
            },
            "google": {
                "api_key": None,
                "base_url": "https://generativelanguage.googleapis.com/v1beta",
                "model": "gemini-pro",
                "timeout": 30,
                "retry_attempts": 3,
                "rate_limit": 1000  # units per minute
            },
            "huggingface": {
                "api_key": None,
                "api_url": "https://api-inference.huggingface.co/models",
                "timeout": 60,
                "retry_attempts": 2
            }
        }
    
    def load_from_env(self):
        """Load API keys from environment variables"""
        import os
        self.settings["openai"]["api_key"] = os.environ.get("OPENAI_API_KEY")
        self.settings["google"]["api_key"] = os.environ.get("GOOGLE_API_KEY")
        self.settings["huggingface"]["api_key"] = os.environ.get("HF_TOKEN")
    
    def validate_api_configs(self) -> Dict[str, list]:
        """Validate API configurations and return issues"""
        issues = {}
        
        for api_name, config in self.settings.items():
            api_issues = []
            
            # Check if API key is provided
            if not config.get("api_key"):
                api_issues.append("API key is not configured")
            
            # Validate rate limits
            rate_limit = config.get("rate_limit", 0)
            if rate_limit <= 0:
                api_issues.append("Rate limit must be positive")
            
            # Validate timeouts
            timeout = config.get("timeout", 0)
            if not (1 <= timeout <= 300):
                api_issues.append("Timeout should be between 1 and 300 seconds")
            
            # Validate retry attempts
            retries = config.get("retry_attempts", 0)
            if not (0 <= retries <= 10):
                api_issues.append("Retry attempts should be between 0 and 10")
            
            if api_issues:
                issues[api_name] = api_issues
        
        return issues
    
    def get_api_config(self, api_name: str) -> Dict[str, Any]:
        """Get configuration for a specific API"""
        if api_name in self.settings:
            return self.settings[api_name].copy()
        else:
            raise ValueError(f"Unknown API: {api_name}")
    
    def update_api_config(self, api_name: str, updates: Dict[str, Any]) -> bool:
        """Update configuration for a specific API"""
        if api_name not in self.settings:
            return False
        
        # Validate updates before applying
        for key, value in updates.items():
            if key in self.settings[api_name]:
                self.settings[api_name][key] = value
        
        return True
```

## 📊 Performance Configuration

### Performance Settings

```python
class PerformanceConfig:
    """
    Manage performance-related configuration settings
    """
    
    def __init__(self):
        self.settings = {
            "caching": {
                "enable_image_cache": True,
                "image_cache_size": 50,
                "text_cache_size": 100,
                "session_cache_size": 25,
                "cache_ttl_seconds": 3600  # 1 hour
            },
            "processing": {
                "max_image_processes": 4,
                "max_text_processes": 2,
                "batch_size": 10,
                "concurrent_requests": 5
            },
            "memory": {
                "max_memory_usage_mb": 1024,
                "gc_threshold_multiplier": 1.5,
                "memory_cleanup_interval": 300  # 5 minutes
            },
            "network": {
                "connection_timeout": 30,
                "read_timeout": 60,
                "max_retries": 3,
                "backoff_factor": 1.0
            }
        }
    
    def get_performance_setting(self, category: str, setting: str, default=None):
        """Get a specific performance setting"""
        if category in self.settings and setting in self.settings[category]:
            return self.settings[category][setting]
        return default
    
    def set_performance_setting(self, category: str, setting: str, value) -> bool:
        """Set a specific performance setting"""
        if category in self.settings and setting in self.settings[category]:
            self.settings[category][setting] = value
            return True
        return False
    
    def get_optimal_config_for_hardware(self, cpu_cores: int = 4, memory_gb: int = 8) -> Dict:
        """Get performance configuration optimized for hardware"""
        optimal_config = {}
        
        # Adjust based on CPU cores
        optimal_config["max_image_processes"] = min(cpu_cores, 8)
        optimal_config["max_text_processes"] = min(max(1, cpu_cores // 2), 4)
        optimal_config["concurrent_requests"] = min(cpu_cores * 2, 10)
        
        # Adjust based on memory
        optimal_config["image_cache_size"] = min(memory_gb * 10, 100)
        optimal_config["text_cache_size"] = min(memory_gb * 20, 200)
        optimal_config["max_memory_usage_mb"] = int(memory_gb * 1024 * 0.8)  # 80% of total memory
        
        return optimal_config
    
    def validate_performance_settings(self) -> Dict[str, list]:
        """Validate performance settings and return issues"""
        issues = {}
        
        cache_settings = self.settings["caching"]
        if cache_settings["image_cache_size"] < 1 or cache_settings["image_cache_size"] > 1000:
            issues["image_cache_size"] = ["Image cache size must be between 1 and 1000"]
        
        processing_settings = self.settings["processing"]
        if processing_settings["max_image_processes"] < 1 or processing_settings["max_image_processes"] > 16:
            issues["max_image_processes"] = ["Max image processes must be between 1 and 16"]
        
        memory_settings = self.settings["memory"]
        if memory_settings["max_memory_usage_mb"] < 128:
            issues["max_memory_usage_mb"] = ["Max memory usage should be at least 128 MB"]
        
        return issues
```

## 🔧 Configuration Management Utilities

### Configuration Validator

```python
import re
from typing import Dict, List

class ConfigValidator:
    """
    Validate configuration settings and provide feedback
    """
    
    @staticmethod
    def validate_api_key(api_key: str, provider: str) -> List[str]:
        """Validate API key format for different providers"""
        issues = []
        
        if not api_key:
            issues.append("API key is required")
            return issues
        
        if provider == "openai":
            # OpenAI keys typically start with "sk-"
            if not api_key.startswith("sk-"):
                issues.append("OpenAI API key should start with 'sk-'")
            if len(api_key) < 20:
                issues.append("OpenAI API key appears too short")
        
        elif provider == "google":
            # Google API keys don't have a specific format, but should be long enough
            if len(api_key) < 20:
                issues.append("Google API key appears too short")
        
        elif provider == "huggingface":
            # Hugging Face tokens typically start with "hf_"
            if not api_key.startswith("hf_"):
                issues.append("Hugging Face token should start with 'hf_'")
        
        return issues
    
    @staticmethod
    def validate_email(email: str) -> List[str]:
        """Validate email format"""
        issues = []
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            issues.append("Invalid email format")
        return issues
    
    @staticmethod
    def validate_url(url: str) -> List[str]:
        """Validate URL format"""
        issues = []
        pattern = r'^https?://(?:[-\w.])+(?:\:[0-9]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?)?$'
        if not re.match(pattern, url):
            issues.append("Invalid URL format")
        return issues
    
    @staticmethod
    def validate_file_path(path: str) -> List[str]:
        """Validate file path"""
        import os
        issues = []
        
        # Check for potentially dangerous patterns
        dangerous_patterns = ['..', '/etc', '/proc', '/sys', 'C:\\Windows']
        for pattern in dangerous_patterns:
            if pattern in path:
                issues.append(f"Potentially dangerous path pattern detected: {pattern}")
        
        return issues
    
    @staticmethod
    def validate_numeric_range(value: float, min_val: float, max_val: float, name: str) -> List[str]:
        """Validate that a numeric value is within a range"""
        issues = []
        if not (min_val <= value <= max_val):
            issues.append(f"{name} must be between {min_val} and {max_val}")
        return issues
```

### Configuration Updater

```python
import json
import os
from pathlib import Path
from typing import Any, Dict

class ConfigUpdater:
    """
    Handle configuration updates and migrations
    """
    
    def __init__(self, config_dir: str = "."):
        self.config_dir = Path(config_dir)
    
    def migrate_config(self, old_config_path: str, new_config_path: str) -> bool:
        """
        Migrate configuration from old format to new format
        """
        try:
            with open(old_config_path, 'r') as f:
                old_config = json.load(f)
            
            # Convert old config format to new format
            new_config = self._convert_old_to_new_format(old_config)
            
            # Save new config
            with open(new_config_path, 'w') as f:
                json.dump(new_config, f, indent=2)
            
            # Backup old config
            backup_path = old_config_path + ".backup"
            os.rename(old_config_path, backup_path)
            
            return True
        except Exception as e:
            print(f"Error migrating config: {e}")
            return False
    
    def _convert_old_to_new_format(self, old_config: Dict[str, Any]) -> Dict[str, Any]:
        """Convert old configuration format to new format"""
        new_config = {
            "version": "2.0",
            "timestamp": str(old_config.get("timestamp", "")),
            "system": {},
            "user": {},
            "api": {},
            "ui": {}
        }
        
        # Map old keys to new structure
        for key, value in old_config.items():
            if key in ['api_key', 'openai_key', 'google_key']:
                new_config["api"][key] = value
            elif key in ['theme', 'font_size', 'high_contrast']:
                new_config["ui"][key] = value
            else:
                new_config["system"][key] = value
        
        return new_config
    
    def backup_config(self, config_path: str) -> bool:
        """Create a backup of the configuration file"""
        try:
            import shutil
            from datetime import datetime
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"{config_path}.backup_{timestamp}"
            
            shutil.copy2(config_path, backup_path)
            return True
        except Exception as e:
            print(f"Error creating backup: {e}")
            return False
    
    def restore_config(self, backup_path: str, config_path: str) -> bool:
        """Restore configuration from backup"""
        try:
            import shutil
            shutil.copy2(backup_path, config_path)
            return True
        except Exception as e:
            print(f"Error restoring config: {e}")
            return False
```

## 🚀 Configuration Best Practices

### Secure Configuration Loading

```python
def load_secure_configuration():
    """
    Load configuration with security best practices
    """
    import os
    from dotenv import load_dotenv
    
    # 1. Load environment variables
    load_dotenv()
    
    # 2. Validate environment security
    from config_validator import validate_environment_security
    security_issues = validate_environment_security()
    
    if security_issues:
        print("Security warnings:")
        for issue in security_issues:
            print(f"  - {issue}")
    
    # 3. Load main configuration
    from system_config import SystemConfig
    system_config = SystemConfig()
    
    # 4. Load API configuration
    from api_config import APIConfig
    api_config = APIConfig()
    api_config.load_from_env()
    
    # 5. Validate all configurations
    config_issues = system_config.validate_settings()
    api_issues = api_config.validate_api_configs()
    
    if config_issues:
        print("Configuration issues:")
        for key, issues in config_issues.items():
            for issue in issues:
                print(f"  - {key}: {issue}")
    
    if api_issues:
        print("API configuration issues:")
        for api_name, issues in api_issues.items():
            for issue in issues:
                print(f"  - {api_name}: {issue}")
    
    return {
        "system": system_config,
        "api": api_config,
        "security_issues": security_issues,
        "config_issues": config_issues,
        "api_issues": api_issues
    }
```

## 📞 Troubleshooting Configuration Issues

### Common Configuration Problems

**API Key Issues:**
- Keys not loaded from environment variables
- Incorrect key formats
- Insufficient permissions

**Performance Issues:**
- Incorrect cache sizes
- Too many concurrent processes
- Memory limits too restrictive

**Security Issues:**
- Insecure file permissions
- Debug mode enabled in production
- Unencrypted sensitive data

### Configuration Testing

```python
def test_configuration():
    """
    Test configuration settings to ensure everything is working properly
    """
    print("Testing Configuration...")
    
    # Test environment loading
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    print("✓ Environment variables loaded")
    
    # Test API key availability
    openai_key = os.environ.get("OPENAI_API_KEY")
    google_key = os.environ.get("GOOGLE_API_KEY")
    
    if not openai_key:
        print("⚠️  OpenAI API key not found")
    else:
        print("✓ OpenAI API key found")
    
    if not google_key:
        print("⚠️  Google API key not found")
    else:
        print("✓ Google API key found")
    
    # Test file permissions
    import stat
    env_file = Path(".env")
    if env_file.exists():
        perms = env_file.stat().st_mode
        if os.name != 'nt':  # Not Windows
            if perms & stat.S_IRWXO:  # Others have permissions
                print("⚠️  .env file has insecure permissions")
            else:
                print("✓ .env file permissions are secure")
    
    print("Configuration test complete!")

# Run the test
if __name__ == "__main__":
    test_configuration()
```

## 📚 Additional Resources

**Configuration Management:**
- Python-dotenv documentation
- Environment variable best practices
- Configuration validation techniques

**Security:**
- OWASP secure configuration guidelines
- API key security best practices
- Environment hardening techniques

**Performance:**
- Configuration optimization strategies
- Resource allocation best practices
- Caching strategies