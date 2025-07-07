import os
import json
import base64
import datetime
import shutil
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import pickle
import os.path
from utils.migrations import migrate_chat_history_format

SCOPES = ['https://www.googleapis.com/auth/drive.file']

def save_to_google_drive(saved_sessions, active_session, custom_filename=None):
    """
    Save both chat logs and images to Google Drive in the VisoLearn folder.

    Args:
        saved_sessions: List of saved session data
        active_session: Current active session data
        custom_filename: Optional custom filename prefix for saved files
    """
    output_dir = None
    try:
        # Handle State objects if needed
        if hasattr(saved_sessions, 'value'):
            saved_sessions = saved_sessions.value
        if hasattr(active_session, 'value'):
            active_session = active_session.value
        if hasattr(custom_filename, 'value'):
            custom_filename = custom_filename.value

        # Generate base filename
        if custom_filename and custom_filename.strip():
            base_filename = custom_filename.strip()
        else:
            base_filename = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        # Create temporary directory for files
        output_dir = f"temp_saved_images_{base_filename}"
        os.makedirs(output_dir, exist_ok=True)

        creds = None
        # The file token.pickle stores the user's access and refresh tokens
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)

        # If there are no (valid) credentials available, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json',
                    SCOPES,
                    redirect_uri='http://localhost:8080/'
                )
                creds = flow.run_local_server(
                    port=8080,
                    prompt='consent',
                    access_type='offline'
                )
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        # Create Drive API service
        service = build('drive', 'v3', credentials=creds)

        # Check if VisoLearn folder exists, if not create it
        folder_name = 'VisoLearn'
        folder_id = None

        # Search for existing VisoLearn folder
        results = service.files().list(
            q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false",
            spaces='drive',
            fields='files(id, name)'
        ).execute()

        # If folder exists, use it; if not, create it
        if results['files']:
            folder_id = results['files'][0]['id']
        else:
            folder_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            folder = service.files().create(body=folder_metadata, fields='id').execute()
            folder_id = folder.get('id')

        # Save images from saved sessions
        for i, session in enumerate(saved_sessions):
            if session.get("image") and isinstance(session["image"], str) and session["image"].startswith("data:image"):
                filename = os.path.join(output_dir, f"{base_filename}_session_{i}.png")
                if save_image_from_data_url(session["image"], filename):
                    # Upload to Drive
                    file_metadata = {
                        'name': f"{base_filename}_session_{i}.png",
                        'parents': [folder_id]
                    }
                    media = MediaFileUpload(filename, mimetype='image/png')
                    service.files().create(
                        body=file_metadata,
                        media_body=media,
                        fields='id'
                    ).execute()

        # Save and upload active session image
        if active_session.get("image") and isinstance(active_session["image"], str) and active_session["image"].startswith("data:image"):
            filename = os.path.join(output_dir, f"{base_filename}_active_session.png")
            if save_image_from_data_url(active_session["image"], filename):
                file_metadata = {
                    'name': f"{base_filename}_active_session.png",
                    'parents': [folder_id]
                }
                media = MediaFileUpload(filename, mimetype='image/png')
                service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id'
                ).execute()

        # Save and upload session log
        log_filename = f"{base_filename}_session_log.json"
        all_sessions = saved_sessions.copy()
        if active_session and active_session.get("prompt"):
            all_sessions.append(active_session)

        clean_sessions = []
        for session in all_sessions:
            clean_session = session.copy()
            if "image" in clean_session:
                clean_session["image"] = "[IMAGE_DATA_REMOVED]"
            clean_sessions.append(clean_session)

        with open(log_filename, "w", encoding="utf-8") as f:
            json.dump(clean_sessions, f, indent=2, ensure_ascii=False)

        # Upload log file to Drive
        file_metadata = {
            'name': log_filename,
            'parents': [folder_id]
        }
        media = MediaFileUpload(log_filename, mimetype='application/json')
        service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()

        # Clean up temporary files
        cleanup_error = None
        try:
            if output_dir and os.path.exists(output_dir):
                for file in os.listdir(output_dir):
                    os.remove(os.path.join(output_dir, file))
                os.rmdir(output_dir)
            if os.path.exists(log_filename):
                os.remove(log_filename)
        except Exception as e:
            cleanup_error = str(e)
            print(f"Warning: Error during cleanup: {cleanup_error}")

        success_message = f"✅ Successfully saved all files to Google Drive folder: VisoLearn"
        if cleanup_error:
            success_message += f"\n(Warning: Cleanup error: {cleanup_error})"
        return success_message

    except Exception as e:
        # Cleanup on error
        if output_dir and os.path.exists(output_dir):
            try:
                for file in os.listdir(output_dir):
                    try:
                        os.remove(os.path.join(output_dir, file))
                    except:
                        pass
                os.rmdir(output_dir)
            except:
                pass  # Ignore cleanup errors in error handler
        return f"❌ Error saving to Google Drive: {str(e)}"

