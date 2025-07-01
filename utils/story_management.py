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
import base64
import io
from PIL import Image
import time
from models.story_agents import generate_enhanced_story
from models.story_generation import generate_scene_prompt, evaluate_story_understanding, evaluate_full_story_understanding, generate_story_key_points
from models.image_generation import generate_image_fn
import gradio as gr
from config import DIFFICULTY_LEVELS, IMAGE_STYLES
import tempfile
import uuid
from models.evaluation import compare_details_chat_fn, parse_evaluation, update_checklist
import math

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
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Use custom story name if provided, otherwise use timestamp
        if story_name and story_name.strip():
            # Clean up the story name to be filename-safe
            safe_name = "".join(c if c.isalnum() or c in [' ', '_', '-'] else '_' for c in story_name.strip())
            # Limit length to avoid path length issues
            safe_name = safe_name[:30].strip()
            base_filename = f"{safe_name}_{timestamp}"
        else:
            base_filename = f"story_{timestamp}"

        # Create temporary directory for files with a short path
        temp_dir = os.path.join(tempfile.gettempdir(), "viso_export")
        output_dir = os.path.join(temp_dir, uuid.uuid4().hex[:8])
        os.makedirs(output_dir, exist_ok=True)

        # Create a copy of story_session with image data URLs instead of file paths
        session_for_save = story_session.copy()
        scene_images_for_save = {}
        
        # Convert any file paths to data URLs
        for scene_num, image_source in story_session.get("scene_images", {}).items():
            if isinstance(image_source, str) and os.path.exists(image_source):
                # Convert file path to data URL
                try:
                    with Image.open(image_source) as img:
                        buffer = io.BytesIO()
                        img.save(buffer, format="PNG")
                        img_bytes = buffer.getvalue()
                        image_data_url = f"data:image/png;base64,{base64.b64encode(img_bytes).decode('utf-8')}"
                        scene_images_for_save[scene_num] = image_data_url
                except Exception as e:
                    print(f"Error converting image file to data URL: {e}")
                    scene_images_for_save[scene_num] = None
            else:
                # Keep existing data URL
                scene_images_for_save[scene_num] = image_source
        
        # Replace the scene_images with data URLs
        session_for_save["scene_images"] = scene_images_for_save

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
        session_filename = os.path.join(output_dir, f"session.json")
        with open(session_filename, "w", encoding="utf-8") as f:
            json.dump(session_for_save, f, indent=2, ensure_ascii=False)

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
        story_filename = os.path.join(output_dir, f"data.json")
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
        for scene_num, image_data_url in session_for_save.get("scene_images", {}).items():
            if image_data_url and image_data_url.startswith("data:image"):
                # Use short filenames to avoid path length issues
                image_filename = os.path.join(output_dir, f"s{scene_num}.png")
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

        # Clean up temporary files
        cleanup_error = None
        try:
            if os.path.exists(output_dir):
                for file in os.listdir(output_dir):
                    try:
                        os.remove(os.path.join(output_dir, file))
                    except Exception as e:
                        print(f"Error removing file: {e}")
                try:
                    os.rmdir(output_dir)
                except Exception as e:
                    print(f"Error removing directory: {e}")
        except Exception as e:
            cleanup_error = str(e)
            print(f"Warning: Error during cleanup: {cleanup_error}")

        story_title = story_name if story_name and story_name.strip() else story_data.get('title', 'Story')
        success_message = f"✅ Successfully saved '{story_title}' to Google Drive folder: VisoLearn"
        return success_message

    except Exception as e:
        # Cleanup on error
        try:
            if 'output_dir' in locals() and os.path.exists(output_dir):
                for file in os.listdir(output_dir):
                    try:
                        os.remove(os.path.join(output_dir, file))
                    except Exception:
                        pass
                try:
                    os.rmdir(output_dir)
                except Exception:
                    pass
        except Exception:
            pass  # Ignore cleanup errors in error handler
        return f"❌ Error saving story to Google Drive: {str(e)}"

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

