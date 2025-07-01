# import io
# import os
# import base64
# import requests
# import time
# from PIL import Image
# import config
# import warnings
# warnings.filterwarnings("ignore", message="IMAGE_SAFETY is not a valid FinishReason")

# # Global variables to store the image data URL and prompt
# global_image_data_url = None
# global_image_prompt = None
# global_image_description = None

# def generate_image_fn(selected_prompt, guidance_scale=3.0,
#                       negative_prompt="blurry, distorted, low quality, pixelated, poorly drawn, deformed, unfinished, sketch marks, rough lines, pencil texture, draft appearance, hand-drawn look, traditional media texture, canvas texture, brush strokes, soft focus, motion blur, depth of field blur, hazy details, visual softness, roughness, blurred",
#                       num_inference_steps=50):
#     """
#     Generate an image from the prompt via the Black Forest Labs FLUX API.
#     Convert the image to a data URL.
#     """
#     global global_image_data_url, global_image_prompt
#     global_image_prompt = selected_prompt

#     try:
#         # Step 1: Submit the generation request
#         response = requests.post(
#             'https://api.us1.bfl.ai/v1/flux-dev',
#             headers={
#                 'accept': 'application/json',
#                 'x-key': os.environ.get("BFL_API_KEY", config.BFL_API_KEY),
#                 'Content-Type': 'application/json',
#             },
#             json={
#                 'prompt': selected_prompt,
#                 'negative_prompt': negative_prompt,
#                 'width': 1024,
#                 'height': 768,
#                 'steps': num_inference_steps,
#                 'safety_tolerance': 6,
#                 'output_format': 'png',
#             }
#         )

#         if response.status_code != 200:
#             print(f"API Error: {response.status_code} - {response.text}")
#             return None

#         request_data = response.json()
#         request_id = request_data.get("id")

#         if not request_id:
#             print("No request ID returned from API")
#             return None

#         print(f"Image generation started with ID: {request_id}")

#         # Step 2: Poll for the result
#         max_attempts = 30
#         for attempt in range(max_attempts):
#             time.sleep(1)  # Wait between polling attempts

#             result = requests.get(
#                 'https://api.us1.bfl.ai/v1/get_result',
#                 headers={
#                     'accept': 'application/json',
#                     'x-key': os.environ.get("BFL_API_KEY", config.BFL_API_KEY),
#                 },
#                 params={
#                     'id': request_id,
#                 }
#             )

#             if result.status_code != 200:
#                 print(f"Error checking status: {result.status_code} - {result.text}")
#                 continue

#             result_data = result.json()
#             status = result_data.get("status")

#             print(f"Status: {status}")

#             if status == "Ready":
#                 image_url = result_data.get("result", {}).get("sample")
#                 if not image_url:
#                     print("No image URL in response")
#                     return None

#                 # Download the image
#                 img_response = requests.get(image_url)
#                 if img_response.status_code != 200:
#                     print(f"Failed to download image: {img_response.status_code}")
#                     return None

#                 # Create PIL Image from response content
#                 image = Image.open(io.BytesIO(img_response.content))

#                 # Convert the PIL Image to a data URL
#                 buffered = io.BytesIO()
#                 image.save(buffered, format="PNG")
#                 img_bytes = buffered.getvalue()
#                 img_b64 = base64.b64encode(img_bytes).decode("utf-8")
#                 global_image_data_url = f"data:image/png;base64,{img_b64}"

#                 print(f"Successfully generated image with prompt: {selected_prompt[:50]}...")
#                 return image  # Return the PIL Image object

#             elif status == "Failed":
#                 print(f"Image generation failed: {result_data.get('message', 'Unknown error')}")
#                 return None

#             # Still processing, continue polling
#             print(f"Image generation in progress ({attempt+1}/{max_attempts})...")

#         print(f"Timed out waiting for image generation after {max_attempts} attempts")
#         return None

#     except Exception as e:
#         print(f"Error generating image: {str(e)}")
#         return None  # Return None on error

# ------------------------------------------------------------------------------------------------------------------------------------------------------


import io
import base64
import os
from PIL import Image
import config
from openai import OpenAI
import warnings
warnings.filterwarnings("ignore", message="IMAGE_SAFETY is not a valid FinishReason")

# Global variables to store the image data URL and prompt
global_image_data_url = None
global_image_prompt = None
global_image_description = None

