from google.generativeai import GenerativeModel
import json
import re
import os
import datetime

class StoryWriterAgent:
    """
    Specialized agent for creating rich, detailed stories with strong visual elements.
    Focuses on creating stories that are optimized for image generation.
    """

    def __init__(self):
        self.model = GenerativeModel('gemini-2.5-flash')

    def log_prompt(self, agent_name, prompt):
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "agent": agent_name,
            "prompt": prompt
        }
        log_path = "story_prompt_logs.jsonl"
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

    def generate_story(self, topic_focus, num_scenes=3, story_style="Movie", user_description=None):
        """
        Generate a rich, detailed story optimized for visual storytelling.
        Returns a tuple: (story_data, prompt)
        """
        print("[StoryWriterAgent] Generating initial story draft...")
        query = f"""
        You are a master storyteller and screenwriter creating an engaging cinematic narrative.
        Design a creative and memorable {story_style.lower()} story about '{topic_focus}'.

        {f"User's story idea: {user_description}" if user_description else ""}

        STORY CREATION GUIDELINES:
        1. USER STORY FOCUS:
           - Maintain the core elements and spirit of the user's story idea
           - Expand on the user's concept while staying true to their vision
           - Ensure all key elements from the user's description are included
           - Develop the user's ideas into a complete narrative
           - Keep the story's essence aligned with the user's input

        2. VISUAL AND NARRATIVE COHERENCE:
           - Create visually striking scenes with clear visual elements
           - Ensure strong visual continuity between consecutive scenes
           - Maintain consistent character appearances across all scenes
           - Keep consistent settings, props, and environments
           - Track visual elements to ensure they persist across scenes
           - Design clear and smooth transitions between scenes
           - Ensure each scene visually flows into the next
           - Avoid sudden unexplained changes in location, time or setting
           - Create logical progression of visual elements
           - Use recurring visual motifs to tie scenes together
           - Ensure lighting, color palettes, and mood are consistent unless there's a narrative reason for change
           - Characters should look the same across scenes (clothing, features, etc.)
           - Maintain consistent scale and perspective

        3. SCENE CONSISTENCY:
           - Characters must persist across scenes with consistent appearance
           - Objects introduced in one scene should reappear in subsequent scenes if relevant
           - Backgrounds and settings should be consistent
           - Weather and time of day should progress naturally
           - Character positioning should be logical between scenes
           - Maintain continuity of character possessions and clothing
           - Any changes to setting or character appearance must be explicitly explained
           - Track all visual elements to ensure nothing disappears unexpectedly
           - Ensure consistent physics and world rules

        4. SCENE-BY-SCENE STRUCTURE:
           - Each scene must be a clear, distinct unit with a specific purpose
           - Clearly describe transitions between scenes (e.g., "They walk into the forest," or "Night begins to fall")
           - Ensure each scene is mappable to a single image frame
           - Make scene boundaries clear and explicit
           - Create natural progression between scenes
           - Explain character movement between locations
           - Explicitly state passage of time between scenes
           - Describe how settings change between scenes
           - Each scene should have a clear beginning and end

        5. DESCRIPTIVE BUT CONCISE:
           - Include enough visual detail for image generation
           - Focus on visually important elements
           - Avoid irrelevant details that don't affect what's seen
           - Prioritize descriptions of characters, actions, settings, and mood
           - Be specific about visual elements (colors, lighting, positioning)
           - Include sensory details that can be visually represented
           - Omit unnecessary backstory or internal thoughts that can't be visualized
           - Describe expressions, body language, and visual emotions

        6. NARRATIVE STRUCTURE:
           - Strong opening that hooks the audience
           - Clear and engaging conflict
           - Satisfying resolution
           - Natural progression between scenes
           - Logical cause-and-effect relationships
           - Cinematic pacing and rhythm
           - Each scene must directly lead to the next
           - Clear plot points that drive the story forward
           - Consistent internal logic throughout
           - No plot holes or illogical jumps
           - Clear stakes and consequences

        7. CHARACTER DEVELOPMENT:
           - Main character with clear goals and personality
           - Supporting characters that add depth
           - Natural character growth and learning
           - Emotional journey that resonates
           - Clear motivations and reactions
           - Memorable character moments
           - Character decisions must make sense in context
           - Consistent character behavior
           - Clear character goals that drive the plot
           - Logical character reactions to events

        Create a story with exactly {num_scenes} scenes that:
        1. Maintains perfect visual continuity between scenes
        2. Has strong visual and narrative coherence
        3. Keeps characters and settings consistent
        4. Has clear, explicit transitions between scenes
        5. Includes appropriate visual detail for image generation
        6. Features clear character development
        7. Fits the {story_style} style perfectly
        8. Has satisfying emotional arcs
        9. Avoids any sudden unexplained changes

        FORMAT YOUR RESPONSE AS A VALID JSON OBJECT with these fields:
        {{
          "title": "Creative and engaging title",
          "premise": "Brief but compelling story overview",
          "story_style": "{story_style}",
          "num_scenes": {num_scenes},
          "main_character": {{
            "name": "Memorable character name",
            "description": "Vivid character description including appearance details",
            "motivation": "Clear character motivation",
            "arc": "Engaging character growth arc",
            "goals": ["Clear character goals"],
            "conflicts": ["Internal and external conflicts"],
            "growth_points": ["Key moments of character development"],
            "visual_traits": ["Distinctive visual features that remain consistent"]
          }},
          "supporting_characters": [
            {{
              "name": "Supporting character name",
              "description": "Visual description with identifying features",
              "relationship": "Relationship to main character",
              "visual_traits": ["Distinctive visual features that remain consistent"]
            }}
          ],
          "timeline": {{
            "total_duration": "Story time span",
            "time_progression": "Natural time progression",
            "key_time_markers": ["Key moments"],
            "seasonal_context": "Seasonal setting",
            "logical_sequence": ["Chronological sequence of events"]
          }},
          "setting": {{
            "primary_location": "Main story location",
            "recurring_elements": ["Visual elements that appear across multiple scenes"],
            "visual_motifs": ["Visual themes that connect scenes"]
          }},
          "plot_structure": {{
            "setup": "Initial situation and conflict",
            "inciting_incident": "Event that starts the story",
            "rising_action": "Key events that build tension",
            "climax": "Major turning point",
            "resolution": "How the story concludes"
          }},
          "scenes": [
            {{
              "scene_number": 1,
              "title": "Creative scene title",
              "description": "Vivid scene description with clear visual details",
              "purpose": "Clear purpose of this scene",
              "key_elements": ["Important elements that must be visualized"],
              "characters_present": ["All characters in this scene"],
              "setting": "Specific location description",
              "explicit_transition": "Clear transition to the next scene (how characters move to next location)",
              "causal_connection": "How this scene connects to previous and next scenes",
              "time_of_day": "Specific time (morning, afternoon, evening, night)",
              "time_elapsed": "Time passed since previous scene",
              "time_indicators": ["Visual time cues"],
              "weather": "Weather conditions if relevant",
              "emotional_state": "Characters' emotional states",
              "character_positioning": "Where characters are in the scene",
              "character_actions": "What characters are doing",
              "important_objects": ["Objects that should appear and persist in future scenes"],
              "visual_focus": "Main visual element that draws attention",
              "lighting": "Scene lighting description",
              "color_palette": ["Main colors that should be used"],
              "visual_continuity": "Specific elements that continue from previous scene",
              "visual_setup": "Elements being set up for future scenes",
              "persistent_elements": ["Elements that must appear in subsequent scenes"]
            }}
          ]
        }}
        """
        self.log_prompt("StoryWriterAgent", query)
        response = self.model.generate_content(query)
        print("[StoryWriterAgent] Story generation prompt used:\n" + query)
        try:
            json_match = re.search(r'\{[\s\S]*\}', response.text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0)), query
            else:
                raise ValueError("No valid JSON found in response")
        except Exception as e:
            print(f"Error in StoryWriterAgent: {e}")
            return self._create_fallback_story(topic_focus, num_scenes), query

    def _create_fallback_story(self, topic_focus, num_scenes):
        """Create a basic fallback story structure if generation fails."""
        return {
            "title": f"A Story About {topic_focus}",
            "premise": f"A simple story about {topic_focus}",
            "story_style": "Movie",
            "num_scenes": num_scenes,
            "main_character": {
                "name": "Main Character",
                "description": "Character description with consistent visual features",
                "motivation": "Character motivation",
                "arc": "Character growth arc",
                "visual_traits": ["Consistent visual features"]
            },
            "supporting_characters": [
                {
                    "name": "Supporting Character",
                    "description": "Visual description with identifying features",
                    "relationship": "Relationship to main character",
                    "visual_traits": ["Distinctive visual features"]
                }
            ],
            "timeline": {
                "total_duration": "One day",
                "time_progression": "Morning to evening",
                "key_time_markers": ["Morning", "Afternoon", "Evening"],
                "seasonal_context": "Current season"
            },
            "setting": {
                "primary_location": "Main story location",
                "recurring_elements": ["Elements appearing in multiple scenes"],
                "visual_motifs": ["Visual themes connecting scenes"]
            },
            "scenes": [{"scene_number": i+1,
                       "title": f"Scene {i+1}",
                       "description": f"Scene {i+1} of the story with clear visual elements",
                       "key_elements": ["character", "setting", "action"],
                       "characters_present": ["Main Character", "Supporting Character"],
                       "setting": "Specific location description",
                       "explicit_transition": f"Clear transition to scene {i+2 if i+2 <= num_scenes else 'end'}",
                       "time_of_day": ["Morning", "Afternoon", "Evening"][min(i, 2)],
                       "time_elapsed": f"{i} hours since story began",
                       "weather": "Clear day",
                       "emotional_state": "Neutral to positive",
                       "character_positioning": "Center of scene",
                       "character_actions": "Engaging with environment",
                       "important_objects": ["Key object that persists"],
                       "visual_focus": "Main character",
                       "lighting": "Natural daylight",
                       "color_palette": ["Natural colors"],
                       "visual_continuity": "Consistent with previous scene",
                       "persistent_elements": ["Elements appearing in next scene"]} for i in range(num_scenes)]
        }

