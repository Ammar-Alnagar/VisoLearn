# API Reference

## Overview

This document provides comprehensive information about the API integrations and external services used in VisoLearn-2, including OpenAI, Google Gemini, and Google Drive.

## API Configuration

### Environment Variables Setup

VisoLearn-2 uses environment variables to securely store API keys and configuration settings. These are typically stored in a `.env` file in the project root.

**Required Environment Variables:**
```
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
HF_TOKEN=your_huggingface_token_here
BFL_API_KEY=your_blue_foundation_api_key_here
```

### API Key Management

**Best Practices:**
- Never commit API keys to version control
- Use `.env` files for local development
- Implement proper environment variables for production
- Regularly rotate API keys
- Monitor API usage and quotas

## Google Generative AI Integration

### Imagen 4.0 Ultra Image Generation

#### Endpoint: `genai.Client().models.generate_images()`
```python
import base64
from google import genai
from config import GOOGLE_API_KEY

def generate_image_with_imagen(prompt, model="models/imagen-4.0-ultra-generate-preview-06-06"):
    """
    Generate an image using Google's Imagen 4.0 Ultra API

    Args:
        prompt (str): Text description of the desired image
        model (str): Imagen model version to use

    Returns:
        PIL.Image: Generated image as PIL Image object
    """
    client = genai.Client(api_key=GOOGLE_API_KEY)

    response = client.models.generate_images(
        model=model,
        prompt=prompt,
        config=dict(
            number_of_images=1,
            output_mime_type="image/jpeg",
            person_generation="ALLOW_ADULT",
            aspect_ratio="1:1",
        )
    )

    # Process response
    image_bytes = response.generated_images[0].image.image_bytes
    image = Image.open(BytesIO(image_bytes))

    return image
```

### Gemini Vision API

#### Multimodal Analysis: `GenerativeModel('gemini-2.5-flash')`
```python
from google.generativeai import GenerativeModel, Content, Part
import base64

def analyze_image_with_gemini(image_data, prompt_text):
    """
    Analyze image content using Gemini Vision capabilities

    Args:
        image_data: PIL Image or base64 data URL
        prompt_text (str): Analysis instructions

    Returns:
        str: AI-generated analysis response
    """
    # Convert image to base64
    if hasattr(image_data, 'save'):  # PIL Image
        buffer = io.BytesIO()
        image_data.save(buffer, format="PNG")
        base64_img = base64.b64encode(buffer.getvalue()).decode('utf-8')
    else:  # Data URL
        base64_img = image_data.split(",")[1]

    vision_model = GenerativeModel('gemini-2.5-flash')
    image_part = Part(inline_data={"mime_type": "image/png", "data": base64.b64decode(base64_img)})
    text_part = Part(text=prompt_text)
    multimodal_content = Content(parts=[image_part, text_part])

    response = vision_model.generate_content(multimodal_content)
    return response.text
```
    Generate an image using OpenAI's DALL-E API
    
    Args:
        prompt (str): Text description of the desired image
        n (int): Number of images to generate (1-10)
        size (str): Size of the generated images (256x256, 512x512, 1024x1024)
        response_format (str): Response format ("url" or "b64_json")
    
    Returns:
        dict: Response containing image URLs or base64 data
    """
    try:
        response = openai.Image.create(
            prompt=prompt,
            n=n,
            size=size,
            response_format=response_format
        )
        return response
    except Exception as e:
        print(f"Image generation failed: {e}")
        return None
```

**Parameters:**
- `prompt`: Up to 1000 characters describing the image
- `n`: Number of images to generate (1-10)
- `size`: Image dimensions (256x256, 512x512, 1024x1024)
- `response_format`: "url" for URLs, "b64_json" for base64 encoded images

**Rate Limits:**
- Standard: 10 requests per minute
- Enhanced: 50 requests per minute for paid accounts
- Images per minute: 50 images per minute

### Text Completion

#### Endpoint: `openai.Completion.create()`
```python
def generate_text(prompt, model="text-davinci-003", max_tokens=150, temperature=0.7):
    """
    Generate text using OpenAI's GPT model
    
    Args:
        prompt (str): Input text for completion
        model (str): Model name (text-davinci-003, text-curie-001, etc.)
        max_tokens (int): Maximum tokens in response (1-4096)
        temperature (float): Sampling temperature (0.0-1.0)
    
    Returns:
        str: Generated text completion
    """
    try:
        response = openai.Completion.create(
            model=model,
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature
        )
        return response.choices[0].text.strip()
    except Exception as e:
        print(f"Text generation failed: {e}")
        return None
```

## Google Generative AI Integration

### Setup Configuration

```python
import google.generativeai as genai
from config import GOOGLE_API_KEY

# Configure the API
genai.configure(api_key=GOOGLE_API_KEY)

# Initialize the model
model = genai.GenerativeModel('gemini-pro')
```

### Text Generation

#### Method: `model.generate_content()`
```python
def generate_text_with_gemini(prompt):
    """
    Generate text using Google's Gemini model
    
    Args:
        prompt (str): Input text for generation
    
    Returns:
        str: Generated text response
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Gemini text generation failed: {e}")
        return None
