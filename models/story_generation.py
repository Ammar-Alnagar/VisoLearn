from google.generativeai import GenerativeModel
import json
import re

def generate_story_premise(topic_focus, difficulty, age, autism_level):
    """
    Generate a story premise based on the user's parameters.

    Returns a JSON object with:
    - premise: A brief description of the story
    - num_scenes: The recommended number of scenes (2-5 based on difficulty)
    - scene_descriptions: Brief descriptions for each scene
    """
    # Calculate appropriate number of scenes based on difficulty and autism level
    scene_counts = {
        "Very Simple": 2,
        "Simple": 3,
        "Moderate": 4,
        "Advanced": 4,
        "Complex": 5
    }

    # Adjust based on autism level
    level_adjustments = {
        "Level 1": 0,
        "Level 2": -1,
        "Level 3": -2
    }

    base_count = scene_counts.get(difficulty, 3)
    adjustment = level_adjustments.get(autism_level, 0)
    num_scenes = max(2, min(5, base_count + adjustment))

    query = f"""
    You are an educational story designer for children with autism. Create a simple story premise related to '{topic_focus}'
    that can be told in exactly {num_scenes} sequential images.

    Consider:
    - Age: {age}
    - Autism Level: {autism_level}
    - Difficulty: {difficulty}

    IMPORTANT: This story will be visualized as a SEQUENCE OF IMAGES that form a clear narrative progression.
    Each scene must visually connect to the previous and next scenes to create a coherent story flow.

    Develop a simple narrative with:
    - Clear beginning, middle, and end
    - Consistent characters throughout (same appearance in all scenes)
    - Simple emotional elements appropriate for autism {autism_level}
    - Visually distinctive scenes that clearly progress the story
    - Educational value related to '{topic_focus}'

    For each scene, provide:
    1. A brief description of what happens
    2. Key visual elements to include (that should be consistent across scenes)
    3. How it visually connects to the previous/next scene

    FORMAT YOUR RESPONSE AS A VALID JSON OBJECT with these fields:
    {{
      "premise": "Brief overview of the story (1-2 sentences)",
      "educational_focus": "Main learning objective",
      "num_scenes": {num_scenes},
      "scenes": [
        {{
          "scene_number": 1,
          "description": "Brief description of what happens in this scene",
          "key_elements": ["element1", "element2", "element3"],
          "transition": "How this scene leads to the next"
        }},
        // Additional scenes...
      ]
    }}

    IMPORTANT: Make sure your scenes tell a complete story with a clear sequence of events.
    The sequence MUST maintain consistent character appearance and setting elements.
    """

    model = GenerativeModel('gemini-2.5-flash')
    response = model.generate_content(query)

    try:
        # Find JSON in the response
        json_match = re.search(r'\{[\s\S]*\}', response.text, re.DOTALL)
        if json_match:
            story_data = json.loads(json_match.group(0))
            return story_data
        else:
            # Fallback structure if no valid JSON found
            return {
                "premise": f"A simple story about {topic_focus}",
                "educational_focus": topic_focus,
                "num_scenes": num_scenes,
                "scenes": [{"scene_number": i+1,
                           "description": f"Scene {i+1} of the story",
                           "key_elements": ["character", "setting", "action"],
                           "transition": "The story continues..."} for i in range(num_scenes)]
            }
    except Exception as e:
        print(f"Error parsing story premise: {e}")
        # Return a basic fallback structure
        return {
            "premise": f"A simple story about {topic_focus}",
            "educational_focus": topic_focus,
            "num_scenes": num_scenes,
            "scenes": [{"scene_number": i+1,
                       "description": f"Scene {i+1} of the story",
                       "key_elements": ["character", "setting", "action"],
                       "transition": "The story continues..."} for i in range(num_scenes)]
        }