class StoryReviewerAgent:
    """
    Specialized agent for critically analyzing stories and providing detailed feedback.
    Focuses on visual consistency, narrative flow, and character development.
    """

    def __init__(self):
        self.model = GenerativeModel('gemini-2.5-flash')

    def log_prompt(self, agent_name, prompt):
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "agent": agent_name,
            "prompt": prompt
        }
        log_path = "story_prompt_logs.jsonl"
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

    def review_story(self, story_data, user_description=None):
        """
        Review the story and provide detailed feedback.

        Args:
            story_data: The story data to review
            user_description: Optional user-provided story description

        Returns:
            Detailed review with specific feedback and suggestions
        """
        print("[StoryReviewerAgent] Reviewing story for visual and logical consistency...")
        query = f"""
        You are a professional story editor reviewing a story for visual consistency and narrative quality.

        STORY TO REVIEW:
        {json.dumps(story_data, indent=2)}

        {f"USER'S ORIGINAL STORY IDEA: {user_description}" if user_description else ""}

        REVIEW THE STORY FOR:
        1. USER STORY ALIGNMENT:
           - Does the story maintain the user's original concept?
           - Are all key elements from the user's story included?
           - Is the story's tone and style consistent with the user's vision?
           - Are the main themes and messages preserved?
           - Does the story expand on the user's ideas effectively?

        2. VISUAL CONSISTENCY AND COHERENCE:
           - Are visual elements consistently maintained across all scenes?
           - Do characters maintain consistent appearance throughout (clothing, features, etc.)?
           - Is character positioning logical from one scene to the next?
           - Are objects that appear in early scenes properly tracked in later scenes?
           - Does each scene visually flow naturally into the next?
           - Are transitions between scenes explicit and clear?
           - Do lighting and color choices remain consistent unless there's a narrative reason for change?
           - Are settings and backgrounds maintained consistently?
           - Do visual elements support the story's progression?
           - Is there clear visual continuity between consecutive scenes?
           - Are any visual elements suddenly introduced or disappearing without explanation?
           - Is weather and time of day progression logical?
           - Do recurring visual motifs connect scenes effectively?

        3. SCENE-TO-SCENE TRANSITIONS:
           - Is each transition between scenes clearly described?
           - Is character movement between locations explained?
           - Is the passage of time between scenes explicitly stated?
           - Are changes in setting properly described?
           - Do scenes have clear boundaries with distinct beginnings and ends?
           - Are scene transitions logical and smooth?
           - Is there clear cause-and-effect between scenes?
           - Does the timeline progression make sense?

        4. DESCRIPTIVE QUALITY:
           - Does each scene include sufficient visual detail for image generation?
           - Is the focus maintained on visually important elements?
           - Are irrelevant details that can't be visualized avoided?
           - Are character actions, expressions, and body language clearly described?
           - Is the level of detail appropriate - not too sparse, not too verbose?
           - Are sensory details included that can be visually represented?
           - Is unnecessary backstory or internal thoughts that can't be visualized omitted?

        5. NARRATIVE STRUCTURE:
           - Is the story cohesive and well-structured?
           - Are cause-and-effect relationships clear?
           - Does the story have a satisfying arc?
           - Are there any plot holes or logical inconsistencies?
           - Does each scene serve a clear purpose?
           - Is the story progression natural and believable?
           - Are the stakes and consequences clear?
           - Does the story maintain consistent internal logic?

        6. CHARACTER DEVELOPMENT:
           - Is the main character's arc clear and compelling?
           - Are character motivations consistent?
           - Is character growth shown effectively?
           - Do characters have clear visual identities?
           - Are emotional states visually clear?
           - Do character decisions make sense in context?
           - Are character goals and conflicts clear?
           - Is character behavior consistent?
           - Do characters react logically to events?

        PROVIDE SPECIFIC FEEDBACK AND SUGGESTIONS FOR IMPROVEMENT.
        FORMAT YOUR RESPONSE AS A JSON OBJECT with these fields:
        {{
          "strengths": ["List of what works well"],
          "weaknesses": ["List of areas needing improvement"],
          "suggestions": ["Specific suggestions for improvement"],
          "critical_issues": ["Any major issues that must be fixed"],
          "minor_issues": ["Smaller issues that could be improved"],
          "visual_consistency_issues": ["Specific issues with visual continuity or character/setting consistency"],
          "scene_transition_issues": ["Issues with scene-to-scene transitions"],
          "descriptive_quality_issues": ["Issues with level of visual detail"],
          "logical_consistency_issues": ["Any logical inconsistencies or plot holes"],
          "character_consistency_issues": ["Issues with character behavior or appearance consistency"],
          "user_story_alignment_score": 85,  // 0-100 score
          "visual_consistency_score": 80,    // 0-100 score
          "scene_transition_score": 75,      // 0-100 score
          "descriptive_quality_score": 70,   // 0-100 score
          "narrative_flow_score": 75,        // 0-100 score
          "character_development_score": 90   // 0-100 score
        }}
        """
        self.log_prompt("StoryReviewerAgent", query)
        response = self.model.generate_content(query)
        print("[StoryReviewerAgent] Story reviewed. Scores:", response.text)
        try:
            json_match = re.search(r'\{[\s\S]*\}', response.text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            else:
                raise ValueError("No valid JSON found in response")
        except Exception as e:
            print(f"Error in StoryReviewerAgent: {e}")
            return {
                "strengths": [],
                "weaknesses": [],
                "suggestions": [],
                "critical_issues": [],
                "minor_issues": [],
                "visual_consistency_issues": [],
                "scene_transition_issues": [],
                "descriptive_quality_issues": [],
                "logical_consistency_issues": [],
                "character_consistency_issues": [],
                "user_story_alignment_score": 50,
                "visual_consistency_score": 50,
                "scene_transition_score": 50,
                "descriptive_quality_score": 50,
                "narrative_flow_score": 50,
                "character_development_score": 50
            }

class StoryRefinerAgent:
    """
    Specialized agent for iteratively improving stories based on feedback.
    Focuses on enhancing visual elements and narrative consistency.
    """

    def __init__(self):
        self.model = GenerativeModel('gemini-2.5-flash')

    def log_prompt(self, agent_name, prompt):
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "agent": agent_name,
            "prompt": prompt
        }
        log_path = "story_prompt_logs.jsonl"
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

    def refine_story(self, story_data, review, user_description=None):
        """
        Improve the story based on the review feedback.

        Args:
            story_data: The original story data
            review: The review feedback
            user_description: Optional user-provided story description

        Returns:
            Enhanced story data with improvements
        """
        print("[StoryRefinerAgent] Refining story based on reviewer and analyzer feedback...")
        # Use a simplified JSON structure in the prompt to reduce parsing errors
        query = f"""
        You are a professional story editor tasked with improving a story based on feedback.

        ORIGINAL STORY STRUCTURE:
        Title: {story_data.get('title', '')}
        Premise: {story_data.get('premise', '')}
        Story Style: {story_data.get('story_style', '')}
        Number of Scenes: {story_data.get('num_scenes', 3)}

        FEEDBACK HIGHLIGHTS:
        Strengths: {', '.join(review.get('strengths', [])[:3]) if review.get('strengths') else 'None specified'}
        Critical Issues: {', '.join(review.get('critical_issues', [])[:3]) if review.get('critical_issues') else 'None specified'}
        Visual Consistency Issues: {', '.join(review.get('visual_consistency_issues', [])[:3]) if review.get('visual_consistency_issues') else 'None specified'}
        Scene Transition Issues: {', '.join(review.get('scene_transition_issues', [])[:3]) if review.get('scene_transition_issues') else 'None specified'}

        {f"USER'S ORIGINAL STORY IDEA: {user_description}" if user_description else ""}

        IMPROVE THE STORY BY:
        1. Addressing all critical issues first
        2. Fixing visual continuity problems
        3. Improving scene-to-scene transitions
        4. Enhancing descriptive quality for better visualization
        5. Implementing suggested improvements
        6. Maintaining the story's core strengths
        7. Ensuring alignment with user's original story concept

        FOCUS ON:
        1. Visual Consistency and Coherence:
           - Ensure characters maintain consistent appearance across all scenes
           - Track all objects and ensure they persist across relevant scenes
           - Make sure settings and backgrounds remain consistent
           - Provide logical progression of visual elements
           - Use recurring visual motifs to strengthen scene connections
           - Ensure lighting and color choices remain consistent unless changes are explained
           - Maintain consistent scale and perspective
           - Eliminate any sudden unexplained changes in visuals
           - Fix any issues where visual elements suddenly appear or disappear

        2. Scene-to-Scene Transitions:
           - Create explicit and clear transitions between every scene
           - Clearly describe how characters move between locations
           - State the passage of time between scenes
           - Describe any changes in setting
           - Ensure each scene has clear boundaries with distinct beginnings and ends
           - Make all scene transitions logical and smooth
           - Establish clear cause-and-effect relationships between scenes
           - Create a sensible timeline progression

        3. Descriptive Quality:
           - Include sufficient visual detail for image generation
           - Focus on visually important elements
           - Remove irrelevant details that don't affect what's seen
           - Clearly describe character actions, expressions, and body language
           - Maintain appropriate level of detail - not too sparse, not too verbose
           - Include sensory details that can be visually represented
           - Remove unnecessary backstory or internal thoughts that can't be visualized

        FORMAT YOUR RESPONSE AS A VALID JSON OBJECT with the same structure as the original story.
        Your response must be a valid JSON object with all property names and string values enclosed in double quotes.
        Use the exact same JSON schema as the original story with no additional fields.
        Ensure proper use of commas between array and object items.

        Here's a template for your response (replace with appropriate values):
        {{
          "title": "Story Title",
          "premise": "Brief story overview",
          "story_style": "Style",
          "num_scenes": 3,
          "main_character": {{
            "name": "Character Name",
            "description": "Character description",
            "motivation": "Motivation",
            "arc": "Character arc",
            "visual_traits": ["Trait 1", "Trait 2"]
          }},
          "scenes": [
            {{
              "scene_number": 1,
              "title": "Scene Title",
              "description": "Scene description",
              "key_elements": ["Element 1", "Element 2"],
              "setting": "Scene setting",
              "explicit_transition": "Transition to next scene"
            }}
          ]
        }}
        """
        self.log_prompt("StoryRefinerAgent", query)
        response = self.model.generate_content(query)
        print("[StoryRefinerAgent] Story refined for next iteration.")
        try:
            # First try to parse the response as a complete JSON document
            json_match = re.search(r'\{[\s\S]*\}', response.text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)

                # Clean up the JSON string
                json_str = re.sub(r'[\n\r\t]', ' ', json_str)
                json_str = re.sub(r' +', ' ', json_str)
                json_str = re.sub(r'//.*?(?=\n|$)', '', json_str)
                json_str = re.sub(r'/\*.*?\*/', '', json_str, flags=re.DOTALL)
                json_str = re.sub(r'([{,]\s*)([a-zA-Z0-9_]+)(\s*:)', r'\1"\2"\3', json_str)
                json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)

                # Fix single-quoted strings
                placeholder = "PLACEHOLDER_FOR_QUOTED_STRING"
                quoted_strings = []

                def replace_quoted_string(match):
                    quoted_strings.append(match.group(0))
                    return placeholder

                json_str = re.sub(r'"(?:[^"\\]|\\.)*"', replace_quoted_string, json_str)
                json_str = re.sub(r'\'([^\'\\]|\\.)*\'', lambda m: '"' + m.group(0)[1:-1].replace('"', '\\"') + '"', json_str)

                for quoted_string in quoted_strings:
                    json_str = json_str.replace(placeholder, quoted_string, 1)

                # Remove control characters
                json_str = re.sub(r'[\x00-\x1F\x7F]', '', json_str)

                try:
                    return json.loads(json_str)
                except json.JSONDecodeError as e:
                    print(f"JSON parsing failed: {e}")
                    # Fall back to targeted refinement
                    return self._fallback_refiner(story_data, review, response.text)
            else:
                print("No valid JSON found in response")
                return self._fallback_refiner(story_data, review, response.text)
        except Exception as e:
            print(f"Error in StoryRefinerAgent: {e}")
            return self._fallback_refiner(story_data, review, response.text)

    def _fallback_refiner(self, story_data, review, response_text):
        """
        Fallback method to refine the story when JSON parsing fails.
        Improves specific aspects of the story without requiring full JSON parsing.

        Args:
            story_data: The original story data
            review: The review feedback
            response_text: The text response from the model

        Returns:
            Refined story data
        """
        print("Using fallback refiner to improve story")
        refined_story = story_data.copy()

        try:
            # Extract any useful scene descriptions from the response
            scene_descriptions = re.findall(r'"description"\s*:\s*"([^"]+)"', response_text)
            scene_titles = re.findall(r'"title"\s*:\s*"([^"]+)"', response_text)
            transitions = re.findall(r'"explicit_transition"\s*:\s*"([^"]+)"', response_text)
            settings = re.findall(r'"setting"\s*:\s*"([^"]+)"', response_text)

            # Update scenes with extracted content if available
            if 'scenes' in refined_story and scene_descriptions:
                for i, scene in enumerate(refined_story['scenes']):
                    if i < len(scene_descriptions):
                        scene['description'] = scene_descriptions[i]
                    if i < len(scene_titles) and scene_titles[i]:
                        scene['title'] = scene_titles[i]
                    if i < len(transitions) and transitions[i]:
                        scene['explicit_transition'] = transitions[i]
                    if i < len(settings) and settings[i]:
                        scene['setting'] = settings[i]

            # Apply targeted improvements based on specific review issues
            self._improve_visual_consistency(refined_story, review)
            self._improve_scene_transitions(refined_story, review)
            self._improve_descriptive_quality(refined_story, review)

            return refined_story
        except Exception as e:
            print(f"Error in fallback refiner: {e}")
            return story_data  # Return original if fallback fails

    def _improve_visual_consistency(self, story_data, review):
        """Add visual consistency improvements to the story"""
        if 'visual_consistency_issues' not in review or not review['visual_consistency_issues']:
            return

        # Extract main character traits to ensure consistency
        main_character = story_data.get('main_character', {})
        character_name = main_character.get('name', 'Main Character')
        character_desc = main_character.get('description', '')
        visual_traits = main_character.get('visual_traits', [])

        # Apply these traits consistently across scenes
        for scene in story_data.get('scenes', []):
            if 'description' in scene:
                # Ensure character is described consistently
                if character_name not in scene['description']:
                    scene['description'] = scene['description'].replace(
                        "the main character", character_name
                    ).replace(
                        "The main character", character_name
                    )

                # Add visual trait references if missing
                for trait in visual_traits:
                    if trait and trait not in scene['description'] and len(scene['description'].split()) < 200:
                        scene['description'] += f" {character_name}'s {trait} is visible in this scene."

    def _improve_scene_transitions(self, story_data, review):
        """Add explicit transitions between scenes"""
        if 'scenes' not in story_data or len(story_data['scenes']) <= 1:
            return

        scenes = story_data['scenes']
        for i in range(len(scenes) - 1):
            current_scene = scenes[i]
            next_scene = scenes[i + 1]

            # Add explicit transition if missing
            if 'explicit_transition' not in current_scene or not current_scene['explicit_transition']:
                time_of_day_current = current_scene.get('time_of_day', '')
                time_of_day_next = next_scene.get('time_of_day', '')

                # Create a basic transition based on time or setting changes
                if time_of_day_current != time_of_day_next and time_of_day_next:
                    current_scene['explicit_transition'] = f"As {time_of_day_next.lower()} arrives, the scene shifts to the next location."
                else:
                    current_scene['explicit_transition'] = f"The scene transitions to the next location."

    def _improve_descriptive_quality(self, story_data, review):
        """Enhance descriptive quality of scenes"""
        for scene in story_data.get('scenes', []):
            # Ensure each scene has key visual elements
            if 'key_elements' not in scene or not scene['key_elements']:
                scene['key_elements'] = ["character", "setting", "action"]

            # Add visual focus if missing
            if 'visual_focus' not in scene:
                scene['visual_focus'] = "Main character"

            # Add color palette if missing
            if 'color_palette' not in scene:
                scene['color_palette'] = ["natural colors", "balanced lighting"]