```

### Content Analysis

#### Method: `model.generate_content()` for Evaluation
```python
def evaluate_user_input(user_description, expected_details):
    """
    Use Gemini to evaluate user's image description against expected details
    
    Args:
        user_description (str): User's description of the image
        expected_details (list): List of details that should be identified
    
    Returns:
        dict: Evaluation results with accuracy score and feedback
    """
    prompt = f"""
    Evaluate the following description of an image:
    User Description: {user_description}
    
    Expected Details: {', '.join(expected_details)}
    
    Provide:
    1. Semantic accuracy score (0-100)
    2. Specific details identified correctly
    3. Details that were missed
    4. Constructive feedback to improve the description
    """
    
    try:
        response = model.generate_content(prompt)
        return parse_evaluation_response(response.text)
    except Exception as e:
        print(f"Evaluation failed: {e}")
        return None
```

### Safety Settings

```python
def create_model_with_safety():
    """
    Create a Gemini model instance with custom safety settings
    """
    model = genai.GenerativeModel(
        model_name='gemini-pro',
        safety_settings={
            'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_NONE',
            'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_NONE',
            'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_NONE',
            'HARM_CATEGORY_HARASSMENT': 'BLOCK_NONE'
        }
    )
    return model
```

## Google Drive API Integration

### Authentication Setup

```python
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

def authenticate_google_drive():
    """
    Authenticate with Google Drive API using OAuth2
    """
    # Use service account credentials or user credentials
    creds = Credentials.from_service_account_file('service_account.json')
    
    # Create Drive API service
    service = build('drive', 'v3', credentials=creds)
    return service
```

### File Operations

#### Upload File to Drive
```python
def upload_to_drive(file_path, folder_id=None):
    """
    Upload a file to Google Drive
    
    Args:
        file_path (str): Local path to the file
        folder_id (str): Optional folder ID to upload to
    
    Returns:
        dict: File metadata from Google Drive
    """
    service = authenticate_google_drive()
    
    file_metadata = {
        'name': os.path.basename(file_path)
    }
    
    if folder_id:
        file_metadata['parents'] = [folder_id]
    
    media = MediaFileUpload(file_path, resumable=True)
    
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id, webViewLink'
    ).execute()
    
    return file
```

#### Download File from Drive
```python
def download_from_drive(file_id, local_path):
    """
    Download a file from Google Drive
    
    Args:
        file_id (str): Google Drive file ID
        local_path (str): Local path to save the file
    
    Returns:
        bool: Success status
    """
    service = authenticate_google_drive()
    
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    
    done = False
    while done is False:
        status, done = downloader.next_chunk()
    
    with open(local_path, 'wb') as f:
        f.write(fh.getvalue())
    
    return True
```

#### Create Shared Folder
```python
def create_shared_folder(folder_name, user_email):
    """
    Create a shared folder in Google Drive with specific permissions
    
    Args:
        folder_name (str): Name of the folder to create
        user_email (str): Email of user to share with
    
    Returns:
        dict: Folder metadata
    """
    service = authenticate_google_drive()
    
    # Create folder
    file_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    
    folder = service.files().create(
        body=file_metadata,
        fields='id'
    ).execute()
    
    # Share folder with user
    permission = {
        'type': 'user',
        'role': 'writer',
        'emailAddress': user_email
    }
    
    service.permissions().create(
        fileId=folder.get('id'),
        body=permission,
        sendNotificationEmail=True
    ).execute()
    
    return folder
```

## API Error Handling

### Common Error Types

**OpenAI API Errors:**
- `AuthenticationError`: Invalid API key
- `RateLimitError`: API rate limit exceeded
- `InvalidRequestError`: Invalid parameters
- `APIError`: General API error

**Google API Errors:**
- `googleapiclient.errors.HttpError`: HTTP error from Google API
- `google.auth.exceptions.DefaultCredentialsError`: Authentication issues
- `google.api_core.exceptions.RetryError`: Rate limiting

### Error Handling Implementation

```python
def safe_api_call(api_function, *args, **kwargs):
    """
    Safely execute an API call with proper error handling
    
    Args:
        api_function: Function to call
        *args, **kwargs: Arguments to pass to function
    
    Returns:
        tuple: (success, result_or_error)
    """
    try:
        result = api_function(*args, **kwargs)
        return True, result
    except openai.error.AuthenticationError:
        return False, "Invalid API key for OpenAI"
    except openai.error.RateLimitError:
        return False, "Rate limit exceeded for OpenAI API"
    except openai.error.APIError as e:
        return False, f"OpenAI API error: {str(e)}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"

