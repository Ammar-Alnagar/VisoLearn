# Models and AI Documentation

## Overview

This document provides comprehensive documentation for the AI models, machine learning components, and AI integration systems in VisoLearn-2. It covers the image generation models, evaluation systems, story generation models, and all related AI functionality.

## AI Architecture Overview

### Model Integration Layers

```
VisoLearn-2 AI Layer
├── External AI Services
│   ├── OpenAI (DALL-E, GPT models)
│   ├── Google Gemini (Text generation, evaluation)
│   └── Hugging Face (Alternative models)
├── Custom Evaluation Engine
│   ├── Semantic Analysis
│   ├── Detail Extraction
│   └── Progress Tracking
├── Prompt Generation System
│   ├── Contextual Prompt Creation
│   ├── Style-based Formatting
│   └── Difficulty Adjustment
├── Computer Vision Components
│   ├── Panel Detection (OpenCV)
│   ├── Image Quality Assessment
│   └── Layout Optimization
└── AI Response Processing
    ├── Response Validation
    ├── Content Filtering
    └── User Feedback Integration
```

### AI Service Dependencies

**Primary Services:**
- OpenAI API (GPT-4, DALL-E 2/3)
- Google Generative AI (Gemini Pro)
- Hugging Face Hub (Alternative models)

**Secondary Services:**
- Computer Vision (OpenCV)
- Image Processing (Pillow)
- Natural Language Processing (Built-in)

## External AI Model Integration

### Google Generative AI (Gemini) Integration

#### Imagen 4.0 Ultra Image Generation

**Primary Model:** `models/imagen-4.0-ultra-generate-preview-06-06`

```python
import io
import base64
import os
from PIL import Image
from google import genai
from io import BytesIO
from config import GOOGLE_API_KEY

def generate_image_fn(selected_prompt, model="models/imagen-4.0-ultra-generate-preview-06-06", output_path=None):
    """
    Generate an image from the prompt via the Google Imagen 4.0 Ultra API.
    Convert the image to a data URL and optionally save it to a file.

    Args:
        selected_prompt (str): The prompt to generate the image from.
        model (str): The Imagen model to use. Defaults to "models/imagen-4.0-ultra-generate-preview-06-06".
        output_path (str, optional): If provided, saves the image to this path. Defaults to None.

    Returns:
        PIL.Image.Image or None: The generated image as a PIL Image object, or None on error.
    """
    try:
        # Initialize Google GenAI client
        client = genai.Client(api_key=GOOGLE_API_KEY)

        # Generate image using Google Imagen 4.0 Ultra
        response = client.models.generate_images(
            model=model,
            prompt=selected_prompt,
            config=dict(
                number_of_images=1,
                output_mime_type="image/jpeg",
                person_generation="ALLOW_ADULT",
                aspect_ratio="1:1",
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

        # Convert to base64 for data URL
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        img_bytes = buffered.getvalue()
        img_b64 = base64.b64encode(img_bytes).decode("utf-8")
        global_image_data_url = f"data:image/jpeg;base64,{img_b64}"

        print(f"Successfully generated image with prompt: {selected_prompt[:50]}...")
        return image
    except Exception as e:
        print(f"Error generating image: {str(e)}")
        return None
```

**Prompt Optimization for Imagen 4.0 Ultra:**
```python
def format_image_prompt(base_prompt, style_params):
    """
    Format prompt for optimal Google Imagen performance

    Args:
        base_prompt (str): Basic image concept
        style_params (dict): Style and difficulty parameters

    Returns:
        str: Optimized prompt string
    """
    # Difficulty-based detail level
    difficulty_details = {
        "Very Simple": "simple, basic shapes, minimal details, clear and uncluttered",
        "Simple": "clear, basic details, colorful, easy to understand",
        "Moderate": "detailed, colorful, educational, moderate complexity",
        "Detailed": "highly detailed, educational, rich colors, complex elements",
        "Very Detailed": "extremely detailed, educational, rich content, maximum complexity"
    }

    # Style-specific instructions (matching config.py IMAGE_STYLES)
    style_instructions = {
        "Realistic": "photorealistic, natural lighting, detailed textures",
        "Illustration": "digital illustration, artistic, vibrant colors",
        "Cartoon": "colorful cartoon, friendly characters, bold lines",
        "Watercolor": "watercolor painting style, soft edges, artistic",
        "3D Rendering": "3D computer rendering, modern graphics, detailed lighting"
    }

    # Combine all elements
    optimized_prompt = (
        f"{base_prompt}, "
        f"{style_instructions.get(style_params['style'], '')}, "
        f"{difficulty_details.get(style_params['difficulty'], '')}, "
        f"autism-friendly, educational, appropriate for children, positive and engaging"
    )

    return optimized_prompt
```

#### Gemini Text Processing

```python
import google.generativeai as genai
from config import GOOGLE_API_KEY

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')

def generate_text_completion(prompt, max_tokens=200, temperature=0.7):
    """
    Generate text using Google's Gemini model

    Args:
        prompt (str): Input text for completion
        max_tokens (int): Maximum tokens in response (approximated)
        temperature (float): Creativity parameter (0.0-1.0)

    Returns:
        str: Generated text completion
    """
    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            )
        )
        return response.text.strip()
    except Exception as e:
        print(f"Gemini text generation error: {e}")
        return ""
```

### OpenAI Integration (Fallback/Alternative)

#### Gemini Vision for Image Analysis and Evaluation

