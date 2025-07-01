import base64
import json
import re
import math
from google.generativeai import GenerativeModel
from google.ai.generativelanguage import Content, Part
import PIL.Image
import io

def generate_detailed_description(image, story_prompt, topic_focus):
    """
    Generate a detailed textual description of a comic image using Gemini Vision Pro.
    The prompt is now standardized for moderate complexity.
    """
    try:
        model = GenerativeModel("gemini-2.0-flash-001")

        # Standardized prompt focusing on moderate complexity
        prompt = f"""
Analyze the following comic image, which is based on the theme: '{story_prompt}'.

The target audience is children, and the educational focus is on '{topic_focus}'. Please provide a detailed, family-friendly description of what you see.

Your description should be:
- Comprehensive: Cover the main characters, setting, and key actions across all panels.
- Clear and Simple: Use language that is easy for a child to understand.
- Objective: Describe what is visually present in the image.
- Structured: Organize the description logically, perhaps by panels or a general overview.

Focus on creating a single, cohesive narrative that ties all the visual elements together into a simple story.
"""

        response = model.generate_content([prompt, image])

        return response.text
    except Exception as e:
        print(f"Error during detailed description generation: {e}")
        return "Could not generate a detailed description for the image."

def extract_key_details(image_input, prompt, topic_focus):
    """
    Extract key details directly from the image using Gemini Vision.
    Returns a list of key elements/details from the image.
    """
    # Check if image_input is None
    if image_input is None:
        return ["Error: No image provided"]

    try:
        # Convert the image to base64 format depending on the input type
        if hasattr(image_input, 'save'):  # This is a PIL Image
            buffer = io.BytesIO()
            image_input.save(buffer, format="PNG")
            img_bytes = buffer.getvalue()
            base64_img = base64.b64encode(img_bytes).decode('utf-8')
        elif isinstance(image_input, str) and image_input.startswith('data:image'):
            # This is a data URL
            base64_img = image_input.split(",")[1]
        else:
            return ["Error: Unsupported image format"]

        query = (
            f"""
            You are analyzing a COMPLEX MULTI-SCENE educational image created for a person with autism, based on the prompt: "{prompt}".
            The image focuses on the topic: "{topic_focus}".

            This image contains 12-15 distinct scenes or vignettes with extensive detail. Your task is to extract a comprehensive list of key details across ALL scenes.

            EXTRACTION REQUIREMENTS:
            1. SCENE ANALYSIS: Systematically examine each identifiable scene/area in the image (foreground, middle ground, background, left, right, center, top, bottom)
            2. DETAIL CATEGORIES: Extract details from these categories:
               - Objects and items (furniture, tools, toys, vehicles, etc.)
               - People and characters (clothing, expressions, poses, activities)
               - Animals and creatures (species, colors, actions, positions)
               - Natural elements (plants, weather, landscapes, water features)
               - Colors and patterns (specific hues, textures, designs)
               - Spatial relationships (positioning, size comparisons)
               - Actions and movements (what's happening, gestures)
               - Environmental details (lighting, atmosphere, time indicators)
               - Text or symbols (signs, numbers, letters visible)
               - Architectural elements (buildings, structures, decorations)

            3. DETAIL QUANTITY: Extract 25-45 unique details (significantly more than simple images due to multi-scene complexity)
            4. DETAIL SPECIFICITY: Each detail should include:
               - What it is
               - Where it's located (which part of image/scene)
               - Key visual characteristics (color, size, condition)

            5. PROGRESSIVE DIFFICULTY ADAPTATION:
               - For "Very Simple" difficulty: Focus on basic, obvious elements
               - For "Simple" difficulty: Include secondary objects and basic relationships
               - For "Medium" difficulty: Add detailed descriptions and spatial relationships
               - For "Complex" difficulty: Include subtle details, background elements, and nuanced observations
               - For "Very Complex" difficulty: Extract fine details, partial objects, reflections, shadows, and complex interactions

            Format your response as a JSON array of strings, each representing one key detail with location context.
            Example format: ["red wooden toy car in the center foreground", "smiling girl with brown braided hair in the left scene", "fluffy white clouds in the upper right sky", "green oak tree with textured bark in the background left", "yellow sunlight streaming from the top right corner"]

            Ensure each detail is:
            1. Directly observable in the image
            2. Unique and non-redundant
            3. Described with specific, concrete language
            4. Includes spatial/scene location context
            5. Appropriate for autism education (clear, unambiguous)
            6. Covers multiple scenes/areas of the image
            7. Ranges from obvious to subtle based on difficulty level
            8. Uses precise color names and descriptive adjectives
            9. Includes both primary subjects and supporting elements
            10. Captures the educational value relevant to "{topic_focus}"

            SYSTEMATIC APPROACH:
            1. First, identify all major scenes/areas in the image
            2. For each scene, extract 2-4 key details
            3. Add cross-scene relationships and overall composition details
            4. Include environmental and atmospheric details
            5. Ensure coverage of all visual elements that support learning objectives

            Remember: This is a highly detailed, multi-scene educational image - extract accordingly!
            """
        )
        vision_model = GenerativeModel('gemini-2.0-flash-001')
        image_part = Part(inline_data={"mime_type": "image/png", "data": base64.b64decode(base64_img)})
        text_part = Part(text=query)
        multimodal_content = Content(parts=[image_part, text_part])
        response = vision_model.generate_content(multimodal_content)
        try:
            details_match = re.search(r'\[.*\]', response.text, re.DOTALL)
            if details_match:
                details_json = details_match.group(0)
                key_details = json.loads(details_json)
                return key_details
            else:
                # If no JSON array is found, try to extract bullet points or lines
                lines = response.text.split('\n')
                details = []
                for line in lines:
                    if line.strip().startswith('-') or line.strip().startswith('*'):
                        details.append(line.strip()[1:].strip())
                return details[:45] if details else ["object in image", "color", "shape", "background", "foreground element", "scene composition"]
        except Exception as e:
            print(f"Error extracting key details from response: {str(e)}")
            return ["object in image", "color", "shape", "background"]
    except Exception as e:
        print(f"Error in extract_key_details: {str(e)}")
        return ["Error processing image", "Please try again"]

