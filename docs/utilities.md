# ⚙️ Utility Functions Documentation

## 📋 Overview

This document provides comprehensive documentation for the utility functions, helper modules, and common services used throughout the VisoLearn-2 platform. These utilities handle file operations, state management, data processing, and other essential system functions.

## 🏗️ Utility Architecture

### Core Utility Components

```
VisoLearn-2 Utilities
├── File Operations
│   ├── Session Management
│   ├── Image Handling
│   ├── Data Serialization
│   └── Export/Import Functions
├── State Management
│   ├── Session State
│   ├── User Preferences
│   ├── Application Settings
│   └── Temporary Data
├── Data Processing
│   ├── Analytics Processing
│   ├── User Input Validation
│   ├── Data Transformation
│   └── Format Conversion
├── System Services
│   ├── Logging
│   ├── Error Handling
│   ├── Performance Monitoring
│   └── Security Functions
└── Visualization Tools
    ├── Chart Generation
    ├── Progress Visualization
    ├── Data Display
    └── Interactive Components
```

## 📁 File Operations

### Session Management

#### Session File Structure

The system organizes session data in a structured directory format:

```
Sessions History/
├── {session_id}/
│   ├── metadata.json
│   ├── user_data.json
│   ├── images/
│   │   ├── original/
│   │   ├── processed/
│   │   └── thumbnails/
│   ├── analytics/
│   │   ├── progress.json
│   │   ├── evaluation.json
│   │   └── feedback.json
│   ├── exports/
│   │   ├── pdf_reports/
│   │   ├── csv_data/
│   │   └── json_snapshots/
│   └── temp/
│       ├── cache/
│       └── work/
└── session_index.json (main index file)
```

#### Session Manager Class

```python
import json
import os
import shutil
from datetime import datetime
from pathlib import Path
import uuid

class SessionManager:
    """
    Manages session creation, saving, loading, and organization
    """
    
    def __init__(self, base_path="Sessions History"):
        self.base_path = Path(base_path)
        self.index_file = self.base_path / "session_index.json"
        self._ensure_base_directory()
        self._load_or_create_index()
    
    def _ensure_base_directory(self):
        """Create base session directory if it doesn't exist"""
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def _load_or_create_index(self):
        """Load session index or create new one if missing"""
        if self.index_file.exists():
            with open(self.index_file, 'r') as f:
                self.session_index = json.load(f)
        else:
            self.session_index = {
                "sessions": [],
                "created_at": datetime.now().isoformat(),
                "version": "1.0"
            }
    
    def create_session(self, user_profile, session_type="image_description"):
        """
        Create a new session with unique ID and proper structure
        
        Args:
            user_profile (dict): User profile information
            session_type (str): Type of session (image_description, comic_story, etc.)
        
        Returns:
            dict: Session information with ID and paths
        """
        session_id = str(uuid.uuid4())
        session_path = self.base_path / session_id
        
        # Create session directory structure
        session_path.mkdir(parents=True, exist_ok=True)
        (session_path / "images").mkdir(exist_ok=True)
        (session_path / "images" / "original").mkdir(exist_ok=True)
        (session_path / "images" / "processed").mkdir(exist_ok=True)
        (session_path / "images" / "thumbnails").mkdir(exist_ok=True)
        (session_path / "analytics").mkdir(exist_ok=True)
        (session_path / "exports").mkdir(exist_ok=True)
        (session_path / "temp").mkdir(exist_ok=True)
        (session_path / "temp" / "cache").mkdir(exist_ok=True)
        (session_path / "temp" / "work").mkdir(exist_ok=True)
        
        # Create initial metadata
        metadata = {
            "session_id": session_id,
            "session_type": session_type,
            "start_time": datetime.now().isoformat(),
            "user_profile": user_profile,
            "status": "active",
            "progress": 0,
            "completed_activities": 0,
            "total_activities": 0
        }
        
        # Save metadata
        metadata_path = session_path / "metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Add to index
        self.session_index["sessions"].append({
            "id": session_id,
            "type": session_type,
            "start_time": metadata["start_time"],
            "user": user_profile.get("name", "Unknown"),
            "path": str(session_path),
            "status": "active"
        })
        
        # Save updated index
        self._save_index()
        
        return metadata
    
    def load_session(self, session_id):
        """
        Load session data from file system
        
        Args:
            session_id (str): Unique session identifier
        
        Returns:
            dict: Session data or None if not found
        """
        session_path = self.base_path / session_id
        
        if not session_path.exists():
            return None
        
        metadata_path = session_path / "metadata.json"
        if metadata_path.exists():
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
        else:
            return None
        
        # Load additional session data
        user_data_path = session_path / "user_data.json"
        if user_data_path.exists():
            with open(user_data_path, 'r') as f:
                user_data = json.load(f)
            metadata["user_data"] = user_data
        
        return metadata
    
    def save_session_data(self, session_id, data_type, data, format="json"):
        """
        Save session-specific data to the appropriate location
        
        Args:
            session_id (str): Session identifier
            data_type (str): Type of data (metadata, analytics, user_data, etc.)
            data (dict/list): Data to save
            format (str): Format to save in (json, csv, etc.)
        
        Returns:
            bool: Success status
        """
        session_path = self.base_path / session_id
        
        if not session_path.exists():
            return False
        
        if format == "json":
            file_path = session_path / f"{data_type}.json"
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            return True
        elif format == "csv":
            import csv
            file_path = session_path / f"{data_type}.csv"
            if isinstance(data, list) and len(data) > 0:
                with open(file_path, 'w', newline='') as f:
                    if isinstance(data[0], dict):
                        writer = csv.DictWriter(f, fieldnames=data[0].keys())
                        writer.writeheader()
                        writer.writerows(data)
                    else:
                        writer = csv.writer(f)
                        writer.writerows(data)
            return True
        
        return False
    
    def get_session_analytics(self, session_id):
        """
        Get analytics data for a specific session
        
        Args:
            session_id (str): Session identifier
        
        Returns:
            dict: Analytics data
        """
        session_path = self.base_path / session_id
        analytics_path = session_path / "analytics"
        
        analytics_data = {}
        
        if analytics_path.exists():
            for analytics_file in analytics_path.glob("*.json"):
                with open(analytics_file, 'r') as f:
                    key = analytics_file.stem
                    analytics_data[key] = json.load(f)
        
        return analytics_data
    
    def update_session_progress(self, session_id, progress_data):
        """
        Update session progress and metadata
        
        Args:
            session_id (str): Session identifier
            progress_data (dict): Progress information
        
        Returns:
            bool: Success status
        """
        session_path = self.base_path / session_id
        metadata_path = session_path / "metadata.json"
        
        if not metadata_path.exists():
            return False
        
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        # Update progress information
        metadata.update({
            "progress": progress_data.get("progress", metadata.get("progress", 0)),
            "completed_activities": progress_data.get("completed", metadata.get("completed_activities", 0)),
            "total_activities": progress_data.get("total", metadata.get("total_activities", 0)),
            "last_updated": datetime.now().isoformat()
        })
        
        # Update session status if complete
        if metadata["completed_activities"] >= metadata["total_activities"]:
            metadata["status"] = "completed"
        
        # Save updated metadata
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return True
    
    def export_session(self, session_id, export_format="zip", destination_path=None):
        """
        Export session data in specified format
        
        Args:
            session_id (str): Session identifier
            export_format (str): Export format (zip, json, csv, pdf)
            destination_path (str): Destination path for export
        
        Returns:
            str: Path to exported file
        """
        session_path = self.base_path / session_id
        
        if not session_path.exists():
            return None
        
        if export_format == "zip":
            import zipfile
            destination = destination_path or f"session_{session_id}_export.zip"
            with zipfile.ZipFile(destination, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(session_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, self.base_path.parent)
                        zipf.write(file_path, arcname)
            return destination
        
        elif export_format == "json":
            # Combine all session data into a single JSON file
            all_data = {}
            for json_file in session_path.rglob("*.json"):
                relative_path = json_file.relative_to(session_path)
                key = str(relative_path).replace(os.sep, "_").replace(".json", "")
                with open(json_file, 'r') as f:
                    all_data[key] = json.load(f)
            
            destination = destination_path or f"session_{session_id}_export.json"
            with open(destination, 'w') as f:
                json.dump(all_data, f, indent=2, default=str)
            return destination
        
        return None
    
    def _save_index(self):
        """Save the session index to file"""
        with open(self.index_file, 'w') as f:
            json.dump(self.session_index, f, indent=2)
    
    def list_sessions(self, user_filter=None, type_filter=None, status_filter=None):
        """
        List sessions with optional filters
        
        Args:
            user_filter (str): Filter by user name
            type_filter (str): Filter by session type
            status_filter (str): Filter by session status
        
        Returns:
            list: Filtered list of sessions
        """
        sessions = self.session_index["sessions"]
        
        if user_filter:
            sessions = [s for s in sessions if user_filter.lower() in s["user"].lower()]
        
        if type_filter:
            sessions = [s for s in sessions if s["type"] == type_filter]
        
        if status_filter:
            sessions = [s for s in sessions if s["status"] == status_filter]
        
        return sessions
```

