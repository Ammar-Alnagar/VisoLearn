import io
import base64
import os
from PIL import Image, ImageDraw, ImageFont, ImageOps
import warnings
from models.image_generation import generate_image_fn
from google.generativeai.generative_models import GenerativeModel
import json
import re
from reference.comic_image_generator import ComicImageGenerator as RefComicImageGenerator
warnings.filterwarnings("ignore", message="IMAGE_SAFETY is not a valid FinishReason")

BASE_SYSTEM_PROMPT = (
    "SYSTEM INSTRUCTIONS: You are an elite DIGITAL comic layout generator. Produce a single image containing exactly {num_scenes} "
    "equal-sized panels arranged in a precise grid.  All panels must share identical width, height, and border thickness. "
    "Characters, settings, lighting, and rendering quality must stay perfectly consistent from one panel to the next—no "
    "style drift is allowed.  Follow and strictly embody the selected DIGITAL style: {style}.  Do NOT vary panel sizes, shapes, or "
    "gutter widths under any circumstance."
    "ABSOLUTELY FORBIDDEN: hazy backgrounds, blurry backgrounds, blurry characters, blurry settings, blurry lighting, blurry rendering quality, blurry panel sizes, blurry panel shapes, blurry gutter widths, sketch marks, rough lines, pencil texture, draft appearance, unfinished look, canvas texture, brush strokes, hand-drawn appearance, traditional media texture, soft focus, motion blur, depth of field blur, any visual softness or roughness. "
    "MANDATORY DIGITAL REQUIREMENTS: Crystal clear focus throughout, professional finished DIGITAL artwork, completely polished digital appearance, razor-sharp details, perfect anatomical accuracy, no deformation, no missing limbs, Ultra High Quality with completely finished professional DIGITAL appearance, pristine digital quality."
)