def compare_details_chat_fn(user_details, active_session, global_image_data_url, global_image_description):
    """
    Evaluate the user's description with a strong focus on conceptual understanding
    and semantic meaning, rather than exact word matching.
    """
    if not global_image_data_url or not global_image_description:
        return "Please generate an image first."

    image_description = active_session.get("image_description", global_image_description)
    chat_history = active_session.get("chat", [])
    history_text = ""
    if chat_history:
        history_text = "\n### Previous Conversation:\n"
        for idx, (speaker, msg) in enumerate(chat_history, 1):
            history_text += f"Turn {idx}:\n{speaker}: {msg}\n"

    key_details = active_session.get("key_details", [])
    identified_details = active_session.get("identified_details", [])
    used_hints = active_session.get("used_hints", [])

    # Filter out key details that have already been identified
    remaining_key_details = [kd for kd in key_details if kd not in identified_details]

    # Format for display
    key_details_text = "\n### Key Details to Identify (Focus on these remaining ones):\n" + "\n".join(f"- {detail}" for detail in remaining_key_details)
    identified_details_text = ""
    if identified_details:
        identified_details_text = "\n### Previously Identified Details:\n" + "\n".join(f"- {detail}" for detail in identified_details)

    used_hints_text = ""
    if used_hints:
        used_hints_text = "\n### Previously Given Hints:\n" + "\n".join(f"- {hint}" for hint in used_hints)

    current_difficulty = active_session.get("difficulty", "Very Simple")
    autism_level = active_session.get("autism_level", "Level 1")
    age = active_session.get("age", "")

    message_text = (
        f"You are a highly specialized, supportive, and insightful teacher evaluating an image description provided by an individual with autism.\n"
        f"Your primary goal is to understand if the user has grasped the CONCEPTS present in this COMPLEX MULTI-SCENE educational image, not just if they used specific words.\n\n"
        f"### COMPLEX IMAGE CONTEXT:\n"
        f"- Original Enhanced Prompt: {active_session.get('prompt', 'No prompt available')}\n"
        f"- Topic Focus: {active_session.get('topic_focus', 'General Observation')}\n"
        f"- Multi-Scene Composition: This image contains 12-15 distinct scenes with 25-45 identifiable details\n"
        f"- Detailed Image Description (Reference Only): {image_description}\n\n"
        f"### User Information:\n"
        f"- Age: {age}\n"
        f"- Autism Level: {autism_level}\n"
        f"- Current Difficulty Level: {current_difficulty}\n\n"
        f"### COMPLEX LEARNING TASK STATE:\n"
        f"- Total Key Details Available: {len(key_details)} (distributed across multiple scenes)\n"
        f"- Details Already Identified: {len(identified_details)}\n"
        f"- Remaining Details to Find: {len(remaining_key_details)}\n"
        f"{key_details_text}"  # Focus evaluation on REMAINING details
        f"{identified_details_text}"
        f"{used_hints_text}"
        f"{history_text}\n"
        f"### User's Current Description (Analyze this carefully):\n'{user_details}'\n\n"
        "----------------------------------------------------\n"
        "### YOUR CRITICAL TASK: ENHANCED MULTI-SCENE CONCEPTUAL EVALUATION\n"
        "Analyze the \"User's Current Description\" and determine which CONCEPTS from the \"Key Details to Identify\" list the user has successfully understood and conveyed across the complex multi-scene composition. Apply the following enhanced rules rigorously:\n\n"
        "### ENHANCED CONCEPTUAL MATCHING RULES FOR COMPLEX IMAGES:\n"
        "1.  **PRIORITIZE MEANING OVER WORDS:** Focus entirely on the SEMANTIC MEANING and the underlying IDEA the user is trying to express. Ignore exact phrasing, grammar, or spelling mistakes.\n"
        "2.  **MULTI-SCENE AWARENESS:** Recognize that users may describe elements from different scenes in the same sentence. Credit understanding even if scene locations aren't perfectly specified.\n"
        "3.  **CONCEPTUAL EQUIVALENCE:** Does the user's statement describe the core concept of a key detail? If yes, it's a match. (e.g., Key Detail: 'Smiling boy waving in left foreground'. User says: 'happy person saying hi' -> MATCHES).\n"
        "4.  **FLEXIBLE INTERPRETATION:** Individuals with autism may use unique, literal, or roundabout phrasing. Interpret generously. Give the benefit of the doubt. Assume competence and focus on their likely intended meaning.\n"
        "5.  **PARTIAL CONCEPTS COUNT:** Especially for Level 2/3 autism, younger ages, or simpler difficulty levels, credit partial understanding. (e.g., Key Detail: 'Large red delivery truck in background scene'. User says: 'big red thing far away' -> MATCHES, as they grasped size, color, and spatial awareness).\n"
        "6.  **SYNONYMS & DESCRIPTIONS:** Accept synonyms, paraphrasing, or descriptive phrases that capture the essence. (e.g., Key Detail: 'Fluffy white cumulus clouds in upper right sky'. User says: 'soft looking things in the sky', 'cotton balls up high' -> MATCHES).\n"
        "7.  **SCENE INTEGRATION:** Credit users who notice relationships between scenes or overall composition elements, even if not explicitly listed as key details.\n"
        "8.  **FOCUS ON OBSERVABLES:** Match based on what the user likely *observed* in the image, linked back to a key detail concept.\n"
        "9.  **PROGRESSIVE COMPLEXITY AWARENESS:** Adjust expectations based on difficulty level - more complex levels should expect more nuanced observations.\n"
        "10. **GENEROSITY IS KEY:** When uncertain, ERR ON THE SIDE OF GIVING CREDIT. The goal is encouragement and identifying understanding, not strict grading.\n"
        "11. **OUTPUT REQUIREMENT:** If you determine a conceptual match, you MUST include the **EXACT ORIGINAL STRING** from the 'Key Details to Identify' list in the `newly_identified_details` field of your JSON response. DO NOT put the user's words there.\n"
        "12. **SCENE CONTEXT AWARENESS:** When providing feedback and hints, reference spatial locations and scene relationships to help guide the user's attention across the complex composition.\n"
        "13. **PROGRESSIVE DISCLOSURE:** For users who seem overwhelmed by the 25-45 details, focus feedback on smaller areas and suggest manageable next steps.\n\n"
        "### RESPONSE REQUIREMENTS:\n"
        "Provide your evaluation STRICTLY as a valid JSON object with the following ENHANCED structure for multi-scene evaluation:\n"
        "```json\n"
        "{\n"
        "  \"feedback\": \"(String) Your encouraging, supportive, and specific feedback to the user. Praise what they identified correctly (conceptually). Reference which scenes or areas they described. Avoid sounding repetitive. Tailor to age/level. Acknowledge multi-scene awareness.\",\n"
        "  \"newly_identified_details\": [\"(String) Exact key detail 1 matched\", \"(String) Exact key detail 2 matched\"], /* List of EXACT strings from 'Key Details to Identify' that were conceptually matched by the user's LATEST description. Empty list if none matched. */\n"
        "  \"scene_awareness_feedback\": \"(String or null) Specific praise if user showed awareness of multiple scenes, spatial relationships, or composition elements. E.g., 'Great job noticing elements in both the foreground and background!' Use null if not applicable.\",\n"
        "  \"hint\": \"(String or null) Provide ONE gentle, scene-specific hint towards a concept NOT YET identified. Include spatial guidance. E.g., 'I notice something interesting in the upper left corner...' or 'Look carefully at what's happening near the center of the image...'. Use null if no hint needed.\",\n"
        "  \"complexity_hint\": \"(String or null) For higher difficulty levels, provide a more nuanced hint about relationships between scenes or subtle details. E.g., 'Notice how the lighting affects different parts of the image...' Use null if not applicable.\",\n"
        "  \"progress_summary\": \"(String) Brief encouraging summary of overall progress. E.g., 'You've now identified 8 out of 32 details across 4 different scenes - excellent exploration!'\",\n"
        "  \"score\": 75, /* (Integer 0-100) An overall score reflecting conceptual understanding shown in this turn, considering difficulty and effort. Be generous. Factor in multi-scene complexity. */\n"
        "  \"detail_categories_identified\": [\"objects\", \"colors\", \"spatial_relationships\"], /* (Array of strings) Categories of details the user successfully identified (objects, people, animals, colors, textures, spatial_relationships, actions, environment, etc.) */\n"
        "  \"advance_difficulty\": false, /* (Boolean) Set to true ONLY if the user shows strong mastery and significant portion of key details are identified across multiple scenes, suggesting they are ready for a harder challenge. */\n"
        "  \"suggest_scene_focus\": \"(String or null) If user seems overwhelmed by complexity, suggest a specific scene or area to focus on next. E.g., 'Try focusing on just the left side of the image for now.' Use null if not needed.\"\n"
        "}\n"
        "```\n\n"
        "### ENHANCED FINAL CHECKLIST FOR MULTI-SCENE EVALUATION:\n"
        "- Did I focus ONLY on conceptual understanding across all scenes?\n"
        "- Did I interpret the user's words generously and flexibly, considering multi-scene complexity?\n"
        "- Does `newly_identified_details` contain the EXACT STRINGS from the key details list?\n"
        "- Is the feedback positive, specific, scene-aware, and appropriate for the complexity level?\n"
        "- Are the hints (both regular and complexity) subtle, spatial, and guiding (or null)?\n"
        "- Did I acknowledge the user's progress across the large number of available details?\n"
        "- Are the detail categories accurately reflecting what the user identified?\n"
        "- Is the advancement consideration appropriate for multi-scene mastery?\n"
        "- Is the entire response a single, valid JSON object with all enhanced fields?\n\n"
        "Now, analyze the user's description based on these instructions and provide the JSON evaluation."
    )

    try:
        model = GenerativeModel('gemini-2.0-flash-001-lite-preview-06-17') # Ensure you are using an appropriate model capable of following complex instructions
        response = model.generate_content(message_text)
        # Adding print statements for debugging
        print("--- LLM Evaluation Prompt Sent ---")
        # print(message_text) # Uncomment for full prompt debugging
        print("--- LLM Evaluation Response Received ---")
        print(response.text)
        print("--- End LLM Evaluation Response ---")
        return response.text
    except Exception as e:
        print(f"Error during LLM call in compare_details_chat_fn: {str(e)}")
        # Fallback response in case of API error
        return json.dumps({
            "feedback": "I'm having a little trouble processing that right now, but thanks for sharing your observations! Let's try again.",
            "newly_identified_details": [],
            "hint": None,
            "score": 0,
            "advance_difficulty": False
        })