class StoryAnalyzerAgent:
    """
    Specialized agent for analyzing story comprehensiveness and coherence.
    Focuses on ensuring the story is complete, logical, and well-structured.
    """

    def __init__(self):
        self.model = GenerativeModel('gemini-2.5-flash')

    def log_prompt(self, agent_name, prompt):
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "agent": agent_name,
            "prompt": prompt
        }
        log_path = "story_prompt_logs.jsonl"
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

    def analyze_story(self, story_data, user_description=None):
        """
        Analyze the story for comprehensiveness and coherence.

        Args:
            story_data: The story data to analyze
            user_description: Optional user-provided story description

        Returns:
            Analysis results with specific feedback and suggestions
        """
        print("[StoryAnalyzerAgent] Analyzing story for completeness and logical coherence...")
        query = f"""
        You are a professional story analyst reviewing a story for comprehensiveness and coherence.

        STORY TO ANALYZE:
        {json.dumps(story_data, indent=2)}

        {f"USER'S ORIGINAL STORY IDEA: {user_description}" if user_description else ""}

        ANALYZE THE STORY FOR:
        1. STORY COMPLETENESS:
           - Does the story have a clear beginning, middle, and end?
           - Are all plot threads resolved?
           - Is the story's scope appropriate for its length?
           - Are all character arcs completed?
           - Is the story's message or theme fully developed?

        2. LOGICAL COHERENCE:
           - Do all events follow logically from previous events?
           - Are character motivations consistent throughout?
           - Is the world-building consistent?
           - Are there any unexplained events or coincidences?
           - Does the story maintain internal consistency?

        3. EMOTIONAL IMPACT:
           - Does the story create emotional engagement?
           - Are emotional beats properly spaced?
           - Is the emotional journey satisfying?
           - Do character emotions feel authentic?
           - Is there appropriate emotional variety?

        4. THEMATIC DEPTH:
           - Is the story's theme clear and well-developed?
           - Are there multiple layers of meaning?
           - Does the theme resonate throughout the story?
           - Are there supporting sub-themes?
           - Is the theme resolution satisfying?

        5. STRUCTURAL BALANCE:
           - Is the pacing appropriate for the story length?
           - Are scenes properly balanced in length and importance?
           - Is there appropriate variation in scene types?
           - Does the story maintain momentum?
           - Is the climax properly built up to?

        PROVIDE SPECIFIC ANALYSIS AND SUGGESTIONS.
        FORMAT YOUR RESPONSE AS A JSON OBJECT with these fields:
        {{
          "completeness_score": 85,  // 0-100 score
          "coherence_score": 80,     // 0-100 score
          "emotional_impact_score": 75,  // 0-100 score
          "thematic_depth_score": 90,    // 0-100 score
          "structural_balance_score": 80, // 0-100 score
          "completeness_issues": ["List of completeness issues"],
          "coherence_issues": ["List of coherence issues"],
          "emotional_issues": ["List of emotional impact issues"],
          "thematic_issues": ["List of thematic depth issues"],
          "structural_issues": ["List of structural balance issues"],
          "overall_assessment": "Comprehensive assessment of the story",
          "improvement_suggestions": ["Specific suggestions for improvement"]
        }}
        """
        self.log_prompt("StoryAnalyzerAgent", query)
        response = self.model.generate_content(query)
        print("[StoryAnalyzerAgent] Story analyzed. Scores:", response.text)
        try:
            json_match = re.search(r'\{[\s\S]*\}', response.text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            else:
                raise ValueError("No valid JSON found in response")
        except Exception as e:
            print(f"Error in StoryAnalyzerAgent: {e}")
            return {
                "completeness_score": 50,
                "coherence_score": 50,
                "emotional_impact_score": 50,
                "thematic_depth_score": 50,
                "structural_balance_score": 50,
                "completeness_issues": [],
                "coherence_issues": [],
                "emotional_issues": [],
                "thematic_issues": [],
                "structural_issues": [],
                "overall_assessment": "Analysis failed due to technical issues",
                "improvement_suggestions": []
            }

def generate_enhanced_story(topic_focus, num_scenes=None, story_style=None, user_description=None, max_iterations=3):
    """
    Generate a high-quality story using the specialized agents.
    Returns (final_story_data, review, analysis, generation_prompt)
    """
    print("[Pipeline] Starting enhanced story generation pipeline...")
    # Initialize agents
    writer = StoryWriterAgent()
    reviewer = StoryReviewerAgent()
    refiner = StoryRefinerAgent()
    analyzer = StoryAnalyzerAgent()

    # Generate initial story
    story_data, generation_prompt = writer.generate_story(topic_focus, num_scenes, story_style, user_description)
    print("[Pipeline] Initial story draft generated.")

    # Track best story version
    best_story = story_data
    best_score = 0

    # Iterative refinement process
    for iteration in range(max_iterations):
        # Review the story
        review = reviewer.review_story(story_data, user_description)
        print("[Pipeline] Story reviewed. Scores:", review)

        # Analyze the story
        analysis = analyzer.analyze_story(story_data, user_description)
        print("[Pipeline] Story analyzed. Scores:", analysis)

        # First check for critical logical issues that must be addressed
        has_critical_logical_issues = False

        # Check for critical logical issues in the review
        if review.get("critical_issues"):
            for issue in review["critical_issues"]:
                # Check if the issue is related to logic or consistency
                if any(keyword in issue.lower() for keyword in ["logic", "consistent", "continuity", "transition", "sequence"]):
                    has_critical_logical_issues = True
                    break

        # Check for severe coherence issues in the analysis
        if analysis.get("coherence_score", 0) < 75 or analysis.get("completeness_score", 0) < 75:
            has_critical_logical_issues = True

        # Check for scene transition issues that break logic
        if review.get("scene_transition_score", 0) < 70:
            has_critical_logical_issues = True

        # Calculate a weighted overall score that prioritizes logic and cohesion
        # Weights emphasize logical coherence and scene transitions
        weights = {
            "coherence_score": 2.5,               # Highest priority - logical coherence
            "scene_transition_score": 2.0,        # High priority - logical scene flow
            "visual_consistency_score": 2.0,      # High priority - visual continuity
            "narrative_flow_score": 1.5,          # Medium-high priority - story flow
            "completeness_score": 1.5,            # Medium-high priority - story completeness
            "descriptive_quality_score": 1.2,     # Medium priority - appropriate detail level
            "structural_balance_score": 1.2,      # Medium priority - structure
            "character_development_score": 1.0,   # Standard priority
            "emotional_impact_score": 0.8,        # Lower priority for visual stories
            "thematic_depth_score": 0.7,          # Lower priority for visual stories
            "user_story_alignment_score": 1.0     # Standard priority
        }

        # Gather scores from both review and analysis
        all_scores = {
            "coherence_score": analysis.get("coherence_score", 50),
            "completeness_score": analysis.get("completeness_score", 50),
            "emotional_impact_score": analysis.get("emotional_impact_score", 50),
            "thematic_depth_score": analysis.get("thematic_depth_score", 50),
            "structural_balance_score": analysis.get("structural_balance_score", 50),
            "visual_consistency_score": review.get("visual_consistency_score", 50),
            "scene_transition_score": review.get("scene_transition_score", 50),
            "descriptive_quality_score": review.get("descriptive_quality_score", 50),
            "narrative_flow_score": review.get("narrative_flow_score", 50),
            "character_development_score": review.get("character_development_score", 50),
            "user_story_alignment_score": review.get("user_story_alignment_score", 50)
        }

        # Calculate weighted score
        weighted_sum = sum(all_scores[key] * weights[key] for key in weights)
        total_weight = sum(weights.values())
        weighted_score = weighted_sum / total_weight

        print(f"Iteration {iteration+1}: Weighted score = {weighted_score:.2f}")

        # Check if this is the best version so far
        if weighted_score > best_score:
            best_score = weighted_score
            best_story = story_data.copy()
            print(f"[Pipeline] New best story found with weighted score: {weighted_score:.2f}")

        # Comprehensive quality check with priority on logical aspects
        # More lenient thresholds for emotional and thematic aspects
        quality_sufficient = (
            all_scores["coherence_score"] >= 90 and         # Strict: Logical coherence is essential
            all_scores["scene_transition_score"] >= 90 and  # Strict: Scene transitions must be clear
            all_scores["visual_consistency_score"] >= 90 and # Strict: Visual elements must be consistent
            all_scores["narrative_flow_score"] >= 85 and    # Medium-high: Story flow must be strong
            all_scores["completeness_score"] >= 85 and      # Medium-high: Story must be complete
            all_scores["descriptive_quality_score"] >= 85 and # Medium-high: Descriptions must be appropriate
            all_scores["character_development_score"] >= 80 and # Medium: Character development
            all_scores["user_story_alignment_score"] >= 80 and # Medium: Alignment with user's concept
            all_scores["structural_balance_score"] >= 80 and # Medium: Overall structure
            all_scores["emotional_impact_score"] >= 75 and  # Lower: Emotional aspects less critical
            all_scores["thematic_depth_score"] >= 75 and    # Lower: Thematic aspects less critical
            not has_critical_logical_issues and             # No critical logical issues
            weighted_score >= 88                            # High overall weighted score
        )

        # Alternative quality check based on exceptional weighted score
        exceptional_score = weighted_score >= 92 and not has_critical_logical_issues

        # Break if quality is sufficient or we have an exceptional score
        if quality_sufficient or exceptional_score:
            # Use current version if it's exceptional, otherwise use best version
            if exceptional_score:
                best_story = story_data
            print("[Pipeline] Quality thresholds met. Ending refinement.")
            break

        # If we have critical logical issues, always continue refining
        # Otherwise, if we're on the last iteration, use the best story we've found
        if iteration == max_iterations - 1:
            story_data = best_story
            print("[Pipeline] Max iterations reached. Using best story found.")
            break

        # Refine the story for the next iteration
        story_data = refiner.refine_story(story_data, review, user_description)
        print("[Pipeline] Story refined for next iteration.")

        # Check for minimal changes - if the refinement didn't change much, use best version and exit
        if iteration > 0 and weighted_score - best_score < 2.0:
            story_data = best_story
            print("[Pipeline] Minimal improvement detected. Using best story found.")
            break

    print("[Pipeline] Story generation pipeline complete.")
    return best_story, review, analysis, generation_prompt