```python
import base64
import json
import re
from google.generativeai import GenerativeModel, Content, Part
from config import GOOGLE_API_KEY

def generate_detailed_description(image_input, prompt, difficulty, topic_focus):
    """
    Generate a detailed description of the image using Gemini Vision (gemini-2.5-flash).
    Converts image to base64 and analyzes with multimodal capabilities.

    Args:
        image_input: PIL Image or data URL
        prompt (str): Original generation prompt
        difficulty (str): Difficulty level
        topic_focus (str): Educational topic

    Returns:
        str: Detailed image description
    """
    try:
        # Convert image to base64
        if hasattr(image_input, 'save'):  # PIL Image
            buffer = io.BytesIO()
            image_input.save(buffer, format="PNG")
            img_bytes = buffer.getvalue()
            base64_img = base64.b64encode(img_bytes).decode('utf-8')
        elif isinstance(image_input, str) and image_input.startswith('data:image'):
            base64_img = image_input.split(",")[1]

        query = f"""
        You are an expert educator specializing in teaching users with autism.
        Please provide a detailed description of this image...

        [Full detailed prompt for educational image analysis]
        """

        vision_model = GenerativeModel('gemini-2.5-flash')
        image_part = Part(inline_data={"mime_type": "image/png", "data": base64.b64decode(base64_img)})
        text_part = Part(text=query)
        multimodal_content = Content(parts=[image_part, text_part])
        response = vision_model.generate_content(multimodal_content)
        return response.text.strip()
    except Exception as e:
        print(f"Error in generate_detailed_description: {str(e)}")
        return f"Error processing image: {str(e)}"

def extract_key_details(image_input, prompt, topic_focus):
    """
    Extract key details directly from the image using Gemini Vision.
    Returns a list of 5-15 key elements/details from the image.

    Args:
        image_input: PIL Image or data URL
        prompt (str): Original prompt
        topic_focus (str): Topic focus

    Returns:
        list: Key details as strings
    """
    try:
        # Convert to base64 (same as above)
        # ...

        query = f"""
        You are analyzing an educational image created for a person with autism...
        Please extract a list of unique key details... minimum 5, max 15...

        Format your response as a JSON array of strings...
        """

        vision_model = GenerativeModel('gemini-2.5-flash')
        # Create multimodal content and generate
        # ...

        # Parse JSON response
        json_match = re.search(r'\[.*\]', response.text, re.DOTALL)
        if json_match:
            key_details = json.loads(json_match.group(0))
            return key_details
        return ["object in image", "color", "shape", "background"]
    except Exception as e:
        print(f"Error in extract_key_details: {str(e)}")
        return ["Error processing image", "Please try again"]
```

#### Conceptual Evaluation with Gemini

```python
def compare_details_chat_fn(user_details, active_session, global_image_data_url, global_image_description):
    """
    Evaluate the user's description with strong focus on conceptual understanding
    and semantic meaning, rather than exact word matching.
    """
    # Build comprehensive evaluation prompt with session context
    message_text = f"""
    You are a highly specialized, supportive, and insightful teacher evaluating...

    ### Image Context:
    - Original Prompt: {active_session.get('prompt', 'No prompt available')}
    - Detailed Image Description: {global_image_description}

    ### Learning Task State:
    {key_details_text}  # Focus evaluation on REMAINING details

    ### User's Current Description (Analyze this carefully):
    '{user_details}'

    ### CONCEPTUAL MATCHING RULES (ABSOLUTELY CRITICAL):
    1. PRIORITIZE MEANING OVER WORDS: Focus entirely on SEMANTIC MEANING...
    2. CONCEPTUAL EQUIVALENCE: Does the user's statement describe the core concept...
    3. FLEXIBLE INTERPRETATION: Individuals with autism may use unique phrasing...

    ### RESPONSE REQUIREMENTS:
    Provide your evaluation STRICTLY as a valid JSON object...
    """

    model = GenerativeModel('gemini-2.5-flash')
    response = model.generate_content(message_text)

    return response.text  # Returns JSON with feedback, newly_identified_details, hint, score, advance_difficulty
```

#### Story Generation and Analysis with Gemini

```python
def generate_story_premise(topic_focus, difficulty, age, autism_level):
    """
    Generate a story premise based on user parameters using Gemini.
    Returns JSON with premise, educational_focus, num_scenes, and scenes array.
    """
    scene_counts = {
        "Very Simple": 2, "Simple": 3, "Moderate": 4,
        "Advanced": 4, "Complex": 5
    }

    num_scenes = max(2, min(5, scene_counts.get(difficulty, 3)))

    query = f"""
    You are an educational story designer for children with autism...
    Develop a simple narrative with clear beginning, middle, and end...

    FORMAT YOUR RESPONSE AS A VALID JSON OBJECT with fields: premise, educational_focus, num_scenes, scenes...
    """

    model = GenerativeModel('gemini-2.5-flash')
    response = model.generate_content(query)

    # Parse JSON response
    json_match = re.search(r'\{[\s\S]*\}', response.text, re.DOTALL)
    if json_match:
        story_data = json.loads(json_match.group(0))
        return story_data
    # Return fallback structure
```

### Hugging Face Integration

```python
from huggingface_hub import InferenceApi
from config import HF_TOKEN

def get_alternative_generation(prompt, model_name):
    """
    Use Hugging Face model as alternative to OpenAI/Gemini
    
    Args:
        prompt (str): Input prompt for generation
        model_name (str): Name of Hugging Face model to use
    
    Returns:
        str: Generated content
    """
    inference = InferenceApi(
        repo_id=model_name,
        token=HF_TOKEN
    )
    
    result = inference(inputs=prompt)
    return result
```

## Custom Evaluation Engine

#### Gemini Vision-Based Evaluation System

The evaluation system uses Google Gemini 2.5 Flash with vision capabilities to provide sophisticated, autism-friendly assessment of user descriptions.