def parse_evaluation(evaluation_text, active_session):
    """
    Parse the evaluation JSON, update session, and determine advancement.
    Relies on the LLM returning conceptually matched EXACT key detail strings.
    """
    try:
        print("--- Parsing evaluation response ---")
        print(f"Raw text: {evaluation_text[:500]}...") # Log beginning of raw text

        # Attempt to extract JSON robustly
        evaluation = {}
        json_str = None
        # Regex to find JSON block, potentially cleaning surrounding text/markdown
        json_match = re.search(r'```(?:json)?\s*(\{[\s\S]*?\})\s*```|(\{[\s\S]*?\})(?=\s*$)', evaluation_text, re.DOTALL)

        if json_match:
            # Prioritize the first capture group if both exist (usually markdown block)
            json_str = json_match.group(1) if json_match.group(1) else json_match.group(2)
            print(f"Found JSON string: {json_str[:200]}...")
            try:
                # Basic cleaning
                json_str = json_str.strip()
                # Attempt standard parsing
                evaluation = json.loads(json_str)
                print(f"Successfully parsed JSON: {evaluation}")
            except json.JSONDecodeError as e:
                print(f"JSON Decode Error: {e}. Attempting manual extraction from string: {json_str}")
                # Fallback to regex on the extracted string if direct parse fails
                evaluation = extract_evaluation_manually(json_str)

        else:
            print("No clear JSON object found. Attempting manual extraction from full text.")
            # Fallback to regex on the entire text if no JSON block found
            evaluation = extract_evaluation_manually(evaluation_text)

        # --- Process Enhanced Evaluation Data ---
        feedback = evaluation.get("feedback", "Great job describing what you see! Can you tell me anything else?")

        # Ensure newly_identified_details is always a list of strings
        newly_identified_details = evaluation.get("newly_identified_details", [])
        if not isinstance(newly_identified_details, list):
            newly_identified_details = [] # Default to empty list if format is wrong
        # Filter out non-strings or empty strings
        newly_identified_details = [str(detail).strip() for detail in newly_identified_details if isinstance(detail, str) and str(detail).strip()]

        # Extract enhanced fields
        scene_awareness_feedback = evaluation.get("scene_awareness_feedback")
        hint = evaluation.get("hint") # Allow None/null
        complexity_hint = evaluation.get("complexity_hint")
        progress_summary = evaluation.get("progress_summary", "")
        detail_categories_identified = evaluation.get("detail_categories_identified", [])
        suggest_scene_focus = evaluation.get("suggest_scene_focus")

        score = evaluation.get("score", 0)
        if not isinstance(score, int) or score < 0 or score > 100:
             score = 0 # Default invalid scores
        advance_difficulty = evaluation.get("advance_difficulty", False)
        if not isinstance(advance_difficulty, bool):
            advance_difficulty = False # Default invalid booleans

        print(f"Parsed - Feedback: {feedback[:50]}...")
        print(f"Parsed - Newly Identified Details: {newly_identified_details}")
        print(f"Parsed - Scene Awareness: {scene_awareness_feedback}")
        print(f"Parsed - Hint: {hint}")
        print(f"Parsed - Complexity Hint: {complexity_hint}")
        print(f"Parsed - Progress Summary: {progress_summary}")
        print(f"Parsed - Detail Categories: {detail_categories_identified}")
        print(f"Parsed - Scene Focus Suggestion: {suggest_scene_focus}")
        print(f"Parsed - Score: {score}")
        print(f"Parsed - Advance Difficulty (LLM): {advance_difficulty}")

        # Update the active session
        # Note: `update_checklist` handles the identification logic now based on these exact strings
        identified_details = active_session.get("identified_details", []).copy()
        details_added_this_turn = []
        for detail in newly_identified_details:
            # Check against the canonical list of key details for validity
            if detail in active_session.get("key_details", []) and detail not in identified_details:
                identified_details.append(detail)
                details_added_this_turn.append(detail) # Track what's new *this* turn
        active_session["identified_details"] = identified_details
        print(f"Updated Session - Total Identified Details: {identified_details}")

        # Enhanced feedback construction
        enhanced_feedback = feedback

        # Add scene awareness feedback if present
        if scene_awareness_feedback and isinstance(scene_awareness_feedback, str) and scene_awareness_feedback.strip():
            enhanced_feedback += f" {scene_awareness_feedback}"

        # Add progress summary if present
        if progress_summary and isinstance(progress_summary, str) and progress_summary.strip():
            enhanced_feedback += f" {progress_summary}"

        # Determine which hint to use (prioritize complexity hint for higher levels)
        current_difficulty = active_session.get("difficulty", "Very Simple")
        selected_hint = None

        if current_difficulty in ["Complex", "Very Complex"] and complexity_hint and isinstance(complexity_hint, str) and complexity_hint.strip():
            selected_hint = complexity_hint
        elif hint and isinstance(hint, str) and hint.strip():
            selected_hint = hint

        # Add scene focus suggestion if user seems overwhelmed
        if suggest_scene_focus and isinstance(suggest_scene_focus, str) and suggest_scene_focus.strip():
            if selected_hint:
                selected_hint += f" {suggest_scene_focus}"
            else:
                selected_hint = suggest_scene_focus

        # Store enhanced information in session
        if detail_categories_identified and isinstance(detail_categories_identified, list):
            active_session["detail_categories_identified"] = detail_categories_identified

        # Manage hints
        if selected_hint and selected_hint.strip():
            used_hints = active_session.get("used_hints", []).copy()
            if selected_hint not in used_hints:
                used_hints.append(selected_hint)
                active_session["used_hints"] = used_hints
                # Append hint to feedback only if it's new and wasn't already included by LLM
                if selected_hint not in enhanced_feedback:
                     # Check for common hint phrases LLM might use
                     if "hint:" not in enhanced_feedback.lower() and "try looking" not in enhanced_feedback.lower() and "what about" not in enhanced_feedback.lower():
                         enhanced_feedback += f"\n\n✨ Maybe look closer at: {selected_hint}"
                     else:
                         # If LLM likely included it, don't double-add
                         pass


        # Determine if difficulty should advance
        key_details = active_session.get("key_details", [])
        details_threshold_percent = active_session.get("details_threshold", 0.7) # e.g., 70%
        threshold_count = math.ceil(len(key_details) * details_threshold_percent) if key_details else 0

        # Advance if LLM recommends it OR threshold is met
        should_advance = advance_difficulty or (len(identified_details) >= threshold_count and threshold_count > 0)
        print(f"Criteria - Identified: {len(identified_details)}, Threshold Count: {threshold_count}, LLM Advance: {advance_difficulty} -> Should Advance: {should_advance}")

        current_difficulty = active_session.get("difficulty", "Very Simple")
        new_difficulty = current_difficulty # Default to current

        # Example: Assuming config.DIFFICULTY_LEVELS exists
        try:
            from VisoLearn import config # Make sure config is accessible
            difficulties = config.DIFFICULTY_LEVELS
        except (ImportError, AttributeError):
            print("Warning: Could not import config.DIFFICULTY_LEVELS. Using default list.")
            difficulties = ["Very Simple", "Simple", "Medium", "Complex", "Very Complex"] # Fallback

        if should_advance:
            try:
                current_index = difficulties.index(current_difficulty)
                if current_index < len(difficulties) - 1:
                    new_difficulty = difficulties[current_index + 1]
                    print(f"Advancing difficulty from {current_difficulty} to {new_difficulty}")
                else:
                    print("Already at max difficulty.")
                    should_advance = False # Cannot advance further
            except ValueError:
                 print(f"Warning: Current difficulty '{current_difficulty}' not in known levels. Cannot advance.")
                 should_advance = False # Cannot advance if current level unknown


        # Return parsed/processed data
        return enhanced_feedback, new_difficulty, should_advance, details_added_this_turn, score

    except Exception as e:
        print(f"FATAL Error processing evaluation: {str(e)}")
        print(f"Raw evaluation text causing error: {evaluation_text}")
        # Return a safe default on major failure
        return ("I see you're describing the image! Can you tell me more about what you notice?",
                active_session.get("difficulty", "Very Simple"),
                False,
                [],
                0)

