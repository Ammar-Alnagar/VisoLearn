import math
import base64
import io
import os
import tempfile
import uuid
from PIL import Image, ImageDraw, ImageFont

def update_difficulty_label(active_session):
    return f"**Current Difficulty:** {active_session.get('difficulty', 'Very Simple')}"

def create_comic_collage(story_session):
    """
    Create a comic-style collage of all scene images in the story session.
    
    Args:
        story_session: The story session containing scene images
        
    Returns:
        The path to the saved collage image file
    """
    scene_images = story_session.get("scene_images", {})
    if not scene_images:
        # Return a placeholder image if no scenes are available
        placeholder = Image.new('RGB', (800, 400), color=(240, 240, 240))
        draw = ImageDraw.Draw(placeholder)
        try:
            # Try to load a font, fall back to default if not available
            font = ImageFont.truetype("arial.ttf", 20)
        except IOError:
            font = ImageFont.load_default()
        
        draw.text((400, 200), "No scene images available", fill=(0, 0, 0), font=font, anchor="mm")
        return _save_temp_image(placeholder)
    
    # Convert data URLs or file paths to PIL Images
    images = []
    for scene_num in sorted(scene_images.keys(), key=lambda x: int(x)):
        image_data = scene_images[scene_num]
        
        # Handle different image formats
        if isinstance(image_data, str):
            if image_data.startswith('data:image'):
                # Handle data URL
                try:
                    base64_img = image_data.split(",")[1]
                    img_bytes = base64.b64decode(base64_img)
                    img = Image.open(io.BytesIO(img_bytes))
                    images.append(img)
                except Exception as e:
                    print(f"Error processing data URL: {e}")
            elif os.path.exists(image_data):
                # Handle file path
                try:
                    img = Image.open(image_data)
                    images.append(img)
                except Exception as e:
                    print(f"Error opening image file {image_data}: {e}")
        elif isinstance(image_data, Image.Image):
            images.append(image_data)
    
    if not images:
        # Return a placeholder image if no valid images were found
        placeholder = Image.new('RGB', (800, 400), color=(240, 240, 240))
        draw = ImageDraw.Draw(placeholder)
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except IOError:
            font = ImageFont.load_default()
        
        draw.text((400, 200), "No valid scene images available", fill=(0, 0, 0), font=font, anchor="mm")
        return _save_temp_image(placeholder)
    
    # Determine the layout based on the number of images
    num_images = len(images)
    if num_images <= 2:
        cols = num_images
        rows = 1
    else:
        cols = min(3, num_images)  # Maximum 3 columns
        rows = math.ceil(num_images / cols)
    
    # Resize images to a consistent size
    target_width = 500
    target_height = 500
    resized_images = []
    for img in images:
        # Preserve aspect ratio
        img = img.copy()  # Create a copy to avoid modifying the original
        img.thumbnail((target_width, target_height), Image.LANCZOS)
        
        # Create a blank canvas with the target dimensions
        new_img = Image.new('RGB', (target_width, target_height), color=(255, 255, 255))
        
        # Paste the resized image centered on the canvas
        x_offset = (target_width - img.width) // 2
        y_offset = (target_height - img.height) // 2
        new_img.paste(img, (x_offset, y_offset))
        
        resized_images.append(new_img)
    
    # Create the comic layout
    margin = 20  # Margin between images and around the collage
    border = 5   # Border width around each image
    
    # Calculate the dimensions of the collage
    collage_width = cols * (target_width + 2 * border) + (cols + 1) * margin
    collage_height = rows * (target_height + 2 * border) + (rows + 1) * margin
    
    # Create a blank canvas for the collage
    collage = Image.new('RGB', (collage_width, collage_height), color=(240, 240, 240))
    draw = ImageDraw.Draw(collage)
    
    # Place each image in the collage with a border and scene number
    for i, img in enumerate(resized_images):
        row = i // cols
        col = i % cols
        
        # Calculate position for this image
        x = margin + col * (target_width + 2 * border + margin)
        y = margin + row * (target_height + 2 * border + margin)
        
        # Draw a border around the image position
        draw.rectangle(
            [(x, y), (x + target_width + 2 * border, y + target_height + 2 * border)],
            fill=(0, 0, 0)
        )
        
        # Paste the image inside the border
        collage.paste(img, (x + border, y + border))
        
        # Add scene number label
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except IOError:
            font = ImageFont.load_default()
        
        scene_num = i + 1
        label_bg_size = 40
        
        # Draw a circular background for the scene number
        draw.ellipse(
            [(x + 10, y + 10), (x + 10 + label_bg_size, y + 10 + label_bg_size)],
            fill=(0, 0, 0)
        )
        
        # Draw the scene number
        draw.text(
            (x + 10 + label_bg_size // 2, y + 10 + label_bg_size // 2),
            str(scene_num),
            fill=(255, 255, 255),
            font=font,
            anchor="mm"
        )
    
    # Save the collage to a temporary file and return the path
    return _save_temp_image(collage)

def _save_temp_image(image):
    """
    Save a PIL image to a temporary file with a short name to avoid path length issues.
    
    Args:
        image: PIL Image object to save
        
    Returns:
        Path to the saved temporary file
    """
    # Create a temporary directory if it doesn't exist
    temp_dir = os.path.join(tempfile.gettempdir(), "visolearn_tmp")
    os.makedirs(temp_dir, exist_ok=True)
    
    # Generate a short unique filename
    filename = f"{uuid.uuid4().hex[:8]}.png"
    filepath = os.path.join(temp_dir, filename)
    
    # Save the image
    try:
        image.save(filepath)
        return filepath
    except Exception as e:
        print(f"Error saving temporary image: {e}")
        # If saving fails, return a placeholder path
        return ""

def save_comic_collage(story_session, filename=None):
    """
    Create and save a comic-style collage of all scene images.
    
    Args:
        story_session: The story session containing scene images
        filename: Optional filename to save the collage (without extension)
        
    Returns:
        Path to the saved collage file, or None if saving failed
    """
    # Get the temporary collage file path
    temp_filepath = create_comic_collage(story_session)
    
    if not temp_filepath:
        print("Failed to create comic collage")
        return None
    
    if not filename:
        # Generate a default filename based on timestamp
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"story_collage_{timestamp}"
    
    # Ensure the filename has a .png extension
    if not filename.lower().endswith(".png"):
        filename += ".png"
    
    try:
        # If the temp file exists, copy it to the desired location
        if os.path.exists(temp_filepath):
            # Open and save to the new location
            img = Image.open(temp_filepath)
            img.save(filename)
            return filename
        return None
    except Exception as e:
        print(f"Error saving comic collage: {e}")
        return None

def update_checklist_html(checklist):
    if not checklist:
        return """
            <div id="checklist-container" style="background-color: #000000; color: #ffffff; padding: 15px; border-radius: 8px;">
                <p>Generate an image to see details to identify.</p>
            </div>
        """

    html_content = """
        <div id="checklist-container" style="background-color: #000000; color: #ffffff; padding: 15px; border-radius: 8px;">
            <style>
                .checklist-item {
                    display: flex;
                    align-items: center;
                    margin-bottom: 10px;
                    padding: 8px;
                    border-radius: 5px;
                    transition: background-color 0.3s;
                }
                .identified {
                    background-color: #1e4620;
                    text-decoration: line-through;
                    color: #7fff7f;
                }
                .not-identified {
                    background-color: #222222;
                    color: #ffffff;
                }
                .checkmark {
                    margin-right: 10px;
                    font-size: 1.2em;
                }
            </style>
    """

    for item in checklist:
        detail = item["detail"]
        identified = item["identified"]
        css_class = "identified" if identified else "not-identified"
        checkmark = "✅" if identified else "❌"
        html_content += f"""
            <div class="checklist-item {css_class}">
                <span class="checkmark">{checkmark}</span>
                <span>{detail}</span>
            </div>
        """

    html_content += """
        </div>
    """
    return html_content

def update_progress_html(checklist, active_session):
    if not checklist:
        return """
            <div id="progress-container" style="background-color: #000000; color: #ffffff; padding: 15px; border-radius: 8px;">
                <p>No active session.</p>
            </div>
        """

    total_items = len(checklist)
    identified_items = sum(1 for item in checklist if item["identified"])
    percentage = (identified_items / total_items) * 100 if total_items > 0 else 0
    progress_bar_width = f"{percentage}%"

    # Calculate threshold
    details_threshold = active_session.get("details_threshold", 0.7)
    threshold_count = math.ceil(total_items * details_threshold)
    threshold_percentage = (threshold_count / total_items) * 100

    html_content = f"""
        <div id="progress-container" style="background-color: #000000; color: #ffffff; padding: 15px; border-radius: 8px;">
            <h3>Progress: {identified_items} / {total_items} details</h3>
            <div style="width: 100%; background-color: #333333; border-radius: 5px; margin-bottom: 10px; position: relative;">
                <div style="width: {progress_bar_width}; height: 24px; background-color: #4CAF50; border-radius: 5px;"></div>
                <div style="position: absolute; top: 0; bottom: 0; left: {threshold_percentage}%; width: 2px; background-color: #ff6b6b;"></div>
                <div style="position: absolute; top: -15px; left: {threshold_percentage - 5}%; color: #ff6b6b; font-weight: bold;">⚠️</div>
            </div>
            <p style="font-size: 14px; text-align: center; color: #dddddd;">
                Need to identify at least {threshold_count} details ({int(details_threshold*100)}%) to advance
            </p>
            <p style="font-size: 16px; font-weight: bold; text-align: center; color: #ffffff;">
    """

    if identified_items >= threshold_count:
        html_content += "🎉 Threshold reached! Ready to advance! 🎉"
    elif percentage >= 75:
        html_content += "Almost there! Keep going!"
    elif percentage >= 50:
        html_content += "Halfway there! You're doing great!"
    elif percentage >= 25:
        html_content += "Good start! Keep looking!"
    else:
        html_content += "Let's find more details!"

    html_content += """
            </p>
        </div>
    """
    return html_content

def update_attempt_counter(active_session):
    current_count = active_session.get("attempt_count", 0)
    limit = active_session.get("attempt_limit", 3)
    return f"""
        <div id="attempt-counter" style="margin-top: 10px; padding: 10px; background-color: #000000; color: #ffffff; border-radius: 5px; border: 1px solid #444;">
            <p style="margin: 0; font-weight: bold; text-align: center;">Attempts: {current_count}/{limit}</p>
        </div>
    """
