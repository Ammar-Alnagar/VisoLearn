import os
import json
import base64
import time
import tempfile
import uuid
from datetime import datetime
from PIL import Image
import io
import gradio as gr
from models.story_generator import StoryGenerator
from models.comic_image_generator import ComicImageGenerator
from models.evaluation import extract_key_details, generate_detailed_description
from new_image_splitting import AutomatedCollageSplitter


def save_image_from_data_url(data_url, filename):
    """Save an image from a data URL to a file."""
    if not data_url or not data_url.startswith("data:image"):
        print(f"Invalid data URL: {data_url[:30] if data_url else None}")
        return False

    try:
        # Extract base64 part
        image_data = data_url.split(",")[1]
        image_bytes = base64.b64decode(image_data)

        # Create directory if needed
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        # Save the image
        with open(filename, "wb") as f:
            f.write(image_bytes)

        return True
    except Exception as e:
        print(f"Error saving image: {e}")
        return False


def generate_comic_story_sequence(age, autism_level, story_prompt, image_style, num_scenes=16, attempt_limit=3):
    """
    Generate a complete story sequence using comic generation approach.
    This function is a generator that yields updates to the UI.
    The comic will always contain exactly 16 scenes.
    """
    start_time = time.time()

    try:
        # Step 1: Generate the story structure from the user's prompt
        story_generator = StoryGenerator()
        if not story_prompt or not story_prompt.strip():
            story_prompt = f"A simple, visually interesting story for a {age}-year-old child."

        generated_story_data = story_generator.generate_story_from_prompt(story_prompt, num_scenes)

        if not generated_story_data:
            raise ValueError("Failed to generate a valid story structure from the prompt.")

        comic_title = generated_story_data.get("title", "A Story")
        comic_description_for_image_gen = generated_story_data.get("comic_description", story_prompt)
        topic_focus = "Story"

        # Create comic image generator
        image_generator = ComicImageGenerator()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = "".join(c if c.isalnum() or c in [' ', '_', '-'] else '_' for c in comic_title[:20]).strip().replace(" ", "_")

        story_dir = f"Story Sessions/{safe_title}_{timestamp}"
        os.makedirs(story_dir, exist_ok=True)

        comic_output_path = os.path.join(story_dir, f"story_comic.png")

        # Step 2: Generate the comic image
        comic_image, data_url = image_generator.generate_comic(
            {
                "title": comic_title,
                "description": comic_description_for_image_gen,
                "characters": generated_story_data.get("characters", []),
                "settings": generated_story_data.get("settings", []),
                "num_scenes": num_scenes
            },
            output_path=comic_output_path,
            style=image_style
        )

        if not comic_image:
            raise ValueError("Comic image generation failed.")

        # Step 3: Yield the generated image and a preliminary state to the UI
        # This allows the user to see the result immediately.
        preliminary_story_data = {
            "title": comic_title, "premise": "Analyzing details...", "scenes": [], "num_scenes": num_scenes
        }
        preliminary_session = {"comic_image_path": comic_output_path}

        yield (
            preliminary_session,
            preliminary_story_data,
            1,
            comic_output_path,
            f"### {comic_title}\n\n⏳ Analyzing story details, please wait...",
            "### Story Details\n\n*Loading...*",
            "",  # Empty nav
            "✅ Image generated! Now analyzing details..."
        )

        # Step 4: Run slow operations (detail extraction) in the "background"
        print("🔬 Analyzing generated comic for details...")
        comic_image_pil = Image.open(comic_output_path)
        # Hardcode difficulty to a sensible default since it's removed from UI
        difficulty = "moderate"
        image_description = generate_detailed_description(comic_image_pil, comic_description_for_image_gen, topic_focus)
        key_details = extract_key_details(comic_image_pil, comic_description_for_image_gen, topic_focus)
        print("✅ Analysis complete.")

        # Hardcode details_threshold to a sensible default
        details_threshold = 0.7
        details_threshold_decimal = max(0.1, min(1.0, float(details_threshold)))

        scene_images = {str(i + 1): comic_output_path for i in range(num_scenes)}

        # Step 5: Create the final, complete session and data objects
        story_session = {
            "age": age, "autism_level": autism_level, "difficulty": difficulty,
            "topic_focus": topic_focus, "story_prompt": story_prompt, "image_style": image_style,
            "num_scenes": num_scenes, "scene_images": scene_images, "comic_image_path": comic_output_path,
            "completed_scenes": [], "scene_responses": {}, "image_description": image_description,
            "key_details": key_details,
            "identified_details_by_scene": {str(i): [] for i in range(1, num_scenes + 1)},
            "attempt_count_by_scene": {str(i): 0 for i in range(1, num_scenes + 1)},
            "attempt_limit": int(attempt_limit), "details_threshold": details_threshold_decimal,
            "used_hints": [], "current_scene_details": key_details,
            "key_points": {
                "educational_points": [f"Understanding the story: '{comic_title}'"],
                "character_points": [f"Following the actions of characters: {', '.join([c['name'] for c in generated_story_data.get('characters', [])])}"],
                "plot_points": ["Story sequence and events"],
                "emotional_points": ["Character feelings and emotions"],
                "cause_effect_points": ["What happens and why"],
                "visual_details_points": ["Important visual elements"],
                "questions": [
                    f"What do you see in the story about '{comic_title}'?",
                    "Who are the main characters?", "What happens in each scene?",
                ]
            },
            "chat_history": {}, "identified_details": {}, "generation_prompt": comic_description_for_image_gen
        }

        story_data = {
            "title": comic_title,
            "premise": generated_story_data.get("overall_description", comic_description_for_image_gen[:150]),
            "educational_focus": topic_focus,
            "num_scenes": num_scenes,
            "scenes": generated_story_data.get("scenes", [])
        }

        if len(story_data["scenes"]) != num_scenes:
            story_data["scenes"] = [
                {"scene_number": i + 1, "title": f"Panel {i + 1}", "description": f"Viewing panel {i + 1} of '{comic_title}'."}
                for i in range(num_scenes)
            ]

        generation_time = time.time() - start_time

        story_info = f"""### {story_data['title']}
**Educational Focus:** {story_data['educational_focus']}
**Number of Scenes:** {num_scenes}
**Story Overview:** {story_data['premise']}
"""
        if story_prompt:
            story_info += f"\n**Story Prompt:** {story_prompt}"

        scene_nav_html = create_scene_navigation_html(num_scenes, 1)

        first_scene = story_data["scenes"][0]
        scene_desc = f"### {first_scene.get('title', f'Panel 1')}\n\n{first_scene.get('panel_description', first_scene.get('description', ''))}\n\n**Note:** You are currently viewing the complete comic. Use 'Extract Individual Scenes' to split the comic into separate panels."

        # Step 6: Yield the final, complete state to the UI
        yield (
            story_session, story_data, 1, comic_output_path, scene_desc, story_info,
            scene_nav_html, f"✅ Comic story generated and analyzed in {generation_time:.2f} seconds!"
        )

        # Split the comic into scenes
        print("⚡️ Using faster, non-vision-based panel splitting.")
        scenes = image_generator.split_comic_into_scenes(
            comic_image, num_scenes, use_gemini_analysis=False
        )

        if not scenes:
            print("❌ Scene extraction failed.")

    except Exception as e:
        print(f"Error generating comic story: {e}")
        yield (
            {}, {}, 1, None, "Error generating story",
            f"An error occurred: {str(e)}", "", f"❌ Error: {str(e)}"
        )