def generate_story_sequence(age, autism_level, difficulty, topic_focus, story_description, image_style, num_scenes=3):
    """
    Generate a complete story sequence using the new agent-based system.
    
    Args:
        age: The child's age
        autism_level: The child's autism level
        difficulty: The difficulty level
        topic_focus: The main topic or theme
        story_description: The user's story description
        image_style: The style of images to generate
        num_scenes: Number of scenes (default: 3)
        
    Returns:
        Complete story data with enhanced scene descriptions
    """
    # Generate story using the new agent-based system
    story_data, _, _, generation_prompt = generate_enhanced_story(
        topic_focus=topic_focus,
        num_scenes=num_scenes,  # Use the user's input for number of scenes
        story_style=image_style,  # Use the user's input for image style
        user_description=story_description
    )
    
    # Ensure story_data is a dictionary
    if isinstance(story_data, tuple):
        story_data = story_data[0]  # Take the first element if it's a tuple
    
    # Generate scene prompts and key points
    for i, scene in enumerate(story_data["scenes"]):
        scene_number = i + 1
        # Generate scene prompt using the user's image style
        scene["prompt"] = generate_scene_prompt(scene, story_data, image_style)
        # Generate key points
        scene["key_points"] = generate_story_key_points(story_data, {
            "age": age,
            "autism_level": autism_level
        })
    
    # Initialize storage for all scene images
    scene_images = {}
    scene_prompts = {}
    
    # Create a temporary directory for images if it doesn't exist
    temp_dir = os.path.join(tempfile.gettempdir(), "visolearn_story_images")
    os.makedirs(temp_dir, exist_ok=True)
    
    # Generate ALL scene images upfront
    print(f"[ImageGen] Starting image generation for {len(story_data['scenes'])} scenes...")
    total_image_start = time.time()
    for i, scene in enumerate(story_data["scenes"]):
        scene_num = i + 1
        scene_prompt = scene.get("prompt", "")
        scene_prompts[str(scene_num)] = scene_prompt
        print(f"[ImageGen] Generating image for scene {scene_num}...")
        img_start = time.time()
        # Generate image for this scene with retry logic
        scene_image = generate_image_with_retry(scene_prompt)
        img_end = time.time()
        print(f"[ImageGen] Scene {scene_num} image generated in {img_end - img_start:.2f} seconds.")
        # Save to a temporary file with a short path
        if hasattr(scene_image, 'save'):  # This is a PIL Image
            # Generate a short unique filename
            image_filename = f"scene_{scene_num}_{uuid.uuid4().hex[:8]}.png"
            image_filepath = os.path.join(temp_dir, image_filename)
            
            try:
                scene_image.save(image_filepath)
                scene_images[str(scene_num)] = image_filepath
            except Exception as e:
                print(f"Error saving scene image: {e}")
                # If saving fails, create a data URL as fallback
                buffer = io.BytesIO()
                scene_image.save(buffer, format="PNG")
                img_bytes = buffer.getvalue()
                image_data_url = f"data:image/png;base64,{base64.b64encode(img_bytes).decode('utf-8')}"
                scene_images[str(scene_num)] = image_data_url
        else:
            scene_images[str(scene_num)] = scene_image  # In case it's already a data URL or filepath
            
        # Add a small delay to avoid API rate limits
        time.sleep(1)
    total_image_end = time.time()
    print(f"[ImageGen] All images generated in {total_image_end - total_image_start:.2f} seconds.")
    
    # Create story session object with chat tracking and detail identification
    story_session = {
        "age": age,
        "autism_level": autism_level,
        "difficulty": difficulty,
        "topic_focus": topic_focus,
        "custom_description": story_description,
        "image_style": image_style,  # Store the user's image style choice
        "num_scenes": num_scenes,  # Store the user's number of scenes choice
        "scene_images": scene_images,
        "scene_prompts": scene_prompts,
        "completed_scenes": [],
        "scene_responses": {},
        "key_points": story_data["scenes"][0]["key_points"],  # Use first scene's key points
        "chat_history": {},  # Initialize chat history tracking
        "identified_details": {},  # Initialize identified details tracking
        "generation_prompt": generation_prompt  # Store the prompt used for generation
    }
    
    # Create summary of the story for display
    num_scenes = len(story_data["scenes"])
    story_title = story_data.get('title', story_data.get('premise', 'Story').split('.')[0])
    
    story_info = f"""### {story_title}
    **Educational Focus:** {story_data.get('educational_focus', topic_focus)}
    **Number of Scenes:** {num_scenes}
    **Story Overview:** {story_data.get('premise', '')}
    """
    
    if story_description:
        story_info += f"\n**User's Description:** {story_description}"
        
    # Create scene navigation display with clickable buttons
    scene_nav_html = f"""
    <div style="display: flex; justify-content: center; align-items: center; padding: 10px; background-color: #000; color: white; border-radius: 8px;">
        <div style="display: flex; gap: 10px;">
    """
    # Add clickable scene buttons
    for i in range(num_scenes):
        scene_num = i + 1
        active_class = "active" if scene_num == 1 else ""
        scene_nav_html += f"""
            <div id="scene-btn-{scene_num}"
                 onclick="document.getElementById('component-{scene_num+38}').click()"
                 style="width: 30px; height: 30px; background-color: {"#4CAF50" if i == 0 else "#666"};
                        border-radius: 50%; display: flex; justify-content: center; align-items: center;
                        font-size: 14px; cursor: pointer; transition: all 0.3s;">
                {scene_num}
            </div>
        """
    scene_nav_html += f"""
        </div>
        <div style="margin-left: 15px;">
            Scene 1 of {num_scenes}
        </div>
    </div>
    """
    
    # Create scene description
    first_scene = story_data["scenes"][0]
    scene_title = first_scene.get('title', 'Scene 1')
    scene_desc = f"### {scene_title}\n\n{first_scene.get('description', '')}"
    
    # Create scene selector choices - ensure at least one choice
    scene_selector_choices = [f"Scene {i+1}" for i in range(num_scenes)]
    if not scene_selector_choices:
        scene_selector_choices = ["Scene 1"]
    scene_selector_value = scene_selector_choices[0]  # Always set to first choice
    
    # Get the first image for display
    first_image = None
    if "1" in scene_images:
        first_image_path = scene_images["1"]
        if isinstance(first_image_path, str):
            if first_image_path.startswith('data:image'):
                # Handle data URL
                base64_img = first_image_path.split(",")[1]
                img_bytes = base64.b64decode(base64_img)
                first_image = Image.open(io.BytesIO(img_bytes))
            elif os.path.exists(first_image_path):
                # Handle file path - return the path directly for Gradio Image with type="filepath"
                first_image = first_image_path
                
    # Return all required outputs
    return (
        story_session,
        story_data,
        1,  # Current scene
        first_image,
        scene_desc,
        story_info,
        scene_nav_html,
        scene_selector_choices,  # Choices for dropdown
        scene_selector_value,    # Value for dropdown
        "✅ Story and images generated successfully!"  # Status message
    )

