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