### Image File Handling

```python
from PIL import Image
import base64
import io
import os
from pathlib import Path

class ImageFileManager:
    """
    Handle image file operations including loading, saving, 
    conversion, and format management
    """
    
    SUPPORTED_FORMATS = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp'}
    DEFAULT_QUALITY = 95
    THUMBNAIL_SIZE = (150, 150)
    
    def __init__(self, session_manager):
        self.session_manager = session_manager
    
    def save_image_from_base64(self, image_base64, session_id, filename, subfolder="original"):
        """
        Save a base64-encoded image to the session directory
        
        Args:
            image_base64 (str): Base64-encoded image data
            session_id (str): Session identifier
            filename (str): Filename to save as
            subfolder (str): Subfolder within images directory
        
        Returns:
            str: Path to saved image file
        """
        # Decode base64 image data
        image_data = base64.b64decode(image_base64)
        image = Image.open(io.BytesIO(image_data))
        
        # Create session image path
        session_path = Path(self.session_manager.base_path) / session_id / "images" / subfolder
        session_path.mkdir(parents=True, exist_ok=True)
        
        # Determine file extension from image format
        file_extension = Path(filename).suffix.lower()
        if not file_extension or file_extension not in self.SUPPORTED_FORMATS:
            file_extension = '.png'  # Default to PNG
        
        file_path = session_path / f"{Path(filename).stem}{file_extension}"
        
        # Save image
        image.save(file_path, quality=self.DEFAULT_QUALITY)
        
        return str(file_path)
    
    def save_pil_image(self, pil_image, session_id, filename, subfolder="original", quality=None):
        """
        Save a PIL Image object to the session directory
        
        Args:
            pil_image (PIL.Image): PIL Image object to save
            session_id (str): Session identifier
            filename (str): Filename to save as
            subfolder (str): Subfolder within images directory
            quality (int): JPEG quality (1-100)
        
        Returns:
            str: Path to saved image file
        """
        session_path = Path(self.session_manager.base_path) / session_id / "images" / subfolder
        session_path.mkdir(parents=True, exist_ok=True)
        
        file_path = session_path / filename
        
        # Save with appropriate settings based on format
        if file_path.suffix.lower() in ['.jpg', '.jpeg']:
            pil_image.save(file_path, quality=quality or self.DEFAULT_QUALITY, optimize=True)
        else:
            pil_image.save(file_path)
        
        return str(file_path)
    
    def create_thumbnail(self, image_path, session_id, thumbnail_name=None):
        """
        Create a thumbnail for an image
        
        Args:
            image_path (str): Path to original image
            session_id (str): Session identifier
            thumbnail_name (str): Name for thumbnail (optional)
        
        Returns:
            str: Path to thumbnail file
        """
        try:
            with Image.open(image_path) as img:
                img.thumbnail(self.THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
                
                # Create thumbnail name if not provided
                if not thumbnail_name:
                    original_path = Path(image_path)
                    thumbnail_name = f"thumb_{original_path.stem}{original_path.suffix}"
                
                # Save thumbnail
                thumbnail_path = Path(self.session_manager.base_path) / session_id / "images" / "thumbnails"
                thumbnail_path.mkdir(parents=True, exist_ok=True)
                
                full_thumbnail_path = thumbnail_path / thumbnail_name
                img.save(full_thumbnail_path, optimize=True)
                
                return str(full_thumbnail_path)
        except Exception as e:
            print(f"Error creating thumbnail: {e}")
            return None
    
    def get_image_info(self, image_path):
        """
        Get information about an image file
        
        Args:
            image_path (str): Path to image file
        
        Returns:
            dict: Image information
        """
        try:
            with Image.open(image_path) as img:
                return {
                    "width": img.width,
                    "height": img.height,
                    "format": img.format,
                    "mode": img.mode,
                    "size_bytes": Path(image_path).stat().st_size
                }
        except Exception as e:
            print(f"Error getting image info: {e}")
            return None
    
    def validate_image_file(self, image_path):
        """
        Validate that an image file is properly formatted and readable
        
        Args:
            image_path (str): Path to image file
        
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            with Image.open(image_path) as img:
                # Try to load and verify the image
                img.verify()
            return True
        except Exception:
            try:
                # If verify fails, try to open again (some formats need this)
                with Image.open(image_path) as img:
                    # Verify dimensions are reasonable
                    if img.width > 0 and img.height > 0:
                        return True
            except Exception:
                pass
            return False
    
    def convert_image_format(self, image_path, new_format, session_id, subfolder="processed"):
        """
        Convert an image to a different format
        
        Args:
            image_path (str): Path to source image
            new_format (str): Target format (png, jpg, etc.)
            session_id (str): Session identifier
            subfolder (str): Subfolder for converted image
        
        Returns:
            str: Path to converted image file
        """
        try:
            with Image.open(image_path) as img:
                session_path = Path(self.session_manager.base_path) / session_id / "images" / subfolder
                session_path.mkdir(parents=True, exist_ok=True)
                
                original_stem = Path(image_path).stem
                new_path = session_path / f"{original_stem}.{new_format.lower()}"
                
                # Convert and save
                if new_format.lower() in ['jpg', 'jpeg']:
                    if img.mode in ('RGBA', 'LA', 'P'):
                        # Convert to RGB if necessary for JPEG
                        img = img.convert('RGB')
                    img.save(new_path, quality=self.DEFAULT_QUALITY)
                else:
                    img.save(new_path)
                
                return str(new_path)
        except Exception as e:
            print(f"Error converting image: {e}")
            return None
```