def generate_image_with_retry(prompt, max_retries=3, delay=2):
    """Generate an image with retry logic in case of API timeouts"""
    start_time = time.time()
    for attempt in range(max_retries):
        try:
            print(f"[ImageGen] Attempt {attempt+1} for prompt: {prompt[:60]}...")
            image = generate_image_fn(prompt)
            if image:
                print(f"[ImageGen] Success on attempt {attempt+1}.")
                break
            print(f"[ImageGen] Attempt {attempt+1}: Image generation returned None, retrying...")
        except Exception as e:
            print(f"[ImageGen] Attempt {attempt+1}: Error generating image: {str(e)}")
        time.sleep(delay * (attempt + 1))
    else:
        print("[ImageGen] All image generation attempts failed, returning placeholder")
        image = create_placeholder_image(f"Failed to generate image for: {prompt[:50]}...")
    end_time = time.time()
    print(f"[ImageGen] Total time for prompt: {end_time - start_time:.2f} seconds.")
    return image

def create_placeholder_image(text):
    """Create a placeholder image with text when generation fails"""
    # Create a simple image with PIL
    width, height = 512, 384
    image = Image.new('RGB', (width, height), color='#333333')
    try:
        # Try to add text to the image
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(image)
        # Use a default font
        try:
            font = ImageFont.truetype("arial.ttf", 20) # changed font to arial.ttf
        except:
            font = ImageFont.load_default()
        # Wrap text to fit width
        lines = []
        words = text.split()
        line = ""
        for word in words:
            test_line = line + word + " "
            # Estimate width with a simple heuristic
            if len(test_line) * 10 > width - 40:
                lines.append(line)
                line = word + " "
            else:
                line = test_line
        if line:
            lines.append(line)
        # Draw each line
        y_position = 150
        for line in lines:
            draw.text((20, y_position), line, font=font, fill="#FFFFFF")
            y_position += 30
    except Exception as e:
        print(f"Error creating placeholder text: {e}")
    return image