```python
def compare_details_chat_fn(user_details, active_session, global_image_data_url, global_image_description):
    """
    Evaluate the user's description with strong focus on conceptual understanding
    and semantic meaning, rather than exact word matching.

    This function implements a comprehensive evaluation pipeline that:
    1. Builds detailed context from session history
    2. Applies conceptual matching rules optimized for autism
    3. Provides encouraging, specific feedback
    4. Tracks progress through identified details
    5. Suggests difficulty advancement when appropriate
    """

    # Build comprehensive evaluation prompt with session context
    message_text = f"""
    You are a highly specialized, supportive teacher evaluating an individual with autism...

    ### CONCEPTUAL MATCHING RULES (ABSOLUTELY CRITICAL):
    1. PRIORITIZE MEANING OVER WORDS: Focus on SEMANTIC MEANING and underlying IDEA
    2. CONCEPTUAL EQUIVALENCE: Accept synonyms, paraphrasing, or descriptive phrases
    3. FLEXIBLE INTERPRETATION: Interpret generously, assume competence
    4. GENEROSITY IS KEY: Err on the side of giving credit for conceptual understanding

    ### RESPONSE REQUIREMENTS:
    Return JSON with: feedback, newly_identified_details, hint, score, advance_difficulty
    """

    model = GenerativeModel('gemini-2.5-flash')
    response = model.generate_content(message_text)

    return response.text  # JSON evaluation results

def parse_evaluation(evaluation_text, active_session):
    """
    Parse LLM evaluation JSON and update session state.
    Handles robust JSON extraction with fallbacks.
    """
    try:
        # Extract JSON from response (handles markdown formatting)
        json_match = re.search(r'```(?:json)?\s*(\{[\s\S]*?\})\s*```|(\{[\s\S]*?\})(?=\s*$)', evaluation_text, re.DOTALL)

        if json_match:
            json_str = json_match.group(1) or json_match.group(2)
            evaluation = json.loads(json_str)
        else:
            evaluation = extract_evaluation_manually(evaluation_text)

        # Process and validate evaluation data
        feedback = evaluation.get("feedback", "Great job describing!")
        newly_identified_details = evaluation.get("newly_identified_details", [])
        score = evaluation.get("score", 0)
        advance_difficulty = evaluation.get("advance_difficulty", False)

        # Update session with newly identified details
        identified_details = active_session.get("identified_details", [])
        for detail in newly_identified_details:
            if detail in active_session.get("key_details", []) and detail not in identified_details:
                identified_details.append(detail)

        # Determine difficulty advancement
        should_advance = advance_difficulty or check_progress_threshold(active_session)

        return feedback, new_difficulty, should_advance, details_added, score

    except Exception as e:
        print(f"Error processing evaluation: {str(e)}")
        return safe_fallback_response()
```

#### Key Details Extraction from Images

```python
def extract_key_details(image_input, prompt, topic_focus):
    """
    Extract 5-15 key observable details from educational images using Gemini Vision.
    Focuses on concrete, visible elements that children can identify.
    """
    try:
        # Convert image to base64 for multimodal processing
        base64_img = convert_image_to_base64(image_input)

        query = f"""
        You are analyzing an educational image created for a person with autism...
        Please extract a list of unique key details... minimum 5, max 15...
        Focus on concrete, visible elements rather than abstract concepts.
        Format as JSON array: ["detail1", "detail2", ...]
        """

        vision_model = GenerativeModel('gemini-2.5-flash')
        image_part = Part(inline_data={"mime_type": "image/png", "data": base64.b64decode(base64_img)})
        text_part = Part(text=query)
        multimodal_content = Content(parts=[image_part, text_part])
        response = vision_model.generate_content(multimodal_content)

        # Parse JSON array from response
        json_match = re.search(r'\[.*\]', response.text, re.DOTALL)
        if json_match:
            key_details = json.loads(json_match.group(0))
            return key_details

        return ["object in image", "color", "shape", "background"]

    except Exception as e:
        print(f"Error in extract_key_details: {str(e)}")
        return ["Error processing image", "Please try again"]
```
    
    def evaluate_description(self, user_description, expected_details, difficulty_level):
        """
        Evaluate user's description against expected details
        """
        # Parse user description into components
        description_components = self.parse_description(user_description)
        
        # Calculate semantic similarity
        semantic_score = self.calculate_semantic_similarity(
            user_description, expected_details
        )
        
        # Calculate detail completeness
        detail_score = self.calculate_detail_completeness(
            description_components, expected_details
        )
        
        # Calculate final score based on difficulty
        final_score = self.weighted_scoring(
            semantic_score, detail_score, difficulty_level
        )
        
        # Generate feedback
        feedback = self.generate_feedback(
            final_score, description_components, 
            expected_details, difficulty_level
        )
        
        return {
            "semantic_score": semantic_score,
            "detail_score": detail_score,
            "final_score": final_score,
            "feedback": feedback,
            "identified_details": self.extract_identified_details(
                description_components, expected_details
            )
        }
    
    def parse_description(self, description):
        """
        Parse description into semantic components
        """
        import re
        from textblob import TextBlob
        
        # Extract nouns (objects)
        blob = TextBlob(description)
        nouns = [noun for noun in blob.noun_phrases]
        
        # Extract colors (using predefined color list)
        colors = re.findall(r'\b(?:red|blue|green|yellow|orange|purple|pink|brown|black|white|gray|grey)\b', description.lower())
        
        # Extract spatial relationships
        spatial = re.findall(r'\b(?:on|in|under|above|next to|behind|in front of)\b', description.lower())
        
        # Extract actions/verbs
        verbs = [word for word, pos in blob.tags if pos.startswith('VB')]
        
        return {
            "nouns": nouns,
            "colors": colors,
            "spatial": spatial,
            "verbs": verbs,
            "text": description
        }
    
    def calculate_semantic_similarity(self, user_desc, expected_details):
        """
        Calculate semantic similarity between user description and expected details
        """
        from sentence_transformers import SentenceTransformer
        
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Encode user description and expected details
        user_embedding = model.encode([user_desc])
        expected_embeddings = model.encode(expected_details)
        
        # Calculate cosine similarity
        from sklearn.metrics.pairwise import cosine_similarity
        similarities = cosine_similarity(user_embedding, expected_embeddings)
        
        # Return average similarity
        avg_similarity = similarities[0].mean()
        return min(avg_similarity * 100, 100)  # Scale to 0-100 range