### Data Serialization and Management

```python
import json
import csv
import pickle
from typing import Dict, List, Any, Optional

class DataManager:
    """
    Handle data serialization, deserialization, and format conversion
    """
    
    def __init__(self):
        self.supported_formats = {'json', 'csv', 'pickle', 'txt'}
    
    def save_data(self, data: Any, filepath: str, format_type: str = 'json'):
        """
        Save data to file in specified format
        
        Args:
            data: Data to save (dict, list, etc.)
            filepath (str): Output file path
            format_type (str): Format to save in (json, csv, pickle)
        
        Returns:
            bool: Success status
        """
        try:
            if format_type.lower() == 'json':
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, default=str, ensure_ascii=False)
            elif format_type.lower() == 'csv':
                self._save_csv(data, filepath)
            elif format_type.lower() == 'pickle':
                with open(filepath, 'wb') as f:
                    pickle.dump(data, f)
            elif format_type.lower() == 'txt':
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(str(data))
            else:
                raise ValueError(f"Unsupported format: {format_type}")
            
            return True
        except Exception as e:
            print(f"Error saving data: {e}")
            return False
    
    def load_data(self, filepath: str, format_type: str = 'json'):
        """
        Load data from file
        
        Args:
            filepath (str): Input file path
            format_type (str): Format of the file (json, csv, pickle)
        
        Returns:
            Loaded data or None if error
        """
        try:
            if format_type.lower() == 'json':
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            elif format_type.lower() == 'csv':
                return self._load_csv(filepath)
            elif format_type.lower() == 'pickle':
                with open(filepath, 'rb') as f:
                    return pickle.load(f)
            elif format_type.lower() == 'txt':
                with open(filepath, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                raise ValueError(f"Unsupported format: {format_type}")
        except Exception as e:
            print(f"Error loading data: {e}")
            return None
    
    def _save_csv(self, data: Any, filepath: str):
        """Helper method to save data as CSV"""
        if isinstance(data, list) and len(data) > 0:
            if isinstance(data[0], dict):
                # List of dictionaries
                with open(filepath, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
            else:
                # List of lists
                with open(filepath, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerows(data)
        elif isinstance(data, dict):
            # Single dictionary - convert to list for CSV
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=data.keys())
                writer.writeheader()
                writer.writerow(data)
    
    def _load_csv(self, filepath: str) -> List[Dict]:
        """Helper method to load CSV data"""
        data = []
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(dict(row))
        return data
    
    def validate_data_structure(self, data: Any, expected_type: str) -> bool:
        """
        Validate that data matches expected structure
        
        Args:
            data: Data to validate
            expected_type (str): Expected type ('dict', 'list', 'str', etc.)
        
        Returns:
            bool: True if valid, False otherwise
        """
        if expected_type == 'dict':
            return isinstance(data, dict)
        elif expected_type == 'list':
            return isinstance(data, list)
        elif expected_type == 'str':
            return isinstance(data, str)
        elif expected_type == 'int':
            return isinstance(data, int)
        elif expected_type == 'float':
            return isinstance(data, float)
        else:
            return type(data).__name__ == expected_type
    
    def sanitize_data(self, data: Any) -> Any:
        """
        Sanitize data to remove potentially harmful content
        
        Args:
            data: Data to sanitize
        
        Returns:
            Sanitized data
        """
        if isinstance(data, dict):
            return {k: self.sanitize_data(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.sanitize_data(item) for item in data]
        elif isinstance(data, str):
            # Remove potentially dangerous characters/patterns
            import html
            return html.escape(data)
        else:
            return data
    
    def transform_data(self, data: Any, transformation_rules: Dict[str, Any]):
        """
        Transform data according to specified rules
        
        Args:
            data: Data to transform
            transformation_rules: Rules for transformation
        
        Returns:
            Transformed data
        """
        # Apply transformations based on rules
        for rule, params in transformation_rules.items():
            if rule == 'add_timestamp' and isinstance(data, dict):
                data['timestamp'] = str(data.get('timestamp', ''))
            elif rule == 'normalize_keys' and isinstance(data, dict):
                data = {k.lower().replace(' ', '_'): v for k, v in data.items()}
            elif rule == 'filter_empty' and isinstance(data, dict):
                data = {k: v for k, v in data.items() if v is not None and v != ''}
        
        return data
```

## 🔄 State Management

### Session State Handler

