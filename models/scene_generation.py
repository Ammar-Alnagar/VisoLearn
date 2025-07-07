query = f"""
You are a professional storyboard artist creating a detailed scene for autistic learners (NO minor characters). If any character is originally a child, age them up to an adult. Design a single scene that:
1. Maintains perfect continuity with previous scenes
2. Follows strict chronological order
3. Has clear cause-and-effect relationships
4. Uses consistent visual elements
5. Provides smooth transitions

SCENE REQUIREMENTS:
1. STRICT TIMELINE:
   - Scene must occur immediately after previous scene
   - No time jumps or flashbacks
   - Clear connection to previous scene's events
   - Explicit setup for next scene

2. LOGICAL PROGRESSION:
   - All actions must have clear motivations
   - Each event must be a direct result of previous events
   - Character movements must be physically possible
   - Settings must change logically

3. VISUAL CONTINUITY:
   - Maintain consistent character appearances
   - Keep objects and elements visually identical
   - Follow natural lighting progression
   - Use consistent camera angles

4. TRANSITION RULES:
   - Start with clear connection to previous scene
   - End with explicit setup for next scene
   - Include at least one visual element from previous scene
   - Set up at least one visual element for next scene

For this scene, provide:
1. Detailed visual description
2. Camera angles and movements
3. Character positions and movements
4. Key visual elements
5. Transition elements
6. Timeline validation:
   - Previous scene connection
   - Current scene events
   - Next scene setup

Previous Scene Summary: {previous_scene_summary}
Current Scene Number: {scene_number}
Total Scenes: {total_scenes}
Story Context: {story_context}
Character Details: {character_details}
Setting Details: {setting_details}
Educational Focus: {educational_focus}
Difficulty Level: {difficulty}
Autism Level: {autism_level}
Learner Age Group (reference only, DO NOT depict minors): {age}

Generate a detailed scene description that maintains perfect continuity and logical progression.
""" 