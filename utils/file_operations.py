import os
import json
import base64
import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import pickle
import os.path


SCOPES = ['https://www.googleapis.com/auth/drive.file']

def save_story_to_google_drive(story_session, story_data, story_name=None):
    """
    Save the story generation data to Google Drive.

    Args:
        story_session: The story session data
        story_data: The story data
        story_name: Optional custom name for the story
    """
    try:
        # Generate base filename
        if story_name and story_name.strip():
            # Use custom story name if provided
            base_name = story_name.strip().replace(" ", "_")
            # Add timestamp to ensure uniqueness
            base_filename = f"{base_name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        else:
            base_filename = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        # Create temporary directory for files
        output_dir = f"temp_story_{base_filename}"
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

        # Save story session data
        session_filename = os.path.join(output_dir, f"{base_filename}_story_session.json")
        with open(session_filename, "w", encoding="utf-8") as f:
            json.dump(story_session, f, indent=2, ensure_ascii=False)

        # Upload session file to Drive
        file_metadata = {
            'name': f"{base_filename}_story_session.json",
            'parents': [folder_id]
        }
        media = MediaFileUpload(session_filename, mimetype='application/json')
        service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()

        # Save story data
        story_filename = os.path.join(output_dir, f"{base_filename}_story_data.json")
        with open(story_filename, "w", encoding="utf-8") as f:
            json.dump(story_data, f, indent=2, ensure_ascii=False)

        # Upload story file to Drive
        file_metadata = {
            'name': f"{base_filename}_story_data.json",
            'parents': [folder_id]
        }
        media = MediaFileUpload(story_filename, mimetype='application/json')
        service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()

        # Save and upload scene images
        scene_images = story_session.get("scene_images", {})
        for scene_num, image_data_url in scene_images.items():
            if image_data_url.startswith("data:image"):
                image_filename = os.path.join(output_dir, f"{base_filename}_scene_{scene_num}.png")
                if save_image_from_data_url(image_data_url, image_filename):
                    # Upload to Drive
                    file_metadata = {
                        'name': f"{base_filename}_scene_{scene_num}.png",
                        'parents': [folder_id]
                    }
                    media = MediaFileUpload(image_filename, mimetype='image/png')
                    service.files().create(
                        body=file_metadata,
                        media_body=media,
                        fields='id'
                    ).execute()

        # Also save a local copy in the Story Sessions directory
        story_sessions_dir = "Story Sessions"
        os.makedirs(story_sessions_dir, exist_ok=True)
        
        # Save local copies of the story files
        local_session_filename = os.path.join(story_sessions_dir, f"{base_filename}_story_session.json")
        with open(local_session_filename, "w", encoding="utf-8") as f:
            json.dump(story_session, f, indent=2, ensure_ascii=False)
            
        local_story_filename = os.path.join(story_sessions_dir, f"{base_filename}_story_data.json")
        with open(local_story_filename, "w", encoding="utf-8") as f:
            json.dump(story_data, f, indent=2, ensure_ascii=False)
            
        # Save local copies of scene images
        for scene_num, image_data_url in scene_images.items():
            if image_data_url.startswith("data:image"):
                local_image_filename = os.path.join(story_sessions_dir, f"{base_filename}_scene_{scene_num}.png")
                save_image_from_data_url(image_data_url, local_image_filename)

        # Clean up temporary files
        cleanup_error = None
        try:
            if output_dir and os.path.exists(output_dir):
                for file in os.listdir(output_dir):
                    os.remove(os.path.join(output_dir, file))
                os.rmdir(output_dir)
        except Exception as e:
            cleanup_error = str(e)
            print(f"Warning: Error during cleanup: {cleanup_error}")

        story_name_display = f"'{story_name}'" if story_name and story_name.strip() else "story data"
        success_message = f"✅ Successfully saved {story_name_display} to Google Drive folder: VisoLearn"
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
        return f"❌ Error saving story to Google Drive: {str(e)}"

def save_all_session_images(saved_sessions, active_session, custom_filename=None):
    """
    Save all images from the saved sessions and active session to disk.

    Args:
        saved_sessions: List of saved session data
        active_session: Current active session data
        custom_filename: Optional custom filename prefix for saved files
    """
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
        if session.get("image") and session.get("image").startswith("data:image"):
            filename = os.path.join(output_dir, f"{base_filename}_session_{i}.png")
            if save_image_from_data_url(session["image"], filename):
                saved_count += 1

    # Save image from active session if it exists
    if active_session.get("image") and active_session.get("image").startswith("data:image"):
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
        if not data_url or not data_url.startswith("data:image"):
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
