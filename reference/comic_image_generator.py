import io
import base64
import os
from PIL import Image, ImageDraw, ImageFont
import config
import warnings
import textwrap
from pathlib import Path
import time
from models.image_generation import generate_image_fn
from google.generativeai import GenerativeModel
import json
import re
import tempfile
import shutil
from google.generativeai.types import GenerationConfig
from utils.comic_panel_splitter import split_comic_panels
import cv2
import numpy as np
warnings.filterwarnings("ignore", message="IMAGE_SAFETY is not a valid FinishReason")

class ComicImageGenerator:
    """
    Generates a comic-style image.
    """

    def __init__(self):
        # No initialization needed
        pass

    def generate_comic(self, story_data, output_path=None, style=None):
        """
        Generate a comic-style image based on the provided story data.

        Args:
            story_data: Dictionary containing the story information
            output_path: Optional path to save the resulting image
            style: Optional comic style to use

        Returns:
            PIL.Image.Image: The comic image
            str: Base64 encoded data URL of the image
        """
        title = story_data.get("title", "My Story")
        description = story_data.get("description", "")
        characters = story_data.get("characters", [])
        settings = story_data.get("settings", [])
        num_scenes = story_data.get("num_scenes", 12)  # Get number of scenes, default to 12

        # Create the prompt for generating the comic
        prompt = self._create_comic_prompt(title, description, characters, settings, style, num_scenes)

        try:
            # Generate the comic image
            print(f"Generating comic with {num_scenes} scenes...")

            # Call the generate_image_fn function
            comic_image = generate_image_fn(
                selected_prompt=prompt,
                output_path=output_path
            )

            # If image generation failed, create a placeholder
            if comic_image is None:
                comic_image = self._create_placeholder_comic(title, description)

                # Save the placeholder if output_path is provided
                if output_path:
                    directory = os.path.dirname(output_path)
                    if directory and not os.path.exists(directory):
                        os.makedirs(directory)
                    comic_image.save(output_path)

            # Create data URL for display
            buffered = io.BytesIO()
            comic_image.save(buffered, format="PNG")
            img_bytes = buffered.getvalue()
            img_b64 = base64.b64encode(img_bytes).decode("utf-8")
            data_url = f"data:image/png;base64,{img_b64}"

            return comic_image, data_url

        except Exception as e:
            print(f"Error generating comic: {str(e)}")
            # Create and return a placeholder page
            placeholder = self._create_placeholder_comic(title, description)

            # Save the placeholder if output_path is provided
            if output_path:
                directory = os.path.dirname(output_path)
                if directory and not os.path.exists(directory):
                    os.makedirs(directory)
                placeholder.save(output_path)

            # Create data URL for the placeholder
            buffered = io.BytesIO()
            placeholder.save(buffered, format="PNG")
            img_bytes = buffered.getvalue()
            img_b64 = base64.b64encode(img_bytes).decode("utf-8")
            data_url = f"data:image/png;base64,{img_b64}"

            return placeholder, data_url

    def _create_comic_prompt(self, title, description, characters=None, settings=None, style=None, num_scenes=1):
        """
        Create a sophisticated, optimized prompt for comic generation with advanced visual consistency techniques.
        Specialized for high-quality multi-panel storytelling with perfect character continuity.

        Args:
            title: Title of the story
            description: Visual description of the story
            characters: List of character data
            settings: List of setting data
            style: Optional visual style
            num_scenes: Number of scenes to include (1-16)

        Returns:
            str: Advanced prompt optimized for professional comic generation with smart detail preservation
        """

        # Priority-based prompt building to ensure critical details come first
        priority_sections = []

        # PRIORITY 1: Critical layout and consistency requirements (always first)
        layout_specs = self._get_optimal_layout_description(num_scenes)
        priority_sections.append(f"CRITICAL LAYOUT: {layout_specs}")

        # Add special compact instructions for layouts with 12+ panels
        if num_scenes >= 12:
            compact_instructions = [
                f"🎯 COMPACT SCENE MASTERY FOR {num_scenes} PANELS:",
                f"SMALL EFFICIENT SCENES: Each panel must be small and visually concise, occupying roughly 1/{num_scenes} of the total image area. Focus on ONE key action or story beat per panel with maximum visual economy.",
                "CLEAR FOCAL POINTS: Every panel needs ONE main subject in sharp focus with minimal background distractions to ensure readability at a small size.",
                "ESSENTIAL ELEMENTS ONLY: Include only the most crucial visual elements needed to advance the story - remove ALL unnecessary details.",
                "READABLE AT SMALL SIZE: All expressions and actions must be clearly visible even when the panel is small. Use bold, simple compositions.",
                "No Speech bubbles or text , just the characters and their enviroment and actions"
            ]
            priority_sections.extend(compact_instructions)

        # PRIORITY 2: Character consistency anchors (most important for visual continuity)
        if characters:
            character_details = self._create_detailed_character_specifications(characters, num_scenes)
            priority_sections.extend(character_details)

        # PRIORITY 3: Core story content with enhanced detail preservation
        enhanced_story = self._create_detailed_story_description(description, title)
        priority_sections.append(enhanced_story)

        # PRIORITY 4: Environmental consistency (important for setting continuity)
        if settings:
            environment_details = self._create_detailed_environment_specifications(settings, num_scenes)
            priority_sections.extend(environment_details)

        # PRIORITY 5: Advanced technical specifications
        technical_specs = self._create_comprehensive_technical_specifications(style, num_scenes)
        priority_sections.extend(technical_specs)

        # PRIORITY 6: Quality and flow instructions
        quality_flow = self._create_advanced_quality_and_flow_instructions(num_scenes)
        priority_sections.extend(quality_flow)

        # Smart assembly with length management
        final_prompt = self._assemble_prompt_with_smart_truncation(priority_sections)

        return final_prompt

    def _create_detailed_character_specifications(self, characters, num_scenes):
        """Create extremely detailed character specifications prioritizing visual consistency."""
        char_specs = []

        char_specs.append("🎭 CRITICAL CHARACTER CONSISTENCY PROTOCOL:")
        char_specs.append("ABSOLUTE REQUIREMENT: Characters MUST look identical in every single panel - same face, hair, clothes, proportions, expressions style")

        for i, character in enumerate(characters[:3]):  # Limit to 3 main characters for detail preservation
            if isinstance(character, dict) and "visual_description" in character:
                char_name = character.get("name", f"Character_{i+1}")
                char_desc = character["visual_description"]

                # Enhanced character specification with critical details first
                char_spec = f"CHARACTER {i+1} - {char_name}: {char_desc}"

                # Add specific visual anchors for consistency
                if "traits" in character and character["traits"]:
                    traits = character["traits"][:5]  # Limit to 5 most important traits
                    char_spec += f" | DISTINCTIVE FEATURES: {', '.join(traits)}"

                # Add consistency reminders
                char_spec += f" | CONSISTENCY RULE: This exact appearance must be maintained across all {num_scenes} panels with zero variation in facial features, hair, clothing, or body proportions"

                char_specs.append(char_spec)

        # Add cross-character consistency instruction
        if len([c for c in characters[:3] if isinstance(c, dict) and 'visual_description' in c]) > 1:
            char_specs.append(f"MULTI-CHARACTER RULE: All characters must maintain their exact individual appearances simultaneously across all {num_scenes} panels - no character design drift allowed")

        return char_specs

    def _create_detailed_story_description(self, description, title):
        """Create enhanced story description with preserved important details."""
        # Extract and prioritize key narrative elements
        story_elements = []

        # Core story with detail enhancement
        enhanced_desc = f"STORY CONTENT: {title} - {description}"

        # Add visual storytelling emphasis
        enhanced_desc += " | VISUAL NARRATIVE FOCUS: Every detail must be clearly visible and contribute to story comprehension through imagery alone"

        # Add emotional and atmospheric details
        enhanced_desc += " | ATMOSPHERIC DETAILS: Include specific lighting, weather, time of day, and environmental mood indicators that enhance the narrative"

        # Add action and expression clarity
        enhanced_desc += " | CHARACTER EXPRESSION CLARITY: All emotions, reactions, and character intentions must be immediately readable through facial expressions, body language, and positioning"

        return enhanced_desc

    def _create_detailed_environment_specifications(self, settings, num_scenes):
        """Create detailed environment specifications with consistency focus."""
        env_specs = []

        env_specs.append(" ENVIRONMENTAL CONSISTENCY PROTOCOL:")

        for i, setting in enumerate(settings[:3]):  # Limit to 3 main settings
            if isinstance(setting, dict) and "description" in setting:
                setting_name = setting.get("name", f"Location_{i+1}")
                setting_desc = setting["description"]

                env_spec = f"LOCATION {i+1} - {setting_name}: {setting_desc}"

                # Add visual elements for consistency
                if "visual_elements" in setting and setting["visual_elements"]:
                    elements = setting["visual_elements"][:5]  # Top 5 visual elements
                    env_spec += f" | KEY VISUAL MARKERS: {', '.join(elements)}"

                # Add mood and atmosphere
                if "mood" in setting:
                    env_spec += f" | ATMOSPHERE: {setting['mood']}"

                # Add consistency requirement
                env_spec += f" | LOCATION CONSISTENCY: When this location appears across multiple panels, all architectural details, lighting, and distinctive features must remain identical"

                env_specs.append(env_spec)

        return env_specs

    def _create_comprehensive_technical_specifications(self, style, num_scenes):
        """Create comprehensive technical specifications with detail preservation and strict quality controls."""
        tech_specs = []

        # CRITICAL: Add anti-blur and anti-deformation constraints first
        critical_constraints = [
            "🚫 CRITICAL NEGATIVE CONSTRAINTS (ABSOLUTE REQUIREMENTS - MUST NEVER VIOLATE):",
            "ZERO BLUR AND SKETCH ENFORCEMENT: Every single panel must have CRYSTAL-CLEAR, razor-sharp focus throughout with completely finished professional DIGITAL artwork. ABSOLUTELY FORBIDDEN: motion blur, depth-of-field blur, out-of-focus areas, soft focus, hazy details, blurry backgrounds, sketch marks, rough lines, pencil texture, draft appearance, unfinished look, hand-drawn appearance, traditional media texture, or ANY visual softness or roughness.",
            "PROFESSIONAL DIGITAL FINISHED QUALITY: All artwork must be completely polished and finished with pristine digital quality - NO sketchy appearance, NO rough drafts, NO pencil marks, NO canvas texture, NO brush strokes, NO unfinished edges, NO traditional media simulation, NO hand-painted look.",
            "MANDATORY FULL COLOR: ALL panels must be in FULL VIBRANT COLOR with rich, saturated colors. ABSOLUTELY FORBIDDEN: black and white, grayscale, monochrome, sepia, or any desaturated artwork.",
            "BOLD BORDER REQUIREMENT: Every panel must have thick, bold BLACK borders (3-5px width) that clearly define each panel boundary.",
            "EQUAL PANEL SIZING: All panels must be EXACTLY the same size and dimensions - no variation in panel sizes, no irregular shapes, no overlapping panels.",
            "UNIFORM PANEL SHAPE: All panels must be the SAME SHAPE - either ALL SQUARES ABSOLUTELY FORBIDDEN: mixing square and rectangular panels in the same comic.",
            "PERFECT ANATOMICAL INTEGRITY: ALL characters and figures must have anatomically FLAWLESS proportions and structure. ZERO TOLERANCE for malformed faces, distorted bodies, warped limbs, or any anatomical impossibilities.",
            "COMPLETE BODY VERIFICATION: Every character must have EXACTLY the correct number of fingers (5 per hand), hands (2), arms (2), legs (2), eyes (2), and all facial features properly formed and positioned.",
            "STRUCTURAL PERFECTION: All objects, buildings, vehicles, and environmental elements must be geometrically perfect with no warping, distortion, or impossible perspectives.",
            ""
        ]
        tech_specs.extend(critical_constraints)

        # Enhanced style specifications
        style_details = self._get_enhanced_style_specifications(style)
        tech_specs.extend(style_details)

        # Panel composition specifications
        composition_specs = [
            "🎨 PANEL COMPOSITION MASTERY:",
            f"Grid Layout: Precisely arranged {self._calculate_optimal_grid_layout(num_scenes)} grid with EQUAL-SIZED PANELS, BOLD BLACK BORDERS (3-5px thick), and professional comic book spacing",
            "EQUAL PANEL SIZING: All panels must be EXACTLY the same size and dimensions - no variation in panel sizes allowed",
            "UNIFORM PANEL SHAPE: All panels must be the SAME SHAPE - either ALL SQUARES or ALL RECTANGLES, no mixing of shapes",
            "BOLD BORDER REQUIREMENT: Each panel must have thick, bold black borders (3-5px width) that clearly separate each scene",
            "FULL COLOR ARTWORK: All panels must be in FULL VIBRANT COLOR - absolutely no black and white, grayscale, or monochrome artwork",
            "Visual Hierarchy: Each panel must have a clear focal point with supporting details that enhance rather than distract from the main action",
            "Depth and Perspective: Use foreground, midground, and background elements to create visual depth and spatial relationships",
            "Color Harmony: Maintain consistent color palette across all panels while using color psychology to enhance mood and narrative flow"
        ]

        # Add specific instructions for compact 16-panel layouts
        if num_scenes >= 16:
            composition_specs.extend([
                "COMPACT PANEL OPTIMIZATION: Design each panel for MAXIMUM visual impact in minimal space",
                "SIMPLE BACKGROUNDS: Use minimal, clean backgrounds that don't compete with main subjects",
                "BOLD CHARACTER POSES: Use clear, distinctive poses and gestures that read well at small sizes",
                "HIGH CONTRAST: Ensure strong contrast between characters and backgrounds for clarity"
            ])

        tech_specs.extend(composition_specs)

        # Portrait format constraints for 1024x1536 generation
        portrait_specs = [
            "📱 PORTRAIT FORMAT OPTIMIZATION (1024x1536):",
            "PANEL SIZE CONSTRAINTS: Each panel must be large enough to be clearly readable and visually appealing in the portrait format - minimum 120x120 pixels",
            "OPTIMAL PANEL PROPORTIONS: Panel aspect ratios should be between 0.5:1 and 2:1 for optimal visual balance in portrait format",
            "VERTICAL LAYOUT PREFERENCE: Prefer taller layouts (more rows, fewer columns) to maximize panel size in the 1024x1536 portrait format",
            "PADDING AND MARGINS: Ensure adequate padding around the entire comic (minimum 20px) and gutters between panels (minimum 10px) to prevent content from being cut off",
            "BORDER CLEARANCE: All panel borders and content must be fully contained within the 1024x1536 canvas with absolutely no cropping or cutoff",
            "READABLE SCALE: All visual elements must be sized appropriately for the portrait format to ensure clarity and readability",
            "VERTICAL FLOW: Use the portrait format to create strong vertical progression and visual hierarchy through the story",
            ""
        ]
        tech_specs.extend(portrait_specs)

        # Detail preservation specifications
        detail_specs = [
            " DETAIL PRESERVATION PROTOCOL:",
            "Facial Detail Consistency: All character faces must maintain identical features - eye shape, nose structure, mouth proportions, facial hair, scars, or distinctive marks",
            "Clothing and Accessory Continuity: Every piece of clothing, jewelry, weapons, or accessories must appear identical across panels",
            "Environmental Detail Tracking: Background objects, architectural elements, vegetation, and atmospheric effects must remain consistent when locations reappear",
            "Lighting Continuity: Maintain logical light sources and shadow patterns that reflect time of day and weather conditions consistently"
        ]
        tech_specs.extend(detail_specs)

        return tech_specs

    def _get_enhanced_style_specifications(self, style):
        """Get enhanced style specifications with technical details."""
        enhanced_styles = {
            "Comic Book Style": [
                "MODERN DIGITAL COMIC BOOK STYLE MASTERY:",
                "Line Art: Ultra-crisp, precision digital ink lines with perfect weight variation - thick bold outlines for character definition, medium weight for important details, fine lines for texture - ABSOLUTELY NO sketchy, rough, hand-drawn, pencil, or draft-like appearance",
                "Color Treatment: Modern digital comic coloring with vibrant saturated hues, professional cell-shading, strategic highlights, and contemporary digital comic book color theory",
                "Shading: Contemporary comic book shadow techniques using clean digital color fills, strategic gradients, and modern lighting effects for maximum visual impact",
                "Panel Borders: Razor-sharp geometric panel borders with mathematically precise gutters and professional modern comic book layout standards",
                "Digital Finish: MODERN COMPUTER-GENERATED APPEARANCE - polished, sleek, contemporary digital art finish typical of current Marvel/DC comics",
                "Quality: ABSOLUTELY FORBIDDEN: sketch marks, rough lines, pencil texture, draft appearance, blur, soft focus, hand-drawn look, traditional media texture, watercolor effects, canvas texture, brush strokes. MANDATORY: Ultra-modern digital comic finish, pristine computer-generated quality, sleek contemporary appearance"
            ],
            "Manga Style": [
                "MODERN DIGITAL MANGA STYLE:",
                "Line Quality: Ultra-precise, computer-perfect digital line work with traditional manga varying line weights - bold for emphasis, delicate for details - ABSOLUTELY NO sketchy, rough, hand-drawn, or pencil appearance",
                "Character Design: Classic manga proportions with expressive large eyes, detailed hair textures, and subtle emotional expressions rendered in modern digital finish",
                "Tone Work: Professional digital screentones, precise digital hatching, and contemporary gradient effects typical of modern digital manga production",
                "Panel Layout: Traditional manga panel flow with dynamic angles and creative panel shapes enhanced with modern digital precision",
                "Digital Finish: SLEEK MODERN COMPUTER-GENERATED APPEARANCE - polished contemporary digital manga finish",
                "Quality: ABSOLUTELY FORBIDDEN: sketch appearance, rough drafts, blur, soft lines, hand-drawn look, traditional media texture, watercolor effects, brush strokes. MANDATORY: Ultra-modern digital manga finish, pristine computer-generated quality, sleek contemporary digital appearance"
            ],
            "Photorealistic": [
                "DIGITAL PHOTOREALISTIC EXCELLENCE:",
                "Rendering Quality: Cinema-quality digital realistic rendering with accurate lighting physics, material properties, and atmospheric effects",
                "Detail Level: Ultra-high digital detail in skin textures, fabric weaves, environmental surfaces, and natural lighting variations",
                "Color Accuracy: Natural color grading with realistic skin tones, environmental colors, and accurate material reflectance",
                "Focus Quality: EVERYTHING in perfect sharp focus - NO depth of field blur, NO soft focus, NO out-of-focus areas, complete edge-to-edge digital sharpness",
                "Quality: ABSOLUTELY FORBIDDEN: any blur, sketch, rough appearance, soft focus, hazy areas, hand-drawn elements, traditional media texture. MANDATORY: Crystal clear digital precision throughout, professional digital rendering quality"
            ],
            "Cinematic Realism": [
                "DIGITAL CINEMATIC VISUAL MASTERY:",
                "Film Quality: Movie-grade digital visual production with professional cinematography techniques and dramatic lighting setups",
                "Color Grading: Digital cinematic color treatment with film-style color palettes, mood enhancement, and atmospheric color shifts",
                "Camera Work: Dynamic camera angles and movements translated to comic panels - close-ups, wide shots, dramatic perspectives",
                "Lighting Design: Professional digital film lighting with three-point lighting, atmospheric effects, and mood-appropriate illumination",
                "Quality: ABSOLUTELY FORBIDDEN: blur, sketch, rough appearance, draft quality, hand-drawn elements, traditional media texture. MANDATORY: Professional digital cinematic quality, clean digital finish"
            ]
        }

        return enhanced_styles.get(style, [
            "MODERN HIGH-QUALITY DIGITAL COMIC ILLUSTRATION:",
            "Professional Digital Art: Gallery-quality contemporary digital comic illustration with masterful composition, modern color theory, and cutting-edge digital execution",
            "Visual Clarity: Ultra-crisp digital details with optimal contrast, vibrant saturation, and modern comic book visual impact and readability",
            "Artistic Consistency: Unified modern digital comic approach across all panels maintaining consistent contemporary quality and sleek style treatment",
            "Digital Finish: MODERN COMPUTER-GENERATED COMIC APPEARANCE - polished, sleek, contemporary digital finish typical of current professional comic publications",
            "Quality: ABSOLUTELY FORBIDDEN: sketch marks, rough appearance, blur, draft quality, hand-drawn elements, traditional media texture, pencil marks, watercolor effects, brush strokes, canvas texture. MANDATORY: Ultra-modern digital comic finish, pristine computer-generated quality, sleek contemporary comic book appearance"
        ])

    def _create_advanced_quality_and_flow_instructions(self, num_scenes):
        """Create advanced quality and flow instructions."""
        quality_instructions = [
            " ADVANCED QUALITY REQUIREMENTS:",
            "Technical Excellence: Ultra-high resolution output with crisp details, optimal contrast, and professional-grade visual quality",
            "Narrative Clarity: Every panel must advance the story visibly - clear cause and effect relationships between sequential panels",
            "Visual Flow: Smooth eye movement guidance from panel to panel using composition, character positioning, and visual elements",
            "Emotional Impact: Each panel must convey specific emotions through character expressions, body language, and environmental mood"
        ]

        if num_scenes > 1:
            flow_instructions = [
                f" {num_scenes}-PANEL FLOW MASTERY:",
                "Sequential Continuity: Logical progression from panel to panel with clear temporal and spatial relationships",
                "Action Sequences: Break complex actions into clear, understandable steps across multiple panels",
                "Character Tracking: Maintain character positions and movements logically across panel transitions",
                "Pacing Control: Balance action panels with character moments and environmental establishing shots for optimal narrative rhythm"
            ]

            # Add specific instructions for 16-panel layouts
            if num_scenes >= 16:
                flow_instructions.extend([
                    "STORY ARC FOR 16 PANELS: Create a complete story with beginning (panels 1-3), rising action (panels 4-7), climax (panels 8-10), and resolution (panels 11-16)",
                    "MICRO-MOMENTS: Each panel captures a single decisive moment - one expression change, one action beat, one story revelation",
                    "VISUAL ECONOMY: Every element in each panel must serve the story - no decorative details that don't advance narrative",
                    "READER ENGAGEMENT: Design panel flow to maintain interest across all 16 panels with strategic use of close-ups, wide shots, and dynamic angles"
                ])

            quality_instructions.extend(flow_instructions)

        return quality_instructions

    def _assemble_prompt_with_smart_truncation(self, priority_sections):
        """Assemble prompt with smart truncation that preserves critical details."""
        MAX_LENGTH = 31500  # Leave buffer for safety

        # STREAMLINED QUALITY ENFORCEMENT PREFIX
        QUALITY_ENFORCEMENT = (
            "MODERN DIGITAL COMIC: Pristine computer-generated quality, zero sketch/hand-drawn appearance, "
            "crystal clear focus, perfect anatomy, professional finish. || "
        )

        # Join sections with strategic separators
        full_prompt = QUALITY_ENFORCEMENT + " || ".join(priority_sections)

        # If within limit, return as-is
        if len(full_prompt) <= MAX_LENGTH:
            return full_prompt + " || FINAL QUALITY: Modern digital comic finish, crystal clear, zero blur, perfect anatomy."

        # Smart truncation: preserve critical sections
        preserved_prompt = QUALITY_ENFORCEMENT
        remaining_length = MAX_LENGTH - len(QUALITY_ENFORCEMENT) - 200  # Reserve space for final mandate

        for i, section in enumerate(priority_sections):
            section_with_separator = section + " || "

            # Always include first 3 sections (layout, characters, story)
            if i < 3:
                preserved_prompt += section_with_separator
                remaining_length -= len(section_with_separator)
            else:
                # For remaining sections, include if space allows
                if len(section_with_separator) <= remaining_length:
                    preserved_prompt += section_with_separator
                    remaining_length -= len(section_with_separator)
                else:
                    # Truncate this section smartly - keep first part
                    truncated = section[:remaining_length-50] + "..."
                    preserved_prompt += truncated + " || "
                    break

        # Add final mandate
        preserved_prompt += "FINAL QUALITY: Modern digital comic finish, crystal clear, zero blur, perfect anatomy."

        return preserved_prompt

    def _get_optimal_layout_description(self, num_scenes):
        """Generate optimal layout description based on scene count."""
        if num_scenes <= 1:
            return "Single panel comic illustration"

        # Calculate optimal layout
        optimal_layout = self._calculate_optimal_grid_layout(num_scenes)
        rows, cols = optimal_layout

        layout_descriptions = {
            (1, 2): "Horizontal two-panel comic strip layout",
            (2, 1): "Vertical two-panel comic strip layout",
            (3, 1): "Vertical three-panel comic strip layout",
            (2, 2): "Classic four-panel comic grid (2x2)",
            (2, 3): "Six-panel comic grid in 2 rows, 3 columns (2x3)",
            (3, 2): "Six-panel comic grid in 3 rows, 2 columns (3x2) - portrait optimized",
            (3, 3): "Nine-panel comic grid (3x3)",
            (4, 2): "Eight-panel comic grid in 4 rows, 2 columns (4x2) - portrait optimized",
            (5, 1): "Vertical five-panel comic strip layout",
            (5, 2): "Ten-panel comic grid in 5 rows, 2 columns (5x2) - portrait optimized",
            (3, 4): "Twelve-panel comic grid in 3 rows, 4 columns(3x4)",
            (4, 3): "Twelve-panel comic grid in 4 rows, 3 columns (4x3) - portrait optimized",
            (4, 4): "Sixteen-panel comic grid (4x4)",
            (5, 3): "Fifteen-panel comic grid in 5 rows, 3 columns (5x3) - portrait optimized",
            (6, 3): "Eighteen-panel comic grid in 6 rows, 3 columns (6x3) - portrait optimized",
            (7, 2): "Fourteen-panel comic grid in 7 rows, 2 columns (7x2) - portrait optimized",
            (4, 6): "Twenty-four panel COMPACT comic grid in 4 rows, 6 columns - SMALL EFFICIENT SCENES with maximum story density per panel (4x6)",
            (6, 4): "Twenty-four panel COMPACT comic grid in 6 rows, 4 columns - SMALL EFFICIENT SCENES with portrait storytelling format (6x4)",
            (3, 8): "Twenty-four panel COMPACT comic grid in 3 rows, 8 columns - SMALL EFFICIENT SCENES with cinematic widescreen format(3x8)",
            (8, 3): "Twenty-four panel comic grid in 8 rows, 3 columns - vertical scroll format (8x3)"
        }

        layout_desc = layout_descriptions.get((rows, cols), f"{rows}x{cols} comic panel grid layout")

        return f"COMIC LAYOUT: {layout_desc} with EQUAL-SIZED PANELS of UNIFORM SHAPE (all squares OR all rectangles), BOLD BLACK BORDERS (3-5px thick), consistent gutters, and professional comic book formatting. All panels must be EXACTLY the same size, dimensions, and shape."

    def _enhance_description_for_visual_consistency(self, description):
        """Enhance the core description with visual consistency keywords."""
        consistency_enhancers = [
            "maintaining perfect visual consistency throughout all panels",
            "identical character appearances across every scene",
            "unified lighting and color palette",
            "consistent artistic style and perspective"
        ]

        enhanced = f"STORY CONTENT: {description}. "
        enhanced += "VISUAL CONSISTENCY REQUIREMENTS: " + ", ".join(consistency_enhancers)

        return enhanced

    def _create_character_consistency_anchors(self, characters, num_scenes):
        """Create sophisticated character consistency instructions."""
        anchors = []

        if characters:
            anchors.append("CHARACTER CONSISTENCY ANCHORS:")

            for i, character in enumerate(characters[:2]):  # Limit to 2 main characters for 12 panels
                if isinstance(character, dict) and "visual_description" in character:
                    char_desc = character["visual_description"]

                    # Create detailed consistency anchor
                    anchor = f"Character {i+1}: {char_desc} - MUST appear IDENTICAL in every single panel with exact same: facial features, hair style, clothing, proportions, and distinctive visual elements"
                    anchors.append(anchor)

            # Add cross-panel consistency instruction
            if num_scenes > 1:
                anchors.append(f"CRITICAL: All {len([c for c in characters[:2] if isinstance(c, dict) and 'visual_description' in c])} characters must look exactly the same across all {num_scenes} panels - same faces, same outfits, same proportions, same artistic rendering")

        return anchors

    def _create_environment_consistency_anchors(self, settings, num_scenes):
        """Create environmental consistency instructions."""
        anchors = []

        if settings:
            anchors.append("ENVIRONMENTAL CONSISTENCY:")

            for setting in settings:
                if isinstance(setting, dict) and "description" in setting:
                    setting_desc = setting["description"]
                    anchors.append(f"Setting: {setting_desc} - maintain consistent architectural details, lighting, and atmospheric elements when this location appears")

            if num_scenes > 1:
                anchors.append(f"Ensure environmental continuity across all {num_scenes} panels with logical spatial relationships and consistent time-of-day lighting")

        return anchors

    def _create_advanced_style_instructions(self, style, num_scenes):
        """Create advanced style instructions with technical specifications."""
        instructions = []

        # Enhanced style mapping with technical details
        advanced_style_map = {
            "Comic Book Style": [
                "professional comic book illustration style",
                "bold clean line art with consistent stroke weight",
                "vibrant saturated colors with strategic highlights and shadows",
                "dynamic panel compositions with varied camera angles",
                "classic comic book rendering techniques"
            ],
            "Manga Style": [
                "authentic manga illustration style",
                "precise clean line work with varying line weights",
                "subtle color palette with strategic screentone effects",
                "expressive character designs with detailed facial features",
                "traditional manga panel composition and flow"
            ],
            "Cartoon Style": [
                "polished cartoon animation style",
                "smooth rounded character designs with appealing proportions",
                "bright harmonious color schemes with soft lighting",
                "clear readable expressions and body language",
                "family-friendly visual appeal with consistent character models"
            ],
            "Photorealistic": [
                "high-quality photorealistic illustration",
                "detailed realistic lighting and shadows",
                "natural color grading with realistic materials and textures",
                "cinematic composition with depth of field effects",
                "professional photography-inspired visual quality"
            ],
            "Cinematic Realism": [
                "cinematic realism with movie-quality visuals",
                "dramatic lighting with atmospheric effects",
                "rich color grading with cinematic color palette",
                "dynamic camera angles and professional composition",
                "film-quality character rendering and environmental detail"
            ],
            "Digital Painting": [
                "masterful digital painting technique",
                "smooth digital finish with refined artistic interpretation",
                "rich color harmony with sophisticated digital lighting",
                "artistic composition with professional digital principles",
                "high-end digital art gallery quality with pristine digital finish"
            ]
        }

        if style and style in advanced_style_map:
            instructions.append("ARTISTIC STYLE SPECIFICATIONS:")
            instructions.extend(advanced_style_map[style])
        else:
            # Default high-quality style
            instructions.extend([
                "ARTISTIC STYLE: High-quality illustration with professional comic book aesthetics",
                "clean precise line work with consistent artistic rendering",
                "harmonious color palette with strategic lighting effects",
                "polished visual presentation with attention to detail"
            ])

        # Add multi-panel specific style consistency
        if num_scenes > 1:
            instructions.append(f"STYLE CONSISTENCY: Maintain identical artistic style, line weight, color saturation, and rendering quality across all {num_scenes} panels")

        return instructions

    def _create_panel_flow_instructions(self, num_scenes):
        """Create instructions for optimal panel flow and transitions."""
        flow_instructions = []

        if num_scenes > 1:
            flow_instructions.extend([
                "PANEL FLOW AND TRANSITIONS:",
                "create smooth visual flow from panel to panel following standard left-to-right, top-to-bottom reading order",
                "design panel compositions that guide the eye naturally through the sequence",
                "establish clear visual relationships between consecutive panels",
                "use consistent perspective and scale to maintain spatial continuity",
                "create visual rhythm through varied but harmonious panel compositions"
            ])

            # Add specific instructions for 12 panels
            if num_scenes >= 10:
                flow_instructions.extend([
                    "COMPREHENSIVE STORYTELLING FLOW: Design a compelling visual narrative that maintains engagement across all 12 panels",
                    "balance action panels with character moments and environmental establishing shots",
                    "create visual crescendos and quiet beats for optimal pacing",
                    "ensure each panel contributes meaningfully to the overall story progression"
                ])

        return flow_instructions

    def _create_quality_specifications(self, num_scenes):
        """Create technical quality specifications with strict anti-blur and anti-deformation constraints."""
        quality_specs = [
            "CRITICAL NEGATIVE CONSTRAINTS (ABSOLUTE REQUIREMENTS - MUST NEVER VIOLATE):",
            "ZERO BLUR POLICY: The ENTIRE comic must have CRYSTAL-CLEAR, razor-sharp focus from edge to edge in every panel. ABSOLUTELY FORBIDDEN: any motion blur, depth-of-field blur, out-of-focus areas, soft focus, hazy details, blurry backgrounds, or ANY form of visual softness.",
            "MANDATORY FULL COLOR: ALL panels must be in FULL VIBRANT COLOR with rich, saturated colors. ABSOLUTELY FORBIDDEN: black and white, grayscale, monochrome, sepia, or any desaturated artwork.",
            "EQUAL PANEL SIZING: All panels must be EXACTLY the same size and dimensions - no variation in panel sizes, no irregular shapes, no overlapping panels.",
            "UNIFORM PANEL SHAPE: All panels must be the SAME SHAPE - either ALL SQUARES or ALL RECTANGLES. ABSOLUTELY FORBIDDEN: mixing square and rectangular panels in the same comic.",
            "BOLD BORDER REQUIREMENT: Every panel must have thick, bold BLACK borders (3-5px width) that clearly define each panel boundary.",
            "PERFECT ANATOMICAL ACCURACY: ALL figures, objects, and architectural elements must be anatomically and structurally FLAWLESS in every panel. ZERO TOLERANCE for malformed, distorted, warped, stretched, compressed, or illogical features.",
            "COMPLETE LIMB VERIFICATION: ALL human and animal figures must have EXACTLY the correct number of limbs, fingers, hands, arms, legs, eyes, and facial features in every panel. MANDATORY CHECK: Count all body parts - no missing, extra, or partially formed appendages allowed.",
            "STRUCTURAL INTEGRITY: All objects, buildings, furniture, and environmental elements must be geometrically perfect and structurally sound. No impossible perspectives, warped surfaces, or architectural impossibilities.",
            "VISUAL PERFECTION STANDARD: Every panel must be aesthetically flawless, avoiding any grotesque, ugly, disturbing, or unsettling content.",
            "",
            "TECHNICAL QUALITY REQUIREMENTS:",
            "ultra-high resolution with crystal clear, razor-sharp details in every panel",
            "professional comic book production quality with zero visual artifacts",
            "optimal contrast and saturation for maximum visual clarity with FULL COLOR artwork",
            "balanced composition with clear focal points in each panel",
            "masterful use of negative space and visual hierarchy",
            "EQUAL-SIZED PANELS: All panels must be perfectly uniform in size and dimensions",
            "UNIFORM PANEL SHAPE: All panels must be the same shape - either ALL SQUARES or ALL RECTANGLES, no mixing",
            "BOLD WHITE BORDERS: Each panel must have thick, bold white borders (3-5px width) for clear separation",
            "VIBRANT COLOR PALETTE: Rich, saturated colors throughout - no monochrome or desaturated artwork"
        ]

        # Add portrait format constraints for 1024x1536 generation
        quality_specs.extend([
            "",
            "PORTRAIT FORMAT OPTIMIZATION (1024x1536):",
            "PANEL SIZE CONSTRAINTS: Each panel must be large enough to be clearly readable and visually appealing in the portrait format.",
            "MINIMUM PANEL DIMENSIONS: No panel should be smaller than 120x120 pixels to ensure readability.",
            "OPTIMAL PANEL PROPORTIONS: Panel aspect ratios should be between 0.5:1 and 2:1 for optimal visual balance in portrait format.",
            "VERTICAL LAYOUT PREFERENCE: Prefer taller layouts (more rows, fewer columns) to maximize panel size in the 1024x1536 portrait format.",
            "PADDING AND MARGINS: Ensure adequate padding around the entire comic (minimum 20px) and gutters between panels (minimum 10px) to prevent content from being cut off.",
            "BORDER CLEARANCE: All panel borders and content must be fully contained within the 1024x1536 canvas with no cropping or cutoff.",
            "READABLE TEXT SIZE: Any text or speech bubbles must be large enough to be clearly readable when the comic is displayed at normal viewing sizes.",
            "VISUAL HIERARCHY: Use the portrait format to create strong vertical flow and visual progression through the story."
        ])

        if num_scenes > 1:
            quality_specs.extend([
                f"perfect grid alignment with consistent panel spacing across all {num_scenes} panels",
                "clear panel borders with professional gutters and margins",
                "unified visual presentation suitable for professional comic publication"
            ])

        return quality_specs

    def _optimize_prompt_structure(self, prompt_parts):
        """Optimize the prompt structure for maximum AI comprehension."""
        # Group related elements and use strategic separators
        structured_prompt = []

        # Add each part with appropriate spacing
        for i, part in enumerate(prompt_parts):
            if isinstance(part, list):
                # Join list items with strategic separators
                structured_prompt.append(" | ".join(part))
            else:
                structured_prompt.append(part)

        # Join with strategic separators for optimal AI parsing
        final_prompt = " || ".join(structured_prompt)

        # Add final quality emphasis
        final_prompt += " || FINAL REQUIREMENT: Create a masterpiece-quality comic that perfectly balances artistic excellence with clear storytelling"

        return final_prompt

    def _calculate_optimal_grid_layout(self, num_scenes):
        """Calculate the most visually appealing grid layout for the given number of scenes."""
        # Optimized layout preferences for 1024x1536 portrait format
        optimal_layouts = {
            1: (1, 1),
            2: (2, 1),     # Vertical strip better for portrait
            3: (3, 1),     # Vertical strip better for portrait
            4: (2, 2),     # Square layout
            5: (5, 1),     # Vertical strip better for portrait
            6: (3, 2),     # More vertical than (2, 3)
            7: (7, 1),     # Vertical strip better for portrait
            8: (4, 2),     # More vertical than (2, 4)
            9: (3, 3),     # Square layout
            10: (5, 2),    # More vertical than (2, 5)
            11: (11, 1),   # Vertical strip better for portrait
            12: (4, 3),    # More vertical than (3, 4) - better for portrait
            13: (13, 1),   # Vertical strip better for portrait
            14: (7, 2),    # More vertical than (2, 7)
            15: (5, 3),    # More vertical than (3, 5)
            16: (4, 4),    # Square layout
            17: (17, 1),   # Vertical strip better for portrait
            18: (6, 3),    # More vertical than (3, 6)
            19: (19, 1),   # Vertical strip better for portrait
            20: (5, 4),    # More vertical than (4, 5)
            21: (7, 3),    # More vertical than (3, 7)
            22: (11, 2),   # More vertical than (2, 11)
            23: (23, 1),   # Vertical strip better for portrait
            24: (6, 4),    # More vertical than (4, 6) - better for portrait
        }

        return optimal_layouts.get(num_scenes, self._calculate_optimal_layout(num_scenes, 1024, 1536))

    def _create_placeholder_comic(self, title, description):
        """
        Create a placeholder comic if image generation fails.

        Args:
            title: Title of the comic
            description: Visual description of the comic

        Returns:
            PIL.Image.Image: Placeholder comic image
        """
        # Create a blank comic
        width, height = 1024, 1536

        comic = Image.new("RGB", (width, height), (255, 255, 255))
        draw = ImageDraw.Draw(comic)

        # Add comic title
        try:
            title_font = ImageFont.truetype("Arial.ttf", 36)
            desc_font = ImageFont.truetype("Arial.ttf", 18)
        except IOError:
            title_font = desc_font = ImageFont.load_default()

        # Draw title
        draw.text((20, 20), title, fill=(0, 0, 0), font=title_font)

        # Draw panel rectangle
        draw.rectangle([50, 80, width-50, height-50], outline=(0, 0, 0), fill=(220, 220, 220))

        # Add description
        if description:
            # Truncate and wrap description
            max_chars = 300
            short_desc = description[:max_chars] + "..." if len(description) > max_chars else description
            wrapped_desc = textwrap.fill(short_desc, width=70)
            draw.text((60, 100), wrapped_desc, fill=(0, 0, 0), font=desc_font)

        return comic

    def split_comic_into_scenes(self, comic_image, num_scenes, preferred_layout=None, use_gemini_analysis=True):
        """
        Split a comic image into individual scenes using advanced analysis techniques.
        Optimized for 12-panel layouts with sophisticated grid detection and quality validation.

        Args:
            comic_image: PIL.Image.Image object of the comic
            num_scenes: Expected number of scenes (for context only, OpenCV script auto-detects)
            preferred_layout: Optional tuple (rows, cols) to override automatic detection (Not used by OpenCV)
            use_gemini_analysis: Whether to use Gemini Vision or OpenCV.
                                 True for Gemini (default), False for OpenCV.

        Returns:
            list: List of PIL.Image.Image objects, one for each detected scene
        """
        if not isinstance(comic_image, Image.Image):
            raise ValueError("comic_image must be a PIL.Image.Image object")

        if num_scenes <= 1 and not use_gemini_analysis: # If OpenCV is used, we might still want to split a single panel image if it contains multiple actual panels
            # If not using Gemini and num_scenes is 1, we could still proceed to OpenCV if we want to detect panels in a single supposed scene.
            # However, the original logic returned early, so we'll keep that for now unless specified otherwise.
            # If OpenCV is intended to run even for num_scenes=1, this condition needs adjustment.
            # For now, if num_scenes is 1, we assume it is indeed a single panel.
            if num_scenes <= 1:
                 return [comic_image]

        width, height = comic_image.size
        print(f"🎯 Splitting {width}x{height} comic into scenes (Target: {num_scenes} scenes if using grid, auto-detect if OpenCV)...")

        if use_gemini_analysis:
            print("🔍 Analyzing comic layout with enhanced Gemini Vision...")
            # Use preferred layout if provided
            if preferred_layout:
                rows, cols = preferred_layout
                print(f"🎯 Using manual override for Gemini: {rows}×{cols} layout")
            else:
                rows, cols = self.analyze_comic_layout_with_enhanced_gemini(comic_image, num_scenes)

            # Validate and optimize the layout
            rows, cols = self._validate_and_optimize_layout(rows, cols, num_scenes, width, height)

            actual_panels = rows * cols
            print(f"✅ Using Gemini-derived {rows}×{cols} grid layout - will extract {min(actual_panels, num_scenes)} panels")

            # Enhanced scene extraction with quality validation
            scenes = self._extract_scenes_with_quality_check(comic_image, rows, cols, num_scenes)

            return scenes
        else:
            print("🔩 Using OpenCV for panel splitting...")
            temp_dir = tempfile.mkdtemp()
            temp_image_path = os.path.join(temp_dir, "source_comic.png")
            panels_output_dir = os.path.join(temp_dir, "output_panels")

            try:
                # Save PIL image to a temporary file for OpenCV
                comic_image.save(temp_image_path, "PNG")

                # Call the OpenCV panel splitter
                # The split_comic_panels function saves panels into panels_output_dir
                split_comic_panels(temp_image_path, panels_output_dir)

                # Load the processed panels
                extracted_scenes = []
                if os.path.exists(panels_output_dir):
                    panel_files = sorted([f for f in os.listdir(panels_output_dir) if f.startswith("panel_") and f.endswith(".png")])
                    for panel_file in panel_files:
                        try:
                            panel_image_path = os.path.join(panels_output_dir, panel_file)
                            # Load with PIL.Image as the rest of the system expects PIL images
                            img = Image.open(panel_image_path)
                            extracted_scenes.append(img)
                        except Exception as e:
                            print(f"Error loading panel image {panel_file}: {e}")

                if not extracted_scenes:
                    print("⚠️ OpenCV panel splitter did not return any panels. Returning original image.")
                    return [comic_image]

                print(f"✅ OpenCV successfully extracted {len(extracted_scenes)} panels.")
                # The num_scenes argument is for context if using grid-based,
                # OpenCV will determine the actual number of scenes.
                # If a specific number of scenes is strictly required, further logic to select/discard panels would be needed here.
                return extracted_scenes

            except Exception as e:
                print(f"❌ Error during OpenCV panel splitting: {e}")
                # Fallback: return the original image if OpenCV fails
                return [comic_image]
            finally:
                # Clean up temporary directory
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)

    def _validate_and_optimize_layout(self, rows, cols, num_scenes, image_width, image_height):
        """Validate and optimize the layout based on image properties and panel count."""
        # Check if the layout makes sense for the image dimensions
        panel_width = image_width / cols
        panel_height = image_height / rows
        panel_aspect_ratio = panel_width / panel_height

        # Validate minimum panel size (panels should be at least 50x50 pixels)
        if panel_width < 50 or panel_height < 50:
            print(f"⚠️ Panels too small ({panel_width:.0f}x{panel_height:.0f}). Recalculating layout...")
            return self._calculate_optimal_grid_layout(num_scenes)

        # Validate aspect ratio (panels shouldn't be extremely thin or wide)
        if panel_aspect_ratio < 0.2 or panel_aspect_ratio > 5.0:
            print(f"⚠️ Panel aspect ratio {panel_aspect_ratio:.2f} is extreme. Optimizing layout...")
            return self._calculate_optimal_grid_layout(num_scenes)

        # For 12 panels, prefer layouts that work well visually
        if num_scenes == 12:
            optimal_12_layouts = [(3, 4), (4, 3), (2, 6), (6, 2)]
            current_layout = (rows, cols)

            if current_layout not in optimal_12_layouts:
                # Calculate which optimal layout is closest to current
                image_aspect = image_width / image_height
                best_layout = (3, 4)  # Default
                best_score = float('inf')

                for opt_rows, opt_cols in optimal_12_layouts:
                    layout_aspect = opt_cols / opt_rows
                    score = abs(layout_aspect - image_aspect)
                    if score < best_score:
                        best_score = score
                        best_layout = (opt_rows, opt_cols)

                print(f"📋 Optimizing 12-panel layout from {rows}×{cols} to {best_layout[0]}×{best_layout[1]}")
                return best_layout

        # For 24 panels, prefer layouts that work well for compact scenes
        if num_scenes == 16:
            optimal_24_layouts = [(4, 6), (6, 4), (3, 8), (8, 3)]
            current_layout = (rows, cols)

            if current_layout not in optimal_24_layouts:
                # Calculate which optimal layout is closest to current
                image_aspect = image_width / image_height
                best_layout = (4, 6)  # Default - good balance for readability
                best_score = float('inf')

                for opt_rows, opt_cols in optimal_24_layouts:
                    layout_aspect = opt_cols / opt_rows
                    score = abs(layout_aspect - image_aspect)
                    if score < best_score:
                        best_score = score
                        best_layout = (opt_rows, opt_cols)

                print(f"📋 Optimizing 16-panel layout from {rows}×{cols} to {best_layout[0]}×{best_layout[1]} for compact scenes")
                return best_layout

        return (rows, cols)

    def _extract_scenes_with_quality_check(self, comic_image, rows, cols, num_scenes):
        """Extract scenes with quality validation and enhancement."""
        width, height = comic_image.size

        # Calculate scene dimensions with proper spacing
        scene_width = width // cols
        scene_height = height // rows

        # Add small margin for better edge detection
        margin = 2  # pixels

        scenes = []
        extracted_count = 0

        for row in range(rows):
            for col in range(cols):
                if extracted_count >= num_scenes:
                    break

                # Calculate coordinates with margin
                x1 = max(0, col * scene_width - margin)
                y1 = max(0, row * scene_height - margin)
                x2 = min(width, (col + 1) * scene_width + margin)
                y2 = min(height, (row + 1) * scene_height + margin)

                # Extract the scene
                scene = comic_image.crop((x1, y1, x2, y2))

                # Quality check: ensure scene isn't mostly empty/blank
                if self._validate_scene_quality(scene):
                    scenes.append(scene)
                    extracted_count += 1
                else:
                    print(f"⚠️ Scene {extracted_count + 1} failed quality check, keeping anyway")
                    scenes.append(scene)  # Keep it anyway for completeness
                    extracted_count += 1

            if extracted_count >= num_scenes:
                break

        print(f"✅ Successfully extracted {len(scenes)} scenes")
        return scenes

    def _validate_scene_quality(self, scene):
        """Validate that a scene contains meaningful content."""
        try:
            import numpy as np

            # Convert to numpy array for analysis
            scene_array = np.array(scene)

            # Check if scene is too uniform (likely blank)
            if len(scene_array.shape) == 3:  # Color image
                variance = np.var(scene_array)
                # If variance is very low, the scene might be mostly blank
                if variance < 10:  # Very low variance threshold
                    return False

            # Check dimensions
            if scene.width < 20 or scene.height < 20:
                return False

            return True

        except Exception as e:
            print(f"Scene quality check failed: {e}")
            return True  # If check fails, assume scene is valid

    def analyze_comic_layout_with_enhanced_gemini(self, comic_image, num_scenes):
        """
        Enhanced Gemini Vision analysis with better prompting and fallback logic.
        Specialized for detecting 12-panel layouts and complex grid structures.

        Args:
            comic_image: PIL.Image.Image object of the comic
            num_scenes: Expected number of scenes (used for context and validation)

        Returns:
            tuple: (rows, cols) representing the detected grid layout
        """
        try:
            # Initialize Gemini Vision model
            model = GenerativeModel('gemini-2.5-flash')

            # Convert PIL image to base64 for Gemini
            buffered = io.BytesIO()
            comic_image.save(buffered, format="PNG")
            img_bytes = buffered.getvalue()

            # Enhanced analysis prompt optimized for grid detection
            analysis_prompt = f"""
            You are a professional comic book layout analyst. Examine this comic image carefully to determine its precise panel grid structure.

            ANALYSIS TASK:
            - Count the exact number of ROWS (horizontal divisions)
            - Count the exact number of COLUMNS (vertical divisions)
            - Expected panels: {num_scenes} (use as context, but trust what you see)

            DETECTION GUIDELINES:
            1. Look for panel borders, gutters, or visual separations
            2. Identify consistent grid patterns
            3. Count horizontal lines that divide rows
            4. Count vertical lines that divide columns
            5. For 12 panels, common layouts are: 3×4, 4×3, 2×6, or 6×2
            6. Trust visual evidence over expected numbers

            VISUAL INDICATORS TO LOOK FOR:
            - Black border lines between panels
            - White gutters or spacing between sections
            - Consistent rectangular divisions
            - Grid-like organization of content
            - Clear separation of distinct visual areas

            IMPORTANT: Be precise about what you actually observe. If you see a clear grid pattern, report it exactly.

            Respond with ONLY this JSON format:
            {{
                "detected_rows": [number of rows you count],
                "detected_cols": [number of columns you count],
                "total_panels_detected": [rows × cols],
                "confidence": "high/medium/low",
                "layout_description": "detailed description of the grid structure you observe",
                "visual_evidence": "description of the visual cues that led to this conclusion"
            }}

            Be extremely precise in your counting.
            """

            # Send to Gemini Vision with retry logic
            max_retries = 2
            for attempt in range(max_retries):
                try:
                    response = model.generate_content([analysis_prompt, comic_image])
                    response_text = response.text.strip()

                    print(f"Gemini Vision analysis (attempt {attempt + 1}): {response_text[:200]}...")

                    # Parse the JSON response
                    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                    if json_match:
                        json_str = json_match.group()
                        analysis_result = json.loads(json_str)

                        rows = analysis_result.get("detected_rows", 0)
                        cols = analysis_result.get("detected_cols", 0)
                        total_detected = analysis_result.get("total_panels_detected", 0)
                        confidence = analysis_result.get("confidence", "unknown")
                        description = analysis_result.get("layout_description", "")
                        evidence = analysis_result.get("visual_evidence", "")

                        # Validate the response
                        if rows > 0 and cols > 0:
                            # Check if the math is consistent
                            if total_detected == rows * cols:
                                print(f"✅ Gemini detected {rows}×{cols} layout ({total_detected} panels) with {confidence} confidence")
                                print(f"Evidence: {evidence}")

                                # Additional validation for 12-panel scenarios
                                if num_scenes == 12:
                                    if total_detected in [10, 11, 12, 13, 14, 15, 16, 17, 18]:
                                        print(f"📋 Layout reasonable for 12-panel comic")
                                        return (rows, cols)
                                    else:
                                        print(f"⚠️ Detected {total_detected} panels for 12-panel comic. Using optimized layout.")
                                        return self._calculate_optimal_grid_layout(num_scenes)
                                else:
                                    return (rows, cols)
                            else:
                                print(f"❌ Math inconsistency: {rows}×{cols} ≠ {total_detected}")
                        else:
                            print(f"❌ Invalid dimensions: {rows}×{cols}")

                except json.JSONDecodeError as e:
                    print(f"❌ JSON parsing error on attempt {attempt + 1}: {e}")
                    if attempt == max_retries - 1:
                        break

                except Exception as e:
                    print(f"❌ Analysis error on attempt {attempt + 1}: {e}")
                    if attempt == max_retries - 1:
                        break

        except Exception as e:
            print(f"❌ Gemini Vision analysis completely failed: {e}")

        # Fallback to optimized calculation
        print("⚠️ Using optimized grid calculation as fallback")
        return self._calculate_optimal_grid_layout(num_scenes)

    def _find_all_factorizations(self, n):
        """
        Find all possible factorizations of a number into rows × columns.
        Enhanced with better algorithm for large numbers like 16.

        Args:
            n: Number to factorize

        Returns:
            list: List of tuples (rows, cols) where rows * cols = n, sorted by preference
        """
        factorizations = []
        for i in range(1, int(n**0.5) + 1):
            if n % i == 0:
                rows, cols = i, n // i
                factorizations.append((rows, cols))
                # Add the reverse unless it's a perfect square
                if rows != cols:
                    factorizations.append((cols, rows))

        # Sort by preference: more square-like layouts first, then by total difference
        factorizations.sort(key=lambda x: (abs(x[0] - x[1]), max(x[0], x[1])))
        return factorizations

    def _calculate_optimal_layout(self, num_scenes, image_width, image_height):
        """
        Calculate the optimal grid layout based on image aspect ratio and scene count.
        Enhanced algorithm with better preferences for different panel counts.

        Args:
            num_scenes: Number of scenes to arrange
            image_width: Width of the comic image
            image_height: Height of the comic image

        Returns:
            tuple: (rows, cols) representing the optimal grid layout
        """
        # Calculate image aspect ratio
        image_aspect_ratio = image_width / image_height

        # Find all possible factorizations of num_scenes
        factorizations = self._find_all_factorizations(num_scenes)

        if not factorizations:
            # Fallback to square-ish layout
            import math
            sqrt_scenes = math.sqrt(num_scenes)
            rows = int(sqrt_scenes)
            cols = math.ceil(num_scenes / rows)
            return (rows, cols)

        # Score each factorization based on how well it matches the image aspect ratio
        best_layout = factorizations[0]
        best_score = float('inf')

        for rows, cols in factorizations:
            # Calculate layout aspect ratio
            layout_aspect_ratio = cols / rows

            # Score based on difference from image aspect ratio
            aspect_diff = abs(layout_aspect_ratio - image_aspect_ratio)

            # Prefer layouts that aren't too extreme (avoid very tall/wide panels)
            panel_aspect = (image_width / cols) / (image_height / rows)
            extremeness_penalty = 0
            if panel_aspect < 0.3 or panel_aspect > 3.0:
                extremeness_penalty = 2.0

            # Combine scores
            total_score = aspect_diff + extremeness_penalty

            if total_score < best_score:
                best_score = total_score
                best_layout = (rows, cols)

        return best_layout

    def get_possible_layouts(self, num_scenes):
        """
        Get all possible layout options for a given number of scenes.
        Enhanced with better layout suggestions.

        Args:
            num_scenes: Number of scenes

        Returns:
            list: List of tuples (rows, cols) representing possible layouts, sorted by preference
        """
        if num_scenes in [1, 2, 3, 4, 5, 6, 8, 9, 10, 12, 15, 16, 18, 20, 21, 24]:
            # Use optimized layout for common panel counts
            optimal = self._calculate_optimal_grid_layout(num_scenes)
            alternatives = self._find_all_factorizations(num_scenes)

            # Put optimal first, then alternatives
            layouts = [optimal]
            layouts.extend([layout for layout in alternatives if layout != optimal])
            return layouts
        else:
            return self._find_all_factorizations(num_scenes)

    def generate_comic_with_quality_metrics(self, story_data, output_path=None, style=None):
        """
        Enhanced comic generation with quality metrics and validation.
        Provides detailed feedback about the generation process.

        Args:
            story_data: Dictionary containing the story information
            output_path: Optional path to save the resulting image
            style: Optional comic style to use

        Returns:
            tuple: (comic_image, data_url, quality_metrics)
        """
        start_time = time.time()

        # Extract and validate story data
        title = story_data.get("title", "Enhanced Comic")
        description = story_data.get("description", "")
        characters = story_data.get("characters", [])
        settings = story_data.get("settings", [])
        num_scenes = story_data.get("num_scenes", 12)

        # Calculate quality metrics
        quality_metrics = {
            "character_count": len([c for c in characters if isinstance(c, dict) and "visual_description" in c]),
            "setting_count": len([s for s in settings if isinstance(s, dict) and "description" in s]),
            "description_length": len(description),
            "optimal_layout": self._calculate_optimal_grid_layout(num_scenes),
            "generation_complexity": "high" if num_scenes >= 20 else "medium" if num_scenes >= 10 else "low"
        }

        # Generate with enhanced prompt
        try:
            prompt = self._create_comic_prompt(title, description, characters, settings, style, num_scenes)

            # Log enhanced prompt details
            print(f"🎨 Generating {num_scenes}-panel comic with enhanced prompt ({len(prompt)} characters)")

            # Generate the comic image
            comic_image = generate_image_fn(
                selected_prompt=prompt,
                output_path=output_path
            )

            if comic_image is None:
                comic_image = self._create_enhanced_placeholder_comic(title, description, num_scenes)
                quality_metrics["generation_status"] = "placeholder"
            else:
                quality_metrics["generation_status"] = "success"

            # Save if path provided
            if output_path:
                directory = os.path.dirname(output_path)
                if directory and not os.path.exists(directory):
                    os.makedirs(directory)
                comic_image.save(output_path)

            # Create data URL
            buffered = io.BytesIO()
            comic_image.save(buffered, format="PNG")
            img_bytes = buffered.getvalue()
            img_b64 = base64.b64encode(img_bytes).decode("utf-8")
            data_url = f"data:image/png;base64,{img_b64}"

            # Calculate final metrics
            end_time = time.time()
            quality_metrics["generation_time"] = end_time - start_time
            quality_metrics["image_size"] = (comic_image.width, comic_image.height)
            quality_metrics["prompt_complexity"] = len(prompt.split())

            return comic_image, data_url, quality_metrics

        except Exception as e:
            print(f"Error in enhanced generation: {str(e)}")
            placeholder = self._create_enhanced_placeholder_comic(title, description, num_scenes)

            # Create placeholder data URL
            buffered = io.BytesIO()
            placeholder.save(buffered, format="PNG")
            img_bytes = buffered.getvalue()
            img_b64 = base64.b64encode(img_bytes).decode("utf-8")
            data_url = f"data:image/png;base64,{img_b64}"

            quality_metrics["generation_status"] = "error"
            quality_metrics["error_message"] = str(e)

            return placeholder, data_url, quality_metrics

    def _create_enhanced_placeholder_comic(self, title, description, num_scenes):
        """
        Create an enhanced placeholder comic that shows the intended layout.

        Args:
            title: Title of the comic
            description: Description of the comic
            num_scenes: Number of scenes the comic should have

        Returns:
            PIL.Image.Image: Enhanced placeholder comic image
        """
        # Use consistent dimensions that match actual image generation
        width, height = 1024, 1536

        # Create the base image
        comic = Image.new("RGB", (width, height), (248, 248, 248))
        draw = ImageDraw.Draw(comic)

        # Load fonts
        try:
            title_font = ImageFont.truetype("Arial.ttf", max(24, width // 40))
            panel_font = ImageFont.truetype("Arial.ttf", max(12, width // 80))
            desc_font = ImageFont.truetype("Arial.ttf", max(10, width // 100))
        except IOError:
            title_font = panel_font = desc_font = ImageFont.load_default()

        # Draw title
        title_text = f"{title} - {num_scenes} Panel Layout Preview"
        draw.text((20, 20), title_text, fill=(50, 50, 50), font=title_font)

        # Calculate layout
        layout = self._calculate_optimal_grid_layout(num_scenes)
        rows, cols = layout

        # Draw layout info
        layout_info = f"Layout: {rows}×{cols} grid ({rows * cols} panels)"
        draw.text((20, 60), layout_info, fill=(100, 100, 100), font=panel_font)

        # Calculate panel dimensions
        panel_area_y = 100
        panel_area_height = height - panel_area_y - 60
        panel_width = (width - 60) // cols
        panel_height = panel_area_height // rows

        # Draw panels
        panel_count = 0
        for row in range(rows):
            for col in range(cols):
                if panel_count >= num_scenes:
                    break

                x = 30 + col * panel_width
                y = panel_area_y + row * panel_height

                # Draw panel border
                draw.rectangle([x, y, x + panel_width - 10, y + panel_height - 10],
                             outline=(150, 150, 150), fill=(255, 255, 255))

                # Draw panel number
                panel_text = f"Panel {panel_count + 1}"
                draw.text((x + 10, y + 10), panel_text, fill=(100, 100, 100), font=panel_font)

                panel_count += 1

            if panel_count >= num_scenes:
                break

        # Draw description at bottom if there's space
        if description and len(description) > 0:
            desc_y = height - 50
            wrapped_desc = textwrap.fill(description[:200] + "..." if len(description) > 200 else description, width=80)
            draw.text((30, desc_y), wrapped_desc, fill=(80, 80, 80), font=desc_font)

        return comic
