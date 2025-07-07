from PIL import Image
import io
import base64
import math
from models.prompt_generation import generate_prompt_from_options
from models.image_generation import generate_image_fn, global_image_data_url, global_image_description
from models.evaluation import generate_detailed_description, extract_key_details, compare_details_chat_fn, parse_evaluation, update_checklist
import os
from utils.migrations import migrate_chat_history_format


def generate_image_and_reset_chat(age, autism_level, topic_focus, treatment_plan, attempt_limit_input, details_threshold_input, active_session, saved_sessions, image_style):
    """
    Generate a new image (with the current difficulty) and reset the chat.
    Also resets the attempt count and uses the user-entered attempt limit and details threshold.
    """
    global global_image_description
    global global_image_data_url

    new_sessions = saved_sessions.copy()
    if active_session.get("prompt"):
        # Migrate chat history before saving
        if "chat" in active_session:
            active_session["chat"] = migrate_chat_history_format(active_session["chat"])
        new_sessions.append(active_session)

    current_difficulty = active_session.get("difficulty", "Very Simple")
    generated_prompt = generate_prompt_from_options(current_difficulty, age, autism_level, topic_focus, treatment_plan, image_style)

    # Get the image from the function
    image = generate_image_fn(generated_prompt)

    # Check if image generation was successful
    if image is None:
        # Handle the error - return appropriate message or default image
        return None, active_session, new_sessions, [], active_session.get("chat", [])

    # Convert the image to a data URL if it's a PIL Image
    if hasattr(image, 'save'):  # This is a PIL Image
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        img_bytes = buffer.getvalue()
        image_data_url = f"data:image/png;base64,{base64.b64encode(img_bytes).decode('utf-8')}"
        # Update the global variable
        global_image_data_url = image_data_url
    else:  # Assume it's already a data URL
        image_data_url = image
        global_image_data_url = image_data_url

    # Now use the image_data_url for generating description and extracting details
    image_description = generate_detailed_description(image, generated_prompt, current_difficulty, topic_focus)
    global_image_description = image_description
    key_details = extract_key_details(image, generated_prompt, topic_focus)

    # Convert details_threshold_input to a percentage if it's greater than 1, or keep as is if it's 0-1
    details_threshold = float(details_threshold_input) if details_threshold_input else 0.7
    if details_threshold > 1:
        details_threshold = details_threshold / 100.0  # Convert from percentage to decimal
    details_threshold = max(0.1, min(1.0, details_threshold))  # Ensure between 0.1 and 1.0

    new_active_session = {
        "prompt": generated_prompt,
        "image": image_data_url,  # Use the data URL
        "image_description": image_description,
        "chat": [],  # Start with empty chat
        "treatment_plan": treatment_plan,
        "topic_focus": topic_focus,
        "key_details": key_details,
        "identified_details": [],
        "used_hints": [],
        "difficulty": current_difficulty,
        "autism_level": autism_level,
        "age": age,
        "attempt_limit": int(attempt_limit_input) if attempt_limit_input else 3,
        "attempt_count": 0,
        "details_threshold": details_threshold,
        "image_style": image_style
    }

    # Add the welcome message only if this is the first session
    if not saved_sessions and not active_session.get("prompt"):
        new_active_session["chat"] = [{"role": "assistant", "content": "Hi, I Am Wisal , It's nice to meet you! let's get started and find out what you can see in this image."}]

    checklist_items = []
    for i, detail in enumerate(key_details):
        checklist_items.append({"detail": detail, "identified": False, "id": i})

    # Return the chat history along with other data
    return image, new_active_session, new_sessions, checklist_items, new_active_session["chat"]

