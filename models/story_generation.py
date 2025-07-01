from google.generativeai import GenerativeModel
import json
import re
from config import get_enhanced_style_specifications, get_style_prompt_enhancement

def manage_story_timeline(story_data):
    """
    Story Timeline Manager agent that ensures consistent time progression throughout the story.
    Enhanced to handle stories with up to 60 scenes.

    Args:
        story_data: The story data to validate and enhance

    Returns:
        Updated story_data with enhanced timeline consistency
    """
    if not story_data or "scenes" not in story_data:
        return story_data

    # Get the timeline from story data or create a default one
    timeline = story_data.get("timeline", {
        "total_duration": "One week",
        "time_progression": "Day by day",
        "key_time_markers": ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5", "Day 6", "Day 7"],
        "seasonal_context": "Current season"
    })

    # Calculate total time span
    total_duration = timeline.get("total_duration", "One week")
    time_markers = timeline.get("key_time_markers", [])

    # Distribute time markers across scenes
    num_scenes = len(story_data["scenes"])
    if num_scenes > 0 and time_markers:
        # Calculate time per scene with more granularity for larger stories
        time_per_scene = len(time_markers) / num_scenes

        # Update each scene with appropriate time markers
        for i, scene in enumerate(story_data["scenes"]):
            scene_num = i + 1
            marker_index = min(int(i * time_per_scene), len(time_markers) - 1)

            # Calculate time of day based on scene position within the day
            scenes_per_day = max(1, num_scenes // len(time_markers))
            scene_in_day = (i % scenes_per_day) + 1
            time_of_day = ["Morning", "Mid-morning", "Afternoon", "Evening", "Night"][
                min(int((scene_in_day / scenes_per_day) * 5), 4)
            ]

            # Update scene time information
            scene["time_of_day"] = f"{time_markers[marker_index]} - {time_of_day}"
            scene["time_elapsed"] = f"{int((i / num_scenes) * 100)}% of {total_duration}"

            # Add detailed time indicators based on the time of day
            if "Morning" in time_of_day:
                scene["time_indicators"] = ["Morning light", "Fresh start", "Early day", "Sunrise"]
            elif "Mid-morning" in time_of_day:
                scene["time_indicators"] = ["Bright sunlight", "Active morning", "Mid-morning"]
            elif "Afternoon" in time_of_day:
                scene["time_indicators"] = ["Afternoon sun", "Midday", "Active time"]
            elif "Evening" in time_of_day:
                scene["time_indicators"] = ["Sunset", "End of day", "Dusk", "Twilight"]
            else:
                scene["time_indicators"] = ["Night", "Moonlight", "Stars", "Quiet time"]

    return story_data

def track_character_development(story_data):
    """
    Character Development Tracker agent that ensures consistent character progression.
    Enhanced to handle longer character arcs across many scenes.

    Args:
        story_data: The story data to validate and enhance

    Returns:
        Updated story_data with enhanced character development tracking
    """
    if not story_data or "scenes" not in story_data:
        return story_data

    # Get main character info
    main_character = story_data.get("main_character", {})
    if not main_character:
        return story_data

    # Define detailed character development stages for longer stories
    development_stages = {
        1: "Introduction and initial state",
        2: "First challenges and reactions",
        3: "Early growth and learning",
        4: "Developing skills and confidence",
        5: "Facing major obstacles",
        6: "Overcoming challenges",
        7: "Achieving significant progress",
        8: "Final challenges and tests",
        9: "Transformation and resolution",
        10: "New beginning and future outlook"
    }

    # Track character's emotional and developmental journey
    num_scenes = len(story_data["scenes"])
    for i, scene in enumerate(story_data["scenes"]):
        scene_num = i + 1
        stage_index = min(int((scene_num / num_scenes) * len(development_stages)) + 1, len(development_stages))

        # Update scene with character development info
        scene["character_development_stage"] = development_stages[stage_index]

        # Add detailed emotional state based on development stage
        if stage_index == 1:
            scene["emotional_state"] = "Curious and hopeful"
            scene["emotional_indicators"] = ["Eager expression", "Open body language", "Bright eyes"]
        elif stage_index == 2:
            scene["emotional_state"] = "Challenged but determined"
            scene["emotional_indicators"] = ["Focused expression", "Determined posture", "Slight tension"]
        elif stage_index == 3:
            scene["emotional_state"] = "Learning and growing"
            scene["emotional_indicators"] = ["Confident expression", "Active engagement", "Positive energy"]
        elif stage_index == 4:
            scene["emotional_state"] = "Building confidence"
            scene["emotional_indicators"] = ["Strong posture", "Clear communication", "Leadership presence"]
        elif stage_index == 5:
            scene["emotional_state"] = "Facing major challenges"
            scene["emotional_indicators"] = ["Intense focus", "Strategic thinking", "Resilient attitude"]
        elif stage_index == 6:
            scene["emotional_state"] = "Overcoming obstacles"
            scene["emotional_indicators"] = ["Determined expression", "Strategic actions", "Problem-solving focus"]
        elif stage_index == 7:
            scene["emotional_state"] = "Achieving progress"
            scene["emotional_indicators"] = ["Proud expression", "Accomplished posture", "Confident presence"]
        elif stage_index == 8:
            scene["emotional_state"] = "Final challenges"
            scene["emotional_indicators"] = ["Focused determination", "Strategic thinking", "Resilient attitude"]
        elif stage_index == 9:
            scene["emotional_state"] = "Transformation complete"
            scene["emotional_indicators"] = ["Wise expression", "Confident presence", "Peaceful demeanor"]
        else:
            scene["emotional_state"] = "New beginning"
            scene["emotional_indicators"] = ["Hopeful expression", "Forward-looking posture", "Bright future outlook"]

    return story_data

def validate_story_flow(story_data):
    """
    Story Flow Validator agent that ensures logical progression and consistency.
    Enhanced to handle complex story structures with many scenes.

    Args:
        story_data: The story data to validate

    Returns:
        Updated story_data with enhanced flow and consistency
    """
    if not story_data or "scenes" not in story_data:
        return story_data

    scenes = story_data["scenes"]
    num_scenes = len(scenes)

    # Define story structure for longer narratives
    story_structure = {
        "setup": (0, 0.2),  # First 20%
        "rising_action": (0.2, 0.5),  # Next 30%
        "climax": (0.5, 0.8),  # Next 30%
        "resolution": (0.8, 1.0)  # Final 20%
    }

    # Validate and enhance scene transitions
    for i in range(num_scenes):
        current_scene = scenes[i]
        next_scene = scenes[i + 1] if i < num_scenes - 1 else None
        prev_scene = scenes[i - 1] if i > 0 else None

        # Determine story phase
        scene_position = i / num_scenes
        current_phase = next(
            (phase for phase, (start, end) in story_structure.items()
             if start <= scene_position < end),
            "setup"
        )

        # Add story phase information
        current_scene["story_phase"] = current_phase

        # Ensure each scene has a clear transition
        if not current_scene.get("transition"):
            if next_scene:
                current_scene["transition"] = f"Leading to {next_scene.get('title', 'the next scene')}"
            else:
                current_scene["transition"] = "The story concludes"

        # Add detailed cause-and-effect relationships
        if prev_scene:
            current_scene["cause_effect"] = {
                "cause": f"Following {prev_scene.get('title', 'previous events')}",
                "effect": current_scene.get("description", ""),
                "connection_strength": "Strong" if i % 3 == 0 else "Moderate"
            }

        # Add narrative tension based on story phase
        if current_phase == "setup":
            current_scene["narrative_tension"] = "Introducing the story world"
        elif current_phase == "rising_action":
            current_scene["narrative_tension"] = "Building towards major events"
        elif current_phase == "climax":
            current_scene["narrative_tension"] = "Reaching the story's peak"
        else:
            current_scene["narrative_tension"] = "Resolving the story's conflicts"

        # Add scene importance indicator
        if i % 5 == 0:  # Every 5th scene is a key scene
            current_scene["scene_importance"] = "Key Scene"
            current_scene["key_elements"].append("Pivotal moment")
        else:
            current_scene["scene_importance"] = "Supporting Scene"

    return story_data

def enhance_story_generation(story_data):
    """
    Main function to enhance story generation with timeline, character, and flow management.

    Args:
        story_data: The initial story data

    Returns:
        Enhanced story data with improved consistency and flow
    """
    # Apply timeline management
    story_data = manage_story_timeline(story_data)

    # Track character development
    story_data = track_character_development(story_data)

    # Validate and enhance story flow
    story_data = validate_story_flow(story_data)

    return story_data

def create_fallback_story(topic_focus, num_scenes=3):
    """
    Create a basic fallback story structure if generation fails.
    """
    # Ensure num_scenes is an integer
    try:
        num_scenes = int(num_scenes)
    except (ValueError, TypeError):
        num_scenes = 3

    return {
        "title": f"A Story About {topic_focus}",
        "premise": f"A simple story about {topic_focus}",
        "story_style": "Movie",
        "num_scenes": num_scenes,
        "main_character": {
            "name": "Main Character",
            "description": "Character description",
            "motivation": "Character motivation",
            "arc": "Character growth arc"
        },
        "timeline": {
            "total_duration": "One day",
            "time_progression": "Morning to evening",
            "key_time_markers": ["Morning", "Afternoon", "Evening"],
            "seasonal_context": "Current season"
        },
        "scenes": [{"scene_number": i+1,
                   "title": f"Scene {i+1}",
                   "description": f"Scene {i+1} of the story",
                   "key_elements": ["character", "setting", "action"],
                   "transition": "The story continues...",
                   "time_of_day": "Morning",
                   "time_elapsed": "0 hours",
                   "time_indicators": ["Morning light", "Fresh start"],
                   "emotional_state": "Neutral",
                   "cinematic_moment": "Key cinematic moment"} for i in range(num_scenes)]
    }

def generate_story_premise(topic_focus, num_scenes=3, story_style="Movie", user_description=None):
    """
    Generate a creative and engaging story premise based on core elements.

    Args:
        topic_focus: The main topic or theme of the story
        num_scenes: Number of scenes in the story (default: 3)
        story_style: The style/genre of the story (default: "Movie")
        user_description: Optional user-provided story description
    """
    query = f"""
    You are a master storyteller and screenwriter creating an engaging cinematic narrative.
    Design a creative and memorable {story_style.lower()} story about '{topic_focus}'.

    {f"User's story idea: {user_description}" if user_description else ""}

    STORY CREATION GUIDELINES:
    1. CINEMATIC ELEMENTS:
       - Create visually striking scenes
       - Use dynamic camera angles and movements
       - Design memorable set pieces
       - Include dramatic lighting and atmosphere
       - Create compelling visual moments
       - Build tension and release

    2. NARRATIVE STRUCTURE:
       - Strong opening that hooks the audience
       - Clear and engaging conflict
       - Satisfying resolution
       - Natural progression between scenes
       - Logical cause-and-effect relationships
       - Cinematic pacing and rhythm

    3. CHARACTER DEVELOPMENT:
       - Main character with clear goals and personality
       - Supporting characters that add depth
       - Natural character growth and learning
       - Emotional journey that resonates
       - Clear motivations and reactions
       - Memorable character moments

    4. STYLE-SPECIFIC ELEMENTS:
       - Follow {story_style} genre conventions
       - Use appropriate tone and atmosphere
       - Include genre-specific elements
       - Maintain style consistency
       - Create appropriate mood
       - Build cinematic tension

    Create a story with exactly {num_scenes} scenes that:
    1. Is visually striking and memorable
    2. Has strong cinematic moments
    3. Features clear character development
    4. Maintains logical progression
    5. Fits the {story_style} style perfectly
    6. Has satisfying emotional arcs
    7. Includes dramatic tension and release

    FORMAT YOUR RESPONSE AS A VALID JSON OBJECT with these fields:
    {{
      "title": "Creative and engaging title",
      "premise": "Brief but compelling story overview",
      "story_style": "{story_style}",
      "num_scenes": {num_scenes},
      "main_character": {{
        "name": "Memorable character name",
        "description": "Vivid character description",
        "motivation": "Clear character motivation",
        "arc": "Engaging character growth arc"
      }},
      "timeline": {{
        "total_duration": "Story time span",
        "time_progression": "Natural time progression",
        "key_time_markers": ["Key moments"],
        "seasonal_context": "Seasonal setting"
      }},
      "scenes": [
        {{
          "scene_number": 1,
          "title": "Creative scene title",
          "description": "Vivid scene description",
          "key_elements": ["Important elements"],
          "transition": "Natural transition to next scene",
          "time_of_day": "Appropriate time",
          "time_elapsed": "Time passed",
          "time_indicators": ["Time cues"],
          "emotional_state": "Character's emotional state",
          "cinematic_moment": "Key cinematic moment"
        }}
      ]
    }}
    """

    model = GenerativeModel('gemini-2.5-flash')
    response = model.generate_content(query)

    try:
        json_match = re.search(r'\{[\s\S]*\}', response.text, re.DOTALL)
        if json_match:
            story_data = json.loads(json_match.group(0))
            # Enhance the generated story with timeline, character, and flow management
            story_data = enhance_story_generation(story_data)
            return story_data
        else:
            raise ValueError("No valid JSON found in response")
    except Exception as e:
        print(f"Error in generate_story_premise: {e}")
        return create_fallback_story(topic_focus, num_scenes)

def generate_initial_story(topic_focus, difficulty, age, autism_level):
    """
    Generator agent that creates the initial story.
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
    You are a professional screenwriter creating an initial draft of a story for children with autism.
    Design a cohesive, logically-sequenced story about '{topic_focus}' with exactly {num_scenes} scenes.

    AUDIENCE CONSIDERATIONS:
    - Age: {age} years old
    - Autism Level: {autism_level}
    - Difficulty: {difficulty}

    STORY REQUIREMENTS:
    1. Clear temporal progression
    2. Consistent character development
    3. Logical cause-and-effect relationships
    4. Appropriate complexity for the audience
    5. Strong educational focus on '{topic_focus}'

    FORMAT YOUR RESPONSE AS A VALID JSON OBJECT with these fields:
    {{
      "title": "Story title",
      "premise": "Story premise",
      "educational_focus": "Educational objective",
      "num_scenes": {num_scenes},
      "main_character": {{
        "name": "Character name",
        "description": "Character description",
        "motivation": "Character motivation",
        "arc": "Character growth arc"
      }},
      "timeline": {{
        "total_duration": "Total time span",
        "time_progression": "Time progression",
        "key_time_markers": ["Time markers"],
        "seasonal_context": "Seasonal context"
      }},
      "scenes": [
        {{
          "scene_number": 1,
          "title": "Scene title",
          "description": "Scene description",
          "key_elements": ["Key elements"],
          "transition": "Transition to next scene",
          "time_of_day": "Time of day",
          "time_elapsed": "Time elapsed",
          "time_indicators": ["Time indicators"]
        }}
      ]
    }}
    """

    model = GenerativeModel('gemini-2.5-flash')
    response = model.generate_content(query)

    try:
        json_match = re.search(r'\{[\s\S]*\}', response.text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
        else:
            raise ValueError("No valid JSON found in response")
    except Exception as e:
        print(f"Error in generate_initial_story: {e}")
        return create_fallback_story(topic_focus, num_scenes)

def critique_story(story_data, topic_focus, difficulty, age, autism_level):
    """
    Critic agent that reviews the story and provides feedback.
    """
    query = f"""
    You are a professional story editor reviewing a story for children with autism.

    STORY TO REVIEW:
    {json.dumps(story_data, indent=2)}

    AUDIENCE CONSIDERATIONS:
    - Age: {age} years old
    - Autism Level: {autism_level}
    - Difficulty: {difficulty}
    - Educational Focus: {topic_focus}

    REVIEW THE STORY FOR:
    1. TEMPORAL CONSISTENCY:
       - Is the timeline logical and consistent?
       - Do time markers make sense?
       - Are transitions between scenes smooth?

    2. CHARACTER DEVELOPMENT:
       - Is the main character's arc clear?
       - Are character motivations consistent?
       - Is character growth shown effectively?

    3. EDUCATIONAL VALUE:
       - Does the story effectively teach about {topic_focus}?
       - Are concepts presented at appropriate complexity?
       - Is learning integrated naturally?

    4. AUTISM ADAPTATION:
       - Is the story appropriate for autism level {autism_level}?
       - Are emotions and social cues clear?
       - Is the structure predictable?

    5. NARRATIVE STRUCTURE:
       - Is the story cohesive?
       - Are scenes well-connected?
       - Is the pacing appropriate?

    PROVIDE SPECIFIC FEEDBACK AND SUGGESTIONS FOR IMPROVEMENT.
    FORMAT YOUR RESPONSE AS A JSON OBJECT with these fields:
    {{
      "strengths": ["List of what works well"],
      "weaknesses": ["List of areas needing improvement"],
      "suggestions": ["Specific suggestions for improvement"],
      "critical_issues": ["Any major issues that must be fixed"],
      "minor_issues": ["Smaller issues that could be improved"]
    }}
    """

    model = GenerativeModel('gemini-2.5-flash')
    response = model.generate_content(query)

    try:
        json_match = re.search(r'\{[\s\S]*\}', response.text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
        else:
            raise ValueError("No valid JSON found in response")
    except Exception as e:
        print(f"Error in critique_story: {e}")
        return {
            "strengths": [],
            "weaknesses": [],
            "suggestions": [],
            "critical_issues": [],
            "minor_issues": []
        }

def refine_story(story_data, critique, topic_focus, difficulty, age, autism_level):
    """
    Refiner agent that improves the story based on the critique.
    """
    query = f"""
    You are a professional story editor tasked with improving a story based on feedback.

    ORIGINAL STORY:
    {json.dumps(story_data, indent=2)}

    CRITIQUE:
    {json.dumps(critique, indent=2)}

    AUDIENCE CONSIDERATIONS:
    - Age: {age} years old
    - Autism Level: {autism_level}
    - Difficulty: {difficulty}
    - Educational Focus: {topic_focus}

    IMPROVE THE STORY BY:
    1. Addressing all critical issues
    2. Implementing suggested improvements
    3. Maintaining the story's core strengths
    4. Ensuring temporal consistency
    5. Enhancing character development
    6. Strengthening educational value
    7. Optimizing for autism adaptation

    FORMAT YOUR RESPONSE AS A VALID JSON OBJECT with the same structure as the original story.
    """

    model = GenerativeModel('gemini-2.5-flash')
    response = model.generate_content(query)

    try:
        json_match = re.search(r'\{[\s\S]*\}', response.text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
        else:
            raise ValueError("No valid JSON found in response")
    except Exception as e:
        print(f"Error in refine_story: {e}")
        return story_data  # Return original story if refinement fails

def generate_scene_prompt(scene_data, story_premise, image_style="Movie", difficulty=None, age=None, autism_level=None):
    """
    Generate a concise and visually rich scene prompt.

    Args:
        scene_data: The scene data dictionary
        story_premise: The story premise or data (can be string or dict)
        image_style: The style of the image (default: "Movie")
        difficulty: Optional difficulty level (kept for backward compatibility)
        age: Optional age parameter (kept for backward compatibility)
        autism_level: Optional autism level (kept for backward compatibility)
    """

    # Get style specifications
    style_enhancement = get_style_prompt_enhancement(image_style)
    scene_number = scene_data.get("scene_number", 1)
    scene_title = scene_data.get("title", f"Scene {scene_number}")
    scene_description = scene_data.get("description", "")
    emotional_state = scene_data.get("emotional_state", "Neutral")
    time_of_day = scene_data.get("time_of_day", "morning")

    # Handle story_premise whether it's a string or dict
    if isinstance(story_premise, str):
        main_character = {}
        story_premise_text = story_premise
    else:
        main_character = story_premise.get("main_character", {})
        story_premise_text = story_premise.get("premise", "")

    query = f"""Create a {image_style.lower()} scene prompt for: "{scene_title}"

SCENE: {scene_description}
CHARACTER: {main_character.get('name', 'Main Character')} - {main_character.get('description', 'Character description')}
MOOD: {emotional_state} | TIME: {time_of_day}
STYLE: {style_enhancement}

FORMAT: Start with "A {image_style.lower()} scene showing..."
Include specific details for composition, lighting, colors, and character actions.
End with: "Professional {image_style.lower()} quality, crystal clear focus"

Create your prompt (150-200 words):"""

    model = GenerativeModel('gemini-2.5-flash')
    response = model.generate_content(query)
    # Fallback if no text is returned
    if hasattr(response, 'text') and response.text:
        return response.text.strip()
    else:
        print("[ScenePrompt] No text returned from model. Using fallback prompt.")
        return f"A cinematic scene showing: {scene_description} (Fallback prompt)"

def get_story_arc_position(scene_number, total_scenes):
    """Determine the position in the story arc (beginning, middle, end)"""
    if scene_number == 1:
        return "Beginning (Setup)"
    elif scene_number == total_scenes:
        return "End (Resolution)"
    elif scene_number <= total_scenes * 0.3:
        return "Early Middle (Rising Action)"
    elif scene_number >= total_scenes * 0.7:
        return "Late Middle (Climax)"
    else:
        return "Middle (Development)"

def get_emotional_arc(scene_number, total_scenes):
    """Determine the emotional arc position"""
    if scene_number == 1:
        return "Introduction (Neutral/Curious)"
    elif scene_number == total_scenes:
        return "Resolution (Satisfied/Learned)"
    elif scene_number <= total_scenes * 0.3:
        return "Building (Excited/Interested)"
    elif scene_number >= total_scenes * 0.7:
        return "Intense (Focused/Determined)"
    else:
        return "Developing (Engaged/Learning)"

def format_previous_scene_context(previous_scene):
    """Format the context from the previous scene"""
    if not previous_scene:
        return "No previous scene"
    return f"""
    - Title: {previous_scene.get('title', 'Previous Scene')}
    - Key Events: {previous_scene.get('description', 'No description')}
    - Time: {previous_scene.get('time_of_day', 'Unknown')}
    - Emotional State: {get_character_emotional_state(previous_scene)}
    - Key Elements: {', '.join(previous_scene.get('key_elements', []))}
    - Transition: {previous_scene.get('transition', 'No transition')}
    """

def format_next_scene_context(next_scene):
    """Format the context for the next scene"""
    if not next_scene:
        return "No next scene"
    return f"""
    - Title: {next_scene.get('title', 'Next Scene')}
    - Setup: {next_scene.get('description', 'No description')}
    - Time: {next_scene.get('time_of_day', 'Unknown')}
    - Key Elements: {', '.join(next_scene.get('key_elements', []))}
    """

def get_active_threads(scene_data):
    """Get the active narrative threads in the scene"""
    return ', '.join(scene_data.get('storyline_tracking', {}).get('active_threads', []))

def get_resolved_threads(scene_data):
    """Get the resolved narrative threads in the scene"""
    return ', '.join(scene_data.get('storyline_tracking', {}).get('resolved_threads', []))

def get_new_threads(scene_data):
    """Get the new narrative threads introduced in the scene"""
    return ', '.join(scene_data.get('storyline_tracking', {}).get('next_setups', []))

def get_character_emotional_state(scene_data):
    """Get the character's emotional state in the scene"""
    return scene_data.get('emotional_state', 'Neutral')

def get_character_growth_progress(scene_number, total_scenes):
    """Determine the character's growth progress"""
    if scene_number == 1:
        return "Beginning of journey"
    elif scene_number == total_scenes:
        return "Full growth achieved"
    elif scene_number <= total_scenes * 0.3:
        return "Early development"
    elif scene_number >= total_scenes * 0.7:
        return "Near completion"
    else:
        return "Significant progress"

def validate_story_continuity(story_data):
    """Check for consistency across all scenes in the story"""
    consistency_errors = []
    characters = {}
    settings = {}
    # Narrative thread validation
    active_threads = set()
    for i, scene in enumerate(story_data["scenes"]):
        tracking = scene.get("storyline_tracking", {})

        # Verify all previous callbacks reference actual threads
        for callback in tracking.get("previous_callbacks", []):
            if callback not in active_threads:
                consistency_errors.append(
                    f"Scene {i+1}: Callback to non-existent thread '{callback}'"
                )

        # Verify new threads don't exceed limit
        new_threads = set(tracking.get("next_setups", [])) - active_threads
        if len(active_threads) + len(new_threads) > 3:
            consistency_errors.append(
                f"Scene {i+1}: Too many active threads ({len(active_threads) + len(new_threads)})"
            )

        # Update active threads
        active_threads.update(tracking.get("next_setups", []))
        active_threads.difference_update(tracking.get("resolved_threads", []))

    for i, scene in enumerate(story_data["scenes"]):
        # Check character consistency
        for element in scene.get("key_elements", []):
            if "character" in element.lower():
                if element not in characters:
                    characters[element] = {
                        "first_appearance": i+1,
                        "description": element
                    }
                else:
                    # Verify consistent description
                    if characters[element]["description"] != element:
                        consistency_errors.append(
                            f"Character inconsistency in scene {i+1}: {element}"
                        )

        # Check setting continuity
        if "setting" in scene.get("description", "").lower():
            if i > 0 and "same location" in scene.get("transition", "").lower():
                if settings.get(i-1) != settings.get(i):
                    consistency_errors.append(
                        f"Setting discontinuity between scenes {i} and {i+1}"
                    )
                    # Check transition techniques
                    transitions = scene.get("transition_techniques", {})
                    if i > 0:
                        prev_transitions = story_data["scenes"][i-1].get("transition_techniques", {})

                        # Verify visual match elements
                        if not transitions.get("visual_match"):
                            consistency_errors.append(
                                f"Scene {i+1}: Missing visual match element"
                            )

                        # Verify motion vector consistency
                        if (prev_transitions.get("motion_vector") and
                            transitions.get("motion_vector") and
                            prev_transitions["motion_vector"] != transitions["motion_vector"]):
                            consistency_errors.append(
                                f"Scene {i+1}: Motion vector discontinuity from previous scene"
                            )

    return {
        "is_consistent": len(consistency_errors) == 0,
        "errors": consistency_errors,
        "character_tracking": characters
    }

def evaluate_story_understanding(user_description, story_data, current_scene, active_session):
    """
    Evaluate the user's understanding of the story based on their description.

    Args:
        user_description: The child's description of the scene
        story_data: The overall story data
        current_scene: The current scene number
        active_session: The active session data

    Returns:
        A JSON object with:
        - feedback: Encouraging feedback on what they described well
        - story_understanding_score: 0-100 score on overall story comprehension
        - scene_details_score: 0-100 score on current scene detail identification
        - narrative_connection_score: 0-100 score on understanding scene's place in story
        - identified_elements: Key story elements they correctly identified
        - missed_elements: Important elements they missed
        - hint: A gentle hint about story progression
        - question_prompt: A question to help them think more about the story
        - advance_to_next_scene: Whether they're ready for the next scene
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

def evaluate_full_story_understanding(user_description, story_data, active_session):
    """
    Evaluate the user's understanding of the entire story based on their description.

    Args:
        user_description: The child's description of the full story
        story_data: The overall story data
        active_session: The active session data

    Returns:
        A JSON object with:
        - feedback: Encouraging feedback on their understanding of the whole story
        - story_understanding_score: 0-100 score on overall story comprehension
        - narrative_coherence_score: 0-100 score on understanding story flow and connections
        - character_understanding_score: 0-100 score on character recognition and development
        - identified_themes: Major themes they correctly identified
        - missed_themes: Important themes they missed
        - identified_sequence: Story events they mentioned in correct order
        - story_completion_understanding: How well they understand the story's conclusion
        - hint: A gentle hint about story elements
        - question_prompt: A question to help them think more about the overall story
    """
    premise = story_data.get("premise", "")
    educational_focus = story_data.get("educational_focus", "")
    total_scenes = len(story_data.get("scenes", []))

    # Create a summary of all scenes for evaluation context
    all_scenes_summary = "Story scenes overview:\n"
    for i, scene in enumerate(story_data.get("scenes", [])):
        all_scenes_summary += f"Scene {i+1}: {scene.get('description', '')}\n"
        if 'key_elements' in scene:
            all_scenes_summary += f"  Key elements: {', '.join(scene['key_elements'])}\n"

    # Get main character information
    main_character = story_data.get("main_character", {})
    character_info = f"Main character: {main_character.get('name', 'Unknown')} - {main_character.get('description', '')}"

    query = f"""
    You're evaluating a child with autism level {active_session.get('autism_level', 'Level 1')} who is describing the ENTIRE STORY.

    FULL STORY INFORMATION:
    - Overall Story Premise: "{premise}"
    - Educational Focus: "{educational_focus}"
    - Total Scenes: {total_scenes}
    - {character_info}

    COMPLETE STORY DETAILS:
    {all_scenes_summary}

    CHILD'S FULL STORY DESCRIPTION:
    "{user_description}"

    EVALUATION TASK:
    Evaluate the child's understanding of:
    1. Overall story narrative and plot progression
    2. Character development throughout the story
    3. Beginning, middle, and end structure
    4. Key themes and educational concepts
    5. Cause-effect relationships across the entire story
    6. Emotional journey and character growth
    7. Story resolution and conclusion

    ADAPTATION CONSIDERATIONS:
    - Age: {active_session.get('age', '3')} years old
    - Autism Level: {active_session.get('autism_level', 'Level 1')}
    - For Level 2/3 autism or young children, focus on basic story understanding
    - Recognize that full story comprehension is more complex than individual scenes

    RESPONSE FORMAT (JSON):
    {{
      "feedback": "Encouraging, specific feedback on their understanding of the complete story. Praise any story elements they mentioned.",
      "story_understanding_score": 85,  // 0-100 score on overall story comprehension
      "narrative_coherence_score": 80,  // 0-100 score on understanding story flow and connections
      "character_understanding_score": 75,  // 0-100 score on character recognition and development
      "identified_themes": ["theme1", "theme2"],  // Major themes they correctly identified
      "missed_themes": ["theme3", "theme4"],  // Important themes they missed
      "identified_sequence": ["event1", "event2"],  // Story events they mentioned in correct order
      "story_completion_understanding": 70,  // 0-100 score on understanding story conclusion
      "hint": "A gentle hint about the overall story or its message",
      "question_prompt": "A question to help them think more about the complete story"
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
                "feedback": "Thank you for telling me about the whole story! You shared some interesting details.",
                "story_understanding_score": 50,
                "narrative_coherence_score": 50,
                "character_understanding_score": 50,
                "identified_themes": [],
                "missed_themes": [],
                "identified_sequence": [],
                "story_completion_understanding": 50,
                "hint": "Think about how the story began and how it ended.",
                "question_prompt": "What was your favorite part of the whole story?"
            }
    except Exception as e:
        print(f"Error parsing full story evaluation: {e}")
        # Fallback structure
        return {
            "feedback": "Thank you for telling me about the whole story! You shared some interesting details.",
            "story_understanding_score": 50,
            "narrative_coherence_score": 50,
            "character_understanding_score": 50,
            "identified_themes": [],
            "missed_themes": [],
            "identified_sequence": [],
            "story_completion_understanding": 50,
            "hint": "Think about how the story began and how it ended.",
            "question_prompt": "What was your favorite part of the whole story?"
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
    1. Uses the scene summaries from the story data where available
    2. Recaps what has happened in a simple, clear way
    3. Reinforces the educational concepts being taught
    4. Builds excitement for the next scene (if any remain) using the next_preview info
    5. Celebrates completion (if all scenes are finished)
    6. Explicitly mention character names if they are in the premise

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

def generate_story_key_points(story_data, active_session):
    """
    Generate key points based on the story that the child should describe or deduce.
    This helps guide the child's learning and comprehension of the story.

    Args:
        story_data: The complete story data including premise and scenes
        active_session: The active session data including age and autism level

    Returns:
        A JSON object with:
        - educational_points: Key educational concepts from the story
        - character_points: Important character observations
        - plot_points: Key events or actions to identify
        - emotional_points: Emotional aspects to recognize
        - cause_effect_points: Cause and effect relationships to understand
        - visual_details_points: Important visual elements to notice
        - questions: Guiding questions to help the child engage with the story
    """
    premise = story_data.get("premise", "")
    educational_focus = story_data.get("educational_focus", "")
    num_scenes = len(story_data.get("scenes", []))

    # Format scenes for context
    scenes_text = ""
    for i, scene in enumerate(story_data.get("scenes", [])):
        scenes_text += f"Scene {i+1}: {scene.get('description', '')}\n"
        scenes_text += f"Key Elements: {', '.join(scene.get('key_elements', []))}\n"
        scenes_text += f"Transition: {scene.get('transition', '')}\n\n"

    query = f"""
    You're creating educational key points for a child with autism level {active_session.get('autism_level', 'Level 1')}
    based on a story they are viewing. These key points will help guide their understanding and learning.

    STORY INFORMATION:
    - Story Premise: "{premise}"
    - Educational Focus: "{educational_focus}"
    - Total Scenes: {num_scenes}

    SCENES:
    {scenes_text}

    TASK:
    Create key points that the child should identify or deduce from the story. These points should:
    1. Be appropriate for a {active_session.get('age', '3')}-year-old child with autism level {active_session.get('autism_level', 'Level 1')}
    2. Focus on the educational concepts being taught
    3. Include both obvious and subtle elements that promote learning
    4. Encourage observation, reasoning, and emotional understanding
    5. Be concrete and specific rather than abstract
    6. Progress from simple to more complex understanding

    ADAPTATION CONSIDERATIONS:
    - For Level 1 autism: Include some subtle social cues and emotions
    - For Level 2 autism: Focus more on concrete actions and clear emotional states
    - For Level 3 autism: Emphasize the most basic and explicit story elements
    - Younger children need simpler points focused on recognition
    - Older children can handle more complex cause-and-effect relationships

    FORMAT YOUR RESPONSE AS A VALID JSON OBJECT with these fields:
    {{
      "educational_points": ["Point 1", "Point 2", "Point 3"],  // Key educational concepts from the story
      "character_points": ["Point 1", "Point 2"],  // Important character observations
      "plot_points": ["Point 1", "Point 2", "Point 3"],  // Key events or actions to identify
      "emotional_points": ["Point 1", "Point 2"],  // Emotional aspects to recognize
      "cause_effect_points": ["Point 1", "Point 2"],  // Cause and effect relationships
      "visual_details_points": ["Point 1", "Point 2", "Point 3"],  // Important visual elements to notice
      "questions": ["Question 1?", "Question 2?", "Question 3?"]  // Guiding questions to help engagement
    }}
    """

    model = GenerativeModel('gemini-2.5-flash')
    response = model.generate_content(query)

    try:
        # Find JSON in the response
        json_match = re.search(r'\{[\s\S]*\}', response.text, re.DOTALL)
        if json_match:
            key_points = json.loads(json_match.group(0))
            return key_points
        else:
            # Fallback structure if no valid JSON found
            return {
                "educational_points": [f"Learn about {educational_focus}", "Observe what happens in the story"],
                "character_points": ["Notice who the main characters are", "See what the characters do"],
                "plot_points": ["Beginning: How the story starts", "Middle: What happens next", "End: How the story finishes"],
                "emotional_points": ["How the characters feel", "Why they feel that way"],
                "cause_effect_points": ["What makes things happen", "What happens because of actions"],
                "visual_details_points": ["Important objects in the story", "The setting or place", "Actions that happen"],
                "questions": ["What do you see in the picture?", "What happens in the story?", "How do the characters feel?"]
            }
    except Exception as e:
        print(f"Error parsing story key points: {e}")
        # Return a basic fallback structure
        return {
            "educational_points": [f"Learn about {educational_focus}", "Observe what happens in the story"],
            "character_points": ["Notice who the main characters are", "See what the characters do"],
            "plot_points": ["Beginning: How the story starts", "Middle: What happens next", "End: How the story finishes"],
            "emotional_points": ["How the characters feel", "Why they feel that way"],
            "cause_effect_points": ["What makes things happen", "What happens because of actions"],
            "visual_details_points": ["Important objects in the story", "The setting or place", "Actions that happen"],
            "questions": ["What do you see in the picture?", "What happens in the story?", "How do the characters feel?"]
        }

def generate_story_with_custom_description(topic_focus, user_description, difficulty, age, autism_level):
    """
    Generate a story premise based on the user's custom description.

    Args:
        topic_focus: The educational topic or theme to focus on
        user_description: The user's custom story description
        difficulty: The complexity level of the story
        age: The child's age
        autism_level: The child's autism level

    Returns:
        A JSON object with the same structure as generate_story_premise
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
    You are a professional storyteller and screenwriter designing an engaging, cinematic story for children with autism.

    THE USER HAS PROVIDED THIS CUSTOM STORY DESCRIPTION:
    "{user_description}"

    Your task is to transform this description into a captivating, movie-like story related to the educational topic '{topic_focus}'
    that unfolds in exactly {num_scenes} sequential scenes, each corresponding to a key moment in a narrative arc.

    CHARACTER CONSISTENCY REQUIREMENTS:
    1. MAIN CHARACTER FOCUS:
       - Identify and maintain a single main character throughout the story
       - Ensure the main character's name and appearance remain consistent
       - Show the main character's emotional journey clearly
       - Keep the main character's personality traits stable
       - Make the main character's actions and decisions logical

    2. SUPPORTING CHARACTERS:
       - Limit the number of supporting characters to 2-3 maximum
       - Give each supporting character a clear, consistent role
       - Maintain consistent relationships between characters
       - Ensure character interactions make sense
       - Keep character appearances stable

    3. CHARACTER DEVELOPMENT:
       - Show clear cause-and-effect in character actions
       - Make character emotions and reactions understandable
       - Ensure character growth follows a logical progression
       - Keep character motivations clear and consistent
       - Show how characters learn from their experiences

    Consider:
    - Child's Age: {age}
    - Autism Level: {autism_level}
    - Difficulty Level: {difficulty}
    - Educational Topic: {topic_focus}

    FOLLOW THESE STEPS:
    1. Extract the core narrative elements from the user's description
    2. Develop these elements into a coherent story structure
    3. Ensure it addresses the educational topic of '{topic_focus}'
    4. Adapt the complexity for a child of age {age} with autism level {autism_level}
    5. Structure it into exactly {num_scenes} scenes that form a complete story arc

    CINEMATIC STORYTELLING GUIDELINES:
    1. CREATE MEMORABLE CHARACTERS: Design distinctive characters with clear visual traits and personalities
    2. ESTABLISH A COMPELLING SETTING: Create a vivid, visually interesting world for the story
    3. FOLLOW THE 3-ACT STRUCTURE:
       - Act 1: Introduction/setup of characters and conflict (25%)
       - Act 2: Rising action/challenges/development (50%)
       - Act 3: Climax and resolution (25%)
    4. INCLUDE CLEAR EMOTIONAL ARCS: Show how characters' feelings change through the story
    5. USE VISUAL STORYTELLING: Focus on actions and expressions that tell the story visually

    ADAPTATION FOR AUTISM (LEVEL {autism_level}):
    - Use clear, predictable story patterns
    - Make emotional states visually obvious
    - Avoid overwhelming sensory details
    - Ensure cause-and-effect relationships are explicit
    - Include concrete rather than abstract concepts

    For each scene, provide:
    1. A compelling description of what happens (like a film scene)
    2. Key visual elements that must appear in the scene
    3. How this scene visually transitions to the next scene
    4. Character consistency verification
    5. Emotional progression tracking

    FORMAT YOUR RESPONSE AS A VALID JSON OBJECT with these fields:
    {{
      "title": "An engaging, descriptive title for the story",
      "premise": "Brief overview of the story (1-2 sentences)",
      "educational_focus": "Main learning objective related to {topic_focus}",
      "num_scenes": {num_scenes},
      "main_character": {{
        "name": "Character name",
        "description": "Detailed physical and personality description",
        "motivation": "What drives the character",
        "arc": "How the character will grow through the story"
      }},
      "timeline": {{
        "total_duration": "Total time span of the story",
        "time_progression": "How time progresses through the story",
        "key_time_markers": ["Morning", "Afternoon", "Evening", etc.],
        "seasonal_context": "Season or time of year if relevant"
      }},
      "scenes": [
      {{
      "scene_number": 1,
      "title": "Descriptive scene title",
      "description": "Detailed description of what happens in this scene",
      "summary": "Brief summary reinforcing key points",
      "next_preview": "Clear hint about what's coming next",
      "key_elements": ["element1", "element2", "element3"],
      "transition": "Explicit connection to next scene",
      "character_consistency": "Verification of character/setting continuity",
      "temporal_consistency": "Verification that time progression is logical and consistent"
      }},
        // Additional scenes...
      ]
    }}

    IMPORTANT:
    - Maintain the spirit and main elements of the user's description
    - The story MUST have a coherent beginning, middle, and end with a clear narrative arc
    - Characters must be consistent across all scenes
    - The story should be educational and relate to '{topic_focus}'
    - The main character must be the focus of the story and their journey must be clearly shown
    - Time progression must be logical and consistent throughout the story.
    - Cause-and-effect relationships must respect realistic timeframes.
    - Environmental changes must follow natural patterns.
    """

    model = GenerativeModel('gemini-2.5-flash')
    response = model.generate_content(query)

    try:
        # Find JSON in the response
        json_match = re.search(r'\{[\s\S]*\}', response.text, re.DOTALL)
        if json_match:
            story_data = json.loads(json_match.group(0))
            # Enhance the generated story with timeline, character, and flow management
            story_data = enhance_story_generation(story_data)
            return story_data
        else:
            # Fallback structure if no valid JSON found
            return {
                "title": f"A Story About {topic_focus}",
                "premise": f"A story about {topic_focus} based on user description: {user_description[:50]}...",
                "educational_focus": topic_focus,
                "num_scenes": num_scenes,
                "main_character": {
                    "name": "Main Character",
                    "description": "Character description",
                    "motivation": "Character motivation",
                    "arc": "Character growth arc"
                },
                "timeline": {
                    "total_duration": "One day",
                    "time_progression": "Morning to evening",
                    "key_time_markers": ["Morning", "Afternoon", "Evening"],
                    "seasonal_context": "Current season"
                },
                "scenes": [{"scene_number": i+1,
                           "title": f"Scene {i+1}",
                           "description": f"Scene {i+1} of the story",
                           "key_elements": ["character", "setting", "action"],
                           "transition": "The story continues...",
                           "character_consistency": "Character consistency check",
                           "temporal_consistency": "Time progression check",
                           "time_of_day": "Morning",
                           "time_elapsed": "0 hours",
                           "time_indicators": ["Morning light", "Fresh start"]} for i in range(num_scenes)]
            }
    except Exception as e:
        print(f"Error parsing story with custom description: {e}")
        # Return a basic fallback structure
        return {
            "title": f"A Story About {topic_focus}",
            "premise": f"A story about {topic_focus} based on user description: {user_description[:50]}...",
            "educational_focus": topic_focus,
            "num_scenes": num_scenes,
            "main_character": {
                "name": "Main Character",
                "description": "Character description",
                "motivation": "Character motivation",
                "arc": "Character growth arc"
            },
            "timeline": {
                "total_duration": "One day",
                "time_progression": "Morning to evening",
                "key_time_markers": ["Morning", "Afternoon", "Evening"],
                "seasonal_context": "Current season"
            },
            "scenes": [{"scene_number": i+1,
                       "title": f"Scene {i+1}",
                       "description": f"Scene {i+1} of the story",
                       "key_elements": ["character", "setting", "action"],
                       "transition": "The story continues...",
                       "character_consistency": "Character consistency check",
                       "temporal_consistency": "Time progression check",
                       "time_of_day": "Morning",
                       "time_elapsed": "0 hours",
                       "time_indicators": ["Morning light", "Fresh start"]} for i in range(num_scenes)]
        }

def generate_detailed_scene_description(scene_data, story_data, scene_number):
    """
    Generate a detailed and engaging description for a scene.

    Args:
        scene_data: The scene data dictionary
        story_data: The complete story data
        scene_number: The current scene number

    Returns:
        Enhanced scene description with rich details
    """
    # Get story context
    main_character = story_data.get("main_character", {})
    timeline = story_data.get("timeline", {})
    total_scenes = len(story_data.get("scenes", []))

    # Get scene-specific information
    time_of_day = scene_data.get("time_of_day", "")
    emotional_state = scene_data.get("emotional_state", "")
    character_development = scene_data.get("character_development_stage", "")
    story_phase = scene_data.get("story_phase", "")
    scene_importance = scene_data.get("scene_importance", "")

    # Generate rich scene description
    description = f"""
    In this {scene_importance.lower()}, {main_character.get('name', 'the main character')} is {emotional_state.lower()}.
    The scene takes place during {time_of_day}, with {', '.join(scene_data.get('time_indicators', []))} visible in the environment.

    {main_character.get('name', 'The character')} is currently in the {character_development.lower()} stage of their journey.
    This is a {story_phase} moment in the story, where {scene_data.get('narrative_tension', 'the tension builds')}.

    The scene features:
    - {', '.join(scene_data.get('key_elements', []))}
    - {', '.join(scene_data.get('emotional_indicators', []))}
    - A clear sense of {scene_data.get('time_elapsed', 'time progression')}

    The environment reflects the {emotional_state.lower()} mood, with appropriate lighting and atmosphere.
    {main_character.get('name', 'The character')}'s actions and expressions clearly show their current emotional state.
    """

    # Add specific details based on story phase
    if story_phase == "setup":
        description += """
        This is an important establishing scene that introduces key elements and sets up the story's foundation.
        The environment and characters are introduced in a way that makes their roles and relationships clear.
        """
    elif story_phase == "rising_action":
        description += """
        The stakes are rising, and the challenges are becoming more significant.
        The scene builds tension and develops the main conflict in an engaging way.
        """
    elif story_phase == "climax":
        description += """
        This is a pivotal moment in the story where major conflicts come to a head.
        The scene is intense and emotionally charged, with high stakes and dramatic tension.
        """
    else:  # resolution
        description += """
        The scene brings closure to the story's main conflicts and shows the character's growth.
        There's a sense of resolution and completion, while still maintaining engagement.
        """

    return description.strip()

def enhance_scene_prompt(scene_data, story_data, scene_number):
    """
    Generate an enhanced prompt for scene visualization.

    Args:
        scene_data: The scene data dictionary
        story_data: The complete story data
        scene_number: The current scene number

    Returns:
        Rich, detailed prompt for scene visualization
    """
    # Get story context
    main_character = story_data.get("main_character", {})
    timeline = story_data.get("timeline", {})

    # Generate detailed scene description
    scene_description = generate_detailed_scene_description(scene_data, story_data, scene_number)

    # Create visualization prompt
    prompt = f"""
    Create a visually stunning scene that captures the following story moment:

    SCENE CONTEXT:
    {scene_description}

    VISUAL ELEMENTS:
    - Time of Day: {scene_data.get('time_of_day', '')}
    - Lighting: Appropriate for {scene_data.get('time_of_day', '').split(' - ')[-1]}
    - Atmosphere: Reflecting {scene_data.get('emotional_state', '')}
    - Key Elements: {', '.join(scene_data.get('key_elements', []))}

    CHARACTER DETAILS:
    - Main Character: {main_character.get('name', '')}
    - Appearance: {main_character.get('description', '')}
    - Emotional State: {scene_data.get('emotional_state', '')}
    - Body Language: {', '.join(scene_data.get('emotional_indicators', []))}

    COMPOSITION REQUIREMENTS:
    1. Create a visually striking composition that guides the viewer's eye
    2. Use appropriate lighting to match the time of day and emotional tone
    3. Include all key elements in a natural, balanced arrangement
    4. Show clear character emotions through expression and body language
    5. Create depth and dimension in the scene
    6. Use color and contrast to enhance the mood

    STYLE GUIDELINES:
    - Professional cinematic quality
    - High attention to detail
    - Clear visual storytelling
    - Appropriate mood and atmosphere
    - Consistent with the story's style
    """

    return prompt.strip()

def generate_story_sequence(topic_focus, difficulty, age, autism_level, num_scenes=3):
    """
    Generate a complete story sequence with enhanced scene descriptions.

    Args:
        topic_focus: The main topic or theme
        difficulty: The difficulty level
        age: The target age
        autism_level: The autism level
        num_scenes: Number of scenes (default: 3)

    Returns:
        Complete story data with enhanced scene descriptions
    """
    # Generate initial story premise
    story_data = generate_story_premise(topic_focus, num_scenes)

    # Enhance the story with timeline, character, and flow management
    story_data = enhance_story_generation(story_data)

    # Generate detailed descriptions for each scene
    for i, scene in enumerate(story_data["scenes"]):
        scene_number = i + 1
        # Generate detailed scene description
        scene["detailed_description"] = generate_detailed_scene_description(scene, story_data, scene_number)
        # Generate enhanced visualization prompt
        scene["visualization_prompt"] = enhance_scene_prompt(scene, story_data, scene_number)

    return story_data