def create_scene_navigation_html(num_scenes, current_scene):
    """Generates HTML for scene navigation buttons."""
    nav_html = '<div style="display: flex; gap: 5px; flex-wrap: wrap;">'
    for i in range(num_scenes):
        scene_num = i + 1
        is_current = scene_num == current_scene
        style = ("background-color: #667eea; color: white; border: 1px solid #667eea;"
                 if is_current else
                 "background-color: transparent; color: #cbd5e1; border: 1px solid #475569;")
        nav_html += (f'<button class="scene-nav-button" onclick="navigate_to_scene({scene_num})" '
                     f'style="{style} border-radius: 8px; padding: 5px 10px; cursor: pointer;">{scene_num}</button>')
    nav_html += '</div>'
    return nav_html

def extract_comic_scenes(comic_image_path, num_scenes):
    """
    Extract individual scenes from a comic image using the new AutomatedCollageSplitter utility.

    Args:
        comic_image_path (str): Path to the comic image that should be split.
        num_scenes (int): Expected number of scenes in the comic image.

    Returns:
        Tuple[list[str], str]: A list with the file paths of extracted scenes and a user-friendly status message.
    """
    try:
        splitter = AutomatedCollageSplitter()

        # The splitter handles its own output directory. We only need the list of segment metadata.
        segments_info = splitter.split_collage(comic_image_path)
        if not segments_info:
            return [], "❌ No scenes could be extracted."

        scene_paths = [seg["path"] for seg in segments_info]
        absolute_dir = os.path.abspath(os.path.dirname(scene_paths[0])) if scene_paths else ""
        save_message = (
            f"<div style=\"padding: 10px; border: 1px solid #4CAF50; border-radius: 5px; background-color: #f1f8e9;\">"
            f"<p><strong>💾 Individual Scenes Extracted Successfully</strong></p>"
            f"<p>Extracted {len(scene_paths)} scenes from the comic image.</p>"
            f"<p>Location: <code>{absolute_dir}</code></p></div>"
        )
        return scene_paths, save_message

    except Exception as e:
        print(f"Error extracting comic scenes with AutomatedCollageSplitter: {e}")
        return [], f"❌ Error extracting scenes: {str(e)}"

def save_comic_story(story_data, comic_image, scenes, session_dir):
    """
    Saves the complete comic story, including the full comic image and individual scenes.
    """
    try:
        # Save story data
        story_data_path = os.path.join(session_dir, "story_data.json")
        with open(story_data_path, "w") as f:
            json.dump(story_data, f, indent=4)

        # Save comic image if it's a PIL Image
        if isinstance(comic_image, Image.Image):
            comic_image_path = os.path.join(session_dir, "story_comic.png")
            comic_image.save(comic_image_path)

        # Save scenes if they are PIL Images
        scene_paths = []
        scenes_dir = os.path.join(session_dir, "story_comic_segments")
        os.makedirs(scenes_dir, exist_ok=True)

        for i, scene in enumerate(scenes):
            if isinstance(scene, Image.Image):
                scene_path = os.path.join(scenes_dir, f"segment_{i+1:02d}.png")
                scene.save(scene_path)
                scene_paths.append(scene_path)

        return True, "Story, comic, and scenes saved successfully."

    except Exception as e:
        print(f"Error saving comic story: {e}")
        return False, f"Error saving story: {e}"