```

### Progress Tracking System

```python
class ProgressTracker:
    """
    Track user progress and learning analytics
    """
    
    def __init__(self):
        self.difficulty_thresholds = {
            "very_simple": {"min_score": 70, "attempts": 3},
            "simple": {"min_score": 75, "attempts": 4},
            "moderate": {"min_score": 80, "attempts": 5},
            "detailed": {"min_score": 85, "attempts": 6},
            "very_detailed": {"min_score": 90, "attempts": 7}
        }
    
    def calculate_progress(self, session_history):
        """
        Calculate overall progress based on session history
        """
        if not session_history:
            return {"level": "very_simple", "score": 0}
        
        # Calculate average performance
        total_score = sum([s.get('score', 0) for s in session_history])
        avg_score = total_score / len(session_history) if session_history else 0
        
        # Calculate trend (improvement over time)
        recent_sessions = session_history[-5:]  # Last 5 sessions
        if len(recent_sessions) >= 2:
            recent_avg = sum([s.get('score', 0) for s in recent_sessions]) / len(recent_sessions)
            overall_avg = avg_score
            trend = recent_avg - overall_avg
        else:
            trend = 0
        
        # Determine current level based on performance and trends
        current_level = self.determine_level(avg_score, trend, session_history)
        
        return {
            "level": current_level,
            "average_score": avg_score,
            "trend": trend,
            "total_sessions": len(session_history),
            "next_level_estimate": self.estimate_next_level(current_level, avg_score)
        }
    
    def determine_level(self, avg_score, trend, session_history):
        """
        Determine the appropriate difficulty level
        """
        # Start conservative, adjust based on performance
        if avg_score >= 85 and trend > 2:
            # Strong performance with positive trend
            return self._advance_level(session_history[-1]['level'] if session_history else "very_simple")
        elif avg_score >= 70 and trend > 0:
            # Decent performance with slight improvement
            return session_history[-1]['level'] if session_history else "very_simple"
        elif avg_score < 60:
            # Poor performance, consider reducing difficulty
            return self._reduce_level(session_history[-1]['level'] if session_history and session_history[-1].get('level') else "very_simple")
        else:
            # Maintain current level
            return session_history[-1]['level'] if session_history and session_history[-1].get('level') else "very_simple"
    
    def estimate_next_level(self, current_level, avg_score):
        """
        Estimate when user will advance to next level
        """
        # Simplified estimate based on current performance
        if avg_score >= 85:
            return "soon"  # Likely to advance soon
        elif avg_score >= 75:
            return "moderate time"
        else:
            return "longer period"
```

## Prompt Generation System

### Dynamic Prompt Creation

```python
class PromptGenerator:
    """
    Generate optimized prompts for AI models based on context and requirements
    """
    
    def __init__(self):
        self.style_templates = {
            "realistic": "photorealistic, natural lighting, detailed textures, realistic proportions",
            "illustration": "digital illustration, artistic, vibrant colors, educational style",
            "cartoon": "colorful cartoon style, friendly characters, bold lines, expressive",
            "watercolor": "watercolor painting, soft edges, artistic, gentle tones",
            "3d_rendering": "3D computer rendering, modern graphics, detailed, realistic lighting"
        }
        
        self.difficulty_templates = {
            "very_simple": "simple shapes, basic concepts, few details, clear focus",
            "simple": "basic details, clear concepts, moderate complexity",
            "moderate": "detailed content, multiple elements, educational context",
            "detailed": "rich details, multiple elements, complex relationships",
            "very_detailed": "highly detailed, complex composition, educational focus"
        }
        
        self.autism_friendly_guidelines = [
            "avoid complex or cluttered backgrounds",
            "use clear, unambiguous visual elements",
            "include friendly, approachable characters",
            "avoid potentially distressing content",
            "maintain educational focus",
            "ensure age-appropriate content"
        ]
    
    def generate_image_prompt(self, base_description, style, difficulty, topic_focus=None):
        """
        Generate optimized image generation prompt
        
        Args:
            base_description (str): Basic image concept
            style (str): Visual style (realistic, cartoon, etc.)
            difficulty (str): Difficulty level
            topic_focus (str): Educational topic focus
        
        Returns:
            str: Optimized prompt for image generation
        """
        # Start with base description
        prompt = base_description
        
        # Add style-specific instructions
        style_instructions = self.style_templates.get(style, "")
        if style_instructions:
            prompt += f", {style_instructions}"
        
        # Add difficulty-based details
        difficulty_instructions = self.difficulty_templates.get(difficulty, "")
        if difficulty_instructions:
            prompt += f", {difficulty_instructions}"
        
        # Add educational focus if specified
        if topic_focus:
            prompt += f", focused on {topic_focus} concepts"
        
        # Add autism-friendly guidelines
        prompt += f", {', '.join(self.autism_friendly_guidelines)}"
        
        # Add quality and safety instructions
        prompt += ", high quality, educational, appropriate for children with autism"
        
        return prompt
    
    def generate_story_prompt(self, concept, characters, setting, difficulty):
        """
        Generate prompt for story creation
        
        Args:
            concept (str): Story concept
            characters (list): Character descriptions
            setting (str): Story setting
            difficulty (str): Story complexity level
        
        Returns:
            dict: Structured prompt for story generation
        """
        story_prompt = {
            "concept": concept,
            "characters": characters,
            "setting": setting,
            "difficulty": difficulty,
            "instructions": [
                "maintain character consistency across panels",
                "ensure narrative coherence",
                "include educational elements appropriate for autism",
                "create age-appropriate content",
                "focus on positive, encouraging themes"
            ],
            "style_guidelines": self.style_templates,
            "complexity_guidelines": self.difficulty_templates
        }
        
        return story_prompt
