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
             "size": "auto" ,
             "quality": "auto"
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
