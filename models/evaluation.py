import base64
import json
import re
import math
from google.generativeai import GenerativeModel
from google.ai.generativelanguage import Content, Part
import PIL.Image
import io

def generate_detailed_description(image_input, prompt, difficulty, topic_focus):
    """
    Generate a detailed description of the image using Gemini Vision.
    """
    # Check if image_input is None or empty
    if image_input is None:
        return "Error: No image provided. Please make sure an image is generated or uploaded first."

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
            return "Error: Unsupported image format"

        query = (
            f"""
            You are an expert educator specializing in teaching users with autism.
            Please provide a detailed description of this image that was generated based on the prompt:
            "{prompt}"
            The image is intended for a person with autism, focusing on the topic: "{topic_focus}" at a {difficulty} difficulty level.
            In your description:
            1. List all key objects, characters, and elements present in the image
            2. Describe colors, shapes, positions, and relationships between elements
            3. Note any emotions, actions, or interactions depicted
            4. Highlight details that would be important for the child to notice
            5. Organize your description in a structured, clear way
            6. Dont generate a certain style , use the topic of focus to guide your descriptions
            Your description will be used as a reference to evaluate the child's observations,
            so please be comprehensive but focus on observable details rather than interpretations.
            """
        )
        vision_model = GenerativeModel('gemini-2.5-flash')
        image_part = Part(inline_data={"mime_type": "image/png", "data": base64.b64decode(base64_img)})
        text_part = Part(text=query)
        multimodal_content = Content(parts=[image_part, text_part])
        response = vision_model.generate_content(multimodal_content)
        return response.text.strip()
    except Exception as e:
        print(f"Error in generate_detailed_description: {str(e)}")
        return f"Error processing image: {str(e)}. Please try again with a valid image."


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
            You are analyzing an educational image created for a person with autism, based on the prompt: "{prompt}".
            The image focuses on the topic: "{topic_focus}".
            Please extract a list of unique key details that a person might identify in this image minimum 5 , max 15 depending on the image.
            Each detail should be a simple, clear phrase describing one observable element.
            Focus on concrete, visible elements rather than abstract concepts.
            Format your response as a JSON array of strings, each representing one key detail.
            Example format: ["red ball on the grass", "smiling girl with brown hair", "blue sky with clouds"]
            Ensure each detail is:
            1. Directly observable in the image
            2. Unique (not a duplicate)
            3. Described in simple, concrete language
            4. Relevant to what a person would notice
            5. Avoid duplicates
            """
        )
        vision_model = GenerativeModel('gemini-2.5-flash')
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
                return details[:15] if details else ["object in image", "color", "shape", "background"]
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
        f"Your primary goal is to understand if the user has grasped the CONCEPTS present in the image, not just if they used specific words.\n\n"
        f"### Image Context:\n"
        f"- Original Prompt: {active_session.get('prompt', 'No prompt available')}\n"
        f"- Topic Focus: {active_session.get('topic_focus', 'General Observation')}\n"
        f"- Detailed Image Description (Reference Only): {image_description}\n\n"
        f"### User Information:\n"
        f"- Age: {age}\n"
        f"- Autism Level: {autism_level}\n"
        f"- Current Difficulty Level: {current_difficulty}\n\n"
        f"### Learning Task State:\n"
        f"{key_details_text}"  # Focus evaluation on REMAINING details
        f"{identified_details_text}"
        f"{used_hints_text}"
        f"{history_text}\n"
        f"### User's Current Description (Analyze this carefully):\n'{user_details}'\n\n"
        "----------------------------------------------------\n"
        "### YOUR CRITICAL TASK: CONCEPTUAL EVALUATION\n"
        "Analyze the \"User's Current Description\" and determine which CONCEPTS from the \"Key Details to Identify\" list the user has successfully understood and conveyed, even if their wording is different. Apply the following rules rigorously:\n\n"
        "### CONCEPTUAL MATCHING RULES (ABSOLUTELY CRITICAL - APPLY WITH EMPATHY):\n"
        "1.  **PRIORITIZE MEANING OVER WORDS:** Focus entirely on the SEMANTIC MEANING and the underlying IDEA the user is trying to express. Ignore exact phrasing, grammar, or spelling mistakes.\n"
        "2.  **CONCEPTUAL EQUIVALENCE:** Does the user's statement describe the core concept of a key detail? If yes, it's a match. (e.g., Key Detail: 'Smiling boy waving'. User says: 'happy person saying hi' -> MATCHES).\n"
        "3.  **FLEXIBLE INTERPRETATION:** Individuals with autism may use unique, literal, or roundabout phrasing. Interpret generously. Give the benefit of the doubt. Assume competence and focus on their likely intended meaning.\n"
        "4.  **PARTIAL CONCEPTS COUNT:** Especially for Level 2/3 autism, younger ages, or simpler difficulty levels, credit partial understanding. (e.g., Key Detail: 'Large red truck'. User says: 'big red thing' -> MATCHES, as they grasped size and color).\n"
        "5.  **SYNONYMS & DESCRIPTIONS:** Accept synonyms, paraphrasing, or descriptive phrases that capture the essence. (e.g., Key Detail: 'Fluffy white clouds'. User says: 'soft looking things in the sky', 'cotton balls up high' -> MATCHES).\n"
        "6.  **FOCUS ON OBSERVABLES:** Match based on what the user likely *observed* in the image, linked back to a key detail concept.\n"
        "7.  **GENEROSITY IS KEY:** When uncertain, ERR ON THE SIDE OF GIVING CREDIT. The goal is encouragement and identifying understanding, not strict grading.\n"
        "8.  **OUTPUT REQUIREMENT:** If you determine a conceptual match, you MUST include the **EXACT ORIGINAL STRING** from the 'Key Details to Identify' list in the `newly_identified_details` field of your JSON response. DO NOT put the user's words there.\n\n"
        "### RESPONSE REQUIREMENTS:\n"
        "Provide your evaluation STRICTLY as a valid JSON object with the following structure:\n"
        "```json\n"
        "{\n"
        "  \"feedback\": \"(String) Your encouraging, supportive, and specific feedback to the user. Praise what they identified correctly (conceptually). Avoid sounding repetitive. Tailor to age/level.\",\n"
        "  \"newly_identified_details\": [\"(String) Exact key detail 1 matched\", \"(String) Exact key detail 2 matched\"], /* List of EXACT strings from 'Key Details to Identify' that were conceptually matched by the user's LATEST description. Empty list if none matched. */\n"
        "  \"hint\": \"(String or null) If appropriate, provide ONE gentle, guiding hint towards a concept NOT YET identified. Phrase it as an observation or question, NOT explicitly as a 'hint'. E.g., 'I also see something bright and yellow in the sky...' or 'What is the dog holding?'. If no hint is needed or helpful, use null.\",\n"
        "  \"score\": 75, /* (Integer 0-100) An overall score reflecting conceptual understanding shown in this turn, considering difficulty and effort. Be generous. */\n"
        "  \"advance_difficulty\": false /* (Boolean) Set to true ONLY if the user shows strong mastery and most key details are identified, suggesting they are ready for a harder challenge. */\n"
        "}\n"
        "```\n\n"
        "### FINAL CHECKLIST BEFORE RESPONDING:\n"
        "- Did I focus ONLY on conceptual understanding?\n"
        "- Did I interpret the user's words generously and flexibly?\n"
        "- Does `newly_identified_details` contain the EXACT STRINGS from the key details list?\n"
        "- Is the feedback positive, specific, and appropriate?\n"
        "- Is the hint subtle and guiding (or null)?\n"
        "- Is the entire response a single, valid JSON object?\n\n"
        "Now, analyze the user's description based on these instructions and provide the JSON evaluation."
    )

    try:
        model = GenerativeModel('gemini-2.5-flash') # Ensure you are using an appropriate model capable of following complex instructions
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

        # --- Process Evaluation Data ---
        feedback = evaluation.get("feedback", "Great job describing what you see! Can you tell me anything else?")
        # Ensure newly_identified_details is always a list of strings
        newly_identified_details = evaluation.get("newly_identified_details", [])
        if not isinstance(newly_identified_details, list):
            newly_identified_details = [] # Default to empty list if format is wrong
        # Filter out non-strings or empty strings
        newly_identified_details = [str(detail).strip() for detail in newly_identified_details if isinstance(detail, str) and str(detail).strip()]

        hint = evaluation.get("hint") # Allow None/null
        score = evaluation.get("score", 0)
        if not isinstance(score, int) or score < 0 or score > 100:
             score = 0 # Default invalid scores
        advance_difficulty = evaluation.get("advance_difficulty", False)
        if not isinstance(advance_difficulty, bool):
            advance_difficulty = False # Default invalid booleans

        print(f"Parsed - Feedback: {feedback[:50]}...")
        print(f"Parsed - Newly Identified Details: {newly_identified_details}")
        print(f"Parsed - Hint: {hint}")
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

        # Manage hints
        if hint and isinstance(hint, str) and hint.strip():
            used_hints = active_session.get("used_hints", []).copy()
            if hint not in used_hints:
                used_hints.append(hint)
                active_session["used_hints"] = used_hints
                # Append hint to feedback only if it's new and wasn't already included by LLM
                if hint not in feedback:
                     # Check for common hint phrases LLM might use
                     if "hint:" not in feedback.lower() and "try looking" not in feedback.lower() and "what about" not in feedback.lower():
                         feedback += f"\n\n✨ Maybe look closer at: {hint}"
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
        return feedback, new_difficulty, should_advance, details_added_this_turn, score

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