def submit_story_description(user_description, story_session, story_data, current_scene, full_story_mode=False):
    """Process the user's description of a story scene or full story."""
    if not story_data or not story_session:
        error_msg = "Please generate a story first."
        return error_msg, ""

    current_scene_num = int(current_scene)
    
    # Initialize chat history and tracking structures
    if "chat_history" not in story_session:
        story_session["chat_history"] = {}
    if "scene_responses" not in story_session:
        story_session["scene_responses"] = {}
    if "full_story_responses" not in story_session:
        story_session["full_story_responses"] = []
    
    if full_story_mode:
        # Full story mode - evaluate against the entire story
        print("🌟 Full Story Mode: Evaluating description against entire story")
        
        # Add to full story chat history
        if "full_story" not in story_session["chat_history"]:
            story_session["chat_history"]["full_story"] = []
        story_session["chat_history"]["full_story"].append(("Child", user_description))
        
        # Evaluate understanding of the full story
        evaluation = evaluate_full_story_understanding(
            user_description,
            story_data,
            story_session
        )
        
        # Store response in full story responses
        story_session["full_story_responses"].append({
            "user_description": user_description,
            "evaluation": evaluation,
            "timestamp": datetime.datetime.now().isoformat()
        })
        
        # Add teacher's feedback to full story chat history
        feedback = evaluation.get("feedback", "Thank you for describing the story!")
        question = evaluation.get("question_prompt", "")
        hint = evaluation.get("hint", "")
        teacher_response = f"{feedback}. {hint if hint else ''} {question if question else ''}"
        story_session["chat_history"]["full_story"].append(("Teacher", teacher_response))
        
    else:
        # Individual panel mode - evaluate against current scene only
        print(f"🎯 Panel Mode: Evaluating description for panel {current_scene_num}")
        
        # Initialize chat history for this scene if it doesn't exist
        if str(current_scene_num) not in story_session["chat_history"]:
            story_session["chat_history"][str(current_scene_num)] = []
        
        # Add user's description to scene chat history
        story_session["chat_history"][str(current_scene_num)].append(("Child", user_description))
        
        # Evaluate understanding using the evaluate_story_understanding function
        evaluation = evaluate_story_understanding(
            user_description,
            story_data,
            current_scene_num,
            story_session
        )
        
        # Store response in session
        story_session["scene_responses"][str(current_scene_num)] = {
            "user_description": user_description,
            "evaluation": evaluation
        }
        
        # Add teacher's feedback to scene chat history
        feedback = evaluation.get("feedback", "Thank you for your description!")
        question = evaluation.get("question_prompt", "")
        hint = evaluation.get("hint", "")
        teacher_response = f"{feedback}. {hint if hint else ''} {question if question else ''}"
        story_session["chat_history"][str(current_scene_num)].append(("Teacher", teacher_response))
    
    # Extract feedback components and format response
    feedback = evaluation.get("feedback", "Thank you for your description!")
    question = evaluation.get("question_prompt", "")
    hint = evaluation.get("hint", "")
    
    # Create rich feedback display
    if full_story_mode:
        rich_feedback = f"""
        ### Full Story Feedback
        {feedback}
        {"**Hint:** " + hint if hint else ""}
        {"**Question to consider:** " + question if question else ""}
        """
        
        # Track overall story understanding
        story_understanding_score = evaluation.get("story_understanding_score", 0)
        story_session["full_story_understanding_score"] = story_understanding_score
        
    else:
        rich_feedback = f"""
        ### Panel {current_scene_num} Feedback
        {feedback}
        {"**Hint:** " + hint if hint else ""}
        {"**Question to consider:** " + question if question else ""}
        """
        
        # Track identified elements in real-time for individual panels
        identified_elements = evaluation.get("identified_elements", [])
        
        # Initialize identified_details if it doesn't exist
        if "identified_details" not in story_session:
            story_session["identified_details"] = {}
        if str(current_scene_num) not in story_session["identified_details"]:
            story_session["identified_details"][str(current_scene_num)] = []
        
        # Add newly identified elements to the list
        for element in identified_elements:
            if element not in story_session["identified_details"][str(current_scene_num)]:
                story_session["identified_details"][str(current_scene_num)].append(element)
        
        # Mark scene as completed if understanding is sufficient
        understanding_score = evaluation.get("story_understanding_score", 0)
        can_advance = evaluation.get("advance_to_next_scene", False) or understanding_score >= 60
        
        # Mark scene as completed if understanding is sufficient
        if can_advance and str(current_scene_num) not in story_session.get("completed_scenes", []):
            story_session["completed_scenes"].append(str(current_scene_num))
    
    return rich_feedback, ""

