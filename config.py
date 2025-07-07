import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API keys
HF_TOKEN = os.environ.get("HF_TOKEN")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

BFL_API_KEY=os.environ.get("BFL_API_KEY")

# Configure difficulty levels
DIFFICULTY_LEVELS = ["Very Simple", "Simple", "Moderate", "Detailed", "Very Detailed"]

# Default treatment plans based on autism level
DEFAULT_TREATMENT_PLANS = {
    "Level 1": "Develop social communication skills and manage specific interests while maintaining independence.",
    "Level 2": "Focus on structured learning environments with visual supports and consistent routines.",
    "Level 3": "Provide highly structured support with simplified visual information and sensory-appropriate environments."
}

# Available image styles with descriptions optimized for single-image consistency - ALL DIGITAL QUALITY
IMAGE_STYLE_INFO = {
    "Modern Digital Comic": "ULTRA-MODERN DIGITAL COMIC ART: This style is defined by its crisp, clean, and vibrant digital execution. Line Art: Impeccably clean, sharp, and precise vector-like digital ink lines. No-aliasing, with dynamic weight variation for emphasis. Absolutely zero tolerance for sketchiness, texture, or rough edges. Color Palette: Bold, vibrant, and saturated colors with smooth, cel-shaded gradients and hard-edged highlights. The colors should be electric and pop off the page. Rendering: Flawless, professional-grade digital rendering. Smooth surfaces, clean shadows, and a polished, almost 'plastic' finish. No digital noise, artifacts, or texture. Overall Feel: A sleek, modern, professional, and hyper-polished aesthetic. Think high-quality webcomics or animated series storyboards. ABSOLUTELY FORBIDDEN: anything resembling traditional media, including but not limited to: sketch marks, pencil or ink texture, paper or canvas texture, brush strokes, watercolor effects, smudging, charcoal, cross-hatching, hand-drawn look, unfinished appearance, blur, haze, soft focus. MANDATORY: Razor-sharp focus, vector-quality lines, vibrant cel-shading, pristine digital quality.",
    "Manga Style": "DIGITAL MANGA STYLE: Line Quality: Precise, clean digital line work with traditional manga varying line weights - bold for emphasis, delicate for details. Character Design: Classic manga proportions with expressive large eyes, detailed hair textures, and subtle emotional expressions. Tone Work: Strategic use of digital screentones, hatching, and gradient effects typical of professional digital manga production. Panel Layout: Traditional manga panel flow with dynamic angles and creative panel shapes that enhance narrative pacing. ABSOLUTELY FORBIDDEN: blur, sketch, rough lines, hand-drawn appearance, traditional media texture, pencil marks, draft quality. MANDATORY: Clean digital finish, professional digital quality.",
    "Cartoon Style": "DIGITAL ANIMATED CARTOON STYLE: Exaggerated features, bright colors, and simplified designs with clean digital finish. Ideal for maintaining character consistency across multiple panels in one image. ABSOLUTELY FORBIDDEN: blur, sketch, rough appearance, hand-drawn look, traditional media texture, draft quality, pencil marks. MANDATORY: Smooth digital cartoon finish, professional digital quality, clean digital edges.",
    "Photorealistic": "DIGITAL PHOTOREALISTIC EXCELLENCE: Rendering Quality: Cinema-quality digital realistic rendering with accurate lighting physics, material properties, and atmospheric effects. Detail Level: Ultra-high digital detail in skin textures, fabric weaves, environmental surfaces, and natural lighting variations. Color Accuracy: Natural color grading with realistic skin tones, environmental colors, and accurate material reflectance. Focus Quality: EVERYTHING must be in perfect sharp focus from foreground to background - NO depth of field blur, NO soft focus, NO out-of-focus areas. ABSOLUTELY FORBIDDEN: any blur, sketch, rough appearance, draft quality, hazy details, motion blur, background blur, traditional media texture, hand-drawn elements. MANDATORY: Crystal clear digital sharpness throughout entire image, professional digital rendering quality.",
    "Cinematic Realism": "DIGITAL CINEMATIC VISUAL MASTERY: Film Quality: Movie-grade digital visual production with professional cinematography techniques and dramatic lighting setups. Color Grading: Digital cinematic color treatment with film-style color palettes, mood enhancement, and atmospheric color shifts. Camera Work: Dynamic camera angles and movements translated to comic panels - close-ups, wide shots, dramatic perspectives. Lighting Design: Professional digital film lighting with three-point lighting, atmospheric effects, and mood-appropriate illumination. ABSOLUTELY FORBIDDEN: blur, sketch, rough appearance, hand-drawn elements, traditional media texture, draft quality. MANDATORY: Professional digital cinematic quality, clean digital finish.",
    "Digital Painting": "PROFESSIONAL DIGITAL PAINTING: Digital art with realistic elements and smooth, refined artistic interpretation. Consistent artistic style throughout multi-panel compositions with clean, polished digital finish. ABSOLUTELY FORBIDDEN: visible brushwork, sketch marks, rough texture, draft appearance, blur, soft edges, unfinished look, pencil texture, canvas texture, traditional media simulation, hand-painted appearance. MANDATORY: Smooth, professional digital finish with crystal clear details and sharp digital edges throughout, pristine digital quality.",
    "Illustration": "HIGH-QUALITY DIGITAL ILLUSTRATION: Professional Digital Art: Gallery-quality digital illustration with masterful composition, color theory, and technical execution. Visual Clarity: Crystal-clear details with optimal contrast and saturation for maximum visual impact and readability. Artistic Consistency: Unified digital artistic approach across all panels maintaining consistent quality and style treatment. ABSOLUTELY FORBIDDEN: blur, sketch, rough appearance, hand-drawn elements, traditional media texture, draft quality, pencil marks. MANDATORY: Professional digital illustration quality, clean digital finish, sharp digital edges."
}

