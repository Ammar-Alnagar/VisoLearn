import os
import json
import base64
import datetime
import shutil

def save_story_locally(story_session, story_data):
    """
    Save the story generation data to local storage in the Story Sessions directory.

    Args:
        story_session: The story session data
        story_data: The story data

    Returns:
        str: Success or error message
    """
    try:
        # Generate base filename with timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create a title for the session based on story data
        if story_data and "title" in story_data:
            title = story_data["title"]
        else:
            title = f"Story {timestamp}"
        
        # Create sanitized filename
        safe_title = "".join(c if c.isalnum() or c in " -_" else "_" for c in title)
        base_filename = f"{timestamp}_{safe_title}"
        
        # Create directory for this story session
        story_sessions_dir = os.path.join(os.getcwd(), "Story Sessions")
        os.makedirs(story_sessions_dir, exist_ok=True)
        
        session_dir = os.path.join(story_sessions_dir, base_filename)
        os.makedirs(session_dir, exist_ok=True)

        # Save story session data
        session_filename = os.path.join(session_dir, "story_session.json")
        with open(session_filename, "w", encoding="utf-8") as f:
            # Create a copy of the session data without the large image data
            session_copy = story_session.copy()
            if "scene_images" in session_copy:
                del session_copy["scene_images"]
            json.dump(session_copy, f, indent=2, ensure_ascii=False)

        # Save story data
        story_filename = os.path.join(session_dir, "story_data.json")
        with open(story_filename, "w", encoding="utf-8") as f:
            json.dump(story_data, f, indent=2, ensure_ascii=False)

        # Save scene images
        scene_images = story_session.get("scene_images", {})
        for scene_num, image_data_url in scene_images.items():
            if image_data_url and image_data_url.startswith("data:image"):
                image_filename = os.path.join(session_dir, f"scene_{scene_num}.png")
                save_image_from_data_url(image_data_url, image_filename)

        # Create a metadata file with summary information for the sidebar
        metadata = {
            "id": base_filename,
            "title": title,
            "timestamp": timestamp,
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "num_scenes": len(story_data.get("scenes", [])),
            "topic": story_data.get("topic", ""),
            "age": story_session.get("age", ""),
            "autism_level": story_session.get("autism_level", ""),
            "difficulty": story_session.get("difficulty", ""),
            "thumbnail": f"scene_1.png" if "1" in scene_images else None
        }
        
        metadata_filename = os.path.join(session_dir, "metadata.json")
        with open(metadata_filename, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        return f"✅ Successfully saved story data to local folder: {base_filename}"

    except Exception as e:
        return f"❌ Error saving story locally: {str(e)}"

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

        return True
    except Exception as e:
        print(f"Error saving image from data URL: {str(e)}")
        return False

def list_saved_stories():
    """
    List all saved story sessions from the Story Sessions directory.

    Returns:
        list: List of story session metadata
    """
    try:
        story_sessions_dir = os.path.join(os.getcwd(), "Story Sessions")
        if not os.path.exists(story_sessions_dir):
            return []

        sessions = []
        for session_dir in os.listdir(story_sessions_dir):
            full_dir_path = os.path.join(story_sessions_dir, session_dir)
            if os.path.isdir(full_dir_path):
                metadata_path = os.path.join(full_dir_path, "metadata.json")
                if os.path.exists(metadata_path):
                    with open(metadata_path, "r", encoding="utf-8") as f:
                        metadata = json.load(f)
                        sessions.append(metadata)
                else:
                    # For older sessions that might not have metadata
                    sessions.append({
                        "id": session_dir,
                        "title": session_dir,
                        "timestamp": session_dir.split("_")[0] if "_" in session_dir else "",
                        "date": ""
                    })

        # Sort by timestamp (newest first)
        sessions.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return sessions
    except Exception as e:
        print(f"Error listing saved stories: {str(e)}")
        return []

def load_story_session(session_id):
    """
    Load a saved story session by its ID.

    Args:
        session_id: The ID of the session to load

    Returns:
        tuple: (story_session, story_data) or (None, None) if not found
    """
    try:
        story_sessions_dir = os.path.join(os.getcwd(), "Story Sessions")
        session_dir = os.path.join(story_sessions_dir, session_id)
        
        if not os.path.exists(session_dir):
            return None, None

        # Load story session data
        session_filename = os.path.join(session_dir, "story_session.json")
        if not os.path.exists(session_filename):
            return None, None
            
        with open(session_filename, "r", encoding="utf-8") as f:
            story_session = json.load(f)

        # Load story data
        story_filename = os.path.join(session_dir, "story_data.json")
        if not os.path.exists(story_filename):
            return story_session, None
            
        with open(story_filename, "r", encoding="utf-8") as f:
            story_data = json.load(f)

        # Load scene images
        scene_images = {}
        for file in os.listdir(session_dir):
            if file.startswith("scene_") and file.endswith(".png"):
                scene_num = file.replace("scene_", "").replace(".png", "")
                image_path = os.path.join(session_dir, file)
                with open(image_path, "rb") as img_file:
                    img_data = img_file.read()
                    base64_data = base64.b64encode(img_data).decode("utf-8")
                    scene_images[scene_num] = f"data:image/png;base64,{base64_data}"

        # Add scene images to session data
        story_session["scene_images"] = scene_images

        return story_session, story_data
    except Exception as e:
        print(f"Error loading story session: {str(e)}")
        return None, None

def delete_story_session(session_id):
    """
    Delete a saved story session by its ID.

    Args:
        session_id: The ID of the session to delete

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        story_sessions_dir = os.path.join(os.getcwd(), "Story Sessions")
        session_dir = os.path.join(story_sessions_dir, session_id)
        
        if not os.path.exists(session_dir):
            return False

        shutil.rmtree(session_dir)
        return True
    except Exception as e:
        print(f"Error deleting story session: {str(e)}")
        return False