```python
import json
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

class StateManager:
    """
    Manage application state, session persistence, and temporary data
    """
    
    def __init__(self, session_timeout_minutes=30):
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.session_timeout = timedelta(minutes=session_timeout_minutes)
        self.lock = threading.Lock()
        self.state_file = "app_state.json"
    
    def create_session(self, user_id: str, initial_state: Dict[str, Any] = None) -> str:
        """
        Create a new session with unique ID
        
        Args:
            user_id (str): User identifier
            initial_state (dict): Initial state data
        
        Returns:
            str: Session ID
        """
        import uuid
        session_id = str(uuid.uuid4())
        
        with self.lock:
            self.sessions[session_id] = {
                'user_id': user_id,
                'created_at': datetime.now().isoformat(),
                'last_accessed': datetime.now().isoformat(),
                'state': initial_state or {},
                'status': 'active'
            }
        
        return session_id
    
    def get_session_state(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the current state for a session
        
        Args:
            session_id (str): Session identifier
        
        Returns:
            Session state or None if session doesn't exist
        """
        with self.lock:
            if session_id in self.sessions:
                session = self.sessions[session_id]
                
                # Update last accessed time
                session['last_accessed'] = datetime.now().isoformat()
                
                # Check if session has expired
                if self._is_session_expired(session):
                    del self.sessions[session_id]
                    return None
                
                # Return a copy to prevent direct modification
                return session['state'].copy()
            else:
                return None
    
    def update_session_state(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update session state with new values
        
        Args:
            session_id (str): Session identifier
            updates (dict): State updates to apply
        
        Returns:
            bool: Success status
        """
        with self.lock:
            if session_id in self.sessions:
                session = self.sessions[session_id]
                
                if self._is_session_expired(session):
                    del self.sessions[session_id]
                    return False
                
                # Update state
                session['state'].update(updates)
                session['last_accessed'] = datetime.now().isoformat()
                
                return True
            else:
                return False
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session
        
        Args:
            session_id (str): Session identifier
        
        Returns:
            bool: Success status
        """
        with self.lock:
            if session_id in self.sessions:
                del self.sessions[session_id]
                return True
            return False
    
    def _is_session_expired(self, session: Dict[str, Any]) -> bool:
        """Check if a session has expired"""
        last_access = datetime.fromisoformat(session['last_accessed'])
        return datetime.now() - last_access > self.session_timeout
    
    def cleanup_expired_sessions(self):
        """Remove expired sessions from memory"""
        with self.lock:
            expired_sessions = []
            for session_id, session in self.sessions.items():
                if self._is_session_expired(session):
                    expired_sessions.append(session_id)
            
            for session_id in expired_sessions:
                del self.sessions[session_id]
    
    def save_state_to_file(self, filepath: str = None):
        """
        Save current state to file
        
        Args:
            filepath (str): File path to save to (optional)
        """
        save_path = filepath or self.state_file
        state_data = {
            'sessions': self.sessions,
            'saved_at': datetime.now().isoformat()
        }
        
        with open(save_path, 'w') as f:
            json.dump(state_data, f, indent=2, default=str)
    
    def load_state_from_file(self, filepath: str = None):
        """
        Load state from file
        
        Args:
            filepath (str): File path to load from (optional)
        """
        load_path = filepath or self.state_file
        
        try:
            with open(load_path, 'r') as f:
                state_data = json.load(f)
            
            self.sessions = state_data.get('sessions', {})
        except FileNotFoundError:
            # File doesn't exist, start fresh
            pass
        except Exception as e:
            print(f"Error loading state from file: {e}")
    
    def get_user_sessions(self, user_id: str) -> list:
        """
        Get all sessions for a specific user
        
        Args:
            user_id (str): User identifier
        
        Returns:
            list: List of session IDs for the user
        """
        user_sessions = []
        with self.lock:
            for session_id, session in self.sessions.items():
                if session['user_id'] == user_id and not self._is_session_expired(session):
                    user_sessions.append(session_id)
        return user_sessions
```

### User Preferences Manager

```python
class UserPreferences:
    """
    Manage user-specific preferences and settings
    """
    
    DEFAULT_PREFERENCES = {
        'difficulty_level': 'simple',
        'image_style': 'cartoon',
        'theme_mode': 'normal',  # normal, high_contrast
        'language': 'english',
        'notifications': {
            'email': True,
            'progress_reports': True,
            'achievements': True
        },
        'accessibility': {
            'font_size': 16,
            'high_contrast': False,
            'reduce_motion': False,
            'screen_reader_mode': False
        },
        'privacy': {
            'data_sharing': False,
            'cloud_sync': True,
            'analytics': True
        }
    }
    
    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
        self.preferences_file = "user_preferences.json"
        self.preferences = self._load_preferences()
    
    def _load_preferences(self) -> Dict[str, Any]:
        """Load user preferences from file or use defaults"""
        loaded_prefs = self.data_manager.load_data(self.preferences_file, 'json')
        if loaded_prefs:
            # Merge with defaults to ensure all keys exist
            return self._merge_preferences(self.DEFAULT_PREFERENCES.copy(), loaded_prefs)
        return self.DEFAULT_PREFERENCES.copy()
    
    def _merge_preferences(self, defaults: Dict, updates: Dict) -> Dict:
        """Merge updates with defaults, preserving nested structures"""
        result = defaults.copy()
        for key, value in updates.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_preferences(result[key], value)
            else:
                result[key] = value
        return result
    
    def get_preference(self, key: str, user_id: str = None):
        """
        Get a specific preference
        
        Args:
            key (str): Preference key (e.g., 'difficulty_level')
            user_id (str): Optional user ID for user-specific preferences
        
        Returns:
            Preference value or None if not found
        """
        keys = key.split('.')
        value = self.preferences
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return None
        
        return value
    
    def set_preference(self, key: str, value, user_id: str = None) -> bool:
        """
        Set a specific preference
        
        Args:
            key (str): Preference key (e.g., 'difficulty_level')
            value: Preference value
            user_id (str): Optional user ID for user-specific preferences
        
        Returns:
            bool: Success status
        """
        keys = key.split('.')
        current = self.preferences
        
        for k in keys[:-1]:
            if k not in current or not isinstance(current[k], dict):
                current[k] = {}
            current = current[k]
        
        current[keys[-1]] = value
        
        return self.save_preferences()
    
    def get_all_preferences(self, user_id: str = None) -> Dict[str, Any]:
        """
        Get all preferences
        
        Args:
            user_id (str): Optional user ID
        
        Returns:
            Dict of all preferences
        """
        return self.preferences.copy()
    
    def reset_preferences(self, user_id: str = None) -> bool:
        """
        Reset preferences to defaults
        
        Args:
            user_id (str): Optional user ID
        
        Returns:
            bool: Success status
        """
        self.preferences = self.DEFAULT_PREFERENCES.copy()
        return self.save_preferences()
    
    def save_preferences(self) -> bool:
        """Save preferences to file"""
        return self.data_manager.save_data(self.preferences, self.preferences_file, 'json')
    
    def validate_preferences(self, preferences: Dict) -> bool:
        """
        Validate that preferences are correctly formatted
        
        Args:
            preferences (dict): Preferences to validate
        
        Returns:
            bool: True if valid, False otherwise
        """
        # This would contain validation logic for each preference type
        return True
```

## 📈 Data Processing Utilities

### Analytics Processing