def generate_scene_prompt(scene_data, story_premise, difficulty, age, autism_level, image_style="Comic"):
    """
    Generate an image prompt for a specific scene in the story, optimized for sequential storytelling.
    """
    scene_number = scene_data.get("scene_number", 1)
    scene_description = scene_data.get("description", "")
    key_elements = scene_data.get("key_elements", [])
    transition = scene_data.get("transition", "")

    # Ensure story continuity with stronger visual cohesion
    continuity_instruction = """
    CRITICAL STORY CONTINUITY REQUIREMENTS:
    - Characters MUST maintain exact same appearance across all scenes (same clothes, hair, etc.)
    - Settings should maintain consistent visual style and color palette
    - Visual elements that appear in multiple scenes should be identical in style and appearance
    - Use matching visual tone, lighting style, and perspective approach across all scenes
    - Match the artistic style precisely to previous scenes in the sequence
    """

    query = f"""
    Your task is to create an image generation prompt for scene {scene_number} in a sequence of connected story images for a child with autism.

    STORY CONTEXT:
    - Overall Premise: "{story_premise}"
    - Scene Description: "{scene_description}"
    - Key Elements: {', '.join(key_elements)}
    - Story Transition: "{transition}"

    PARAMETERS:
    - Child's Age: {age}
    - Autism Level: {autism_level}
    - Difficulty Level: {difficulty}
    - Image Style: {image_style}

    {continuity_instruction}

    CRITICAL PROMPT REQUIREMENTS:
    1. START WITH: "A {image_style.lower()} scene showing [description]"
    2. ULTRA-SPECIFIC VISUAL DETAILS: Include at least 8-10 specific visual elements with clear positions
    3. MAINTAIN VISUAL CONSISTENCY: Ensure all recurring characters/objects look identical across scenes
    4. COLOR PALETTE: Use the same color palette as earlier scenes for continuity
    5. COMPOSITION: Create a balanced visual composition that clearly shows the narrative
    6. CAMERA ANGLE: Use a consistent approach to camera angles and framing
    7. EMOTIONAL CLARITY: Make emotions clear through expressions and body language
    8. TIME OF DAY: Maintain consistent time of day across scenes unless the story specifically involves time passing

    TECHNICAL REQUIREMENTS:
    - Your prompt MUST be at least 150 words long
    - Include the exact phrase "high detail, coherent story sequence, consistent characters"
    - End with: "8k resolution, professional {image_style.lower()}, part of a continuous story sequence"
    - Clearly specify this is scene {scene_number} in a connected sequence

    CREATE YOUR DETAILED SCENE PROMPT NOW:
    """

    model = GenerativeModel('gemini-2.5-flash')
    response = model.generate_content(query)
    return response.text.strip()

def evaluate_story_understanding(user_description, story_data, current_scene, active_session):
    """
    Evaluate the user's understanding of the story based on their description.
    Provides feedback on story comprehension, not just image details.
    """
    scene_info = story_data["scenes"][current_scene-1] if current_scene <= len(story_data["scenes"]) else None
    premise = story_data.get("premise", "")
    educational_focus = story_data.get("educational_focus", "")

    # Format previous scenes for context
    previous_scenes = ""
    if current_scene > 1:
        previous_scenes = "Previous scenes:\n"
        for i in range(current_scene-1):
            prev_scene = story_data["scenes"][i]
            previous_scenes += f"Scene {i+1}: {prev_scene.get('description', '')}\n"

    # Format next scene for context (if not the last scene)
    next_scene = ""
    if current_scene < len(story_data["scenes"]):
        next_scene = f"Next scene: {story_data['scenes'][current_scene].get('description', '')}"

    query = f"""
    You're evaluating a child with autism level {active_session.get('autism_level', 'Level 1')} who is describing a story.

    STORY INFORMATION:
    - Overall Story Premise: "{premise}"
    - Educational Focus: "{educational_focus}"
    - Total Scenes: {len(story_data["scenes"])}
    - Current Scene: {current_scene} of {len(story_data["scenes"])}

    CURRENT SCENE DETAILS:
    Description: "{scene_info.get('description', '')}"
    Key Elements: {', '.join(scene_info.get('key_elements', []))}
    Transition: "{scene_info.get('transition', '')}"

    NARRATIVE CONTEXT:
    {previous_scenes}
    {next_scene}

    CHILD'S DESCRIPTION:
    "{user_description}"

    EVALUATION TASK:
    Evaluate the child's understanding of:
    1. The current scene details
    2. How this scene connects to the overall story
    3. Character continuity and development (are they recognizing the same characters?)
    4. Cause-effect relationships
    5. Emotional understanding appropriate to their autism level

    ADAPTATION CONSIDERATIONS:
    - Age: {active_session.get('age', '3')} years old
    - Autism Level: {active_session.get('autism_level', 'Level 1')}
    - For Level 2/3 autism or young children, even partial understanding is significant

    RESPONSE FORMAT (JSON):
    {{
      "feedback": "Encouraging, specific feedback on what they described well.  Mention if they recognized character continuity.",
      "story_understanding_score": 85,  // 0-100 score on overall story comprehension
      "scene_details_score": 80,  // 0-100 score on current scene detail identification
      "narrative_connection_score": 75,  // 0-100 score on understanding scene's place in story
      "identified_elements": ["element1", "element2"],  // Key story elements they correctly identified
      "missed_elements": ["element3", "element4"],  // Important elements they missed
      "hint": "A gentle hint about story progression without giving away too much",
      "question_prompt": "A question to help them think more about the story",
      "advance_to_next_scene": false  // Whether they're ready for the next scene
    }}
    """

    model = GenerativeModel('gemini-2.5-flash')
    response = model.generate_content(query)

    try:
        # Find JSON in the response
        json_match = re.search(r'\{[\s\S]*\}', response.text, re.DOTALL)
        if json_match:
            evaluation = json.loads(json_match.group(0))
            return evaluation
        else:
            # Fallback structure
            return {
                "feedback": "Thank you for your description! Can you tell me more about what you see in the story?",
                "story_understanding_score": 50,
                "scene_details_score": 50,
                "narrative_connection_score": 50,
                "identified_elements": [],
                "missed_elements": [],
                "hint": "Look at what the characters are doing.",
                "question_prompt": "What do you think happens next?",
                "advance_to_next_scene": False
            }
    except Exception as e:
        print(f"Error parsing story evaluation: {e}")
        # Fallback structure
        return {
            "feedback": "Thank you for your description! Can you tell me more about what you see in the story?",
            "story_understanding_score": 50,
            "scene_details_score": 50,
            "narrative_connection_score": 50,
            "identified_elements": [],
            "missed_elements": [],
            "hint": "Look at what the characters are doing.",
            "question_prompt": "What do you think happens next?",
            "advance_to_next_scene": False
        }

