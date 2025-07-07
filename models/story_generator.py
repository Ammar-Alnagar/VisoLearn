from google.generativeai.generative_models import GenerativeModel
import json
import re

class StoryGenerator:
    """
    Generates a story from a user prompt using a Gemini model.
    """

    def __init__(self):
        self.model = GenerativeModel('gemini-2.5-flash')

    def _truncate_prompt_by_tokens(self, prompt, max_tokens=4096):
        """
        Truncates the prompt to be within the specified token limit (default 4096 tokens).
        This is a simple implementation that truncates text. It may cut words.
        """
        # A common approximation is ~3 chars/token as a safe floor.
        char_limit = max_tokens * 3
        if len(prompt) > char_limit:
            print(f"⚠️ User prompt is too long ({len(prompt)} chars). Truncating to {char_limit} chars to stay within token limit.")
            return prompt[:char_limit]
        return prompt

    def is_prompt_sufficient(self, user_prompt):
        """
        Uses Gemini to determine if a user's prompt is detailed enough.
        """
        print("🔎 Assessing prompt sufficiency...")
        assessment_prompt = f"""
        Analyze the following user prompt for a comic story. Is it sufficiently detailed to create a compelling, multi-panel story?
        A sufficient prompt should provide a clear idea of characters, setting, or plot. It should be more than just a few generic words.

        User Prompt: "{user_prompt}"

        Respond with only "true" if the prompt is sufficient or "false" if it is too generic or simple.
        """
        try:
            response = self.model.generate_content(assessment_prompt)
            decision = response.text.strip().lower()
            print(f"✅ Prompt sufficiency assessment: {decision}")
            return decision == "true"
        except Exception as e:
            print(f"⚠️ Prompt assessment failed: {e}. Assuming enhancement is needed.")
            return False # Default to enhancing if the check fails

    def enhance_user_story(self, user_description):
        """
        Enhance the user's story with more vibrancy, detail, and narrative richness.
        """
        print(f"✨ Enhancing user story: {user_description[:100]}...")

        # Updated prompt: keep the story enhancement focused on plot and momentum, with minimal scenic padding.
        enhancement_prompt = f"""
        ROLE: Expert comic writer.

        TASK: Rewrite the following concept into a punchy, engaging comic-story setup that jumps straight into the plot.

        GUIDELINES:
        1. Focus on characters, conflict, and goal within the first sentence.
        2. Keep scenic or environmental detail to a minimum—only what is essential for the reader to understand the context.
        3. The entire result must fit in ONE short paragraph (≈ 120 words max).
        4. If the concept features a child/minor character, seamlessly age them up to an adult version (e.g., "child" → "young adult").
        5. Use active voice and clear, concise language.

        ORIGINAL CONCEPT:
        "{user_description}"

        OUTPUT:
        A single, streamlined paragraph suitable for immediate storyboarding.
        """
        try:
            response = self.model.generate_content(enhancement_prompt)
            enhanced_story = response.text.strip()
            print("✅ Story successfully enhanced.")
            return enhanced_story
        except Exception as e:
            print(f"⚠️ Story enhancement failed: {e}. Using original prompt.")
            return user_description

    def generate_story_from_prompt(self, user_prompt, num_scenes=16):
        """
        Takes a user prompt and generates a story structure for a comic.
        It will first check if the prompt is sufficient, and if not, enhance it.

        Args:
            user_prompt (str): The user's initial idea for the story.
            num_scenes (int): The number of scenes the story should have.

        Returns:
            dict: A dictionary containing the story structure (title, description, characters, settings, scenes)
                  or None if generation fails.
        """
        # The user's raw prompt is what needs to be checked for token length.
        truncated_user_prompt = self._truncate_prompt_by_tokens(user_prompt)

        authoritative_prompt = self._create_story_generation_prompt(truncated_user_prompt, num_scenes)

        try:
            print("🧠 Generating story from user prompt with Gemini...")
            response = self.model.generate_content(authoritative_prompt)
            story_json = self._extract_json_from_response(response.text)

            if story_json:
                # Basic validation of the returned structure
                if all(k in story_json for k in ["title", "description", "characters", "settings", "scenes"]):
                    if isinstance(story_json.get("scenes"), list) and len(story_json.get("scenes")) > 0:
                        print("✅ Story generated and parsed successfully.")

                        # Enumerate panel descriptions to give the image model explicit scene anchors
                        comic_description = " ".join([
                            f"Panel {idx+1}: {scene.get('panel_description', '')}." for idx, scene in enumerate(story_json.get('scenes', []))
                        ])

                        # Sanitize any references to children/minors to avoid image policy violations
                        comic_description = self._replace_child_terms(comic_description)
                        story_json["description"] = self._replace_child_terms(story_json.get("description", ""))
                        for scene in story_json.get("scenes", []):
                            if "panel_description" in scene:
                                scene["panel_description"] = self._replace_child_terms(scene["panel_description"])
                        for char in story_json.get("characters", []):
                            if "visual_description" in char:
                                char["visual_description"] = self._replace_child_terms(char["visual_description"])
                        for setting in story_json.get("settings", []):
                            if "description" in setting:
                                setting["description"] = self._replace_child_terms(setting["description"])

                        story_data = {
                            "title": story_json.get("title", "Untitled"),
                            "overall_description": story_json.get("description", ""), # The one-sentence summary
                            "comic_description": comic_description, # The full narrative for image gen
                            "characters": story_json.get("characters", []),
                            "settings": story_json.get("settings", []),
                            "num_scenes": len(story_json.get("scenes", [])),
                            "scenes": story_json.get("scenes", []) # Keep original scenes for other uses
                        }
                        return story_data
                    else:
                         print("❌ Parsed JSON is missing scenes or the scenes list is empty.")
                         return None

            print(f"❌ Failed to parse a valid story from model response. Response: {response.text}")
            return None

        except Exception as e:
            print(f"❌ Story generation failed: {e}")
            return None

    def _create_story_generation_prompt(self, user_prompt, num_scenes):
        """
        Creates a streamlined and efficient prompt for story generation.
        """
        return f"""Generate a concise {num_scenes}-panel comic story from this idea: "{user_prompt}"

CRITICAL OUTPUT FORMAT:
- Start your response with ```json
- End your response with ```
- NO text before the ```json line
- NO text after the ``` line
- NO explanations, reasoning, or comments
- ONLY the JSON object inside the code block

EXACT JSON STRUCTURE (copy this format exactly):
```json
{{
  "title": "Story title here",
  "description": "One-sentence summary of the plot",
  "num_scenes": {num_scenes},
  "characters": [
    {{"name": "Character Name", "visual_description": "Key visual traits in 20 words or less"}}
  ],
  "settings": [
    {{"name": "Setting Name", "description": "Essential context only in 20 words or less"}}
  ],
  "scenes": [
    {{"scene_number": 1, "panel_description": "Action-focused description in 40 words or less"}}
  ]
}}
```

STRICT REQUIREMENTS:
1. Valid JSON syntax - no trailing commas, no comments, proper quotes
2. Each scene must have scene_number and panel_description
3. Replace any child/minor references with adult equivalents
4. Keep descriptions concise within word limits
5. Logical story flow from beginning to end
6. ASCII characters only - no special symbols or unicode

RESPONSE FORMAT EXAMPLE:
```json
{{"title": "The Magic Test", "description": "A young wizard learns a difficult spell.", "num_scenes": 4, "characters": [{{"name": "Alex", "visual_description": "Determined young adult wizard with messy brown hair and focused eyes"}}], "settings": [{{"name": "Magic Academy", "description": "Stone classroom with floating books and glowing crystals"}}], "scenes": [{{"scene_number": 1, "panel_description": "Alex opens an ancient spellbook in a candlelit study room"}}]}}
```

Remember: ONLY return the JSON in the specified format. No additional text."""

    def _extract_json_from_response(self, text):
        """
        Extracts a JSON object from the model's response text, accommodating markdown code blocks
        and attempting to fix common syntax errors like missing commas.
        """
        # Clean up the text first
        text = text.strip()

        # First, try to find JSON within ```json ... ```
        json_block_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
        if json_block_match:
            # Extract the content within the code block and then use balanced extraction
            block_content = json_block_match.group(1)
            json_str = self._extract_balanced_json(block_content)
            if not json_str:
                # Fallback to using the entire block content if balanced extraction fails
                json_str = block_content.strip()
        else:
            # Look for JSON object with proper brace matching in the entire text
            json_str = self._extract_balanced_json(text)
            if not json_str:
                print("❌ Could not find any valid JSON in the response text.")
                print(f"📄 Response text preview: '{text[:200]}...'")
                return None

        # Clean the JSON string
        json_str = self._clean_json_string(json_str)

        # Attempt to fix common LLM JSON errors
        json_str = self._fix_common_json_errors(json_str)

        try:
            parsed_json = json.loads(json_str)
            # Validate the JSON structure
            if self._validate_story_json(parsed_json):
                return parsed_json
            else:
                print("❌ JSON structure validation failed")
                return None
        except json.JSONDecodeError as e:
            print(f"❌ JSON Decode Error even after attempting to fix: {e}")
            print(f"📄 Problematic JSON string snippet: '{json_str[:500]}...'")

            # Check if the JSON might be double-escaped
            if '\\' in json_str and any(pattern in json_str for pattern in ['\\"', '\\n', '\\t']):
                print("🔍 Detected possible double-escaped JSON, attempting to unescape...")
                try:
                    # Try to decode as a string first (removes one layer of escaping)
                    unescaped = json_str.encode().decode('unicode_escape')
                    # Clean and parse the unescaped JSON
                    unescaped = self._clean_json_string(unescaped)
                    unescaped = self._fix_common_json_errors(unescaped)
                    parsed_json = json.loads(unescaped)
                    if self._validate_story_json(parsed_json):
                        print("✅ Successfully parsed double-escaped JSON")
                        return parsed_json
                except Exception as inner_e:
                    print(f"❌ Failed to parse double-escaped JSON: {inner_e}")

            # Try one more time with aggressive cleanup
            return self._fallback_json_extraction(text)

    def _extract_balanced_json(self, text):
        """Extract JSON with proper brace matching to avoid capturing extra content."""
        # Find the first opening brace
        start_idx = text.find('{')
        if start_idx == -1:
            return None

        # Count braces to find the matching closing brace
        brace_count = 0
        end_idx = start_idx
        in_string = False
        escaped = False

        for i in range(start_idx, len(text)):
            char = text[i]

            if escaped:
                escaped = False
                continue

            if char == '\\' and in_string:
                escaped = True
                continue

            if char == '"' and not escaped:
                in_string = not in_string
                continue

            if not in_string:
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end_idx = i
                        break

        if brace_count == 0:
            return text[start_idx:end_idx + 1]
        return None

    def _clean_json_string(self, json_str):
        """Clean up the JSON string by removing unwanted characters and formatting."""
        # Remove any non-ASCII characters that may have been inserted
        json_str = json_str.encode('ascii', 'ignore').decode()

        # Remove any comments or explanatory text within the JSON
        json_str = re.sub(r'//.*?(?=\n|$)', '', json_str, flags=re.MULTILINE)
        json_str = re.sub(r'/\*.*?\*/', '', json_str, flags=re.DOTALL)

        # Remove any reasoning text that might have been mixed in
        json_str = re.sub(r'reasoning[^:]*:', '', json_str, flags=re.IGNORECASE)

        return json_str.strip()

    def _fix_common_json_errors(self, json_str):
        """Fix common JSON formatting errors from LLM responses."""
        # First, check if the JSON has escaped quotes in property names (e.g., \"title" instead of "title")
        # This happens when the JSON is double-escaped
        if '\\"' in json_str:
            # Count different quote patterns to detect double-escaping
            escaped_quotes = json_str.count('\\"')
            regular_quotes = json_str.count('"') - escaped_quotes

            # If we have more escaped quotes than regular quotes, it's likely double-escaped
            if escaped_quotes > regular_quotes:
                print(f"🔧 Fixing double-escaped JSON (escaped: {escaped_quotes}, regular: {regular_quotes})")
                # Replace escaped quotes with regular quotes
                json_str = json_str.replace('\\"', '"')
                # Fix any double backslashes
                json_str = json_str.replace('\\\\', '\\')
                # Remove any remaining single backslashes before quotes
                json_str = re.sub(r'\\(?=")', '', json_str)

        # Fix missing commas between objects in arrays: {...} {...} -> {...}, {...}
        json_str = re.sub(r'\}\s*\{', '}, {', json_str)

        # Fix trailing commas in objects or arrays: ,} -> } or ,] -> ]
        json_str = re.sub(r',\s*(\]|\})', r'\1', json_str)

        # Fix missing commas in arrays and objects
        json_str = re.sub(r'"\s*\n\s*"', '",\n"', json_str)
        json_str = re.sub(r'}\s*\n\s*{', '},\n{', json_str)

        # Fix unescaped quotes in strings (but be careful not to break already escaped ones)
        # Only apply this if we didn't already fix escaped quotes above
        if '\\"' not in json_str:
            json_str = re.sub(r'(?<!\\)"(?![,\]\}:\s])', '\\"', json_str)

        return json_str

    def _validate_story_json(self, json_obj):
        """Validate that the JSON has the required structure for a story."""
        required_fields = ['title', 'description', 'num_scenes', 'scenes']

        for field in required_fields:
            if field not in json_obj:
                print(f"❌ Missing required field: {field}")
                return False

        # Validate scenes array
        scenes = json_obj.get('scenes', [])
        if not isinstance(scenes, list) or len(scenes) == 0:
            print("❌ Scenes must be a non-empty array")
            return False

        # Validate each scene has required fields
        for i, scene in enumerate(scenes):
            if not isinstance(scene, dict):
                print(f"❌ Scene {i} must be an object")
                return False
            if 'panel_description' not in scene:
                print(f"❌ Scene {i} missing panel_description")
                return False

        return True

    def _fallback_json_extraction(self, text):
        """Last resort JSON extraction with very aggressive cleanup."""
        try:
            # Remove everything before the first {
            start_idx = text.find('{')
            if start_idx == -1:
                return None

            # Remove everything after the last }
            end_idx = text.rfind('}')
            if end_idx == -1:
                return None

            json_str = text[start_idx:end_idx + 1]

            # Very aggressive cleanup
            json_str = re.sub(r'[^\x00-\x7F]+', '', json_str)  # Remove non-ASCII
            json_str = re.sub(r'reasoning.*?(?=[\}\],])', '', json_str, flags=re.IGNORECASE | re.DOTALL)

            return json.loads(json_str)
        except:
            return None

    @staticmethod
    def _replace_child_terms(text):
        """Replace child-related words with adult equivalents to satisfy image policy."""
        if not text:
            return text
        replacements = {
            r"\bchild\b": "adult",
            r"\bchildren\b": "adults",
            r"\bboy\b": "man",
            r"\bgirl\b": "woman",
            r"\btoddler\b": "young adult",
            r"\bteenager\b": "young adult",
            r"\bteen\b": "young adult",
        }
        for pattern, repl in replacements.items():
            text = re.sub(pattern, repl, text, flags=re.IGNORECASE)
        return text