def chat_respond(user_message, active_session, saved_sessions, checklist):
    """
    Process a chat message with improved state management when advancing levels.
    """
    # Migrate chat history to new format if needed
    if "chat" in active_session:
        active_session["chat"] = migrate_chat_history_format(active_session["chat"])

    if not active_session.get("image"):
        bot_message = "Please generate an image first."
        updated_chat = active_session.get("chat", []) + [{"role": "user", "content": user_message}, {"role": "assistant", "content": bot_message}]
        active_session["chat"] = updated_chat
        return "", updated_chat, saved_sessions, active_session, checklist, None

    # Get the current image for display
    current_image = None
    try:
        image_data = active_session.get("image")
        if image_data:
            if image_data.startswith("data:image"):
                # Handle data URL
                base64_img = image_data.split(",")[1]
                img_bytes = base64.b64decode(base64_img)
                current_image = Image.open(io.BytesIO(img_bytes))
            elif os.path.exists(image_data):
                # Handle file path
                current_image = Image.open(image_data)
    except Exception as e:
        print(f"Error loading image: {str(e)}")

    # Get evaluation of the child's message
    raw_evaluation = compare_details_chat_fn(user_message, active_session, active_session.get("image"), active_session.get("image_description"))
    feedback, updated_difficulty, should_advance, newly_identified, score = parse_evaluation(raw_evaluation, active_session)

    if not newly_identified:
        active_session["attempt_count"] = active_session.get("attempt_count", 0) + 1

    # Update the checklist with the newly identified details
    updated_checklist = update_checklist(checklist, newly_identified, active_session.get("key_details", []))

    # Update the conversation history
    updated_chat = active_session.get("chat", []) + [{"role": "user", "content": user_message}, {"role": "assistant", "content": feedback}]
    active_session["chat"] = updated_chat

    # Check if the threshold has been reached
    identified_count = len(active_session.get("identified_details", []))
    key_details = active_session.get("key_details", [])
    details_threshold = active_session.get("details_threshold", 0.7)
    threshold_count = math.ceil(len(key_details) * details_threshold)

    # Determine if conditions are met to generate a new image
    all_identified = all(item["identified"] for item in updated_checklist)
    threshold_reached = identified_count >= threshold_count
    attempts_exhausted = active_session.get("attempt_count", 0) >= active_session.get("attempt_limit", 3)

    print(f"Details identified: {identified_count}/{len(key_details)}")
    print(f"Threshold count: {threshold_count}")
    print(f"Threshold reached: {threshold_reached}")
    print(f"All identified: {all_identified}")
    print(f"Attempts exhausted: {attempts_exhausted}")
    print(f"Should advance: {should_advance}")

    # If conditions are met to generate a new image and advance
    if threshold_reached or all_identified or attempts_exhausted or should_advance:
        print("Generating new image and advancing...")

        # Save the current session before creating a new one
        new_sessions = saved_sessions.copy()
        completed_session = active_session.copy()
        completed_session["completed"] = True
        new_sessions.append(completed_session)

        # Get parameters for the new session
        age = active_session.get("age", "3")
        autism_level = active_session.get("autism_level", "Level 1")
        topic_focus = active_session.get("topic_focus", "")
        treatment_plan = active_session.get("treatment_plan", "")
        image_style = active_session.get("image_style", "Realistic")

        # Determine the difficulty level for the new session
        if threshold_reached or should_advance:
            difficulty_to_use = updated_difficulty
        else:
            difficulty_to_use = active_session.get("difficulty", "Very Simple")

        print(f"Using difficulty level: {difficulty_to_use} for new image")

        # Generate a new image with the appropriate difficulty and image style
        generated_prompt = generate_prompt_from_options(difficulty_to_use, age, autism_level, topic_focus, treatment_plan, image_style)

        # Get the image from the function
        image = generate_image_fn(generated_prompt)

        # Check if image generation was successful
        if image is None:
            # Handle the error - use a placeholder message
            advancement_message = "There was an issue generating a new image. Please try again."
            updated_chat.append({"role": "system", "content": advancement_message})
            return "", updated_chat, new_sessions, active_session, updated_checklist, current_image

        # Convert the image to a data URL if it's a PIL Image
        global global_image_data_url
        if hasattr(image, 'save'):  # This is a PIL Image
            buffer = io.BytesIO()
            image.save(buffer, format="PNG")
            img_bytes = buffer.getvalue()
            image_data_url = f"data:image/png;base64,{base64.b64encode(img_bytes).decode('utf-8')}"
            # Update the global variable
            global_image_data_url = image_data_url
        else:  # Assume it's already a data URL
            image_data_url = image
            global_image_data_url = image_data_url

        # Now use the image_data_url for generating description and extracting details
        image_description = generate_detailed_description(image, generated_prompt, difficulty_to_use, topic_focus)
        key_details = extract_key_details(image, generated_prompt, topic_focus)

        # Create a completely new session
        new_active_session = {
            "prompt": generated_prompt,
            "image": image_data_url,  # Use the data URL
            "image_description": image_description,
            "chat": [],  # Start with empty chat
            "treatment_plan": treatment_plan,
            "topic_focus": topic_focus,
            "key_details": key_details,
            "identified_details": [],  # Reset identified details
            "used_hints": [],  # Reset hints
            "difficulty": difficulty_to_use,
            "autism_level": autism_level,
            "age": age,
            "attempt_limit": active_session.get("attempt_limit", 3),
            "attempt_count": 0,  # Reset attempt count
            "details_threshold": active_session.get("details_threshold", 0.7),
            "image_style": image_style  # Keep the same image style
        }

        # Create a new checklist for the new details
        new_checklist = []
        for i, detail in enumerate(key_details):
            new_checklist.append({"detail": detail, "identified": False, "id": i})

        # Create an appropriate advancement message
        if attempts_exhausted:
            advancement_message = "You've used all your allowed attempts. Let's try a new image."
        elif threshold_reached and updated_difficulty != active_session.get("difficulty", "Very Simple"):
            advancement_message = f"Congratulations! You've identified enough details ({identified_count}/{len(key_details)}) to advance to {updated_difficulty} difficulty! Here's a new image to describe."
        elif should_advance:
            advancement_message = f"Congratulations! You've advanced to {updated_difficulty} difficulty! Here's a new image to describe."
        elif threshold_reached or all_identified:
            advancement_message = f"Great job identifying the details! Here's a new image at the same difficulty level."
        else:
            advancement_message = "Let's try a new image!"

        # Add the advancement message to the chat history
        new_active_session["chat"] = [{"role": "system", "content": advancement_message}]

        print(f"New session created with {len(key_details)} key details at {difficulty_to_use} difficulty")

        # Return everything for the UI update with the new image
        return "", new_active_session["chat"], new_sessions, new_checklist, image

    # If not generating a new image, return the updated state
    return "", updated_chat, saved_sessions, active_session, updated_checklist, current_image

def update_sessions(saved_sessions, active_session):
    """
    Combine finished sessions with the active session for display.
    """
    if active_session and active_session.get("prompt"):
        return saved_sessions + [active_session]
    return saved_sessions



def load_checklist_from_session(active_session):
    """
    Generate checklist items from a loaded session

    Args:
        active_session: The loaded active session data

    Returns:
        list: Checklist items with identified status
    """
    if not active_session or not active_session.get("key_details"):
        return []

    key_details = active_session.get("key_details", [])
    identified_details = active_session.get("identified_details", [])

    checklist_items = []
    for i, detail in enumerate(key_details):
        identified = detail in identified_details
        checklist_items.append({"detail": detail, "identified": identified, "id": i})

    return checklist_items
