import io
import base64
import os
from PIL import Image
import config
from google import genai
from google.genai import types
from io import BytesIO
import warnings
warnings.filterwarnings("ignore", message="IMAGE_SAFETY is not a valid FinishReason")

# Global variables to store the image data URL and prompt
global_image_data_url = None
global_image_prompt = None
global_image_description = None

def generate_image_fn(selected_prompt, model="imagen-3.0-generate-002", output_path=None):
    """
    Generate an image from the prompt via the Google Imagen 3 API.
    Convert the image to a data URL and optionally save it to a file.

    Args:
        selected_prompt (str): The prompt to generate the image from.
        model (str): The Imagen model to use. Defaults to "imagen-3.0-generate-002".
        output_path (str, optional): If provided, saves the image to this path. Defaults to None.

    Returns:
        PIL.Image.Image or None: The generated image as a PIL Image object, or None on error.
    """
    global global_image_data_url, global_image_prompt
    global_image_prompt = selected_prompt

    try:
        # Initialize Google GenAI client with API key from environment variables or config
        # Try to get API key from environment first, then from config, and handle missing attribute
        gemini_api_key = os.environ.get("GEMINI_API_KEY")
        if not gemini_api_key:
            try:
                gemini_api_key = config.GEMINI_API_KEY
            except AttributeError:
                # If config doesn't have GEMINI_API_KEY attribute, look for other possible attributes
                if hasattr(config, "GOOGLE_API_KEY"):
                    gemini_api_key = config.GOOGLE_API_KEY
                elif hasattr(config, "API_KEY"):
                    gemini_api_key = config.API_KEY
                else:
                    raise ValueError("No Google API key found in environment variables or config")

        client = genai.Client(api_key=gemini_api_key)

        # Generate image using Google Imagen 3
        response = client.models.generate_images(
            model=model,
            prompt=selected_prompt,
            config=types.GenerateImagesConfig(
                number_of_images=2,  # Only generate one image

            )
        )

        # Check if we got any images
        if not response.generated_images or len(response.generated_images) == 0:
            print("No images were generated")
            return None

        # Get the first (and only) generated image
        image_bytes = response.generated_images[0].image.image_bytes

        # Create PIL Image from bytes
        image = Image.open(BytesIO(image_bytes))

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