def generate_image_fn(selected_prompt, model="gpt-image-1", output_path=None):
    """
    Generate an image from the prompt via the OpenAI API using gpt-image-1.
    Convert the image to a data URL and optionally save it to a file.

    Args:
        selected_prompt (str): The prompt to generate the image from.
        model (str): Should be "gpt-image-1". Parameter kept for compatibility.
        output_path (str, optional): If provided, saves the image to this path. Defaults to None.

    Returns:
        PIL.Image.Image or None: The generated image as a PIL Image object, or None on error.
    """
    global global_image_data_url, global_image_prompt

    # Smart prompt truncation that preserves critical details
    MAX_PROMPT_LENGTH = 32000
    if len(selected_prompt) > MAX_PROMPT_LENGTH:
        selected_prompt = smart_truncate_prompt(selected_prompt, MAX_PROMPT_LENGTH)
        print(f"Warning: Prompt was smartly truncated to {len(selected_prompt)} characters while preserving critical details")

    global_image_prompt = selected_prompt

    # Always use gpt-image-1 regardless of what's passed
    model = "gpt-image-1"

    try:
        # Initialize OpenAI client with API key from environment variables or config
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", config.OPENAI_API_KEY))

        # Prepare API parameters for gpt-image-1
        api_params = {
            "model": model,
            "prompt": selected_prompt,
            # "response_format": "b64_json",
            "size": "1024x1536" ,
            "quality": "high"
        }

        # Generate image using OpenAI
        result = client.images.generate(**api_params)

        # Get the base64 encoded image from the response
        image_base64 = result.data[0].b64_json

        # Decode the base64 string to bytes
        image_bytes = base64.b64decode(image_base64)

        # Create PIL Image from bytes
        image = Image.open(io.BytesIO(image_bytes))

        # Save the image to a file if output_path is provided
        if output_path:
            try:
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, "wb") as f:
                    f.write(image_bytes)
                print(f"Successfully saved image to {output_path}")
            except Exception as e:
                print(f"Error saving image to {output_path}: {str(e)}")

        # Convert to base64 for data URL
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_bytes = buffered.getvalue()
        img_b64 = base64.b64encode(img_bytes).decode("utf-8")
        global_image_data_url = f"data:image/png;base64,{img_b64}"

        print(f"Successfully generated image with prompt: {selected_prompt[:50]}...")
        return image  # Return the PIL Image object
    except Exception as e:
        print(f"Error generating image: {str(e)}")
        return None  # Return None on error

def smart_truncate_prompt(prompt, max_length):
    """
    Smart truncation that preserves critical details and visual consistency information.
    Prioritizes character descriptions, layout specifications, and technical requirements.
    """
    if len(prompt) <= max_length:
        return prompt

    # Define critical sections in order of priority
    critical_sections = [
        "CRITICAL LAYOUT:",
        "🎭 CRITICAL CHARACTER CONSISTENCY PROTOCOL:",
        "CHARACTER 1",
        "CHARACTER 2",
        "CHARACTER 3",
        "STORY CONTENT:",
        "🏗️ ENVIRONMENTAL CONSISTENCY PROTOCOL:",
        "🎨 COMIC BOOK STYLE MASTERY:",
        "🎨 AUTHENTIC MANGA STYLE:",
        "🎨 PHOTOREALISTIC EXCELLENCE:",
        "🎨 CINEMATIC VISUAL MASTERY:",
        "🎨 HIGH-QUALITY ILLUSTRATION:",
        "📐 PANEL COMPOSITION MASTERY:",
        "🔍 DETAIL PRESERVATION PROTOCOL:",
        "⚡ ADVANCED QUALITY REQUIREMENTS:"
    ]

    # Split prompt into sections
    sections = prompt.split(" || ")

    # Preserve critical sections first
    preserved_sections = []
    preserved_length = 0

    # Always preserve the first few critical sections
    for section in sections:
        section_trimmed = section.strip()
        if not section_trimmed:
            continue

        # Check if this is a critical section
        is_critical = any(critical_marker in section_trimmed for critical_marker in critical_sections[:8])  # Top 8 critical sections

        # If critical or we have space, include it
        if is_critical or (preserved_length + len(section_trimmed) + 4 < max_length - 200):  # Reserve 200 chars for final mandate
            preserved_sections.append(section_trimmed)
            preserved_length += len(section_trimmed) + 4  # +4 for " || "
        elif preserved_length < max_length * 0.7:  # If we haven't used 70% of space, try to include more
            # Truncate this section to fit
            available_space = max_length - preserved_length - 200
            if available_space > 100:  # Only if we have meaningful space
                truncated_section = section_trimmed[:available_space-20] + "..."
                preserved_sections.append(truncated_section)
                break

    # Join preserved sections
    preserved_prompt = " || ".join(preserved_sections)

    # Add final mandate if space allows
    final_mandate = " || FINAL MANDATE: Create a masterpiece with perfect character consistency and narrative clarity"
    if len(preserved_prompt) + len(final_mandate) <= max_length:
        preserved_prompt += final_mandate

    return preserved_prompt