def summarize_story_progress(story_data, completed_scenes, active_session):
    """
    Generate a summary of the story progress so far.
    Useful when advancing to a new scene or completing the story.
    """
    num_scenes = len(story_data["scenes"])
    completed_count = len(completed_scenes)
    remaining_count = num_scenes - completed_count

    # Format completed scenes
    completed_text = ""
    for i, scene in enumerate(completed_scenes):
        scene_num = i + 1
        scene_info = story_data["scenes"][scene_num-1]
        completed_text += f"Scene {scene_num}: {scene_info.get('description', '')}\n"

    query = f"""
    You're creating a story progress summary for a child with autism level {active_session.get('autism_level', 'Level 1')}.

    STORY INFORMATION:
    - Story Premise: "{story_data.get('premise', '')}"
    - Educational Focus: "{story_data.get('educational_focus', '')}"
    - Total Scenes: {num_scenes}
    - Completed Scenes: {completed_count}
    - Remaining Scenes: {remaining_count}

    COMPLETED SCENES:
    {completed_text}

    TASK:
    Create an encouraging summary of the story so far that:
    1. Recaps what has happened in a simple, clear way
    2. Reinforces the educational concepts being taught
    3. Builds excitement for the next scene (if any remain)
    4. Celebrates completion (if all scenes are finished)
    5. Explicitly mention character names if they are in the premise

    ADAPTATION CONSIDERATIONS:
    - Age: {active_session.get('age', '3')} years old
    - Autism Level: {active_session.get('autism_level', 'Level 1')}
    - Use clear, concrete language
    - Highlight patterns and sequences
    - Emphasize emotions at an appropriate level
    - Keep summary brief and focused

    FORMAT YOUR RESPONSE IN PLAIN TEXT (not JSON).
    """

    model = GenerativeModel('gemini-2.5-flash')
    response = model.generate_content(query)
    return response.text.strip()

def extract_story_elements(image_input, scene_prompt, story_data, scene_number):
    """
    Extract key story elements from a scene image with improved error handling.
    """
    #try:
        # Replace this with your actual implementation for extracting elements
        # This is a placeholder example, you'll need to integrate with an image analysis service (e.g., Google Cloud Vision API, Clarifai, or similar)
        # or a simpler object detection/extraction method depending on your needs
    elements_list = [
        "Example Element 1",
        "Example Element 2",
        "Example Element 3"
    ]
        # Ensure we return a list of strings even if the API fails
    return elements_list  # Your existing return value
    #except Exception as e:
        #print(f"Error in extract_story_elements: {str(e)}")
        # Fallback elements based on the scene data
    scene_info = story_data["scenes"][scene_number-1] if scene_number <= len(story_data["scenes"]) else None
    if scene_info and "key_elements" in scene_info:
            # Use the key elements from the story data as fallback
        return scene_info["key_elements"]
    else:
            # Generic fallback elements
        return [
            "character in the scene",
            "setting or location",
            "main action happening",
            "important object",
            "emotional expression",
            "background detail",
            "narrative element"
        ]