```python
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict
import json

class AnalyticsProcessor:
    """
    Process and analyze user interaction data for insights and metrics
    """
    
    def __init__(self, session_manager: SessionManager):
        self.session_manager = session_manager
    
    def process_session_analytics(self, session_id: str) -> Dict[str, Any]:
        """
        Process analytics for a specific session
        
        Args:
            session_id (str): Session identifier
        
        Returns:
            dict: Processed analytics data
        """
        session_data = self.session_manager.load_session(session_id)
        if not session_data:
            return {}
        
        analytics_data = self.session_manager.get_session_analytics(session_id)
        
        # Calculate engagement metrics
        engagement_metrics = self._calculate_engagement_metrics(analytics_data)
        
        # Calculate progress metrics
        progress_metrics = self._calculate_progress_metrics(analytics_data)
        
        # Calculate learning metrics
        learning_metrics = self._calculate_learning_metrics(analytics_data)
        
        # Generate insights
        insights = self._generate_insights(engagement_metrics, progress_metrics, learning_metrics)
        
        return {
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "engagement": engagement_metrics,
            "progress": progress_metrics,
            "learning": learning_metrics,
            "insights": insights
        }
    
    def _calculate_engagement_metrics(self, analytics_data: Dict) -> Dict:
        """Calculate engagement-related metrics"""
        if not analytics_data or 'progress' not in analytics_data:
            return {"engagement_score": 0, "time_spent": 0, "interactions": 0}
        
        progress_data = analytics_data['progress']
        
        # Calculate time spent
        start_time = datetime.fromisoformat(progress_data.get('start_time', datetime.now().isoformat()))
        end_time = datetime.fromisoformat(progress_data.get('end_time', datetime.now().isoformat()))
        time_spent = (end_time - start_time).total_seconds()
        
        # Calculate interactions
        interactions = progress_data.get('interactions_count', 0)
        
        # Calculate engagement score
        engagement_score = min(100, (interactions * 10 + time_spent / 60) / 2)
        
        return {
            "engagement_score": engagement_score,
            "time_spent": time_spent,
            "interactions": interactions,
            "session_completion": progress_data.get('completion_percentage', 0)
        }
    
    def _calculate_progress_metrics(self, analytics_data: Dict) -> Dict:
        """Calculate progress-related metrics"""
        if not analytics_data or 'progress' not in analytics_data:
            return {"completion_rate": 0, "accuracy": 0, "improvement": 0}
        
        progress_data = analytics_data['progress']
        evaluation_data = analytics_data.get('evaluation', {})
        
        completion_rate = progress_data.get('completed_activities', 0) / max(progress_data.get('total_activities', 1), 1) * 100
        accuracy = np.mean(evaluation_data.get('accuracy_scores', [])) if evaluation_data.get('accuracy_scores') else 0
        
        # Calculate improvement over time
        accuracy_scores = evaluation_data.get('accuracy_scores', [])
        if len(accuracy_scores) > 1:
            recent_avg = np.mean(accuracy_scores[-3:]) if len(accuracy_scores) >= 3 else np.mean(accuracy_scores)
            earlier_avg = np.mean(accuracy_scores[:3]) if len(accuracy_scores) >= 3 else np.mean(accuracy_scores)
            improvement = recent_avg - earlier_avg
        else:
            improvement = 0
        
        return {
            "completion_rate": completion_rate,
            "accuracy": accuracy,
            "improvement": improvement,
            "current_level": progress_data.get('current_level', 'beginner'),
            "next_milestone": progress_data.get('next_milestone', '')
        }
    
    def _calculate_learning_metrics(self, analytics_data: Dict) -> Dict:
        """Calculate learning-related metrics"""
        if not analytics_data or 'evaluation' not in analytics_data:
            return {"detail_identification": 0, "semantic_understanding": 0, "vocabulary_growth": 0}
        
        evaluation_data = analytics_data['evaluation']
        
        # Detail identification rate
        identified_details = evaluation_data.get('identified_details_count', [])
        total_expected_details = evaluation_data.get('total_expected_details', [])
        detail_identification = (sum(identified_details) / len(identified_details)) if identified_details else 0
        
        # Semantic understanding (based on evaluation scores)
        semantic_scores = evaluation_data.get('semantic_accuracy', [])
        semantic_understanding = np.mean(semantic_scores) if semantic_scores else 0
        
        # Vocabulary growth (simplified calculation)
        vocabulary_samples = evaluation_data.get('vocabulary_usage', [])
        vocabulary_growth = len(set(vocabulary_samples)) if vocabulary_samples else 0
        
        return {
            "detail_identification": detail_identification,
            "semantic_understanding": semantic_understanding,
            "vocabulary_growth": vocabulary_growth,
            "cognitive_load": evaluation_data.get('cognitive_load', 0)
        }
    
    def _generate_insights(self, engagement: Dict, progress: Dict, learning: Dict) -> Dict:
        """Generate actionable insights from metrics"""
        insights = []
        
        # Engagement insights
        if engagement['engagement_score'] < 50:
            insights.append("Low engagement detected. Consider adjusting difficulty or providing more encouragement.")
        if engagement['session_completion'] < 70:
            insights.append("Session completion rate is low. Check for potential obstacles or distractions.")
        
        # Progress insights
        if progress['improvement'] > 10:
            insights.append("Significant improvement in recent activities. Continue current approach.")
        elif progress['improvement'] < -5:
            insights.append("Performance decline detected. Consider reducing difficulty or providing additional support.")
        
        # Learning insights
        if learning['detail_identification'] > 80:
            insights.append("Strong detail identification skills. Ready for more complex visual elements.")
        if learning['semantic_understanding'] < 60:
            insights.append("Semantic understanding needs improvement. Focus on concept-based activities.")
        
        return {
            "overall_insight": self._get_overall_insight(engagement, progress, learning),
            "actionable_items": insights,
            "recommendations": self._generate_recommendations(progress, learning)
        }
    
    def _get_overall_insight(self, engagement: Dict, progress: Dict, learning: Dict) -> str:
        """Generate overall session insight"""
        if (engagement['engagement_score'] > 70 and 
            progress['accuracy'] > 70 and 
            progress['improvement'] > 0):
            return "Positive learning session with good engagement and progress."
        elif engagement['engagement_score'] < 30:
            return "Low engagement session. May need different approach or content."
        else:
            return "Session completed with mixed results. Review specific metrics."
    
    def _generate_recommendations(self, progress: Dict, learning: Dict) -> List[str]:
        """Generate specific recommendations"""
        recommendations = []
        
        if progress['current_level'] == 'beginner' and progress['completion_rate'] > 80:
            recommendations.append("Ready to advance to next difficulty level.")
        if learning['detail_identification'] < 60:
            recommendations.append("Focus on activities that improve visual detail recognition.")
        if learning['semantic_understanding'] < 60:
            recommendations.append("Incorporate more concept-focused activities.")
        
        return recommendations
    
    def export_analytics_report(self, user_id: str, start_date: str, end_date: str, format_type: str = 'json') -> str:
        """
        Export analytics report for a user over a date range
        
        Args:
            user_id (str): User identifier
            start_date (str): Start date (YYYY-MM-DD)
            end_date (str): End date (YYYY-MM-DD)  
            format_type (str): Export format (json, csv, pdf)
        
        Returns:
            str: Path to exported report
        """
        # Get all sessions for the user in the date range
        all_sessions = self.session_manager.list_sessions(user_filter=user_id)
        
        filtered_sessions = []
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)
        
        for session in all_sessions:
            session_start = datetime.fromisoformat(session['start_time'])
            if start_dt <= session_start <= end_dt:
                filtered_sessions.append(session)
        
        # Process analytics for each session
        report_data = []
        for session in filtered_sessions:
            analytics = self.process_session_analytics(session['id'])
            report_data.append(analytics)
        
        # Export in requested format
        if format_type == 'json':
            output_path = f"analytics_report_{user_id}_{start_date}_to_{end_date}.json"
            with open(output_path, 'w') as f:
                json.dump(report_data, f, indent=2, default=str)
        elif format_type == 'csv':
            output_path = f"analytics_report_{user_id}_{start_date}_to_{end_date}.csv"
            if report_data:
                df = pd.json_normalize(report_data)
                df.to_csv(output_path, index=False)
            else:
                # Create empty CSV with headers
                pd.DataFrame(columns=['session_id', 'timestamp']).to_csv(output_path, index=False)
        
        return output_path
    
    def calculate_long_term_trends(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """
        Calculate long-term learning trends for a user
        
        Args:
            user_id (str): User identifier
            days (int): Number of days to analyze
        
        Returns:
            dict: Trend analysis
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        all_sessions = self.session_manager.list_sessions(user_filter=user_id)
        
        # Filter sessions within date range
        date_filtered_sessions = []
        for session in all_sessions:
            session_start = datetime.fromisoformat(session['start_time'])
            if start_date <= session_start <= end_date:
                date_filtered_sessions.append(session)
        
        # Calculate trends
        accuracies = []
        completions = []
        engagement_scores = []
        
        for session in date_filtered_sessions:
            analytics = self.process_session_analytics(session['id'])
            if analytics:
                accuracies.append(analytics['progress']['accuracy'])
                completions.append(analytics['progress']['completion_rate'])
                engagement_scores.append(analytics['engagement']['engagement_score'])
        
        # Calculate trend directions
        accuracy_trend = self._calculate_trend_direction(accuracies) if accuracies else 0
        completion_trend = self._calculate_trend_direction(completions) if completions else 0
        engagement_trend = self._calculate_trend_direction(engagement_scores) if engagement_scores else 0
        
        return {
            "time_period": f"{days} days",
            "total_sessions": len(date_filtered_sessions),
            "accuracy_trend": accuracy_trend,
            "completion_trend": completion_trend, 
            "engagement_trend": engagement_trend,
            "average_accuracy": np.mean(accuracies) if accuracies else 0,
            "average_completion": np.mean(completions) if completions else 0,
            "average_engagement": np.mean(engagement_scores) if engagement_scores else 0
        }
    
    def _calculate_trend_direction(self, values: list) -> float:
        """Calculate trend direction using linear regression"""
        if len(values) < 2:
            return 0
        
        x = np.arange(len(values))
        y = np.array(values)
        
        # Calculate slope of best fit line
        if len(x) != len(y):
            return 0
        
        # Simple trend calculation (slope of linear regression)
        slope = np.polyfit(x, y, 1)[0] if len(set(values)) > 1 else 0
        return slope
```

