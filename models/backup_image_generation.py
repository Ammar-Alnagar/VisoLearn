import io
import base64
from huggingface_hub import InferenceClient
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

def generate_image_fn(selected_prompt, guidance_scale=5.5,
                      negative_prompt="blurry, distorted, low quality, pixelated, poorly drawn, deformed, unfinished, sketchy, cartoon, blurred",
                      num_inference_steps=35):
    """
    Generate an image from the prompt via the Hugging Face Inference API.
    Convert the image to a data URL.
    """
    global global_image_data_url, global_image_prompt
    global_image_prompt = selected_prompt

    try:
        image_client = InferenceClient(provider="hf-inference", api_key=config.HF_TOKEN)
        image = image_client.text_to_image(
            selected_prompt,
            model="black-forest-labs/FLUX.1-dev",
            guidance_scale=guidance_scale,
            # negative_prompt=negative_prompt,
            num_inference_steps=num_inference_steps
        )

        # Convert the PIL Image to a data URL
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
# -------------------------------------------------------------------------------------
#
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
#                       negative_prompt="blurry, distorted, low quality, pixelated, poorly drawn, deformed, unfinished, sketchy, cartoon, blurred",
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