def submit_story_description_enhanced(user_description, story_session, story_data, current_scene, full_story_mode=False):
    """
    Enhanced version of submit_story_description that includes details tracking,
    attempt management, and potential new image generation like the single image implementation.
    """
    if not story_data or not story_session:
        error_msg = "Please generate a story first."
        return "", [], story_session, error_msg, story_session.get("scene_images", {}).get(str(current_scene))

    # Import evaluation functions
    from models.evaluation import compare_details_chat_fn, parse_evaluation, update_checklist
    import math
    
    current_scene_num = int(current_scene)
    current_scene_str = str(current_scene_num)
    
    # Initialize structures if they don't exist
    if "chat_history" not in story_session:
        story_session["chat_history"] = {}
    if "identified_details_by_scene" not in story_session:
        story_session["identified_details_by_scene"] = {}
    if "attempt_count_by_scene" not in story_session:
        story_session["attempt_count_by_scene"] = {}
    if "used_hints" not in story_session:
        story_session["used_hints"] = []
        
    # Initialize for current scene
    if current_scene_str not in story_session["chat_history"]:
        story_session["chat_history"][current_scene_str] = []
    if current_scene_str not in story_session["identified_details_by_scene"]:
        story_session["identified_details_by_scene"][current_scene_str] = []
    if current_scene_str not in story_session["attempt_count_by_scene"]:
        story_session["attempt_count_by_scene"][current_scene_str] = 0

    # Get current scene image for evaluation
    scene_image = None
    if "scene_images" in story_session and current_scene_str in story_session["scene_images"]:
        scene_image_path = story_session["scene_images"][current_scene_str]
        if os.path.exists(scene_image_path):
            scene_image = scene_image_path

    if not scene_image:
        return "", [], story_session, "No image available for evaluation.", None

    # Create a temporary session object compatible with the evaluation function
    temp_session = {
        "image": scene_image,
        "image_description": story_session.get("image_description", ""),
        "prompt": story_session.get("generation_prompt", ""),
        "topic_focus": story_session.get("topic_focus", "Story"),
        "key_details": story_session.get("current_scene_details", story_session.get("key_details", [])),
        "identified_details": story_session["identified_details_by_scene"][current_scene_str],
        "used_hints": story_session.get("used_hints", []),
        "difficulty": story_session.get("difficulty", "Very Simple"),
        "autism_level": story_session.get("autism_level", "Level 1"),
        "age": story_session.get("age", ""),
        "attempt_limit": story_session.get("attempt_limit", 3),
        "attempt_count": story_session["attempt_count_by_scene"][current_scene_str],
        "details_threshold": story_session.get("details_threshold", 0.7),
        "chat": story_session["chat_history"][current_scene_str]
    }

    # Get evaluation using the existing compare_details_chat_fn
    raw_evaluation = compare_details_chat_fn(user_description, temp_session, scene_image, story_session.get("image_description", ""))
    feedback, updated_difficulty, should_advance, newly_identified, score = parse_evaluation(raw_evaluation, temp_session)

    # Update attempt count if no new details were identified
    if not newly_identified:
        story_session["attempt_count_by_scene"][current_scene_str] += 1

    # Update identified details for this scene
    for detail in newly_identified:
        if detail not in story_session["identified_details_by_scene"][current_scene_str]:
            story_session["identified_details_by_scene"][current_scene_str].append(detail)

    # Update chat history
    story_session["chat_history"][current_scene_str].append(("Child", user_description))
    story_session["chat_history"][current_scene_str].append(("Teacher", feedback))

    # Create checklist for current scene
    key_details = story_session.get("current_scene_details", story_session.get("key_details", []))
    checklist_items = []
    for i, detail in enumerate(key_details):
        is_identified = detail in story_session["identified_details_by_scene"][current_scene_str]
        checklist_items.append({"detail": detail, "identified": is_identified, "id": i})

    # Check if conditions are met to generate a new image
    identified_count = len(story_session["identified_details_by_scene"][current_scene_str])
    details_threshold = story_session.get("details_threshold", 0.7)
    threshold_count = math.ceil(len(key_details) * details_threshold)
    attempts_exhausted = story_session["attempt_count_by_scene"][current_scene_str] >= story_session.get("attempt_limit", 3)
    
    all_identified = all(item["identified"] for item in checklist_items)
    threshold_reached = identified_count >= threshold_count

    # Determine if we should generate a new image
    should_generate_new = attempts_exhausted or threshold_reached or all_identified

    new_image = None
    status_message = feedback

    if should_generate_new:
        # Import comic generation function
        from utils.comic_story_management import generate_comic_story_sequence
        
        # Generate new comic image with same parameters
        try:
            new_story_session, new_story_data, new_current_scene, new_scene_image, new_scene_desc, new_story_info, new_scene_nav, new_scene_selector, new_status = generate_comic_story_sequence(
                story_session.get("age", "3"),
                story_session.get("autism_level", "Level 1"),
                story_session.get("difficulty", "Very Simple"),
                story_session.get("story_prompt", ""),
                story_session.get("image_style", "Illustration"),
                story_session.get("num_scenes", 4),
                story_session.get("attempt_limit", 3),
                int(story_session.get("details_threshold", 0.7) * 100)
            )
            
            # Update the current story session with new image data
            story_session.update(new_story_session)
            
            # Reset attempts and identified details for the new image
            story_session["attempt_count_by_scene"] = {str(i): 0 for i in range(1, story_session.get("num_scenes", 4) + 1)}
            story_session["identified_details_by_scene"] = {str(i): [] for i in range(1, story_session.get("num_scenes", 4) + 1)}
            
            # Update checklist for new image
            new_key_details = story_session.get("key_details", [])
            checklist_items = []
            for i, detail in enumerate(new_key_details):
                checklist_items.append({"detail": detail, "identified": False, "id": i})
            
            new_image = story_session.get("scene_images", {}).get(str(current_scene_num))
            
            if attempts_exhausted:
                status_message = f"{feedback}\n\n**New Image Generated:** You've used all your allowed attempts. Let's try a new image!"
            elif threshold_reached:
                status_message = f"{feedback}\n\n**Great Progress!** You've identified enough details ({identified_count}/{len(key_details)}). Here's a new image to explore!"
            else:
                status_message = f"{feedback}\n\n**Excellent!** You've identified all the details. Here's a new challenge!"
                
        except Exception as e:
            print(f"Error generating new comic image: {e}")
            status_message = f"{feedback}\n\n**Note:** There was an issue generating a new image."

    # Convert chat history to messages format for display
    chat_messages = []
    for speaker, message in story_session["chat_history"][current_scene_str]:
        chat_messages.append({"role": "user" if speaker == "Child" else "assistant", "content": message})

    return "", chat_messages, story_session, status_message, new_image or story_session.get("scene_images", {}).get(current_scene_str)