## 🔧 System Services

### Logging Service

```python
import logging
import os
from datetime import datetime
from pathlib import Path

class LoggingService:
    """
    Handle application logging with appropriate levels and formatting
    """
    
    def __init__(self, log_directory="logs", app_name="VisoLearn-2"):
        self.log_directory = Path(log_directory)
        self.log_directory.mkdir(parents=True, exist_ok=True)
        self.app_name = app_name
        
        # Configure logging
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging configuration"""
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Create handlers
        # File handler for all logs
        all_logs_handler = logging.FileHandler(
            self.log_directory / f"{self.app_name.lower()}_all.log"
        )
        all_logs_handler.setLevel(logging.DEBUG)
        all_logs_handler.setFormatter(formatter)
        
        # File handler for errors only
        error_handler = logging.FileHandler(
            self.log_directory / f"{self.app_name.lower()}_errors.log"
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        
        # Console handler for important messages
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        
        # Get root logger and add handlers
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        logger.addHandler(all_logs_handler)
        logger.addHandler(error_handler)
        logger.addHandler(console_handler)
    
    def log_info(self, message: str, component: str = "general"):
        """Log an informational message"""
        logger = logging.getLogger(f"{self.app_name}.{component}")
        logger.info(message)
    
    def log_warning(self, message: str, component: str = "general"):
        """Log a warning message"""
        logger = logging.getLogger(f"{self.app_name}.{component}")
        logger.warning(message)
    
    def log_error(self, message: str, component: str = "general", exception: Exception = None):
        """Log an error message"""
        logger = logging.getLogger(f"{self.app_name}.{component}")
        if exception:
            logger.error(f"{message} - Exception: {str(exception)}", exc_info=True)
        else:
            logger.error(message)
    
    def log_debug(self, message: str, component: str = "general"):
        """Log a debug message"""
        logger = logging.getLogger(f"{self.app_name}.{component}")
        logger.debug(message)
    
    def log_performance(self, operation: str, duration: float, component: str = "general"):
        """Log performance metrics"""
        logger = logging.getLogger(f"{self.app_name}.{component}")
        logger.info(f"Performance: {operation} took {duration:.3f}s")
    
    def cleanup_old_logs(self, days_to_keep: int = 30):
        """Remove log files older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        for log_file in self.log_directory.glob("*.log"):
            if datetime.fromtimestamp(log_file.stat().st_mtime) < cutoff_date:
                log_file.unlink()
    
    def get_log_file_path(self, component: str) -> str:
        """Get path to log file for specific component"""
        return str(self.log_directory / f"{self.app_name.lower()}_{component}.log")
```

### Error Handling Utilities