def get_enhanced_style_specifications(style):
    """Get enhanced style specifications with technical details for use throughout the system - ALL DIGITAL QUALITY."""
    enhanced_styles = {
        "Modern Digital Comic": [
            "ULTRA-MODERN DIGITAL COMIC ART:",
            "Line Art: Impeccably clean, sharp, and precise vector-like digital ink lines. No-aliasing, with dynamic weight variation for emphasis. Absolutely zero tolerance for sketchiness, texture, or rough edges.",
            "Color Palette: Bold, vibrant, and saturated colors with smooth, cel-shaded gradients and hard-edged highlights. The colors should be electric and pop off the page.",
            "Rendering: Flawless, professional-grade digital rendering. Smooth surfaces, clean shadows, and a polished, almost 'plastic' finish. No digital noise, artifacts, or texture.",
            "Overall Feel: A sleek, modern, professional, and hyper-polished aesthetic. Think high-quality webcomics or animated series storyboards.",
            "Quality: ABSOLUTELY FORBIDDEN: anything resembling traditional media, including but not limited to: sketch marks, pencil or ink texture, paper or canvas texture, brush strokes, watercolor effects, smudging, charcoal, cross-hatching, hand-drawn look, unfinished appearance, blur, haze, soft focus. MANDATORY: Razor-sharp focus, vector-quality lines, vibrant cel-shading, pristine digital quality."
        ],
        "Manga Style": [
            "DIGITAL MANGA STYLE:",
            "Line Quality: Precise, clean digital line work with traditional manga varying line weights - bold for emphasis, delicate for details",
            "Character Design: Classic manga proportions with expressive large eyes, detailed hair textures, and subtle emotional expressions",
            "Tone Work: Strategic use of digital screentones, hatching, and gradient effects typical of professional digital manga production",
            "Panel Layout: Traditional manga panel flow with dynamic angles and creative panel shapes that enhance narrative pacing",
            "Quality: ABSOLUTELY FORBIDDEN: blur, sketch, rough lines, draft appearance, hand-drawn look, traditional media texture, unfinished look. MANDATORY: Clean precise digital linework, professional digital quality"
        ],
        "Cartoon Style": [
            "DIGITAL CARTOON STYLE EXCELLENCE:",
            "Character Design: Animated cartoon style with exaggerated features, bright colors, and simplified designs with clean digital finish",
            "Visual Consistency: Ideal for maintaining character consistency across multiple panels in one image with digital precision",
            "Color Palette: Vibrant, saturated digital colors with clear contrast and playful visual appeal",
            "Style Approach: Clean, friendly digital aesthetic perfect for educational content",
            "Quality: ABSOLUTELY FORBIDDEN: blur, sketch, rough appearance, draft quality, hand-drawn look, traditional media texture. MANDATORY: Clean digital cartoon finish with sharp digital edges, professional digital quality"
        ],
        "Photorealistic": [
            "DIGITAL PHOTOREALISTIC EXCELLENCE:",
            "Rendering Quality: Cinema-quality digital realistic rendering with accurate lighting physics, material properties, and atmospheric effects",
            "Detail Level: Ultra-high digital detail in skin textures, fabric weaves, environmental surfaces, and natural lighting variations",
            "Color Accuracy: Natural color grading with realistic skin tones, environmental colors, and accurate material reflectance",
            "Focus Quality: EVERYTHING in perfect sharp focus - NO depth of field, NO blur zones, complete edge-to-edge digital sharpness",
            "Quality: ABSOLUTELY FORBIDDEN: any blur, sketch, rough appearance, soft focus, hazy areas, hand-drawn elements, traditional media texture. MANDATORY: Crystal clear digital precision throughout, professional digital rendering quality"
        ],
        "Cinematic Realism": [
            "DIGITAL CINEMATIC VISUAL MASTERY:",
            "Film Quality: Movie-grade digital visual production with professional cinematography techniques and dramatic lighting setups",
            "Color Grading: Digital cinematic color treatment with film-style color palettes, mood enhancement, and atmospheric color shifts",
            "Camera Work: Dynamic camera angles and movements translated to comic panels - close-ups, wide shots, dramatic perspectives",
            "Lighting Design: Professional digital film lighting with three-point lighting, atmospheric effects, and mood-appropriate illumination",
            "Quality: ABSOLUTELY FORBIDDEN: blur, sketch, rough appearance, hand-drawn elements, traditional media texture, draft quality. MANDATORY: Professional digital cinematic quality, clean digital finish"
        ],
        "Digital Painting": [
            "PROFESSIONAL DIGITAL PAINTING MASTERY:",
            "Artistic Technique: Refined digital art with realistic elements and smooth artistic interpretation - NO visible brushwork, texture, or traditional media simulation",
            "Visual Consistency: Consistent digital artistic style throughout multi-panel compositions with polished digital finish",
            "Surface Quality: Smooth digital finish with clean edges and professional polish - NO brush texture, canvas texture, rough marks, or traditional media effects",
            "Color Treatment: Sophisticated digital color blending with seamless gradients and artistic interpretation of lighting and atmosphere",
            "Quality: ABSOLUTELY FORBIDDEN: brushwork, sketch marks, rough texture, blur, soft edges, unfinished appearance, traditional media simulation, hand-painted look. MANDATORY: Smooth professional digital finish, pristine digital quality"
        ],
        "Illustration": [
            "HIGH-QUALITY DIGITAL ILLUSTRATION:",
            "Professional Digital Art: Gallery-quality digital illustration with masterful composition, color theory, and technical execution",
            "Visual Clarity: Crystal-clear digital details with optimal contrast and saturation for maximum visual impact and readability",
            "Artistic Consistency: Unified digital artistic approach across all panels maintaining consistent quality and style treatment",
            "Design Approach: Clean digital illustration style with consistent character design and clear visual storytelling elements",
            "Quality: ABSOLUTELY FORBIDDEN: blur, sketch, rough appearance, hand-drawn elements, traditional media texture, draft quality. MANDATORY: Professional digital illustration quality, clean digital finish, sharp digital edges"
        ]
    }

    return enhanced_styles.get(style, [
        "HIGH-QUALITY DIGITAL VISUAL STYLE:",
        "Professional Digital Art: Gallery-quality digital rendering with masterful composition, color theory, and technical execution",
        "Visual Clarity: Crystal-clear digital details with optimal contrast and saturation for maximum visual impact and readability",
        "Artistic Consistency: Unified digital artistic approach maintaining consistent quality and style treatment",
        "Quality: ABSOLUTELY FORBIDDEN: blur, sketch, rough appearance, hand-drawn elements, traditional media texture, draft quality. MANDATORY: Professional digital quality, clean digital finish"
    ])

def get_style_prompt_enhancement(style):
    """Get style-specific prompt enhancements for image generation."""
    specifications = get_enhanced_style_specifications(style)
    return " ".join(specifications)

# List of available styles (for backwards compatibility)
IMAGE_STYLES = list(IMAGE_STYLE_INFO.keys())

# Default session settings
DEFAULT_SESSION = {
    "prompt": None,
    "image": None,
    "image_description": None,
    "chat": [],
    "treatment_plan": "",
    "topic_focus": "",
    "key_details": [],
    "identified_details": [],
    "used_hints": [],
    "difficulty": "Very Simple",
    "age": "3",
    "autism_level": "Level 1",
    "attempt_limit": 3,
    "attempt_count": 0,
    "details_threshold": 0.7,
    "image_style": "Modern Digital Comic"
}