def extract_evaluation_manually(text):
    """Helper function to extract evaluation fields using regex as a fallback."""
    evaluation = {}
    print("Attempting manual extraction via Regex...")

    # More tolerant regex patterns
    feedback_match = re.search(r'"feedback"\s*:\s*"(.*?)"(?=\s*,\s*"\w+"\s*:|\s*\})', text, re.DOTALL)
    if feedback_match:
        evaluation["feedback"] = feedback_match.group(1).replace('\\"', '"').replace('\\n', '\n')
    else: # Fallback: less strict
         feedback_match = re.search(r'feedback["\']?\s*[:=]\s*["\']?(.*?)["\']?\s*(?:,|\n\s*["\']?(?:newly|hint|score|advance)|$)', text, re.IGNORECASE | re.DOTALL)
         if feedback_match: evaluation["feedback"] = feedback_match.group(1).strip()


    details_match = re.search(r'"newly_identified_details"\s*:\s*(\[.*?\])', text, re.DOTALL)
    if details_match:
        details_str = details_match.group(1)
        try:
            # Try parsing the list directly
             evaluation["newly_identified_details"] = json.loads(details_str)
             if not isinstance(evaluation["newly_identified_details"], list): evaluation["newly_identified_details"] = [] # Ensure list type
        except json.JSONDecodeError:
             # If direct parse fails, extract strings from it
             evaluation["newly_identified_details"] = [d.strip() for d in re.findall(r'"(.*?)"', details_str) if d.strip()]
    else: # Fallback: less strict list detection
        details_match = re.search(r'newly.*?details["\']?\s*[:=]\s*\[?(.*?)\]?(?:,|\n\s*["\']?(?:hint|score|advance)|$)', text, re.IGNORECASE | re.DOTALL)
        if details_match:
             details_text = details_match.group(1).strip()
             # Extract from comma/newline sep, or bullet points
             details = [d.strip().strip('"\'') for d in re.split(r'[,\n]|\s*-\s*|\s*\*\s*', details_text) if d.strip()]
             evaluation["newly_identified_details"] = details


    hint_match = re.search(r'"hint"\s*:\s*(?:"(.*?)"|null)', text, re.DOTALL)
    if hint_match:
        evaluation["hint"] = hint_match.group(1).replace('\\"', '"').replace('\\n', '\n') if hint_match.group(1) is not None else None
    else: # Fallback: less strict
        hint_match = re.search(r'hint["\']?\s*[:=]\s*["\']?(.*?)["\']?\s*(?:,|\n\s*["\']?(?:score|advance)|$)', text, re.IGNORECASE | re.DOTALL)
        if hint_match:
            hint_text = hint_match.group(1).strip()
            evaluation["hint"] = None if hint_text.lower() in ['null', 'none', ''] else hint_text


    score_match = re.search(r'"score"\s*:\s*(\d+)', text)
    if score_match:
        evaluation["score"] = int(score_match.group(1))
    else: # Fallback: less strict
        score_match = re.search(r'score["\']?\s*[:=]\s*(\d+)', text, re.IGNORECASE)
        if score_match: evaluation["score"] = int(score_match.group(1))

    advance_match = re.search(r'"advance_difficulty"\s*:\s*(true|false)', text, re.IGNORECASE)
    if advance_match:
        evaluation["advance_difficulty"] = advance_match.group(1).lower() == "true"
    else: # Fallback: less strict
        advance_match = re.search(r'advance.*?difficulty["\']?\s*[:=]\s*(true|false)', text, re.IGNORECASE)
        if advance_match: evaluation["advance_difficulty"] = advance_match.group(1).lower() == "true"

    print(f"Manual extraction result: {evaluation}")
    return evaluation