```

## Story Generation Models

### Gemini-Powered Sequential Story Creation

```python
def generate_story_premise(topic_focus, difficulty, age, autism_level):
    """
    Generate a story premise based on user parameters using Gemini.
    Creates structured JSON with premise, educational focus, scene count, and scene details.

    Args:
        topic_focus (str): Educational topic for the story
        difficulty (str): Complexity level (Very Simple to Complex)
        age (str): Child's age
        autism_level (str): Autism support level

    Returns:
        dict: Story structure with scenes array
    """
    # Calculate appropriate number of scenes based on parameters
    scene_counts = {
        "Very Simple": 2, "Simple": 3, "Moderate": 4,
        "Advanced": 4, "Complex": 5
    }

    # Adjust for autism level
    level_adjustments = {"Level 1": 0, "Level 2": -1, "Level 3": -2}
    base_count = scene_counts.get(difficulty, 3)
    adjustment = level_adjustments.get(autism_level, 0)
    num_scenes = max(2, min(5, base_count + adjustment))

    query = f"""
    You are an educational story designer for children with autism...
    Create a simple story premise related to '{topic_focus}' that can be told in {num_scenes} sequential images.

    IMPORTANT: Each scene must visually connect to create a coherent story flow.
    Maintain consistent characters throughout all scenes.

    FORMAT AS JSON: premise, educational_focus, num_scenes, scenes array
    """

    model = GenerativeModel('gemini-2.5-flash')
    response = model.generate_content(query)

    # Parse JSON response with robust error handling
    try:
        json_match = re.search(r'\{[\s\S]*\}', response.text, re.DOTALL)
        if json_match:
            story_data = json.loads(json_match.group(0))
            return story_data
    except Exception as e:
        print(f"Error parsing story premise: {e}")

    # Return fallback structure
    return {
        "premise": f"A simple story about {topic_focus}",
        "educational_focus": topic_focus,
        "num_scenes": num_scenes,
        "scenes": [{"scene_number": i+1, "description": f"Scene {i+1}",
                   "key_elements": ["character", "setting", "action"],
                   "transition": "The story continues..."} for i in range(num_scenes)]
    }

def generate_scene_prompt(scene_data, story_premise, difficulty, age, autism_level, image_style="Comic"):
    """
    Generate optimized image prompt for individual story scenes.
    Emphasizes visual continuity and character consistency across panels.
    """
    scene_number = scene_data.get("scene_number", 1)
    scene_description = scene_data.get("description", "")
    key_elements = scene_data.get("key_elements", [])

    continuity_instruction = """
    CRITICAL STORY CONTINUITY REQUIREMENTS:
    - Characters MUST maintain exact same appearance across all scenes
    - Settings should maintain consistent visual style and color palette
    - Visual elements should be identical in style and appearance
    - Use matching artistic style, lighting, and perspective
    """

    query = f"""
    Create an image generation prompt for scene {scene_number} in a sequence...

    STORY CONTEXT: "{story_premise}"
    SCENE: "{scene_description}"
    KEY ELEMENTS: {', '.join(key_elements)}

    {continuity_instruction}

    REQUIREMENTS:
    - Start with "A {image_style.lower()} scene showing [description]"
    - Include 8-10 specific visual elements with positions
    - Maintain visual consistency with previous scenes
    - At least 150 words, end with "8k resolution, professional {image_style.lower()}"
    """

    model = GenerativeModel('gemini-2.5-flash')
    response = model.generate_content(query)
    return response.text.strip()