def save_all_session_images(saved_sessions, active_session, custom_filename=None):
    """
    Save all images from the saved sessions and active session to disk.

    Args:
        saved_sessions: List of saved session data
        active_session: Current active session data
        custom_filename: Optional custom filename prefix for saved files
    """
    # Handle State objects if needed
    if hasattr(saved_sessions, 'value'):
        saved_sessions = saved_sessions.value
    if hasattr(active_session, 'value'):
        active_session = active_session.value
    if hasattr(custom_filename, 'value'):
        custom_filename = custom_filename.value

    if custom_filename and custom_filename.strip():
        base_filename = custom_filename.strip()
    else:
        base_filename = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    saved_count = 0

    # Create a directory for the images if it doesn't exist
    output_dir = f"saved_images_{base_filename}"
    os.makedirs(output_dir, exist_ok=True)

    # Save images from saved sessions
    for i, session in enumerate(saved_sessions):
        if session.get("image") and isinstance(session["image"], str) and session["image"].startswith("data:image"):
            filename = os.path.join(output_dir, f"{base_filename}_session_{i}.png")
            if save_image_from_data_url(session["image"], filename):
                saved_count += 1

    # Save image from active session if it exists
    if active_session.get("image") and isinstance(active_session["image"], str) and active_session["image"].startswith("data:image"):
        filename = os.path.join(output_dir, f"{base_filename}_active_session.png")
        if save_image_from_data_url(active_session["image"], filename):
            saved_count += 1

    return f"✅ Successfully saved {saved_count} images to folder: {output_dir}"