def navigate_to_scene(story_session, story_data, current_scene, scene_change):
    """
    Navigate to a specific scene in the story sequence
    Args:
        story_session: The active session data
        story_data: The story premise and scene data
        current_scene: The current scene number
        scene_change: The number of scenes to change (+1, -1, or specific scene offset)
    Returns:
        Updated scene-related outputs
    """
    # Calculate new scene number
    num_scenes = len(story_data.get("scenes", []))
    if not num_scenes:
        return current_scene, None, "No scenes available", "", "", gr.update(choices=[], value=None)
    
    # Handle both direct scene selection and navigation
    if isinstance(scene_change, str) and scene_change.startswith("Scene "):
        # Direct scene selection from dropdown
        try:
            new_scene = int(scene_change.split(" ")[1])
        except (IndexError, ValueError):
            new_scene = int(current_scene)
    else:
        # Navigation via previous/next buttons
        new_scene = int(current_scene) + int(scene_change)
    
    # Handle wrap-around navigation
    if new_scene < 1:
        new_scene = num_scenes  # Wrap to the last scene
    elif new_scene > num_scenes:
        new_scene = 1  # Wrap to the first scene
        
    scene_num = str(new_scene)
    
    # Get scene data
    scene_index = new_scene - 1
    if 0 <= scene_index < len(story_data["scenes"]):
        scene_data = story_data["scenes"][scene_index]
    else:
        scene_data = {"description": f"Scene {new_scene}", "key_elements": []}
    
    # Get scene image - prioritize direct file paths
    scene_image = None
    if "scene_images" in story_session and scene_num in story_session["scene_images"]:
        scene_image_path = story_session["scene_images"][scene_num]
        # Check if it's a file path that exists
        if isinstance(scene_image_path, str):
            if os.path.exists(scene_image_path):
                # This is a file path that exists - use it directly
                scene_image = scene_image_path
            elif scene_image_path.startswith('data:image'):
                # This is a data URL - use it as is
                scene_image = scene_image_path
            else:
                # Invalid path or URL
                print(f"Warning: Scene image path not found: {scene_image_path}")
                scene_image = None
    
    # Get scene title and description - support both old and new story formats
    if "title" in scene_data:
        scene_title = scene_data.get("title", f"Scene {new_scene}")
        scene_description = scene_data.get("description", "No description available")
        scene_desc_markdown = f"### {scene_title}\n\n{scene_description}"
    else:
        # Legacy format without scene titles
        scene_description = scene_data.get("description", "No description available")
        scene_desc_markdown = f"### Scene {new_scene}\n\n{scene_description}"
    
    # Get previous user input and feedback for this scene (if any)
    user_description = ""
    feedback = ""
    if "scene_responses" in story_session and scene_num in story_session["scene_responses"]:
        user_description = story_session["scene_responses"][scene_num].get("user_description", "")
        
        if "evaluation" in story_session["scene_responses"][scene_num]:
            eval_data = story_session["scene_responses"][scene_num]["evaluation"]
            feedback_text = eval_data.get("feedback", "")
            hint = eval_data.get("hint", "")
            question = eval_data.get("question_prompt", "")
            
            feedback = f"""### Previous Feedback
            {feedback_text}
            {"**Hint:** " + hint if hint else ""}
            {"**Question to consider:** " + question if question else ""}
            """
    
    # Update scene selector
    scene_selector_update = gr.update(value=f"Scene {new_scene}")
    
    # Return only the necessary outputs - no button updates
    return (
        new_scene,  # Current scene number
        scene_image,  # Scene image
        scene_desc_markdown,  # Scene description as markdown
        user_description,  # User's previous input for this scene
        feedback,  # Previous feedback for this scene
        scene_selector_update  # Scene selector update
    )

def save_story_data_handler(story_session, story_data, story_name=None):
    """Handles saving story data to Google Drive and returns a status message."""
    if not story_session or not story_data:
        return "❌ No story data to save. Please generate a story first."
    try:
        message = save_story_to_google_drive(story_session, story_data, story_name)
        return message
    except Exception as e:
        return f"❌ Error saving story data: {str(e)}"

def save_story_locally(story_session, story_data, story_name=None):
    """
    Save the story generation data to a local directory.

    Args:
        story_session: The story session data
        story_data: The story premise and scene data
        story_name: Optional custom name for the story
        
    Returns:
        Success or error message
    """
    try:
        # Generate base filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Use custom story name if provided, otherwise use timestamp
        if story_name and story_name.strip():
            # Clean up the story name to be filename-safe
            safe_name = "".join(c if c.isalnum() or c in [' ', '_', '-'] else '_' for c in story_name.strip())
            # Limit length to avoid path length issues
            safe_name = safe_name[:30].strip()
            base_filename = f"{safe_name}_{timestamp}"
        else:
            # Use story title if available
            title = story_data.get('title', '')
            if title:
                safe_title = "".join(c if c.isalnum() or c in [' ', '_', '-'] else '_' for c in title)
                safe_title = safe_title[:30].strip()
                base_filename = f"{safe_title}_{timestamp}"
            else:
                base_filename = f"story_{timestamp}"
            
        # Create Story Sessions directory if it doesn't exist
        story_dir = "Story Sessions"
        os.makedirs(story_dir, exist_ok=True)
        
        # Create a copy of story_session with image data URLs instead of file paths
        session_for_save = story_session.copy()
        scene_images_for_save = {}
        
        # Convert any file paths to data URLs for JSON storage
        for scene_num, image_source in story_session.get("scene_images", {}).items():
            if isinstance(image_source, str) and os.path.exists(image_source):
                # Convert file path to data URL
                try:
                    with Image.open(image_source) as img:
                        buffer = io.BytesIO()
                        img.save(buffer, format="PNG")
                        img_bytes = buffer.getvalue()
                        image_data_url = f"data:image/png;base64,{base64.b64encode(img_bytes).decode('utf-8')}"
                        scene_images_for_save[scene_num] = image_data_url
                except Exception as e:
                    print(f"Error converting image file to data URL: {e}")
                    scene_images_for_save[scene_num] = None
            else:
                # Keep existing data URL
                scene_images_for_save[scene_num] = image_source
        
        # Replace the scene_images with data URLs for storage
        session_for_save["scene_images"] = scene_images_for_save
        
        # Save story session data
        session_filename = os.path.join(story_dir, f"{base_filename}_story_session.json")
        with open(session_filename, "w", encoding="utf-8") as f:
            json.dump(session_for_save, f, indent=2, ensure_ascii=False)
            
        # Save story data
        story_filename = os.path.join(story_dir, f"{base_filename}_story_data.json")
        with open(story_filename, "w", encoding="utf-8") as f:
            json.dump(story_data, f, indent=2, ensure_ascii=False)
            
        # Save scene images as PNG files
        image_dir = os.path.join(story_dir, f"{base_filename}_images")
        os.makedirs(image_dir, exist_ok=True)
        
        for scene_num, image_data_url in session_for_save.get("scene_images", {}).items():
            if image_data_url and image_data_url.startswith("data:image"):
                # Save image as PNG file
                image_filename = os.path.join(image_dir, f"scene_{scene_num}.png")
                save_image_from_data_url(image_data_url, image_filename)
                
        # Use a friendly display name
        display_name = story_name if story_name and story_name.strip() else story_data.get('title', 'Story')
        success_message = f"✅ Successfully saved '{display_name}' to local folder: {story_dir}"
        return success_message
    
    except Exception as e:
        return f"❌ Error saving story locally: {str(e)}"