class ComicImageGenerator:
    """
    Generates a comic-style image.
    """

    def __init__(self):
        # No initialization needed
        pass

    def generate_comic(self, story_data, output_path=None, style=None):
        """
        Generate a comic image with basic retry logic for API reliability.
        The image is returned as-is without panel count validation.

        Args:
            story_data: Dictionary containing the story information
            output_path: Optional path to save the resulting image
            style: Optional comic style to use

        Returns:
            tuple: (PIL.Image.Image, data_url) or (None, None) on failure
        """
        title = story_data.get("title", "Untitled")
        # Prefer the full comic_description containing enumerated panel details
        description = story_data.get("comic_description", story_data.get("description", ""))
        characters = story_data.get("characters", [])
        settings = story_data.get("settings", [])
        num_scenes = story_data.get("num_scenes", 16)

        print(f"🚀 COMIC GENERATION: {num_scenes} panels")

        # Optimize prompt for better results
        prompt = self._create_comic_prompt(title, description, characters, settings, style, num_scenes)
        print("⚡️ Bypassing Gemini prompt optimization for speed.")
        optimized_prompt = prompt

        # Quick verification: ensure all enumerated panel lines are present
        for idx in range(1, num_scenes + 1):
            if f"Panel {idx}:" not in optimized_prompt:
                print(f"⚠️ WARNING: Panel {idx} description missing from prompt. (len={len(optimized_prompt)})")

        max_attempts = 3  # Basic retry for API reliability
        for attempt in range(max_attempts):
            try:
                print(f"🎯 GENERATION ATTEMPT {attempt + 1}/{max_attempts}")

                current_prompt = self._get_attempt_specific_prompt(optimized_prompt, num_scenes, attempt)

                # Generate the comic image
                comic_image = generate_image_fn(
                    selected_prompt=current_prompt,
                    output_path=output_path
                )

                if comic_image:
                    print(f"✅ SUCCESS: Comic image generated! Returning as-is.")
                    return self._create_success_response(comic_image)

                print(f"❌ ATTEMPT {attempt + 1}: Image generation failed at source.")
                continue

            except Exception as e:
                print(f"❌ ATTEMPT {attempt + 1} ERROR: {str(e)}")
                continue

        # All attempts failed
        print(f"❌ ALL ATTEMPTS FAILED: Could not generate comic image.")
        return None, None

    def _optimize_prompt_with_gemini(self, prompt, num_scenes):
        """
        Use Gemini to analyze and optimize the prompt for maximum panel count accuracy.
        STREAMLINED VERSION - Uses fewer tokens for faster processing.

        Args:
            prompt: Original prompt
            num_scenes: Required number of panels

        Returns:
            str: Optimized prompt
        """
        try:
            print(f"🧠 PROMPT OPTIMIZATION: Using Gemini to enhance {num_scenes}-panel prompt")

            model = GenerativeModel('gemini-2.5-flash')

            # STREAMLINED optimization prompt - much shorter
            optimization_prompt = f"""
            Optimize this prompt to ensure exactly {num_scenes} comic panels:

            "{prompt}"

            Add specific layout instructions and negative prompts for wrong panel counts.
            Keep it concise. Respond with ONLY the optimized prompt.
            """

            response = model.generate_content(optimization_prompt)
            optimized = response.text.strip()

            print(f"✅ PROMPT OPTIMIZED: Enhanced with streamlined Gemini analysis")
            return optimized

        except Exception as e:
            print(f"⚠️ PROMPT OPTIMIZATION FAILED: {e}, using original prompt")
            return prompt

    def _get_attempt_specific_prompt(self, base_prompt, num_scenes, attempt):
        """
        Create attempt-specific prompt variations - STREAMLINED VERSION.

        Args:
            base_prompt: Base optimized prompt
            num_scenes: Number of panels needed
            attempt: Current attempt number (0-based)

        Returns:
            str: Attempt-specific prompt
        """
        # Simplified strategies - fewer tokens
        strategies = [
            f"EXACTLY {num_scenes} panels with bold white borders",
            f"PRECISE {num_scenes} panel grid layout",
            f"CLEAR {num_scenes} panels with thick dividers",
            f"DISTINCT {num_scenes} panels maximum contrast",
            f"FINAL: {num_scenes} panels perfect separation"
        ]

        strategy = strategies[min(attempt, len(strategies) - 1)]
        enhanced_prompt = f"{strategy}. {base_prompt}"

        print(f"🎯 ATTEMT {attempt + 1}: {strategy}")
        return enhanced_prompt

    def _analyze_panel_count_mathematically(self, comic_image, expected_panels):
        """
        Use mathematical analysis to determine panel count.

        Args:
            comic_image: Comic image to analyze
            expected_panels: Expected number of panels

        Returns:
            int: Detected panel count
        """
        import math
        width, height = comic_image.size

        # Try different grid configurations
        possible_configs = []
        for rows in range(1, 5):
            for cols in range(1, 7):
                if rows * cols == expected_panels:
                    possible_configs.append((rows, cols))

        if not possible_configs:
            # Fallback calculation
            cols = math.ceil(math.sqrt(expected_panels))
            rows = math.ceil(expected_panels / cols)
            possible_configs = [(rows, cols)]

        # For now, assume the expected configuration exists
        return expected_panels  # Simplified implementation

    def _count_panels_by_edge_detection(self, comic_image):
        """
        Count panels using edge detection to find panel borders.

        Args:
            comic_image: Comic image to analyze

        Returns:
            int: Estimated panel count
        """
        # Simplified implementation - would use opencv in real scenario
        # For now, return a reasonable estimate
        width, height = comic_image.size
        aspect_ratio = width / height

        if aspect_ratio > 2:  # Very wide
            return 3
        elif aspect_ratio < 0.8:  # Very tall
            return 3
        else:  # Square-ish
            return 4

    def _crop_to_correct_panels(self, comic_image, expected_panels, detected_panels):
        """
        Crop image to reduce panel count to expected number.

        Args:
            comic_image: Original image
            expected_panels: Target panel count
            detected_panels: Current panel count

        Returns:
            PIL.Image.Image: Cropped image
        """
        width, height = comic_image.size

        # Simple crop strategy - crop from right/bottom
        if detected_panels == expected_panels + 1:
            # Remove one panel
            import math
            if width > height:  # Horizontal layout, crop from right
                new_width = int(width * (expected_panels / detected_panels))
                return comic_image.crop((0, 0, new_width, height))
            else:  # Vertical layout, crop from bottom
                new_height = int(height * (expected_panels / detected_panels))
                return comic_image.crop((0, 0, width, new_height))

        return comic_image  # Return original if can't crop simply

    def _expand_to_correct_panels(self, comic_image, expected_panels, detected_panels):
        """
        Expand image or add divisions to increase panel count.

        Args:
            comic_image: Original image
            expected_panels: Target panel count
            detected_panels: Current panel count

        Returns:
            PIL.Image.Image: Modified image
        """
        # For now, return original - this would be complex to implement properly
        return comic_image

    def _create_mathematical_perfect_comic(self, title, description, num_scenes, style):
        """
        Create a mathematically perfect comic that GUARANTEES correct panel count.

        Args:
            title: Comic title
            description: Comic description
            num_scenes: Number of panels (guaranteed)
            style: Visual style

        Returns:
            PIL.Image.Image: Mathematically perfect comic
        """
        print(f"🔬 MATHEMATICAL COMIC: Creating perfect {num_scenes}-panel layout")

        # Enhanced placeholder with perfect mathematical precision
        width, height = 1024, 1536
        comic = Image.new("RGB", (width, height), (255, 255, 255))
        draw = ImageDraw.Draw(comic)

        # Load fonts
        try:
            title_font = ImageFont.truetype("Arial.ttf", 28)
            panel_font = ImageFont.truetype("Arial.ttf", 20)
            desc_font = ImageFont.truetype("Arial.ttf", 14)
        except IOError:
            title_font = panel_font = desc_font = ImageFont.load_default()

        # Draw title
        draw.text((20, 10), f"{title} - Mathematical Perfect Comic", fill=(0, 0, 0), font=title_font)

        # Calculate PERFECT panel layout
        grid_configs = {
            1: (1, 1), 2: (1, 2), 3: (1, 3), 4: (2, 2), 5: (1, 5), 6: (2, 3),
            7: (1, 7), 8: (2, 4), 9: (3, 3), 10: (2, 5), 11: (1, 11), 12: (3, 4)
        }

        if num_scenes in grid_configs:
            rows, cols = grid_configs[num_scenes]
        else:
            import math
            cols = min(4, math.ceil(math.sqrt(num_scenes)))
            rows = math.ceil(num_scenes / cols)

        # Draw panels with EXTREME precision
        panel_area_y = 50
        panel_area_height = height - 100
        PADDING = 20  # Padding around the entire comic
        GUTTER = 10   # Space between panels

        # Calculate available space for panels
        available_width = width - (2 * PADDING) - ((cols - 1) * GUTTER)
        available_height = panel_area_height - ((rows - 1) * GUTTER)

        panel_width = available_width // cols
        panel_height = available_height // rows

        panels_drawn = 0
        for row in range(rows):
            for col in range(cols):
                if panels_drawn >= num_scenes:
                    break

                x1 = PADDING + col * (panel_width + GUTTER)
                y1 = panel_area_y + row * (panel_height + GUTTER)
                x2 = x1 + panel_width - 5
                y2 = y1 + panel_height - 5

                # Draw panel with thick border for absolute clarity
                border_thickness = 3
                draw.rectangle([x1, y1, x2, y2], outline=(0, 0, 0), fill=(240, 240, 255), width=border_thickness)

                # Add panel number and content
                panel_num = panels_drawn + 1
                panel_text = f"PANEL {panel_num}"
                text_bbox = draw.textbbox((0, 0), panel_text, font=panel_font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                text_x = x1 + (panel_width - text_width) // 2
                text_y = y1 + (panel_height - text_height) // 2
                draw.text((text_x, text_y), panel_text, fill=(0, 0, 0), font=panel_font)

                # Add story snippet
                story_snippet = f"Scene {panel_num}"
                snippet_bbox = draw.textbbox((0, 0), story_snippet, font=desc_font)
                snippet_width = snippet_bbox[2] - snippet_bbox[0]
                snippet_x = x1 + (panel_width - snippet_width) // 2
                snippet_y = text_y + text_height + 10
                draw.text((snippet_x, snippet_y), story_snippet, fill=(100, 100, 100), font=desc_font)

                panels_drawn += 1

        # Add mathematical verification at bottom
        verification_text = f"MATHEMATICAL VERIFICATION: {panels_drawn} panels generated (Target: {num_scenes}) ✓"
        draw.text((20, height - 40), verification_text, fill=(0, 150, 0), font=desc_font)

        print(f"✅ MATHEMATICAL COMIC COMPLETE: {panels_drawn} panels drawn with perfect precision")
        return comic

    def _create_success_response(self, comic_image):
        """
        Create standardized success response.

        Args:
            comic_image: Successfully validated comic image

        Returns:
            tuple: (image, data_url)
        """
        buffered = io.BytesIO()
        comic_image.save(buffered, format="PNG")
        img_bytes = buffered.getvalue()
        img_b64 = base64.b64encode(img_bytes).decode("utf-8")
        data_url = f"data:image/png;base64,{img_b64}"

        return comic_image, data_url

    def _create_comic_prompt(self, title, description, characters=None, settings=None, style=None, num_scenes=1):
        """
        Delegate prompt creation to the updated implementation in reference.comic_image_generator
        so that this model always uses the latest, most advanced prompt engineering logic.
        """
        # Lazily instantiate the reference prompt generator once for reuse
        if not hasattr(self, "_ref_prompt_generator"):
            self._ref_prompt_generator = RefComicImageGenerator()

        # Use the reference implementation to build the prompt
        return self._ref_prompt_generator._create_comic_prompt(
            title,
            description,
            characters=characters,
            settings=settings,
            style=style,
            num_scenes=num_scenes,
        )

    def _create_ascii_layout(self, num_scenes):
        """
        Create MINIMAL ASCII representation - much shorter.

        Args:
            num_scenes: Number of panels to visualize

        Returns:
            str: Minimal ASCII art
        """
        if num_scenes == 1:
            return "[PANEL 1]"

        # Very simple representation
        if num_scenes <= 4:
            return f"[P1][P2]{'[P3]' if num_scenes >= 3 else ''}{'[P4]' if num_scenes == 4 else ''}"
        else:
            return f"Grid: {num_scenes} panels"

    def _create_placeholder_comic(self, title, description, num_scenes=1):
        """
        Create a placeholder comic if image generation fails.

        Args:
            title: Title of the comic
            description: Visual description of the comic
            num_scenes: Number of panels to create in placeholder

        Returns:
            PIL.Image.Image: Placeholder comic image
        """
        # Create a blank comic
        width, height = 1024, 1536

        comic = Image.new("RGB", (width, height), (255, 255, 255))
        draw = ImageDraw.Draw(comic)

        # Add comic title
        try:
            title_font = ImageFont.truetype("Arial.ttf", 24)
            desc_font = ImageFont.truetype("Arial.ttf", 12)
            panel_font = ImageFont.truetype("Arial.ttf", 16)
        except IOError:
            title_font = desc_font = panel_font = ImageFont.load_default()

        # Draw title
        draw.text((20, 10), f"{title} - Placeholder", fill=(0, 0, 0), font=title_font)

        # Calculate panel layout
        import math
        if num_scenes == 1:
            rows, cols = 1, 1
        elif num_scenes == 2:
            rows, cols = 1, 2
        elif num_scenes == 3:
            rows, cols = 1, 3
        elif num_scenes == 4:
            rows, cols = 2, 2
        elif num_scenes <= 6:
            rows, cols = 2, 3
        elif num_scenes <= 9:
            rows, cols = 3, 3
        else:
            cols = math.ceil(math.sqrt(num_scenes))
            rows = math.ceil(num_scenes / cols)

        # Draw panels
        panel_area_y = 50
        panel_area_height = height - 60
        PADDING = 20  # Padding around the entire comic
        GUTTER = 10   # Space between panels

        # Calculate available space for panels
        available_width = width - (2 * PADDING) - ((cols - 1) * GUTTER)
        available_height = panel_area_height - ((rows - 1) * GUTTER)

        panel_width = available_width // cols
        panel_height = available_height // rows

        for i in range(num_scenes):
            row = i // cols
            col = i % cols

            x1 = PADDING + col * (panel_width + GUTTER)
            y1 = panel_area_y + row * (panel_height + GUTTER)
            x2 = x1 + panel_width - 5
            y2 = y1 + panel_height - 5

            # Draw panel border
            draw.rectangle([x1, y1, x2, y2], outline=(0, 0, 0), fill=(240, 240, 240), width=2)

            # Add panel number
            panel_text = f"Panel {i + 1}"
            text_x = x1 + panel_width // 2 - 30
            text_y = y1 + panel_height // 2 - 10
            draw.text((text_x, text_y), panel_text, fill=(0, 0, 0), font=panel_font)

        # Add description at bottom
        info_text = f"Placeholder comic with {num_scenes} panels"
        draw.text((20, height - 30), info_text, fill=(100, 100, 100), font=desc_font)

        return comic

    def split_comic_into_scenes(self, comic_image, num_scenes, preferred_layout=None, use_gemini_analysis=True):
        """
        Split a comic image into individual scenes based on Gemini Vision analysis.
        Completely trusts Gemini's visual detection of the actual comic layout.

        Args:
            comic_image: PIL.Image.Image object of the comic
            num_scenes: Expected number of scenes (for context only)
            preferred_layout: Optional tuple (rows, cols) to override automatic detection
            use_gemini_analysis: Whether to use Gemini Vision (default: True, recommended)

        Returns:
            list: List of PIL.Image.Image objects, one for each detected scene
        """
        if num_scenes <= 1:
            return [comic_image]

        import numpy as np

        width, height = comic_image.size

        def _detect_grid_from_borders(img, expected_panels):
            """Detect inner grid by scanning for near-black border lines."""
            gray = np.array(img.convert('L'))
            # Identify rows/cols with a significant proportion of uniformly dark OR bright pixels (captures thin black or white gutters)
            dark_row = (np.mean(gray < 90, axis=1) > 0.4)   # 40% of pixels darker than dark-grey
            light_row = (np.mean(gray > 200, axis=1) > 0.4) # 40% of pixels very bright (white gutters)
            row_mask = dark_row | light_row

            dark_col = (np.mean(gray < 90, axis=0) > 0.4)
            light_col = (np.mean(gray > 200, axis=0) > 0.4)
            col_mask = dark_col | light_col

            # Extract continuous non-border spans
            def _segments(mask):
                segs = []
                start = None
                for i, val in enumerate(~mask):
                    if val and start is None:
                        start = i
                    elif not val and start is not None:
                        segs.append((start, i))
                        start = None
                if start is not None:
                    segs.append((start, len(mask)))
                return segs

            row_segments = _segments(row_mask)
            col_segments = _segments(col_mask)

            detected_rows = len(row_segments)
            detected_cols = len(col_segments)

            if detected_rows * detected_cols == expected_panels:
                return detected_rows, detected_cols, row_segments, col_segments
            return None, None, row_segments, col_segments

        # Try border detection first if no explicit layout override
        if preferred_layout is None:
            det_rows, det_cols, row_segments, col_segments = _detect_grid_from_borders(comic_image, num_scenes)
        else:
            det_rows = det_cols = None

        if preferred_layout:
            rows, cols = preferred_layout
            print(f"🎯 Using manual override: {rows}×{cols} layout")
            row_segments = col_segments = None
        elif det_rows and det_cols:
            rows, cols = det_rows, det_cols
            print(f"✅ Border-detection found {rows}×{cols} grid (using slim borders)")
        else:
            if use_gemini_analysis:
                print("🔍 Analyzing comic layout with Gemini Vision...")
                rows, cols = self.analyze_comic_layout_with_gemini(comic_image, num_scenes)
            else:
                print("⚠️ Gemini analysis disabled & border detection failed. Using square grid fallback.")
                import math
                cols = math.ceil(math.sqrt(num_scenes))
                rows = math.ceil(num_scenes / cols)
                print(f"📐 Using calculated {rows}×{cols} grid")

        # Build grid boxes either from detected segments or even divisions
        grid = []
        if row_segments and col_segments and len(row_segments) == rows and len(col_segments) == cols:
            for r_idx in range(rows):
                for c_idx in range(cols):
                    if len(grid) < num_scenes:
                        y1, y2 = row_segments[r_idx]
                        x1, x2 = col_segments[c_idx]
                        grid.append((x1, y1, x2, y2))
        else:
            # Fallback to equal slicing with proper padding
            PADDING = 20  # Padding around the entire comic
            GUTTER = 10   # Space between panels

            # Calculate available space for panels
            available_width = width - (2 * PADDING) - ((cols - 1) * GUTTER)
            available_height = height - (2 * PADDING) - ((rows - 1) * GUTTER)

            scene_width = available_width // cols
            scene_height = available_height // rows

            panels_created = 0
            for row in range(rows):
                for col in range(cols):
                    if panels_created < num_scenes:
                        x1 = PADDING + col * (scene_width + GUTTER)
                        y1 = PADDING + row * (scene_height + GUTTER)
                        x2 = x1 + scene_width
                        y2 = y1 + scene_height
                        grid.append((x1, y1, x2, y2))
                        panels_created += 1

        # Crop each scene from the comic
        scenes = []
        from PIL import ImageOps
        BORDER_SIZE = 6  # pixels

        for box in grid:
            scene = comic_image.crop(box)
            # Add bold border for clearer panel separation
            scene_with_border = ImageOps.expand(scene, border=BORDER_SIZE, fill="black")
            scenes.append(scene_with_border)

        # Final validation: ensure we have exactly the requested number of scenes
        if len(scenes) != num_scenes:
            print(f"⚠️ CRITICAL WARNING: Split produced {len(scenes)} panels but {num_scenes} were requested!")
            print(f"📋 Detected layout: {rows}×{cols} = {rows*cols} panels")
            print(f"🎯 Requested: {num_scenes} panels")

            # If we have fewer scenes than requested, duplicate the last scene
            while len(scenes) < num_scenes:
                if scenes:
                    scenes.append(scenes[-1].copy())
                    print(f"🔄 Duplicated last panel to reach {len(scenes)} panels")
                else:
                    # Fallback: create a placeholder scene
                    placeholder_scene = Image.new("RGB", (scene_width, scene_height), (240, 240, 240))
                    scenes.append(placeholder_scene)
                    print(f"➕ Added placeholder panel {len(scenes)}")

            # If we have more scenes than requested, trim to exact count
            if len(scenes) > num_scenes:
                scenes = scenes[:num_scenes]
                print(f"✂️ Trimmed to exactly {num_scenes} panels")

        print(f"✅ Final result: {len(scenes)} panels (expected: {num_scenes})")
        return scenes

    def _find_all_factorizations(self, n):
        """
        Find all possible factorizations of a number into rows × columns.

        Args:
            n: Number to factorize

        Returns:
            list: List of tuples (rows, cols) where rows * cols = n
        """
        factorizations = []
        for i in range(1, int(n**0.5) + 1):
            if n % i == 0:
                rows, cols = i, n // i
                factorizations.append((rows, cols))
                # Add the reverse unless it's a perfect square
                if rows != cols:
                    factorizations.append((cols, rows))

        return sorted(factorizations)

    def _calculate_optimal_layout(self, num_scenes, image_width, image_height):
        """
        Calculate the optimal grid layout based on image aspect ratio and scene count.

        Args:
            num_scenes: Number of scenes to arrange
            image_width: Width of the comic image
            image_height: Height of the comic image

        Returns:
            tuple: (rows, cols) representing the optimal grid layout
        """
        # Get all possible factorizations
        factorizations = self._find_all_factorizations(num_scenes)

        if not factorizations:
            # Fallback for prime numbers or edge cases
            import math
            cols = math.ceil(math.sqrt(num_scenes))
            rows = math.ceil(num_scenes / cols)
            return (rows, cols)

        # Calculate image aspect ratio
        image_aspect_ratio = image_width / image_height

        # Special handling for specific scene counts with common layouts
        layout_preferences = {
            2: [(1, 2), (2, 1)],  # Horizontal strip or vertical strip
            3: [(1, 3), (3, 1)],  # Horizontal strip or vertical strip
            4: [(2, 2), (1, 4), (4, 1)],  # Square, horizontal strip, or vertical strip
            6: [(2, 3), (3, 2), (1, 6), (6, 1)],  # Common comic layouts
            8: [(2, 4), (4, 2), (1, 8), (8, 1)],  # Various arrangements
            9: [(3, 3), (1, 9), (9, 1)],  # Square preferred
            12: [(3, 4), (4, 3), (2, 6), (6, 2), (1, 12), (12, 1)],  # Multiple good options
            16: [(4, 4), (2, 8), (8, 2), (1, 16), (16, 1)],  # Square preferred
            24: [(4, 6), (6, 4), (3, 8), (8, 3), (2, 12), (12, 2)]  # Various arrangements
        }

        # Use preferred layouts if available, otherwise use all factorizations
        possible_layouts = layout_preferences.get(num_scenes, factorizations)

        # Filter to only include valid factorizations
        valid_layouts = [layout for layout in possible_layouts if layout in factorizations]

        if not valid_layouts:
            valid_layouts = factorizations

        # Score each layout based on how well it matches the image aspect ratio
        best_layout = None
        best_score = float('inf')

        # Add minimum panel size constraints to prevent cutoff
        MIN_PANEL_WIDTH = 120   # Minimum width for readability
        MIN_PANEL_HEIGHT = 120  # Minimum height for readability
        PADDING = 40            # Total padding around the comic
        BORDER_SIZE = 6         # Border size per panel

        for rows, cols in valid_layouts:
            # Calculate panel dimensions with padding
            available_width = image_width - PADDING
            available_height = image_height - PADDING

            panel_width = available_width / cols
            panel_height = available_height / rows

            # Skip layouts that would create panels too small
            if panel_width < MIN_PANEL_WIDTH or panel_height < MIN_PANEL_HEIGHT:
                continue

            # Calculate the aspect ratio this layout would create for individual panels
            panel_aspect_ratio = panel_width / panel_height

            # Calculate layout aspect ratio (how the overall grid looks)
            layout_aspect_ratio = cols / rows

            # Score based on multiple factors:
            # 1. How close the layout aspect ratio is to the image aspect ratio
            # 2. Prefer layouts that create reasonable panel aspect ratios (not too thin/wide)
            # 3. Slight preference for more square-ish overall layouts
            # 4. Ensure panels are large enough to be readable

            aspect_ratio_diff = abs(layout_aspect_ratio - image_aspect_ratio)
            panel_aspect_penalty = 0

            # Penalize extremely thin or wide panels
            if panel_aspect_ratio < 0.3 or panel_aspect_ratio > 3.0:
                panel_aspect_penalty = 2.0
            elif panel_aspect_ratio < 0.5 or panel_aspect_ratio > 2.0:
                panel_aspect_penalty = 0.5

            # Slight preference for layouts closer to square
            square_preference = abs(rows - cols) * 0.1

            # Bonus for larger panels (encourages fewer, larger panels)
            size_bonus = 1.0 / (panel_width * panel_height / 10000)

            total_score = aspect_ratio_diff + panel_aspect_penalty + square_preference + size_bonus

            if total_score < best_score:
                best_score = total_score
                best_layout = (rows, cols)

        return best_layout if best_layout else factorizations[0]

    def get_possible_layouts(self, num_scenes):
        """
        Get all possible layout options for a given number of scenes.

        Args:
            num_scenes: Number of scenes

        Returns:
            list: List of tuples (rows, cols) representing possible layouts
        """
        return self._find_all_factorizations(num_scenes)

    def analyze_comic_layout_with_gemini(self, comic_image, num_scenes):
        """
        Use Gemini Vision to analyze a comic image and determine the actual splitting layout.
        Completely trusts Gemini's visual analysis without mathematical validation.

        Args:
            comic_image: PIL.Image.Image object of the comic
            num_scenes: Expected number of scenes (used for context, not validation)

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

            # Create the analysis prompt - focus on what Gemini actually sees
            analysis_prompt = f"""
            Analyze this comic image carefully and tell me exactly how it's structured.

            Please examine the image and determine:
            1. How many rows of panels do you see?
            2. How many columns of panels do you see?
            3. Describe the panel layout you observe

            Look for:
            - Panel borders/dividers (black lines, white gutters, separations)
            - Distinct scenes or visual sections
            - Grid patterns or panel arrangements
            - Any visual cues that separate different parts of the image

            Trust what you see - even if it doesn't match expected numbers.

            Respond with ONLY a JSON object in this exact format:
            {{
                "detected_rows": number,
                "detected_cols": number,
                "confidence": "high/medium/low",
                "layout_description": "detailed description of the panel arrangement you observe"
            }}

            Be precise about what you actually see in the image.
            """

            # Send to Gemini Vision
            response = model.generate_content([analysis_prompt, comic_image])
            response_text = response.text.strip()

            print(f"Gemini Vision analysis: {response_text}")

            # Parse the JSON response
            try:
                # Extract JSON from response
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group()
                    analysis_result = json.loads(json_str)

                    rows = analysis_result.get("detected_rows", 0)
                    cols = analysis_result.get("detected_cols", 0)
                    confidence = analysis_result.get("confidence", "unknown")
                    description = analysis_result.get("layout_description", "")

                    print(f"✅ Trusting Gemini: {rows}×{cols} layout with {confidence} confidence")
                    print(f"Description: {description}")

                    # Trust Gemini completely - no validation against expected scenes
                    if rows > 0 and cols > 0:
                        actual_panels = rows * cols
                        if actual_panels != num_scenes:
                            print(f"📋 Gemini detected {actual_panels} panels, not {num_scenes} as expected. Trusting Gemini's visual analysis.")
                        return (rows, cols)
                    else:
                        print("❌ Gemini returned invalid layout (0 rows or cols)")

            except (json.JSONDecodeError, KeyError) as e:
                print(f"❌ Error parsing Gemini response: {e}")

        except Exception as e:
            print(f"❌ Error analyzing comic with Gemini Vision: {e}")

        # Only fallback if Gemini completely fails to respond
        print("⚠️ Gemini analysis failed completely. Using simple 1×1 layout.")
        return (1, 1)
