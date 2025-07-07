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
    Generate an image from the prompt via the OpenAI API.
    Convert the image to a data URL and optionally save it to a file.

    Args:
        selected_prompt (str): The prompt to generate the image from.
        model (str): The model to use for image generation (e.g., "gpt-image-1").
        output_path (str, optional): If provided, saves the image to this path. Defaults to None.

    Returns:
        PIL.Image.Image or None: The generated image as a PIL Image object, or None on error.
    """
    global global_image_data_url, global_image_prompt

    # MAXIMUM QUALITY ENFORCEMENT: Add ultra-strong quality prefixes and suffixes
    ULTRA_QUALITY_PREFIX = (
        "ULTRA-MODERN DIGITAL MASTERPIECE REQUIREMENT: Create a PRISTINE, COMPUTER-GENERATED digital artwork with ZERO sketchy, hand-drawn, or traditional media appearance. "
        "MANDATORY: Sleek, contemporary, polished digital finish typical of current Marvel/DC professional digital comics. "
        "ABSOLUTELY FORBIDDEN: sketch marks, rough lines, pencil texture, hand-drawn look, traditional media texture, canvas texture, brush strokes, watercolor effects, charcoal, cross-hatching, artistic texture, unfinished appearance, draft quality, blur, soft focus, haze. "
    )

    ULTRA_QUALITY_SUFFIX = (
        " || FINAL ULTRA-QUALITY MANDATE: The output MUST be a modern, computer-generated digital masterpiece with pristine quality. "
        "ZERO TOLERANCE for: sketchy appearance, rough textures, hand-drawn elements, traditional media simulation, blur, soft focus, unfinished look. "
        "MANDATORY: Ultra-modern digital comic finish, sleek contemporary appearance, professional computer-generated quality, razor-sharp details, perfect anatomical accuracy, pristine digital execution."
    )

    # Enhance the prompt with maximum quality enforcement
    enhanced_prompt = f"{ULTRA_QUALITY_PREFIX}{selected_prompt}{ULTRA_QUALITY_SUFFIX}"

    global_image_prompt = enhanced_prompt

    try:
        # Initialize OpenAI client with API key from environment variables or config
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", config.OPENAI_API_KEY))

        # Generate image using OpenAI with maximum quality settings
        result = client.images.generate(
            model=model,
            prompt=enhanced_prompt,
            size="1024x1536",
            quality="high",  # Use HD quality instead of "high"
            moderation="low",

        )

        # Get the base64 encoded image from the response
        image_base64 = result.data[0].b64_json

        # Decode the base64 string to bytes
        image_bytes = base64.b64decode(image_base64)

        # Create PIL Image from bytes
        image = Image.open(io.BytesIO(image_bytes))

        # Save the image to a file if output_path is provided
        if output_path:
            try:
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

        print(f"Successfully generated ULTRA-QUALITY image with enhanced prompt: {enhanced_prompt[:50]}...")
        return image  # Return the PIL Image object
    except Exception as e:
        print(f"Error generating image: {str(e)}")
        return None  # Return None on error




# import io
# import base64
# import os
# from PIL import Image
# import config
# from google import genai
# from io import BytesIO
# import warnings
# warnings.filterwarnings("ignore", message="IMAGE_SAFETY is not a valid FinishReason")

# # Global variables to store the image data URL and prompt
# global_image_data_url = None
# global_image_prompt = None
# global_image_description = None

# def generate_image_fn(selected_prompt, model="imagen-4.0-ultra-generate-preview-06-06", output_path=None):
#     """
#     Generate an image from the prompt via the Google Imagen 4.0 Ultra API.
#     Convert the image to a data URL and optionally save it to a file.

#     Args:
#         selected_prompt (str): The prompt to generate the image from.
#         model (str): The Imagen model to use. Defaults to "models/imagen-4.0-generate-preview-06-06".
#         output_path (str, optional): If provided, saves the image to this path. Defaults to None.

#     Returns:
#         PIL.Image.Image or None: The generated image as a PIL Image object, or None on error.
#     """
#     global global_image_data_url, global_image_prompt
#     global_image_prompt = selected_prompt

#     try:
#         # Initialize Google GenAI client with API key from environment variables or config
#         gemini_api_key = os.environ.get("GEMINI_API_KEY")
#         if not gemini_api_key:
#             try:
#                 gemini_api_key = config.GEMINI_API_KEY
#             except AttributeError:
#                 # If config doesn't have GEMINI_API_KEY attribute, look for other possible attributes
#                 if hasattr(config, "GOOGLE_API_KEY"):
#                     gemini_api_key = config.GOOGLE_API_KEY
#                 elif hasattr(config, "API_KEY"):
#                     gemini_api_key = config.API_KEY
#                 else:
#                     raise ValueError("No Google API key found in environment variables or config")

#         client = genai.Client(api_key=gemini_api_key)

#         # Generate image using Google Imagen 4.0 Ultra
#         response = client.models.generate_images(
#             model=model,
#             prompt=selected_prompt,
#             config=dict(
#                 number_of_images=1,
#                 output_mime_type="image/jpeg",
#                 person_generation="ALLOW_ADULT",
#                 aspect_ratio="1:1",
#             )
#         )

#         # Check if we got any images
#         if not response.generated_images or len(response.generated_images) == 0:
#             print("No images were generated")
#             return None

#         # Get the first (and only) generated image
#         image_bytes = response.generated_images[0].image.image_bytes

#         # Create PIL Image from bytes
#         image = Image.open(BytesIO(image_bytes))

#         # Save the image to a file if output_path is provided
#         if output_path:
#             try:
#                 os.makedirs(os.path.dirname(output_path), exist_ok=True)
#                 with open(output_path, "wb") as f:
#                     f.write(image_bytes)
#                 print(f"Successfully saved image to {output_path}")
#             except Exception as e:
#                 print(f"Error saving image to {output_path}: {str(e)}")

#         # Convert to base64 for data URL
#         buffered = io.BytesIO()
#         image.save(buffered, format="JPEG")  # Changed to JPEG to match output_mime_type
#         img_bytes = buffered.getvalue()
#         img_b64 = base64.b64encode(img_bytes).decode("utf-8")
#         global_image_data_url = f"data:image/jpeg;base64,{img_b64}"  # Changed to jpeg

#         print(f"Successfully generated image with prompt: {selected_prompt[:50]}...")
#         return image  # Return the PIL Image object
#     except Exception as e:
#         print(f"Error generating image: {str(e)}")
#         return None  # Return None on error
