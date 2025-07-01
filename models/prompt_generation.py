from google.generativeai import GenerativeModel
from config import DEFAULT_TREATMENT_PLANS, get_enhanced_style_specifications, get_style_prompt_enhancement

def generate_prompt_from_options(difficulty, age, autism_level, topic_focus, treatment_plan="", image_style="Photorealistic"):
    """
    Generate an optimized image prompt using Google's Gemini model.
    If no treatment plan is provided, use a default one based on the autism level.
    """
    # Use default treatment plan if none provided
    if not treatment_plan or treatment_plan.strip() == "":
        treatment_plan = DEFAULT_TREATMENT_PLANS.get(autism_level, DEFAULT_TREATMENT_PLANS["Level 1"])
        print(f"Using default treatment plan for {autism_level}: {treatment_plan}")

    # Get enhanced style specifications
    style_instruction = get_style_prompt_enhancement(image_style)

    query = f"""Create a detailed image generation prompt for a 16-scene educational composition.

PARAMETERS:
- Difficulty: {difficulty} | Age: {age} | Autism Level: {autism_level}
- Topic: {topic_focus} | Treatment Plan: {treatment_plan}
- Style: {style_instruction}

REQUIREMENTS:
1. LAYOUT: 16 distinct scenes in a 4x4 grid, each scene 3-5% of canvas
2. QUALITY: Modern digital finish, crystal clear, zero blur/sketch, perfect anatomy
3. CONTENT: All scenes relate to "{topic_focus}" and incorporate treatment plan elements
4. TECHNICAL: Ultra-high detail, 16k resolution, professional {image_style.lower()}

FORMAT: Start with "A {image_style.lower()} 16-scene composition featuring {topic_focus}..."
Include specific details for lighting, colors, textures, and spatial relationships.
End with: "16k resolution, crystal clear focus, zero blur, professional {image_style.lower()}, perfect anatomical accuracy"

Create your prompt (200-300 words):"""

    model = GenerativeModel('gemini-2.5-flash')
    response = model.generate_content(query)
    return response.text.strip()