def evaluate_story_understanding(user_description, story_data, current_scene, active_session):
    """
    Evaluate child's understanding of story comprehension, not just image details.
    Returns JSON with multiple comprehension metrics.
    """
    scene_info = story_data["scenes"][current_scene-1]
    premise = story_data.get("premise", "")

    query = f"""
    Evaluate a child with autism level {active_session.get('autism_level')} describing a story...

    STORY: "{premise}"
    CURRENT SCENE: "{scene_info.get('description', '')}"
    CHILD'S DESCRIPTION: "{user_description}"

    Evaluate understanding of:
    1. Current scene details
    2. Story connections
    3. Character continuity
    4. Cause-effect relationships
    5. Emotional understanding

    Return JSON: feedback, story_understanding_score, scene_details_score,
    narrative_connection_score, identified_elements, missed_elements,
    hint, question_prompt, advance_to_next_scene
    """

    model = GenerativeModel('gemini-2.5-flash')
    response = model.generate_content(query)

    # Parse and return evaluation JSON
    try:
        json_match = re.search(r'\{[\s\S]*\}', response.text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
    except Exception as e:
        print(f"Error parsing story evaluation: {e}")

    return fallback_evaluation_structure()
```
    
    def generate_concept(self, topic, difficulty):
        """
        Generate initial story concept based on topic and difficulty
        """
        prompt = f"""
        Create an educational story concept for children with autism.
        
        TOPIC: {topic}
        DIFFICULTY: {difficulty}
        
        Requirements:
        - Educational focus on the given topic
        - Appropriate for children with autism
        - Clear, simple narrative structure
        - Positive, encouraging message
        - Should work well as a {difficulty} level story
        
        Provide: brief concept summary, educational goals, target age group
        """
        
        gemini_response = self.call_gemini(prompt)
        return self.parse_concept_response(gemini_response)
    
    def generate_characters(self, concept, num_panels):
        """
        Generate consistent characters for the story
        """
        prompt = f"""
        Create character descriptions for this story:
        {concept}
        
        Create characters that:
        - Are appropriate for the educational topic
        - Will remain consistent across {num_panels} panels
        - Are approachable and friendly for children with autism
        - Support the educational goals of the story
        
        Provide: character names, physical descriptions, personality traits, roles
        """
        
        gemini_response = self.call_gemini(prompt)
        return self.parse_character_response(gemini_response)
    
    def generate_plot(self, concept, characters, num_panels):
        """
        Generate plot structure for the story
        """
        prompt = f"""
        Create a {num_panels}-panel plot structure for this story:
        Concept: {concept}
        Characters: {characters}
        
        Structure:
        - Panel {num_panels} should cover the complete narrative arc
        - Each panel should advance the story meaningfully
        - Maintain character consistency
        - Include educational elements
        - Ensure smooth transitions between panels
        
        Provide: plot outline with key events for each panel
        """
        
        gemini_response = self.call_gemini(prompt)
        return self.parse_plot_response(gemini_response)
    
    def generate_panels(self, plot, characters, style, difficulty, num_panels):
        """
        Generate individual comic panels
        """
        panels = []
        
        for panel_num in range(1, num_panels + 1):
            panel_prompt = f"""
            Generate panel {panel_num} of {num_panels} for this story:
            Plot: {plot}
            Characters: {characters}
            Style: {style}
            Difficulty: {difficulty}
            
            Panel {panel_num} should:
            - Show the scene described in the plot
            - Include the relevant characters
            - Match the specified visual style
            - Be appropriate for the difficulty level
            - Maintain visual consistency with other panels
            
            Provide: detailed scene description, character positioning, visual elements
            """
            
            gemini_response = self.call_gemini(panel_prompt)
            panel_data = self.parse_panel_response(gemini_response)
            
            # Generate image for the panel
            image_prompt = self.prompt_generator.generate_image_prompt(
                panel_data["scene_description"],
                style,
                difficulty
            )
            
            panel_image = self.generate_panel_image(image_prompt)
            
            panels.append({
                "panel_number": panel_num,
                "scene_description": panel_data["scene_description"],
                "character_positions": panel_data["character_positions"],
                "key_elements": panel_data["key_elements"],
                "image_prompt": image_prompt,
                "image_url": panel_image,
                "educational_elements": panel_data.get("educational_elements", [])
            })
        
        return panels
    
    def validate_story_coherence(self, panels):
        """
        Validate that the story maintains narrative coherence
        """
        # Check for consistency in character appearance
        character_consistency = self.check_character_consistency(panels)
        
        # Check for logical story progression
        narrative_flow = self.check_narrative_flow(panels)
        
        # Check for visual continuity
        visual_continuity = self.check_visual_continuity(panels)
        
        # Calculate overall coherence score
        coherence_score = (character_consistency + narrative_flow + visual_continuity) / 3
        
        return coherence_score >= 0.7  # Return True if coherence is sufficient
    
    def check_character_consistency(self, panels):
        """
        Check for consistency in character appearance across panels
        """
        # Implementation for character consistency check
        # This would compare character descriptions across panels
        # and return a score between 0 and 1
        return 0.8  # Placeholder score
    
    def check_narrative_flow(self, panels):
        """
        Check for logical story progression
        """
        # Implementation for narrative flow check
        # This would analyze the plot progression
        return 0.9  # Placeholder score
    
    def check_visual_continuity(self, panels):
        """
        Check for visual continuity across panels
        """
        # Implementation for visual continuity check
        # This would analyze visual elements across panels
        return 0.85  # Placeholder score
```

## Computer Vision Components

### Panel Detection with OpenCV

```python
import cv2
import numpy as np
from PIL import Image
import math

class PanelDetector:
    """
    Detect and extract comic panels using computer vision
    """
    
    def __init__(self):
        self.min_panel_area = 1000  # Minimum area for a valid panel
        self.max_panel_aspect_ratio = 3.0  # Max width/height ratio
        self.min_panel_width = 50  # Minimum panel width
        self.min_panel_height = 50  # Minimum panel height
    
    def detect_panels(self, comic_image_path):
        """
        Detect comic panels in a multi-panel comic image
        
        Args:
            comic_image_path (str): Path to the comic image
            
        Returns:
            list: List of panel coordinates and extracted images
        """
        # Load image
        image = cv2.imread(comic_image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply threshold to create binary image
        _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        panels = []
        for contour in contours:
            # Calculate bounding rectangle
            x, y, w, h = cv2.boundingRect(contour)
            
            # Filter based on size and aspect ratio
            if self.is_valid_panel(w, h):
                # Extract panel from original image
                panel_image = image[y:y+h, x:x+w]
                
                panels.append({
                    'x': x,
                    'y': y,
                    'width': w,
                    'height': h,
                    'image': panel_image,
                    'area': w * h
                })
        
        # Sort panels from left to right, top to bottom
        panels.sort(key=lambda p: (p['y'], p['x']))
        
        return panels
    
    def is_valid_panel(self, width, height):
        """
        Check if a detected region is a valid comic panel
        """
        area = width * height
        aspect_ratio = max(width, height) / min(width, height) if min(width, height) > 0 else float('inf')
        
        return (
            area >= self.min_panel_area and
            width >= self.min_panel_width and
            height >= self.min_panel_height and
            aspect_ratio <= self.max_panel_aspect_ratio
        )
    
    def extract_and_process_panels(self, comic_image_path):
        """
        Extract and process comic panels with quality validation
        """
        detected_panels = self.detect_panels(comic_image_path)
        
        processed_panels = []
        for panel in detected_panels:
            # Convert OpenCV image to PIL for further processing
            pil_image = Image.fromarray(cv2.cvtColor(panel['image'], cv2.COLOR_BGR2RGB))
            
            # Validate panel quality
            if self.validate_panel_quality(pil_image):
                # Resize if necessary
                resized_panel = self.resize_panel(pil_image)
                
                processed_panels.append({
                    'coordinates': (panel['x'], panel['y'], panel['width'], panel['height']),
                    'image': resized_panel,
                    'width': resized_panel.width,
                    'height': resized_panel.height
                })
        
        return processed_panels
    
    def validate_panel_quality(self, image):
        """
        Validate that the extracted panel meets quality standards
        """
        # Check image sharpness
        np_image = np.array(image)
        gray_image = cv2.cvtColor(np_image, cv2.COLOR_RGB2GRAY)
        
        # Calculate Laplacian variance for sharpness
        laplacian_var = cv2.Laplacian(gray_image, cv2.CV_64F).var()
        
        # Check for minimum sharpness
        min_sharpness_threshold = 100  # Adjust based on testing
        
        return laplacian_var > min_sharpness_threshold
    
    def resize_panel(self, image, target_size=(400, 400)):
        """
        Resize panel to target dimensions while maintaining aspect ratio
        """
        image.thumbnail(target_size, Image.Resampling.LANCZOS)
        return image
```

## AI Response Processing

### Response Validation and Filtering

```python
import re
from typing import Dict, List, Any

class AIResponseProcessor:
    """
    Process and validate AI model responses
    """
    
    def __init__(self):
        self.content_filters = [
            self._filter_inappropriate_content,
            self._filter_violent_content,
            self._filter_disturbing_imagery,
            self._validate_educational_appropriateness
        ]
        
        self.safety_keywords = [
            "violence", "injury", "harm", "weapon", "blood", 
            "scary", "frightening", "disturbing", "inappropriate",
            "adult", "nudity", "drugs", "alcohol"
        ]
    
    def process_image_generation(self, raw_response):
        """
        Process image generation response
        
        Args:
            raw_response: Raw response from image generation API
            
        Returns:
            dict: Processed and validated response
        """
        if isinstance(raw_response, dict) and 'data' in raw_response:
            processed_images = []
            
            for item in raw_response['data']:
                # Validate content safety
                if not self._is_content_safe(item.get('revised_prompt', '')):
                    continue  # Skip unsafe content
                
                processed_images.append({
                    'url': item.get('url'),
                    'revised_prompt': item.get('revised_prompt'),
                    'content_safe': True
                })
            
            return {'images': processed_images, 'count': len(processed_images)}
        else:
            return {'images': [], 'count': 0, 'error': 'Invalid response format'}
    
    def process_text_generation(self, raw_response, context_type='general'):
        """
        Process text generation response based on context
        
        Args:
            raw_response: Raw text from AI model
            context_type: Type of content being generated
            
        Returns:
            dict: Processed and validated text response
        """
        processed_text = raw_response.strip()
        
        # Apply content filters
        if not self._is_text_content_safe(processed_text, context_type):
            return {'text': '', 'safe': False, 'reason': 'Content filtered'}
        
        # Format for different contexts
        if context_type == 'feedback':
            processed_text = self._format_feedback(processed_text)
        elif context_type == 'story':
            processed_text = self._format_story(processed_text)
        elif context_type == 'evaluation':
            processed_text = self._parse_evaluation_response(processed_text)
        
        return {'text': processed_text, 'safe': True}
    
    def _is_content_safe(self, prompt, image_analysis=None):
        """
        Check if content is safe for children with autism
        """
        prompt_lower = prompt.lower()
        
        for keyword in self.safety_keywords:
            if keyword in prompt_lower:
                return False
        
        # Additional checks could include image analysis if available
        return True
    
    def _is_text_content_safe(self, text, context_type):
        """
        Validate that generated text is appropriate
        """
        text_lower = text.lower()
        
        # Check for safety keywords
        for keyword in self.safety_keywords:
            if keyword in text_lower:
                return False
        
        # Context-specific validation
        if context_type == 'feedback':
            # Ensure feedback is constructive and encouraging
            if self._contains_negative_or_discouraging_language(text):
                return False
        
        return True
    
    def _contains_negative_or_discouraging_language(self, text):
        """
        Check if text contains negative or discouraging language
        """
        negative_patterns = [
            r'\b(wrong\b|bad\b|stupid\b|dumb\b|hopeless\b|can\'t\b|never\b)',
            r'\b(should have\b|could have\b|better than\b)',
            r'(you are not\b|you can\'t\b|this is wrong\b)'
        ]
        
        for pattern in negative_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    def _format_feedback(self, feedback_text):
        """
        Format feedback to be encouraging and autism-friendly
        """
        # Ensure feedback is constructive
        sentences = feedback_text.split('.')
        
        formatted_feedback = []
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                # Make sure it's encouraging
                sentence = self._make_sentence_encouraging(sentence)
                formatted_feedback.append(sentence)
        
        return '. '.join(formatted_feedback)
    
    def _make_sentence_encouraging(self, sentence):
        """
        Transform potentially discouraging sentences into encouraging ones
        """
        # Replace negative constructions with positive ones
        replacements = {
            "you can't": "you're learning to",
            "wrong": "not quite right, let's try",
            "bad": "needs practice, you're doing well",
            "incorrect": "different from expected, interesting perspective"
        }
        
        for old, new in replacements.items():
            sentence = re.sub(old, new, sentence, flags=re.IGNORECASE)
        
        return sentence
    
    def _parse_evaluation_response(self, response_text):
        """
        Parse evaluation response into structured format
        """
        # Look for common patterns in evaluation responses
        import json
        
        try:
            # Try to parse as JSON if it's formatted that way
            eval_data = json.loads(response_text)
            return eval_data
        except json.JSONDecodeError:
            # Parse using regex patterns
            accuracy_match = re.search(r'accuracy[:\s]+(\d+)', response_text, re.IGNORECASE)
            feedback_match = re.search(r'feedback[:\s]+(.+?)(?:\n|$)', response_text, re.IGNORECASE | re.DOTALL)
            
            result = {}
            if accuracy_match:
                result['accuracy'] = int(accuracy_match.group(1))
            
            if feedback_match:
                result['feedback'] = feedback_match.group(1).strip()
            
            return result
```

## Model Configuration and Optimization

### Performance Optimization

```python
import asyncio
import concurrent.futures
from functools import lru_cache

class ModelOptimizer:
    """
    Optimize AI model usage and caching
    """
    
    def __init__(self):
        self.image_cache = {}
        self.text_cache = {}
        self.max_cache_size = 1000
    
    @lru_cache(maxsize=128)
    def cached_image_generation(self, prompt_hash, prompt, style, difficulty):
        """
        Cache image generations to reduce API calls
        """
        from models.image_generation import generate_image
        
        return generate_image(prompt, style, difficulty)
    
    def get_cache_key(self, prompt, style, difficulty):
        """
        Generate cache key for a request
        """
        import hashlib
        content = f"{prompt}_{style}_{difficulty}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def smart_generate_image(self, prompt, style, difficulty):
        """
        Generate image with caching
        """
        cache_key = self.get_cache_key(prompt, style, difficulty)
        
        if cache_key in self.image_cache:
            return self.image_cache[cache_key]
        
        # Generate new image
        result = self.cached_image_generation(cache_key, prompt, style, difficulty)
        
        # Add to cache if not full
        if len(self.image_cache) < self.max_cache_size:
            self.image_cache[cache_key] = result
        
        return result
    
    def async_process_batch(self, requests):
        """
        Process multiple requests asynchronously
        """
        async def process_single_request(request):
            # Process individual request based on type
            if request['type'] == 'image':
                return self.smart_generate_image(
                    request['prompt'], 
                    request['style'], 
                    request['difficulty']
                )
            elif request['type'] == 'text':
                from models.evaluation import evaluate_response
                return evaluate_response(
                    request['user_input'],
                    request['expected_details'],
                    request['difficulty']
                )
        
        async def process_batch():
            tasks = [process_single_request(req) for req in requests]
            return await asyncio.gather(*tasks)
        
        return asyncio.run(process_batch())
```

## Safety and Moderation

### Content Moderation System

```python
class ContentModerator:
    """
    Moderate content generated by AI models
    """
    
    def __init__(self):
        self.moderation_threshold = 0.7  # Score threshold for content approval
        
    def moderate_image_content(self, image_url, prompt):
        """
        Moderate image content using OpenAI's moderation API
        """
        try:
            import openai
            # Check prompt for safety
            prompt_moderation = openai.Moderation.create(input=prompt)
            prompt_results = prompt_moderation.results[0]
            
            if prompt_results.flagged:
                return {
                    'allowed': False,
                    'reason': f'Prompt flagged for: {", ".join([category for category, flagged in prompt_results.categories.__dict__.items() if flagged])}',
                    'prompt_moderation': prompt_results
                }
            
            # Image moderation would require analyzing the image content
            # This could involve another API or different approach
            return {
                'allowed': True,
                'reason': 'Content approved',
                'prompt_moderation': prompt_results
            }
            
        except Exception as e:
            # If moderation fails, we should be conservative
            return {
                'allowed': False,
                'reason': f'Moderation error: {str(e)}',
                'prompt_moderation': None
            }
    
    def moderate_text_content(self, text, context_type='general'):
        """
        Moderate text content based on context
        """
        try:
            import openai
            moderation = openai.Moderation.create(input=text)
            results = moderation.results[0]
            
            if results.flagged:
                categories_flagged = [category for category, flagged in results.categories.__dict__.items() if flagged]
                return {
                    'allowed': False,
                    'reason': f'Text flagged for: {", ".join(categories_flagged)}',
                    'moderation_results': results
                }
            
            return {
                'allowed': True,
                'reason': 'Text approved',
                'moderation_results': results
            }
            
        except Exception as e:
            return {
                'allowed': False,
                'reason': f'Moderation error: {str(e)}',
                'moderation_results': None
            }
```

## Analytics and Model Performance

### Model Usage Analytics

```python
import time
import json
from datetime import datetime

class ModelAnalytics:
    """
    Track and analyze model usage and performance
    """
    
    def __init__(self):
        self.analytics_data = {
            'api_calls': 0,
            'response_times': [],
            'success_rate': 0.0,
            'error_types': {},
            'cost_tracking': 0.0
        }
    
    def log_api_call(self, model_name, response_time, success=True, cost=0.0):
        """
        Log API call for analytics
        """
        self.analytics_data['api_calls'] += 1
        self.analytics_data['response_times'].append(response_time)
        
        if success:
            successful_calls = sum(1 for x in self.analytics_data['response_times'] if x > 0)
            self.analytics_data['success_rate'] = successful_calls / len(self.analytics_data['response_times'])
        else:
            self.analytics_data['success_rate'] = (self.analytics_data['api_calls'] - 1) / self.analytics_data['api_calls']
        
        self.analytics_data['cost_tracking'] += cost
    
    def get_performance_metrics(self):
        """
        Get current performance metrics
        """
        if not self.analytics_data['response_times']:
            return {
                'api_calls': 0,
                'avg_response_time': 0,
                'success_rate': 0,
                'total_cost': 0
            }
        
        avg_response_time = sum(self.analytics_data['response_times']) / len(self.analytics_data['response_times'])
        
        return {
            'api_calls': self.analytics_data['api_calls'],
            'avg_response_time': round(avg_response_time, 2),
            'success_rate': round(self.analytics_data['success_rate'], 3),
            'total_cost': round(self.analytics_data['cost_tracking'], 4)
        }
    
    def export_analytics(self, filename=None):
        """
        Export analytics data to file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_filename = filename or f"model_analytics_{timestamp}.json"
        
        with open(export_filename, 'w') as f:
            json.dump(self.analytics_data, f, indent=2, default=str)
        
        return export_filename
```

## Future AI Enhancements

### Planned AI Improvements

**Short-term Enhancements (Q1 2024):**
- Fine-tuned models for autism-specific content
- Improved evaluation algorithms
- Enhanced story coherence systems

**Medium-term Goals (Q2-Q3 2024):**
- Multimodal AI for image-text understanding
- Personalized model adaptation
- Advanced analytics and insights

**Long-term Vision (2024-2025):**
- Real-time adaptation algorithms
- Predictive AI for skill development
- Multilingual support expansion

## Troubleshooting

### Common AI Issues

**API Rate Limiting:**
- Implement proper rate limiting
- Use caching strategies
- Monitor usage quotas

**Content Quality Issues:**
- Refine prompt engineering
- Adjust model parameters
- Implement content validation

**Response Time Problems:**
- Use async processing
- Implement fallback models
- Optimize request batching

## Additional Resources

**AI Model Documentation:**
- OpenAI API: https://platform.openai.com/docs/
- Google Generative AI: https://ai.google.dev/
- Hugging Face: https://huggingface.co/docs

**Research Papers:**
- "AI in Autism Education" research
- "Multimodal Learning for Children with Autism"
- "Personalized AI Learning Systems"

**Development Tools:**
- Sentence Transformers library
- TextBlob for NLP
- OpenCV for computer vision
- PyTorch/TensorFlow for custom models