```python
import traceback
from typing import Dict, Any, Callable
from functools import wraps

class ErrorHandler:
    """
    Handle errors gracefully and provide appropriate user feedback
    """
    
    def __init__(self, logging_service: LoggingService):
        self.logging_service = logging_service
    
    def handle_error(self, error: Exception, context: str = "", user_friendly: bool = True) -> Dict[str, Any]:
        """
        Handle an error and return appropriate response
        
        Args:
            error: The exception that occurred
            context: Context where error occurred
            user_friendly: Whether to return user-friendly message
        
        Returns:
            dict: Error information
        """
        error_info = {
            'type': type(error).__name__,
            'message': str(error),
            'context': context,
            'timestamp': datetime.now().isoformat()
        }
        
        # Log the error
        self.logging_service.log_error(
            f"Error in {context}: {str(error)}",
            component="error_handler",
            exception=error
        )
        
        # Return user-friendly message if requested
        if user_friendly:
            user_message = self._get_user_friendly_message(error, context)
            error_info['user_message'] = user_message
        
        return error_info
    
    def _get_user_friendly_message(self, error: Exception, context: str) -> str:
        """Generate user-friendly error message based on error type"""
        error_type = type(error).__name__
        
        if error_type == "ConnectionError":
            return "Unable to connect to the service. Please check your internet connection and try again."
        elif error_type == "TimeoutError":
            return "The request took too long to complete. Please try again."
        elif error_type == "PermissionError":
            return "You don't have permission to access this resource. Please contact your administrator."
        elif error_type == "FileNotFoundError":
            return "The required file was not found. Please try the operation again."
        elif error_type == "ValueError":
            return "Invalid input provided. Please check your input and try again."
        else:
            return "An unexpected error occurred. Please try again or contact support if the problem persists."
    
    def error_handler_decorator(self, context: str = "", user_friendly: bool = True):
        """
        Decorator to automatically handle errors in functions
        
        Args:
            context: Context description for logging
            user_friendly: Whether to return user-friendly message
        """
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    error_info = self.handle_error(e, context, user_friendly)
                    if user_friendly:
                        return {'error': error_info['user_message'], 'success': False}
                    else:
                        return {'error': error_info['message'], 'success': False}
            return wrapper
        return decorator
    
    def retry_on_error(self, max_attempts: int = 3, delay: float = 1.0, exceptions: tuple = (Exception,)):
        """
        Decorator to retry function on specific exceptions
        
        Args:
            max_attempts: Maximum number of retry attempts
            delay: Delay between attempts in seconds
            exceptions: Tuple of exceptions to retry on
        """
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                last_exception = None
                
                for attempt in range(max_attempts):
                    try:
                        return func(*args, **kwargs)
                    except exceptions as e:
                        last_exception = e
                        if attempt < max_attempts - 1:
                            time.sleep(delay)
                        else:
                            # Log the final failure
                            self.handle_error(e, f"{func.__name__} after {max_attempts} attempts")
                
                # If all attempts failed, raise the last exception
                raise last_exception
            return wrapper
        return decorator
```

## 📊 Visualization Tools

### Chart Generation Utilities

```python
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import io
import base64
from typing import List, Dict, Any

class ChartGenerator:
    """
    Generate various types of charts and visualizations for analytics
    """
    
    def __init__(self):
        # Set up matplotlib for accessibility
        plt.style.use('default')
        plt.rcParams.update({
            'font.size': 12,
            'axes.titlesize': 14,
            'axes.labelsize': 12,
            'xtick.labelsize': 10,
            'ytick.labelsize': 10,
            'legend.fontsize': 10,
        })
    
    def generate_progress_chart(self, data: List[Dict[str, Any]], chart_type: str = 'line') -> str:
        """
        Generate progress visualization chart
        
        Args:
            data: List of dictionaries with date and progress values
            chart_type: Type of chart ('line', 'bar', 'area')
        
        Returns:
            str: Base64 encoded image string
        """
        if not data:
            return self._create_empty_chart("No progress data available")
        
        # Convert data to pandas DataFrame
        df = pd.DataFrame(data)
        
        # Convert date column to datetime if it exists
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 6))
        
        if chart_type == 'line':
            ax.plot(df['date'], df['progress'], marker='o', linewidth=2, markersize=6)
            ax.set_title('Progress Over Time')
            ax.set_ylabel('Progress (%)')
            # Format x-axis for dates
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=2))
            plt.xticks(rotation=45)
        elif chart_type == 'bar':
            ax.bar(df['date'], df['progress'])
            ax.set_title('Progress by Session')
            ax.set_ylabel('Progress (%)')
        elif chart_type == 'area':
            ax.fill_between(df['date'], df['progress'], alpha=0.3)
            ax.plot(df['date'], df['progress'], alpha=0.8)
            ax.set_title('Cumulative Progress')
            ax.set_ylabel('Progress (%)')
        
        ax.set_xlabel('Date')
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # Convert to base64 string
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight')
        img_buffer.seek(0)
        img_str = base64.b64encode(img_buffer.getvalue()).decode()
        plt.close()
        
        return f"data:image/png;base64,{img_str}"
    
    def generate_accuracy_trend_chart(self, accuracy_data: List[float], labels: List[str] = None) -> str:
        """
        Generate accuracy trend chart
        
        Args:
            accuracy_data: List of accuracy percentages
            labels: Optional labels for x-axis
        
        Returns:
            str: Base64 encoded image string
        """
        if not accuracy_data:
            return self._create_empty_chart("No accuracy data available")
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        x_values = range(len(accuracy_data))
        ax.plot(x_values, accuracy_data, marker='o', linewidth=2, markersize=6, color='green')
        ax.set_title('Accuracy Trend Over Time')
        ax.set_ylabel('Accuracy (%)')
        ax.set_ylim(0, 100)
        
        if labels:
            ax.set_xticks(x_values)
            ax.set_xticklabels(labels, rotation=45)
        else:
            ax.set_xlabel('Session Number')
        
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # Convert to base64 string
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight')
        img_buffer.seek(0)
        img_str = base64.b64encode(img_buffer.getvalue()).decode()
        plt.close()
        
        return f"data:image/png;base64,{img_str}"
    
    def generate_engagement_chart(self, engagement_data: Dict[str, List]) -> str:
        """
        Generate engagement metrics visualization
        
        Args:
            engagement_data: Dictionary with engagement metrics
        
        Returns:
            str: Base64 encoded image string
        """
        if not engagement_data:
            return self._create_empty_chart("No engagement data available")
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Time spent chart
        if 'time_spent' in engagement_data and engagement_data['time_spent']:
            ax1.bar(range(len(engagement_data['time_spent'])), engagement_data['time_spent'])
            ax1.set_title('Time Spent per Session')
            ax1.set_ylabel('Minutes')
            ax1.set_xlabel('Session')
        
        # Engagement score chart
        if 'engagement_score' in engagement_data and engagement_data['engagement_score']:
            ax2.plot(range(len(engagement_data['engagement_score'])), engagement_data['engagement_score'], 
                    marker='o', color='blue')
            ax2.set_title('Engagement Score Over Time')
            ax2.set_ylabel('Score')
            ax2.set_xlabel('Session')
            ax2.set_ylim(0, 100)
            ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Convert to base64 string
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight')
        img_buffer.seek(0)
        img_str = base64.b64encode(img_buffer.getvalue()).decode()
        plt.close()
        
        return f"data:image/png;base64,{img_str}"
    
    def generate_skill_assessment_chart(self, skills_data: Dict[str, float]) -> str:
        """
        Generate skill assessment visualization
        
        Args:
            skills_data: Dictionary with skill names and scores
        
        Returns:
            str: Base64 encoded image string
        """
        if not skills_data:
            return self._create_empty_chart("No skill data available")
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        skills = list(skills_data.keys())
        scores = list(skills_data.values())
        
        bars = ax.bar(skills, scores, color=['#4F8BF9' if score >= 70 else '#F59E0B' for score in scores])
        ax.set_title('Skill Assessment')
        ax.set_ylabel('Proficiency (%)')
        ax.set_ylim(0, 100)
        
        # Add value labels on bars
        for bar, score in zip(bars, scores):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                   f'{int(score)}%', ha='center', va='bottom')
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Convert to base64 string
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight')
        img_buffer.seek(0)
        img_str = base64.b64encode(img_buffer.getvalue()).decode()
        plt.close()
        
        return f"data:image/png;base64,{img_str}"
    
    def _create_empty_chart(self, message: str) -> str:
        """Create a chart with a message when no data is available"""
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, message, horizontalalignment='center', verticalalignment='center', 
                transform=ax.transAxes, fontsize=14)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        
        # Convert to base64 string
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight')
        img_buffer.seek(0)
        img_str = base64.b64encode(img_buffer.getvalue()).decode()
        plt.close()
        
        return f"data:image/png;base64,{img_str}"
    
    def generate_achievement_badges(self, achievements: List[Dict[str, Any]]) -> str:
        """
        Generate visual representation of achievements/badges
        
        Args:
            achievements: List of achievement dictionaries
        
        Returns:
            str: HTML string for badge display
        """
        if not achievements:
            return "<div class='no-achievements'>No achievements yet. Keep learning!</div>"
        
        html_parts = ['<div class="achievement-container">']
        
        for achievement in achievements:
            icon = achievement.get('icon', '🏆')
            title = achievement.get('title', 'Achievement')
            description = achievement.get('description', 'Completed')
            earned_date = achievement.get('earned_date', 'Today')
            
            badge_html = f"""
            <div class="achievement-badge">
                <div class="badge-icon">{icon}</div>
                <div class="badge-title">{title}</div>
                <div class="badge-description">{description}</div>
                <div class="badge-date">{earned_date}</div>
            </div>
            """
            html_parts.append(badge_html)
        
        html_parts.append('</div>')
        
        return '\n'.join(html_parts)
```

