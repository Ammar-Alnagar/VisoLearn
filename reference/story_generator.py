from google.generativeai import GenerativeModel
import json
import re
import os
import datetime
import openai
import config

class StoryGenerator:
    """
    Direct story generator that creates comic panel style stories from user input.
    """

    def __init__(self):
        self.model = GenerativeModel('gemini-2.5-flash')

    def log_prompt(self, prompt, log_file="story_prompt_logs.jsonl"):
        """Log the prompt to a file for debugging and improvement purposes."""
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "prompt": prompt
        }
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

    def enhance_user_story(self, user_description, max_retries=3, current_retry=0):
        """
        Enhance the user's story with more vibrancy, detail, and narrative richness using
        optimized AI prompting techniques for visual storytelling with smart detail preservation.
        
        Args:
            user_description: The user's original story idea or prompt
            max_retries: Maximum number of retry attempts (default: 3)
            current_retry: Current retry attempt number (default: 0)
            
        Returns:
            enhanced_story: A more vibrant and detailed version of the story with preserved key elements
        """
        print(f"[StoryGenerator] Enhancing user story (attempt {current_retry + 1}/{max_retries}): {user_description[:100]}...")
        
        # Recursion protection
        if current_retry >= max_retries:
            print(f"[StoryGenerator] Max retries reached, returning original description")
            return user_description
        
        try:
            # Smart enhancement prompt with detail preservation focus
            enhancement_prompt = self._create_detail_focused_enhancement_prompt(user_description)
            
            self.log_prompt(enhancement_prompt)
            
            # Generate with timeout protection
            try:
                response = self.model.generate_content(enhancement_prompt)
                enhanced_story = response.text.strip()
                
                # Validate response and preserve original details if enhancement is poor
                if self._validate_enhancement_quality(enhanced_story, user_description):
                    print(f"[StoryGenerator] Story successfully enhanced with detail preservation")
                    return enhanced_story
                else:
                    print(f"[StoryGenerator] Enhancement quality insufficient, using original with minimal enhancement")
                    return self._create_minimal_enhancement(user_description)
                
            except Exception as gemini_error:
                print(f"[StoryGenerator] Gemini API error: {gemini_error}")
                # Retry with simplified prompt if API fails
                if current_retry < max_retries - 1:
                    print(f"[StoryGenerator] Retrying with simplified approach...")
                    return self._simplified_enhancement(user_description)
                else:
                    raise gemini_error
                    
        except Exception as e:
            print(f"[StoryGenerator] Enhancement error: {e}")
            # Recursive retry with exponential backoff
            if current_retry < max_retries - 1:
                import time
                time.sleep(1 * (current_retry + 1))  # Exponential backoff
                return self.enhance_user_story(user_description, max_retries, current_retry + 1)
            else:
                print(f"[StoryGenerator] All enhancement attempts failed, returning original")
                return user_description

    def _create_detail_focused_enhancement_prompt(self, user_description):
        """Create a concise enhancement prompt that adds coherence and enough detail for exactly 12 scenes."""
        
        return f"""
        You are an expert visual storytelling assistant. Take the user's story concept and enhance it with just enough detail to create a coherent visual narrative across exactly 12 scenes.

        ORIGINAL STORY: "{user_description}"

        ENHANCEMENT GOALS:
        • Add key character details (main appearance features, clothing style)
        • Establish clear setting and atmosphere
        • Create logical scene progression for exactly 12 panels
        • Ensure visual coherence across all scenes
        • Keep descriptions concise but vivid

        REQUIREMENTS:
        • Focus on 1-2 main characters with consistent visual details
        • Establish 1-2 primary locations with clear visual identity
        • Create a simple but complete story arc suitable for exactly 12 scenes
        • Add specific visual details only where needed for consistency
        • Maintain the original story's core essence and tone

        OUTPUT: Enhanced story description (2-3 paragraphs maximum) that provides coherent visual storytelling structure for exactly 12 sequential scenes.
        """

    def _validate_enhancement_quality(self, enhanced_story, original_story):
        """Validate that the enhancement adds coherence and appropriate detail for 12-15 scenes."""
        # Basic validation checks
        if not enhanced_story or len(enhanced_story) < 50:
            return False
        
        # Check if response is reasonable length (not too short or excessively long)
        enhanced_words = len(enhanced_story.split())
        original_words = len(original_story.split())
        
        # Enhancement should be longer than original but not excessively so
        if enhanced_words < original_words or enhanced_words > original_words * 5:
            return False
        
        # Check for key narrative elements
        story_elements = ['character', 'scene', 'story', 'visual', 'setting', 'action']
        has_story_elements = sum(1 for element in story_elements if element.lower() in enhanced_story.lower())
        
        # Should have at least 2-3 story elements mentioned
        if has_story_elements < 2:
            return False
        
        # Check that it's not just repeating the original
        similarity_threshold = 0.8
        original_lower = original_story.lower()
        enhanced_lower = enhanced_story.lower()
        
        # Simple similarity check - if too similar, enhancement failed
        common_words = set(original_lower.split()) & set(enhanced_lower.split())
        original_unique = len(set(original_lower.split()))
        
        if original_unique > 0:
            similarity = len(common_words) / original_unique
            if similarity > similarity_threshold and enhanced_words < original_words * 1.5:
                return False
        
        return True

    def _create_minimal_enhancement(self, user_description):
        """Create minimal enhancement that preserves original while adding basic coherence for exactly 12 scenes."""
        
        # Add basic structural enhancement without lengthy details
        enhanced = f"""
        Enhanced Story: {user_description}
        
        Visual Coherence Elements:
        - Main character with consistent appearance throughout all scenes
        - Clear setting that remains visually consistent
        - Logical progression suitable for exactly 12 sequential panels
        - Simple but complete story arc with beginning, middle, and end
        
        This story will unfold across exactly 12 scenes showing the character's journey with visual consistency and narrative coherence.
        """
        
        return enhanced.strip()

    def _simplified_enhancement(self, user_description):
        """
        Simplified enhancement fallback when the main enhancement fails.
        
        Args:
            user_description: Original user story description
            
        Returns:
            str: Simplified enhanced description focused on coherence for exactly 12 scenes
        """
        try:
            simplified_prompt = f"""
            Enhance this story for exactly 12 visual scenes. Keep it concise but coherent:
            
            Original: {user_description}
            
            Add:
            - Key character appearance details
            - Main setting description  
            - Clear story progression for 12 scenes
            - Visual consistency elements
            
            Enhanced story (2-3 sentences max):
            """
            
            response = self.model.generate_content(simplified_prompt)
            enhanced_story = response.text.strip()
            
            if enhanced_story and len(enhanced_story) > 20:
                print(f"[StoryGenerator] Used simplified enhancement successfully")
                return enhanced_story
            else:
                return user_description
                
        except Exception as e:
            print(f"[StoryGenerator] Simplified enhancement also failed: {e}")
            return user_description

    def generate_story(self, user_description, panels_per_page=8, num_pages=1):
        """
        Generate a comic panel style story directly from user input.
        
        Args:
            user_description: The user's story idea or prompt
            panels_per_page: Number of panels per comic page (default is 8)
            num_pages: Number of pages to generate (default is 1)
            
        Returns:
            story_data: Structured data for the story with panels organized by pages
        """
        # Enhance the user's story with more vibrancy and detail
        enhanced_story = self.enhance_user_story(user_description)
        
        total_panels = panels_per_page * num_pages
        print(f"[StoryGenerator] Generating comic story with {num_pages} pages, {panels_per_page} panels per page ({total_panels} total panels) from enhanced story...")
        
        query = f"""
        You are a world-class comic book writer and visual storyteller known for creating engaging and logically coherent comic narratives. 
        Using the following enhanced story concept:
        
        "{enhanced_story}"
        
        create an original, SINGLE CONTINUOUS STORY that spans exactly {num_pages} pages, with each page containing exactly {panels_per_page} sequential panels (total of {total_panels} panels).
        
        Story Continuity and Details:
        
        STORY PROGRESSION:
        - The story MUST progress continuously from one page to the next; each page must pick up seamlessly where the previous one ended.
        - DO NOT restart or rehash past events; do not summarize, but continually drive the narrative forward.
        - Ensure logical cause and effect: every event should naturally lead to the next.
        - Incorporate explicit timeline markers and transitional phrases (e.g., "later that day", "the next morning") to clearly indicate the passage of time.
        
        NARRATIVE QUALITY:
        - Develop a fluid narrative with a well-structured beginning, development, and conclusion.
        - Create meaningful character development with clear motivations and organic conflict.
        - Follow the Three-Act Structure (Setup, Confrontation, Resolution), integrating subtle foreshadowing and satisfying payoffs.
        - Ensure the language is fluent, clear, and logically organized, avoiding disjointed or contradictory sequences.
        - Enhance descriptions with specific, sensory details (e.g., time of day, weather, emotional cues) to enrich the narrative experience.
        
        VISUAL STORYTELLING:
        - Each page will be generated as a SINGLE IMAGE with a grid of {panels_per_page} panels.
        - Craft visual descriptions that emphasize actions, expressions, and settings to convey the story without relying on text.
        - Emphasize timely transitions and evolving settings that reflect the narrative's timeline progression.
        - Although dialogue may accompany the visual, the final images must communicate the narrative purely through visuals.
         - Focus on creating EXTREMELY DETAILED visual descriptions that ensure the narrative can be understood solely through images.
         - CRITICAL: Maintain consistent character appearances, settings, and visual elements across ALL panels and pages.
        
        CONTINUITY REQUIREMENTS (ESSENTIAL):
        1. Before writing ANY panels, first create a detailed character sheet for each main character with:
           - Precise physical appearance (height, build, facial features, hair style/color, clothing/costume, etc.)
           - Unique identifying visual traits that will remain consistent throughout ALL panels
           - Character's personality traits that will be expressed visually
           - Background and motivations that drive their actions
           - Character arc - how they change throughout the story
        2. Create a setting guide defining key locations that will appear, including:
           - Detailed descriptions of recurring environments with specific visual elements
           - Color schemes and lighting characteristics for each location
           - Notable objects or landmarks that provide context and consistency
           - Logical spatial relationship between different settings
        3. Plot progression must be LOGICAL from panel to panel and page to page
           - Each event should have a clear cause that preceded it
           - Character decisions must be consistent with their established personality and motivations
           - Track the passage of time consistently (day/night cycles, aging, decay, growth, etc.)
        4. Avoid continuity errors like:
           - Characters' appearances changing between panels/pages
           - Objects appearing/disappearing without explanation
           - Impossible spatial relationships or teleporting characters
           - Time of day changing abruptly without reason
           - Characters knowing information they couldn't have learned
           - Abilities or traits that weren't previously established
        5. When transitioning between pages, the first panel of each new page MUST directly continue the action from the last panel of the previous page

        OVERALL STORY STRUCTURE:
        - Plan a complete narrative with a clear beginning (page 1), middle development (subsequent pages), and satisfying conclusion (final page).
        - For multi-page stories, create a plot that naturally spans the exact number of pages requested.
        - Ensure each page pushes the story forward in a meaningful way.
        - Include these essential story elements:
          1. HOOK: An engaging opening that introduces the protagonist and situation
          2. INCITING INCIDENT: The event that disrupts the status quo and starts the main conflict
          3. RISING ACTION: Escalating challenges that test the protagonist
          4. MIDPOINT: A significant turning point that raises the stakes
          5. COMPLICATIONS: New obstacles that make the protagonist's goal more difficult
          6. CLIMAX: The final confrontation where the main conflict comes to a head
          7. RESOLUTION: The aftermath showing the consequences and new status quo

        VISUAL STORYTELLING TECHNIQUES TO INCORPORATE:
        1. Character Design: Provide detailed, unique character designs with distinctive features that make them instantly recognizable across panels
        2. Emotional Clarity: Make emotions and reactions extremely clear through exaggerated facial expressions and body language
        3. Visual Continuity: Use consistent visual motifs, colors, and settings to establish locations and transitions
        4. Action Sequencing: Break down action sequences into clear cause-and-effect panel transitions
        5. Visual Symbols: Use universal visual symbols and metaphors that readers understand without explanation
        6. Environment Details: Make settings rich with contextual details that establish time, place, and mood
        7. Contrast & Focus: Use composition techniques to draw attention to the most important elements in each panel
        8. Progressive Revelation: Structure the narrative to visually reveal information in a clear, logical sequence
        9. Parallel Action: Show simultaneous events occurring in different locations when relevant
        10. Visual Callbacks: Reference earlier visual elements to reinforce themes and story connections
        
        FOR EACH PANEL, provide the following details:
        1. A concise but evocative title that captures the essence of this moment
        2. An extremely detailed visual description including:
           - Precise character positioning, expressions, and body language
           - Specific environmental details (lighting, weather, setting elements)
           - Color palette and mood
           - Perspective/camera angle
           - Clear emotional expressions that convey meaning without requiring text
           - Visual cues that establish the narrative relationship to previous and next panels
        3. The dialogue or narration that would normally appear (for context only, will NOT be shown in images)
        4. The panel's purpose in advancing the narrative
        5. Any symbolism or visual elements that connect to other panels
        
        Make sure the panels flow logically from one to the next IN READING ORDER (typically left-to-right, top-to-bottom),
        creating a cohesive page that tells part of the overall story through visuals alone.
        
        The transitions between pages should occur at natural breakpoints in the narrative while maintaining continuous story flow.
        
        FORMAT YOUR RESPONSE AS A VALID JSON OBJECT with the following structure:
        {{
          "title": "An evocative title for the overall story",
          "premise": "A detailed overview of the story concept, themes, and setting",
          "characters": [
            {{
              "name": "Character Name",
              "visual_description": "Detailed visual description of the character's appearance",
              "traits": ["Distinctive visual trait 1", "Distinctive visual trait 2", "etc"],
              "background": "Character's backstory and motivations",
              "arc": "How this character changes throughout the story"
            }},
            ... (repeat for all main characters)
          ],
          "settings": [
            {{
              "name": "Setting Name",
              "description": "Detailed visual description of this recurring location",
              "visual_elements": ["Notable visual element 1", "Notable visual element 2", "etc"],
              "mood": "The emotional atmosphere of this location"
            }},
            ... (repeat for all important settings)
          ],
          "pages": [
            {{
              "page_number": 1,
              "panels": [
                {{
                  "panel_number": 1,
                  "title": "Title for this panel",
                  "visual_description": "Extremely detailed visual description for image generation",
                  "text": "Any dialogue or caption text (for context only, will NOT be shown in images)",
                  "purpose": "This panel's role in the narrative",
                  "symbolism": "Any symbolic elements or foreshadowing in this panel"
                }},
                ... (repeat for all {panels_per_page} panels on page 1)
              ]
            }},
            ... (repeat for all {num_pages} pages)
          ]
        }}
        
        Pay extremely close attention to making each panel's visual elements tell the story without needing text.
        The entire story should be coherent and understandable through visuals alone when the panels are viewed in sequence.
        Remember that all panels on a page will be rendered together in a single image, so they should have
        visual and thematic coherence while still being distinct and sequential.
        """
        
        self.log_prompt(query)
        response = self.model.generate_content(query)
        
        try:
            json_match = re.search(r'\{[\s\S]*\}', response.text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                
                # Clean the JSON string
                json_str = self._fix_json(json_str)
                
                story_data = json.loads(json_str)
                
                # Validate and fix the structure if needed
                story_data = self._validate_and_fix_structure(story_data, panels_per_page, num_pages)
                
                print(f"[StoryGenerator] Successfully generated story: {story_data.get('title', 'Untitled')}")
                return story_data
            else:
                print("[StoryGenerator] No valid JSON found in response.")
                raise ValueError("No valid JSON found in response")
        except Exception as e:
            print(f"Error in StoryGenerator: {e}")
            return self._create_fallback_story(user_description, panels_per_page, num_pages)

    def _validate_and_fix_structure(self, story_data, panels_per_page, num_pages):
        """Validate and fix the story structure if needed."""
        # Ensure we have the required keys
        if "title" not in story_data:
            story_data["title"] = "Untitled Comic"
            
        if "premise" not in story_data:
            story_data["premise"] = "A visual story."
            
        # Ensure we have characters with all required fields
        if "characters" not in story_data:
            story_data["characters"] = []
        
        for character in story_data.get("characters", []):
            if "visual_description" not in character:
                character["visual_description"] = "A character in the story."
            if "traits" not in character:
                character["traits"] = []
            if "background" not in character:
                character["background"] = "Unknown background."
            if "arc" not in character:
                character["arc"] = "Experiences events throughout the story."
            
        # Ensure we have settings with all required fields
        if "settings" not in story_data:
            story_data["settings"] = []
            
        for setting in story_data.get("settings", []):
            if "description" not in setting:
                setting["description"] = "A location in the story."
            if "visual_elements" not in setting:
                setting["visual_elements"] = []
            if "mood" not in setting:
                setting["mood"] = "Neutral."
            
        # Ensure we have the 'pages' key
        if "pages" not in story_data:
            # If we have 'panels' directly, convert to page-based structure
            if "panels" in story_data:
                panels = story_data.pop("panels")
                story_data["pages"] = []
                
                # Distribute panels across pages
                for i in range(num_pages):
                    start_idx = i * panels_per_page
                    end_idx = start_idx + panels_per_page
                    page_panels = panels[start_idx:end_idx] if start_idx < len(panels) else []
                    
                    # Fill with placeholder panels if needed
                    while len(page_panels) < panels_per_page:
                        panel_num = len(page_panels) + 1 + (i * panels_per_page)
                        page_panels.append({
                            "panel_number": panel_num,
                            "title": f"Panel {panel_num}",
                            "visual_description": "A placeholder panel",
                            "text": "",
                            "purpose": "Continuation of the story",
                            "symbolism": ""
                        })
                    
                    story_data["pages"].append({
                        "page_number": i + 1,
                        "panels": page_panels
                    })
            else:
                # Create a completely new structure
                story_data["pages"] = []
                for i in range(num_pages):
                    page_panels = []
                    for j in range(panels_per_page):
                        panel_num = j + 1 + (i * panels_per_page)
                        page_panels.append({
                            "panel_number": panel_num,
                            "title": f"Panel {panel_num}",
                            "visual_description": "A placeholder panel",
                            "text": "",
                            "purpose": "Continuation of the story",
                            "symbolism": ""
                        })
                    
                    story_data["pages"].append({
                        "page_number": i + 1,
                        "panels": page_panels
                    })
        
        # Check for continuity between pages and enhance transitions
        for i in range(len(story_data["pages"]) - 1):
            current_page = story_data["pages"][i]
            next_page = story_data["pages"][i + 1]
            
            # Get the last panel of current page and first panel of next page
            if "panels" in current_page and "panels" in next_page and current_page["panels"] and next_page["panels"]:
                last_panel = current_page["panels"][-1]
                first_panel = next_page["panels"][0]
                
                # Extract key details from the last panel
                last_panel_desc = last_panel.get("visual_description", "")
                last_panel_action = last_panel.get("text", "")
                
                # Add a detailed continuity note
                continuity_note = f"Continues directly from page {current_page.get('page_number', i+1)}, panel {last_panel.get('panel_number', len(current_page['panels']))}: {last_panel_desc[:100]}..."
                
                # Update the first panel with continuity info
                first_panel["continuity_note"] = continuity_note
                
                # If the first panel's description doesn't seem to continue the story,
                # enhance it with a reminder to maintain story progression
                if "visual_description" in first_panel:
                    if not first_panel["visual_description"].startswith("CONTINUING DIRECTLY"):
                        first_panel["visual_description"] = "CONTINUING DIRECTLY from previous page: " + first_panel["visual_description"]
        
        # Ensure each page has the correct number of panels
        for i, page in enumerate(story_data["pages"]):
            # Make sure we have the page_number field
            if "page_number" not in page:
                page["page_number"] = i + 1
                
            # Make sure we have a panels list
            if "panels" not in page:
                page["panels"] = []
                
            # Fill or trim panels as needed
            if len(page["panels"]) > panels_per_page:
                page["panels"] = page["panels"][:panels_per_page]
            
            while len(page["panels"]) < panels_per_page:
                panel_num = len(page["panels"]) + 1 + (i * panels_per_page)
                
                # Get context from previous panel if available
                context_desc = ""
                if page["panels"]:
                    prev_panel = page["panels"][-1]
                    prev_desc = prev_panel.get("visual_description", "")
                    context_desc = f"Continuing from previous panel: {prev_desc[:50]}... "
                
                page["panels"].append({
                    "panel_number": panel_num,
                    "title": f"Panel {panel_num}",
                    "visual_description": f"{context_desc}A scene related to the story, moving the narrative forward.",
                    "text": "",
                    "purpose": "Continuation of the story progression",
                    "symbolism": ""
                })
            
            # Make sure each panel has all required fields
            for j, panel in enumerate(page["panels"]):
                panel_num = j + 1 + (i * panels_per_page)
                
                if "panel_number" not in panel:
                    panel["panel_number"] = panel_num
                
                if "title" not in panel or not panel["title"]:
                    panel["title"] = f"Panel {panel_num}"
                
                if "visual_description" not in panel or not panel["visual_description"]:
                    # Get context from previous panel if available
                    context_desc = ""
                    if j > 0:
                        prev_panel = page["panels"][j-1]
                        prev_desc = prev_panel.get("visual_description", "")
                        context_desc = f"Following from previous panel: {prev_desc[:50]}... "
                    
                    panel["visual_description"] = f"{context_desc}A scene that advances the story narrative."
                
                if "text" not in panel:
                    panel["text"] = ""
                
                if "purpose" not in panel:
                    panel["purpose"] = "Advancing the story progression"
                
                if "symbolism" not in panel:
                    panel["symbolism"] = ""
        
        # Add missing pages if needed
        while len(story_data["pages"]) < num_pages:
            page_num = len(story_data["pages"]) + 1
            page_panels = []
            
            # Get context from the last panel of the previous page if available
            context_from_prev_page = ""
            if story_data["pages"]:
                prev_page = story_data["pages"][-1]
                if prev_page.get("panels"):
                    last_panel = prev_page["panels"][-1]
                    last_desc = last_panel.get("visual_description", "")
                    context_from_prev_page = f"Continuing directly from the previous page: {last_desc[:100]}... "
            
            for j in range(panels_per_page):
                panel_num = j + 1 + ((page_num - 1) * panels_per_page)
                
                # First panel of the page gets continuity context from previous page
                panel_desc = "A scene that advances the story narrative."
                if j == 0 and context_from_prev_page:
                    panel_desc = context_from_prev_page + panel_desc
                # Other panels get context from the previous panel in the same page
                elif j > 0 and page_panels:
                    prev_panel = page_panels[j-1]
                    prev_desc = prev_panel.get("visual_description", "")
                    panel_desc = f"Following from previous panel: {prev_desc[:50]}... " + panel_desc
                
                page_panels.append({
                    "panel_number": panel_num,
                    "title": f"Panel {panel_num}",
                    "visual_description": panel_desc,
                    "text": "",
                    "purpose": "Advancing the story progression",
                    "symbolism": ""
                })
            
            story_data["pages"].append({
                "page_number": page_num,
                "panels": page_panels
            })
            
        return story_data

    def _create_fallback_story(self, user_description, panels_per_page, num_pages):
        """Create a basic fallback story structure if generation fails."""
        pages = []
        
        for i in range(num_pages):
            page_panels = []
            for j in range(panels_per_page):
                panel_num = j + 1 + (i * panels_per_page)
                page_panels.append({
                    "panel_number": panel_num,
                    "title": f"Panel {panel_num}",
                    "visual_description": f"A scene related to {user_description[:30]}...",
                    "text": f"Text for panel {panel_num}",
                    "purpose": f"Part of the story progression",
                    "symbolism": ""
                })
            
            pages.append({
                "page_number": i + 1,
                "panels": page_panels
            })
        
        return {
            "title": f"A Story About {user_description[:30]}...",
            "premise": f"A comic story about {user_description[:50]}...",
            "pages": pages
        }

    def _fix_json(self, json_str):
        """Attempt to fix common JSON issues from LLM responses."""
        # Remove comments (both // and /* */)
        json_str = re.sub(r'//.*?', '', json_str)
        json_str = re.sub(r'/\*[\s\S]*?\*/', '', json_str, flags=re.DOTALL)

        # Attempt to fix missing quotes around keys
        json_str = re.sub(r'([{, ]\s*)([a-zA-Z_][a-zA-Z0-9_]*)(\s*:)', r'\1"\2"\3', json_str)

        # Remove trailing commas before closing braces/brackets
        json_str = re.sub(r',(\s*[}\\]])', r'\1', json_str)
        return json_str

    def generate_panel_image_prompt(self, panel_data, style=None):
        """Generate a prompt for image generation from panel data."""
        style_text = f" in {style} style" if style else ""
        
        prompt = f"Create a comic book panel{style_text} showing: {panel_data['visual_description']}. "
        if 'text' in panel_data and panel_data['text']:
            prompt += f"The panel includes the dialogue: '{panel_data['text']}'. "
        return prompt 