def save_image_from_data_url(data_url, filename):
    """
    Extract base64 data from a data URL, decode it, and save it as an image file.

    Args:
        data_url (str): The data URL containing the base64-encoded image
        filename (str): The filename to save the image as

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        if not data_url or not isinstance(data_url, str) or not data_url.startswith("data:image"):
            print(f"Invalid data URL format")
            return False

        # Extract the base64 part from the data URL
        base64_data = data_url.split(",")[1]

        # Decode the base64 data
        image_data = base64.b64decode(base64_data)

        # Save to file
        with open(filename, "wb") as f:
            f.write(image_data)

        print(f"Successfully saved image to {filename}")
        return True
    except Exception as e:
        print(f"Error saving image from data URL: {str(e)}")
        return False

def save_session_log(saved_sessions, active_session, custom_filename=None):
    """
    Save all session data (including active session) to a JSON file.

    Args:
        saved_sessions: List of saved session data
        active_session: Current active session data
        custom_filename: Optional custom filename prefix for saved files
    """
    try:
        # Handle State objects if needed
        if hasattr(saved_sessions, 'value'):
            saved_sessions = saved_sessions.value
        if hasattr(active_session, 'value'):
            active_session = active_session.value
        if hasattr(custom_filename, 'value'):
            custom_filename = custom_filename.value

        if custom_filename and custom_filename.strip():
            base_filename = custom_filename.strip()
        else:
            base_filename = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        filename = f"{base_filename}_session_log.json"

        # Combine all sessions
        all_sessions = saved_sessions.copy()
        if active_session and active_session.get("prompt"):
            all_sessions.append(active_session)

        # Clean up the sessions for saving (removing data URLs to reduce file size)
        clean_sessions = []
        for session in all_sessions:
            clean_session = session.copy()
            # Replace image data URL with a placeholder to save space
            if "image" in clean_session:
                clean_session["image"] = "[IMAGE_DATA_REMOVED]"
            clean_sessions.append(clean_session)

        # Save to file
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(clean_sessions, f, indent=2, ensure_ascii=False)

        return f"✅ Session log saved to: {filename}"
    except Exception as e:
        print(f"Error saving session log: {str(e)}")
        return f"❌ Error saving session log: {str(e)}"

def save_session_to_filesystem(active_session, saved_sessions, custom_name=None):
    """
    Save the current session state to a local directory structure.

    Args:
        active_session: Current active session data
        saved_sessions: List of saved session data
        custom_name: Optional custom name for the session folder

    Returns:
        str: Status message about the save operation
    """
    try:
        # Handle State objects if needed
        if hasattr(active_session, 'value'):
            active_session = active_session.value
        if hasattr(saved_sessions, 'value'):
            saved_sessions = saved_sessions.value
        if hasattr(custom_name, 'value'):
            custom_name = custom_name.value

        # Create base directory if it doesn't exist
        base_dir = Path("Sessions History")
        base_dir.mkdir(exist_ok=True)

        # Generate folder name
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        if custom_name and custom_name.strip():
            folder_name = f"{timestamp}_{custom_name.strip()}"
        else:
            folder_name = timestamp

        # Sanitize folder name to be safe for file systems
        folder_name = "".join(c if c.isalnum() or c in "._- " else "_" for c in folder_name)

        # Create session directory
        session_dir = base_dir / folder_name
        session_dir.mkdir(exist_ok=True)

        # Create images directory
        images_dir = session_dir / "images"
        images_dir.mkdir(exist_ok=True)

        # Combine all sessions
        all_sessions = saved_sessions.copy()
        if active_session and active_session.get("prompt"):
            all_sessions.append(active_session)

        # Save each session
        session_data = []
        for i, session in enumerate(all_sessions):
            session_copy = session.copy()

            # Save image to file if it exists
            if session.get("image") and isinstance(session["image"], str) and session["image"].startswith("data:image"):
                image_filename = f"session_{i}.png"
                image_path = images_dir / image_filename

                # Extract and save the image
                try:
                    # Extract the base64 part from the data URL
                    base64_data = session["image"].split(",")[1]

                    # Decode the base64 data
                    image_data = base64.b64decode(base64_data)

                    # Save to file
                    with open(image_path, "wb") as f:
                        f.write(image_data)

                    print(f"Successfully saved image to {image_path}")

                    # Replace image data with reference to file
                    session_copy["image_file"] = f"images/{image_filename}"
                    # Store a smaller version in the JSON
                    session_copy["image"] = None
                except Exception as img_err:
                    print(f"Error saving image: {img_err}")
                    session_copy["image_file"] = None

            session_data.append(session_copy)

        # Save metadata file
        metadata = {
            "timestamp": timestamp,
            "sessions_count": len(session_data),
            "custom_name": custom_name if custom_name else "",
            "active_session_index": len(saved_sessions) if active_session and active_session.get("prompt") else -1
        }

        with open(session_dir / "metadata.json", "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        # Save sessions data
        with open(session_dir / "sessions.json", "w", encoding="utf-8") as f:
            json.dump(session_data, f, indent=2)

        return f"✅ Session saved to local folder: {session_dir}"

    except Exception as e:
        print(f"Error saving session to filesystem: {str(e)}")
        return f"❌ Error saving session: {str(e)}"

def list_saved_filesystem_sessions():
    """
    List all saved sessions in the local filesystem.

    Returns:
        list: List of session metadata
    """
    try:
        base_dir = Path("Sessions History")
        if not base_dir.exists():
            return []

        sessions = []
        for session_dir in base_dir.iterdir():
            if not session_dir.is_dir():
                continue

            # Try to load metadata
            metadata_file = session_dir / "metadata.json"
            if not metadata_file.exists():
                continue

            try:
                with open(metadata_file, "r", encoding="utf-8") as f:
                    metadata = json.load(f)

                display_name = metadata.get("custom_name") or session_dir.name
                timestamp = metadata.get("timestamp") or session_dir.name
                sessions_count = metadata.get("sessions_count", 0)

                sessions.append({
                    "id": session_dir.name,
                    "display_name": display_name,
                    "timestamp": timestamp,
                    "sessions_count": sessions_count,
                    "path": str(session_dir)
                })
            except Exception as e:
                print(f"Error reading metadata from {session_dir}: {e}")

        # Sort by timestamp (newest first)
        return sorted(sessions, key=lambda x: x["timestamp"], reverse=True)

    except Exception as e:
        print(f"Error listing saved sessions: {str(e)}")
        return []

def load_session_from_filesystem(session_id):
    """
    Load a session from the local filesystem.

    Args:
        session_id: The ID (directory name) of the session to load

    Returns:
        tuple: (active_session, saved_sessions, success_message, checklist_items)
    """
    try:
        # Handle State object if needed
        if hasattr(session_id, 'value'):
            session_id = session_id.value

        print(f"Loading session: {session_id}")

        base_dir = Path("Sessions History")
        session_dir = base_dir / session_id

        if not session_dir.exists() or not session_dir.is_dir():
            print(f"Session directory not found: {session_dir}")
            return None, [], f"❌ Session not found: {session_id}", []

        # Load metadata
        metadata_file = session_dir / "metadata.json"
        if not metadata_file.exists():
            print(f"Metadata file not found: {metadata_file}")
            return None, [], f"❌ Metadata file not found for session: {session_id}", []

        with open(metadata_file, "r", encoding="utf-8") as f:
            metadata = json.load(f)

        # Load sessions data
        sessions_file = session_dir / "sessions.json"
        if not sessions_file.exists():
            print(f"Sessions file not found: {sessions_file}")
            return None, [], f"❌ Sessions data file not found for session: {session_id}", []

        with open(sessions_file, "r", encoding="utf-8") as f:
            sessions_data = json.load(f)

        # Load images for each session - point directly to local files instead of using data URLs
        for session in sessions_data:
            if session.get("image_file"):
                image_path = session_dir / session["image_file"]
                if image_path.exists():
                    # Store the full path to the image file
                    session["image"] = str(image_path)
                    print(f"Loaded image reference: {image_path}")
                else:
                    print(f"Image file not found: {image_path}")
                    session["image"] = None

        # Determine active session and saved sessions
        active_session_index = metadata.get("active_session_index", -1)

        if active_session_index >= 0 and active_session_index < len(sessions_data):
            active_session = sessions_data[active_session_index]
            saved_sessions = sessions_data[:active_session_index]
            print(f"Using active session at index {active_session_index}")
        else:
            # If no active session index, use the last session as active
            if sessions_data:
                active_session = sessions_data[-1]
                saved_sessions = sessions_data[:-1]
                print("Using last session as active session")
            else:
                active_session = None
                saved_sessions = []
                print("No sessions found in data")

        # Migrate chat history format for all sessions
        if active_session and "chat" in active_session:
            active_session["chat"] = migrate_chat_history_format(active_session["chat"])

        for session in saved_sessions:
            if "chat" in session:
                session["chat"] = migrate_chat_history_format(session["chat"])

        # Generate checklist items
        checklist_items = []
        if active_session and active_session.get("key_details"):
            key_details = active_session.get("key_details", [])
            identified_details = active_session.get("identified_details", [])

            for i, detail in enumerate(key_details):
                identified = detail in identified_details
                checklist_items.append({"detail": detail, "identified": identified, "id": i})

        return active_session, saved_sessions, f"✅ Loaded session: {metadata.get('custom_name') or session_id}", checklist_items

    except Exception as e:
        print(f"Error loading session from filesystem: {str(e)}")
        return None, [], f"❌ Error loading session: {str(e)}", []

def delete_filesystem_session(session_id):
    """
    Delete a session from the local filesystem.

    Args:
        session_id: The ID (directory name) of the session to delete

    Returns:
        str: Status message about the delete operation
    """
    try:
        # Handle State object if needed
        if hasattr(session_id, 'value'):
            session_id = session_id.value

        base_dir = Path("Sessions History")
        session_dir = base_dir / session_id

        if not session_dir.exists() or not session_dir.is_dir():
            return f"❌ Session not found: {session_id}"

        # Delete the directory and all contents
        shutil.rmtree(session_dir)

        return f"✅ Session deleted: {session_id}"

    except Exception as e:
        print(f"Error deleting session from filesystem: {str(e)}")
        return f"❌ Error deleting session: {str(e)}"