## 🚀 Performance Optimization Utilities

### Caching System

```python
import time
import threading
from functools import wraps
from typing import Any, Callable

class LRUCache:
    """
    Simple LRU (Least Recently Used) Cache implementation
    """
    
    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self.cache = {}
        self.access_order = []  # Track access order
        self.lock = threading.Lock()
    
    def get(self, key: str) -> Any:
        """Get value from cache, updating access order"""
        with self.lock:
            if key in self.cache:
                # Move to end (most recently used)
                self.access_order.remove(key)
                self.access_order.append(key)
                return self.cache[key]
            return None
    
    def put(self, key: str, value: Any):
        """Put value in cache, managing size"""
        with self.lock:
            if key in self.cache:
                # Update existing key
                self.cache[key] = value
                self.access_order.remove(key)
                self.access_order.append(key)
            else:
                # Add new key
                if len(self.cache) >= self.max_size:
                    # Remove least recently used item
                    lru_key = self.access_order.pop(0)
                    del self.cache[lru_key]
                
                self.cache[key] = value
                self.access_order.append(key)
    
    def clear(self):
        """Clear the cache"""
        with self.lock:
            self.cache.clear()
            self.access_order.clear()
    
    def size(self) -> int:
        """Get current cache size"""
        with self.lock:
            return len(self.cache)

class PerformanceOptimizer:
    """
    Utilities for optimizing performance through caching and async operations
    """
    
    def __init__(self):
        self.image_cache = LRUCache(max_size=50)
        self.text_cache = LRUCache(max_size=100)
        self.computation_cache = LRUCache(max_size=25)
    
    def memoize(self, cache_type: str = 'computation'):
        """
        Decorator for caching function results
        
        Args:
            cache_type: Type of cache to use ('computation', 'image', 'text')
        """
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Create cache key from function name and arguments
                cache_key = f"{func.__name__}:{str(args)}:{str(sorted(kwargs.items()))}"
                
                # Select appropriate cache
                if cache_type == 'image':
                    cache = self.image_cache
                elif cache_type == 'text':
                    cache = self.text_cache
                else:  # computation
                    cache = self.computation_cache
                
                # Check cache first
                result = cache.get(cache_key)
                if result is not None:
                    return result
                
                # Execute function and cache result
                result = func(*args, **kwargs)
                cache.put(cache_key, result)
                
                return result
            return wrapper
        return decorator
    
    def time_execution(self, log_level: str = 'info'):
        """
        Decorator to time function execution
        
        Args:
            log_level: Logging level for timing info
        """
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                result = func(*args, **kwargs)
                end_time = time.time()
                execution_time = end_time - start_time
                
                if log_level == 'info':
                    print(f"{func.__name__} executed in {execution_time:.3f}s")
                elif log_level == 'debug':
                    print(f"DEBUG: {func.__name__} took {execution_time:.3f}s")
                
                return result
            return wrapper
        return decorator
```

## 📚 Common Utilities

### Input Validation

```python
import re
from typing import Union, List

class InputValidator:
    """
    Validate user input and ensure data integrity
    """
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_age(age: Union[str, int]) -> bool:
        """Validate age input"""
        try:
            age_int = int(age)
            return 3 <= age_int <= 18
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_description(description: str, min_length: int = 5, max_length: int = 500) -> bool:
        """Validate description input"""
        if not isinstance(description, str):
            return False
        length = len(description.strip())
        return min_length <= length <= max_length
    
    @staticmethod
    def validate_difficulty(difficulty: str) -> bool:
        """Validate difficulty level"""
        valid_levels = ["very_simple", "simple", "moderate", "detailed", "very_detailed"]
        return difficulty.lower() in valid_levels
    
    @staticmethod
    def validate_image_style(style: str) -> bool:
        """Validate image style"""
        valid_styles = ["realistic", "illustration", "cartoon", "watercolor", "3d_rendering"]
        return style.lower() in valid_styles
    
    @staticmethod
    def sanitize_text(text: str) -> str:
        """Sanitize text input"""
        if not isinstance(text, str):
            return ""
        
        # Remove potentially harmful characters
        sanitized = re.sub(r'[<>"\']', '', text)
        return sanitized.strip()
    
    @staticmethod
    def validate_session_data(session_data: dict) -> List[str]:
        """Validate session data and return list of errors"""
        errors = []
        
        if not isinstance(session_data, dict):
            errors.append("Session data must be a dictionary")
            return errors
        
        # Check required fields
        required_fields = ['user_id', 'session_type', 'start_time']
        for field in required_fields:
            if field not in session_data:
                errors.append(f"Missing required field: {field}")
        
        # Validate specific field formats
        if 'user_id' in session_data:
            if not isinstance(session_data['user_id'], str) or len(session_data['user_id']) < 1:
                errors.append("user_id must be a non-empty string")
        
        if 'age' in session_data:
            if not InputValidator.validate_age(session_data['age']):
                errors.append("Invalid age value")
        
        return errors
```