# Example usage:
success, result = safe_api_call(generate_image, "A cat", n=1, size="512x512")
if success:
    print("Image generated successfully")
else:
    print(f"Error: {result}")
```

## API Performance Optimization

### Rate Limiting

```python
import time
from functools import wraps

def rate_limit(calls_per_minute=60):
    """
    Decorator to implement rate limiting
    """
    min_interval = 60.0 / calls_per_minute
    last_called = [0.0]

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            left_to_wait = min_interval - elapsed
            if left_to_wait > 0:
                time.sleep(left_to_wait)
            ret = func(*args, **kwargs)
            last_called[0] = time.time()
            return ret
        return wrapper
    return decorator

@rate_limit(calls_per_minute=30)
def generate_image_with_rate_limit(prompt):
    return generate_image(prompt)
```

### Caching API Responses

```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=128)
def cached_image_generation(prompt_hash, prompt, size, style):
    """
    Cache image generations based on prompt content
    """
    return generate_image(prompt, size=size)

def get_prompt_hash(prompt, size, style):
    """
    Generate a hash for caching
    """
    content = f"{prompt}_{size}_{style}"
    return hashlib.md5(content.encode()).hexdigest()

def smart_generate_image(prompt, size="1024x1024", style="realistic"):
    """
    Generate image with caching
    """
    prompt_hash = get_prompt_hash(prompt, size, style)
    return cached_image_generation(prompt_hash, prompt, size, style)
```

## Security Best Practices

### API Key Security

**Client-Side Security:**
- Never expose API keys in client-side code
- Use server-side calls for all API interactions
- Implement proper authentication
- Validate and sanitize all inputs

**Server-Side Security:**
- Store keys in environment variables
- Use proper server authentication
- Implement request logging
- Monitor for unusual usage patterns

### Data Privacy

**User Data Protection:**
- Encrypt sensitive data in transit and at rest
- Minimize data collection
- Implement data retention policies
- Comply with GDPR, COPPA regulations

## API Monitoring

### Usage Tracking

```python
import logging

def log_api_usage(api_name, request_type, cost_estimate=None):
    """
    Log API usage for monitoring and billing
    """
    logger = logging.getLogger('api_usage')
    logger.info(f"API: {api_name}, Request: {request_type}, Cost: ${cost_estimate}")

# Example usage in API calls
def generate_image_with_logging(prompt):
    result = generate_image(prompt)
    log_api_usage("OpenAI", "Image Generation", 0.018)  # approximate cost
    return result
```

### Performance Monitoring

**Key Metrics:**
- API response times
- Success/failure rates
- Daily/monthly usage
- Error types and frequencies
- Cost tracking

## API Upgrade Paths

### OpenAI API Versions

**Current Usage:**
- GPT-3.5 and GPT-4 models
- DALL-E 2 and DALL-E 3 for image generation
- Whisper API for speech recognition (future)

**Future Upgrades:**
- GPT-4 Turbo for faster responses
- DALL-E 3 for higher quality images
- Custom fine-tuned models
- Real-time API capabilities

### Google API Features

**Current Support:**
- Gemini Pro for text generation
- Google Drive API for storage
- Google OAuth for authentication

**Future Integration:**
- Vision API for image analysis
- Translation API for multilingual support
- Sheets API for data management
- Calendar API for scheduling

## Support and Troubleshooting

### Common Issues

**Rate Limiting Issues:**
- Implement proper rate limiting in your code
- Use caching to reduce API calls
- Monitor your usage quotas

**Authentication Issues:**
- Verify your API keys are correct
- Check environment variable configuration
- Ensure proper credentials file access

**Response Quality Issues:**
- Adjust prompt engineering techniques
- Modify temperature and other parameters
- Consider using different models

### Contact Support

**For API-related issues:**
- OpenAI: https://help.openai.com/
- Google AI: https://cloud.google.com/ai-platform/docs/getting-support
- Google Drive API: https://developers.google.com/drive/api/support

**For VisoLearn-2 specific API questions:**
- GitHub Issues: https://github.com/visolearn/visolearn-2/issues
- Email: api-support@visolearn.org