def update_checklist(checklist, newly_identified_exact_strings, key_details):
    """
    Update the checklist based on the EXACT key detail strings identified conceptually by the LLM.
    """
    print(f"--- Updating checklist ---")
    print(f"Newly identified (exact strings from LLM): {newly_identified_exact_strings}")
    # print(f"Current checklist state: {checklist}")

    if not newly_identified_exact_strings:
        print("No new details identified by LLM. Checklist unchanged.")
        return checklist  # No change if LLM reported no new matches

    # Normalize the list received from the LLM just in case (lower, strip)
    # Although the LLM was asked for exact strings, this adds robustness
    normalized_identified_set = {detail.lower().strip() for detail in newly_identified_exact_strings}
    print(f"Normalized identified set for matching: {normalized_identified_set}")

    new_checklist = []
    updated_count = 0
    for item in checklist:
        detail_text = item["detail"]
        is_identified = item["identified"]
        item_id = item["id"]

        # Normalize the checklist item detail for comparison
        normalized_detail_text = detail_text.lower().strip()

        # If not already identified, check if it's in the newly identified set
        if not is_identified and normalized_detail_text in normalized_identified_set:
            print(f"✓ Marking '{detail_text}' as identified.")
            new_checklist.append({"detail": detail_text, "identified": True, "id": item_id})
            updated_count += 1
        else:
            # Keep the existing state (identified or not)
            new_checklist.append({"detail": detail_text, "identified": is_identified, "id": item_id})

    print(f"Checklist update complete. {updated_count} items marked as newly identified.")
    # print(f"New checklist state: {new_checklist}")
    return new_checklist