def save_story_locally_handler(story_session, story_data, story_name=None):
    """Handles saving story data locally and returns a status message."""
    if not story_session or not story_data:
        return "❌ No story data to save. Please generate a story first."
    try:
        message = save_story_locally(story_session, story_data, story_name)
        return message
    except Exception as e:
        return f"❌ Error saving story data: {str(e)}"

def create_story_tab():
    """Create the UI components for the Story Sequence Generator tab"""
    # State variables
    story_session = gr.State({})
    story_data = gr.State({})
    current_scene = gr.State(1)
    
    # Get the list of saved stories
    saved_stories = list_saved_stories()
    story_choices = [name for name, _ in saved_stories] if saved_stories else []

    # Main vertical layout
    with gr.Column():
        gr.Markdown("# Story Sequence Generator")
        gr.Markdown(
            "This tool helps generate a sequence of images that tell a story. "
            "Perfect for teaching narrative understanding and sequencing concepts."
        )

        # Story control section
        with gr.Row():
            # Sidebar for saved stories
            with gr.Column(scale=1):
                gr.Markdown("## Saved Stories")
                story_sidebar = gr.Dropdown(
                    label="Load Saved Story",
                    choices=story_choices,
                    value=None,
                    interactive=True,
                    info="Select a saved story to load"
                )
                refresh_stories_btn = gr.Button("🔄 Refresh Stories")
                story_name_input = gr.Textbox(
                    label="Story Name",
                    placeholder="Enter the name of the story...",
                    lines=1
                )

        # Story settings section
        with gr.Column():
            gr.Markdown("## Story Settings")
            
            with gr.Row():
                age_input = gr.Textbox(label="Child's Age", placeholder="Enter age...", value="3")
                autism_level_dropdown = gr.Dropdown(
                    label="Autism Level",
                    choices=["Level 1", "Level 2", "Level 3"],
                    value="Level 1"
                )
            
            with gr.Row():
                difficulty_dropdown = gr.Dropdown(
                    label="Story Complexity",
                    choices=DIFFICULTY_LEVELS,
                    value="Very Simple"
                )
                
                image_style_dropdown = gr.Dropdown(
                    label="Image Style",
                    choices=IMAGE_STYLES,
                    value="Illustration",
                    info="Select the visual style for story images"
                )
                
                num_scenes_input = gr.Slider(
                    label="Number of Scenes",
                    minimum=2,
                    maximum=6,
                    value=3,
                    step=1,
                    info="Select how many scenes the story should have"
                )
            
            topic_focus_input = gr.Textbox(
                label="Story Topic/Theme",
                placeholder="Enter a topic for the story (e.g., 'friendship', 'going to school', 'emotions')...",
                lines=1
            )
            
            story_description_input = gr.Textbox(
                label="Story Description (optional)",
                placeholder="Describe the story you want, or leave blank for automatic generation...",
                lines=3
            )
            
            with gr.Row():
                generate_story_btn = gr.Button("Generate Story", variant="primary")
                generation_status = gr.Markdown("", elem_id="generation-status")

        # Story information section
        with gr.Column():
            story_info_box = gr.Markdown(
                """### Story Information

                Generate a story to see details.
                """
            )
            
            scene_navigation = gr.HTML(
                """<div style="display: flex; justify-content: center; padding: 10px;">
                    <span>Generate a story to navigate between scenes</span>
                </div>"""
            )

        # Scene display and interaction section
        with gr.Column():
            scene_image = gr.Image(label="Story Scene", type="filepath")
            scene_description = gr.Markdown("Generate a story to see scene descriptions.")
            
            with gr.Row():
                prev_scene_btn = gr.Button("← Previous Scene", interactive=False)
                scene_selector = gr.Dropdown(
                    choices=[],
                    label="Jump to Scene",
                    interactive=False
                )
                next_scene_btn = gr.Button("Next Scene →", interactive=False)
            
            user_description_input = gr.Textbox(
                label="Child's Description",
                placeholder="Type what the child says about this scene...",
                lines=3
            )
            
            submit_description_btn = gr.Button("Submit Description")
            feedback_display = gr.Markdown("Feedback will appear here...")

        # Key points section
        with gr.Column():
            gr.Markdown("## Key Points for Learning")
            key_points_display = gr.Markdown("", elem_id="key-points-display")
        
        # Session details section
        with gr.Column():
            gr.Markdown("## Session Details")
            session_details_output = gr.JSON(label="Session Details", value={})

        # Comic collage section
        with gr.Column():
            gr.Markdown("## Story Comic Collage")
            comic_collage_btn = gr.Button("🖼️ Generate Comic Collage")
            comic_collage_display = gr.Image(label="Story Comic Collage", type="filepath", interactive=False)
        
        # Save story section
        with gr.Column():
            gr.Markdown("## Save Story")
            with gr.Row():
                save_local_btn = gr.Button("💾 Save Story Locally")
                save_google_drive_btn = gr.Button("☁️ Save Story to Google Drive")
                save_result = gr.Textbox(label="Save Result", interactive=False)

        # Event handlers
        generate_story_btn.click(
            fn=lambda: "Generating story and images... this may take a minute...",
            inputs=None,
            outputs=generation_status
        ).then(
            generate_story_sequence,
            inputs=[
                age_input,
                autism_level_dropdown,
                difficulty_dropdown,
                topic_focus_input,
                story_description_input,
                image_style_dropdown,
                num_scenes_input
            ],
            outputs=[
                story_session,
                story_data,
                current_scene,
                scene_image,
                scene_description,
                story_info_box,
                scene_navigation,
                prev_scene_btn,
                next_scene_btn,
                scene_selector,
                generation_status
            ]
        ).then(
            update_session_details,
            inputs=[story_session, story_data],
            outputs=[session_details_output]
        ).then(
            format_key_points,
            inputs=[story_session],
            outputs=[key_points_display]
        )

        submit_description_btn.click(
            submit_story_description,
            inputs=[
                user_description_input,
                story_session,
                story_data,
                current_scene
            ],
            outputs=[
                feedback_display,
                user_description_input,
                story_session,
                story_data,
                scene_image
            ]
        ).then(
            format_key_points,
            inputs=[story_session],
            outputs=[key_points_display]
        ).then(
            update_session_details,
            inputs=[story_session, story_data],
            outputs=[session_details_output]
        )

        # Navigation handlers
        next_scene_btn.click(
            navigate_to_scene,
            inputs=[
                story_session,
                story_data,
                current_scene,
                gr.Number(value=1, visible=False)
            ],
            outputs=[
                current_scene,
                scene_image,
                scene_description,
                user_description_input,
                feedback_display,
                prev_scene_btn,
                next_scene_btn,
                scene_selector
            ]
        )

        prev_scene_btn.click(
            navigate_to_scene,
            inputs=[
                story_session,
                story_data,
                current_scene,
                gr.Number(value=-1, visible=False)
            ],
            outputs=[
                current_scene,
                scene_image,
                scene_description,
                user_description_input,
                feedback_display,
                prev_scene_btn,
                next_scene_btn,
                scene_selector
            ]
        )

        # Scene selector dropdown handler
        scene_selector.change(
            lambda choice, session, data, current: navigate_to_scene(
                session, 
                data, 
                current, 
                choice
            ),
            inputs=[
                scene_selector,
                story_session,
                story_data,
                current_scene
            ],
            outputs=[
                current_scene,
                scene_image,
                scene_description,
                user_description_input,
                feedback_display,
                prev_scene_btn,
                next_scene_btn,
                scene_selector
            ]
        )

        # Comic collage button handler
        comic_collage_btn.click(
            lambda session: create_comic_collage(session),
            inputs=[story_session],
            outputs=[comic_collage_display]
        )
        
        # Save buttons handlers
        save_local_btn.click(
            save_story_locally_handler,
            inputs=[story_session, story_data, story_name_input],
            outputs=[save_result]
        )
        
        save_google_drive_btn.click(
            save_story_data_handler,
            inputs=[story_session, story_data, story_name_input],
            outputs=[save_result]
        )
        
        # Load story event handlers
        story_sidebar.change(
            load_story_handler,
            inputs=[story_sidebar],
            outputs=[
                story_session,
                story_data,
                current_scene,
                scene_image,
                scene_description,
                story_info_box,
                scene_navigation,
                prev_scene_btn,
                next_scene_btn,
                scene_selector,
                story_name_input
            ]
        )
        
        refresh_stories_btn.click(
            refresh_stories_list,
            inputs=[],
            outputs=[story_sidebar]
        )
