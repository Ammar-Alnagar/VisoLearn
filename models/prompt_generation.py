from google.generativeai import GenerativeModel
from config import DEFAULT_TREATMENT_PLANS

def generate_prompt_from_options(difficulty, age, autism_level, topic_focus, treatment_plan="", image_style="Realistic"):
    """
    Generate an image prompt using Google's Gemini model.
    If no treatment plan is provided, use a default one based on the autism level.
    """
    # Use default treatment plan if none provided
    if not treatment_plan or treatment_plan.strip() == "":
        treatment_plan = DEFAULT_TREATMENT_PLANS.get(autism_level, DEFAULT_TREATMENT_PLANS["Level 1"])
        print(f"Using default treatment plan for {autism_level}: {treatment_plan}")

    # Modify the prompt to incorporate the selected style
    style_instruction = ""
    if image_style == "Realistic":
        style_instruction = "Create a  realistic image with natural lighting and detailed textures, capturing the essence of real-world environments. Ensure the scene has a lifelike feel, with accurate light and shadow play, and textures that convey a true-to-life appearance."
    elif image_style == "Illustration":
        style_instruction = "Create a clean and colorful illustration in the style of children's books, featuring bold outlines, vibrant colors, and a playful, engaging composition. Ensure the artwork has a soft, friendly feel with well-defined shapes and a sense of warmth and charm."
    elif image_style == "Cartoon":
        style_instruction = "Create a friendly cartoon-style illustration with simplified shapes, bold outlines, and expressive characters. Ensure the characters have exaggerated facial expressions and dynamic poses to convey emotion and personality in a warm and inviting way."
    elif image_style == "Watercolor":
        style_instruction = "Create a soft watercolor illustration with gentle color transitions, delicate brushstrokes, and a dreamy, ethereal quality. Ensure the colors blend seamlessly, evoking a sense of warmth and tranquility."
    elif image_style == "3D Rendering":
        style_instruction = "Create a highly detailed 3D-rendered image with realistic depth, rich textures, and natural lighting effects. Ensure accurate reflections, shadows, and materials to enhance the sense of realism and immersion."

    query = (
        f"""
        Your task is to create an EXCEPTIONAL image generation prompt that will produce an educational image.
        PARAMETERS:
        - Difficulty: {difficulty}
        - Person's Age: {age}
        - Autism Level: {autism_level}
        - Topic Focus: {topic_focus}
        - Treatment Plan: {treatment_plan}
        - Image Style: {style_instruction}
        CRITICAL PROMPT REQUIREMENTS:
        1. START WITH A CLEAR CONCEPT: Begin with "A {image_style.lower()} [scene description]" or "An {image_style.lower()} of [scene description]"
        2. ULTRA-SPECIFIC VISUAL DETAILS: Include at least 8-10 specific visual elements with clear positions and relationships
        3. EXACT COLOR SPECIFICATION: Use precise color terminology (e.g., "pastel mint green" not just "green")
        4. LIGHTING DIRECTIVES: Specify lighting quality (e.g., "soft diffused morning light", "dramatic side lighting")
        5. CAMERA ANGLE & PERSPECTIVE: Include exact viewing angle (e.g., "eye-level close-up", "overhead view")
        6. ARTISTIC STYLE: Reference specific art styles appropriate for autism education reflecting the selected style: {image_style}
        7. EMOTIONAL TONE: Explicitly state the emotional quality (e.g., "calm", "joyful", "serene atmosphere")
        8. TEXTURE SPECIFICS: Detail textures visible in the image (e.g., "soft plush texture", "smooth polished surface")
        9. Realism: Incorporate elements, textures, and lighting to enhance the image's depth according to the {image_style} style.
        TECHNICAL REQUIREMENTS:
        - Your prompt MUST be at least 150 words long
        - Include the exact phrase "high detail, high quality , 4k"  in your prompt
        - End with a technical directive: "8k resolution, professional {image_style.lower()}, masterful composition"
        - Add style-appropriate elements for {image_style} imagery
        - Ensure the Image follows the {image_style} style guidelines
        - Ensure the Image is not blurry or pixelated.
        - Ensure the Image is not overly saturated or desaturated.
        - Ensure the Image is not overly bright or dark.
        - Ensure the Image is not overly contrasty or flat.
        - Ensure the Image is not overly abstract or overly detailed for the selected style.
        - Ensure there are no deformations or distortions.
        - Ensure the image is not blurry
        -Ensure maximum detail and  quality.

        TOPIC INTEGRATION:
        The image MUST focus primarily on "{topic_focus}" while incorporating elements from the treatment plan: "{treatment_plan}".
        EXAMPLE FORMAT:
        "A {image_style.lower()} scene of [main subject] with [specific details]. The [subject] is positioned [exact location] with [specific posture/action]. The lighting is [specific lighting description] creating [specific effect]. The background features [specific background elements] in [specific colors]. The foreground includes [specific foreground elements]. The scene conveys a feeling of [emotional quality]. In the style of [specific artistic reference]. High detail, sharp focus, 8k resolution, professional {image_style.lower()}, masterful composition."
        CREATE YOUR DETAILED PROMPT NOW:
        """
    )
    model = GenerativeModel('gemini-2.5-flash')
    response = model.generate_content(query)
    return response.text.strip()
