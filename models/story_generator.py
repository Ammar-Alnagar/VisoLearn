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

        enhancement_prompt = f"""
        ROLE: You are a master visual storytelling specialist.
        TASK: Transform the following simple story concept into a more detailed, visually-rich narrative suitable for a comic.
        Expand on the core idea, adding interesting characters, a vivid setting, and a clear plot progression.

        ORIGINAL STORY CONCEPT:
        "{user_description}"

        OUTPUT:
        Provide an enhanced, single-paragraph story description that is much more detailed and ready for storyboarding.
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

                        # The 'description' for the comic generator should be the combination of scene descriptions.
                        # This gives the image model the full narrative context.
                        comic_description = " ".join([scene.get('panel_description', '') for scene in story_json.get("scenes", [])])

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
        return f"""Generate a {num_scenes}-panel comic story from this idea: "{user_prompt}"

OUTPUT: JSON only, no additional text.

FORMAT:
{{
  "title": "Story title",
  "description": "One-sentence summary",
  "num_scenes": {num_scenes},
  "characters": [
    {{
      "name": "Character Name",
      "visual_description": "Detailed visual description for consistent illustration"
    }}
  ],
  "settings": [
    {{
      "name": "Setting Name",
      "description": "Detailed environment description"
    }}
  ],
  "scenes": [
    {{
      "scene_number": 1,
      "panel_description": "Vivid description of this panel's action, character poses, expressions, and background"
    }}
  ]
}}

REQUIREMENTS:
1. Exactly {num_scenes} scenes with clear story progression
2. No filler - every panel advances the plot
3. Rich visual details for each scene
4. Connected, logical action flow
5. Clear beginning, middle, end structure"""

    def _extract_json_from_response(self, text):
        """
        Extracts a JSON object from the model's response text, accommodating markdown code blocks
        and attempting to fix common syntax errors like missing commas.
        """
        # First, try to find JSON within ```json ... ```
        match = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
        if match:
            json_str = match.group(1)
        else:
            # If not found, assume the whole text is a JSON object or it's embedded.
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                print("❌ Could not find any JSON in the response text.")
                return None

        # Attempt to fix common LLM JSON errors
        # 1. Fix missing commas between objects in arrays: {...} {...} -> {...}, {...}
        json_str = re.sub(r'\}\s*\{', '}, {', json_str)
        # 2. Fix trailing commas in objects or arrays: ,} -> } or ,] -> ]
        json_str = re.sub(r',\s*(\]|\})', r'\1', json_str)

        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"❌ JSON Decode Error even after attempting to fix: {e}")
            print(f"📄 Problematic JSON string snippet: '{json_str[:500]}...'")
            return None
