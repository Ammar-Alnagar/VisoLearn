import gradio as gr
import os
import json
import base64
from utils.story_management import submit_story_description, navigate_to_scene, save_story_locally_handler, save_story_data_handler
from utils.comic_story_management import generate_comic_story_sequence, extract_comic_scenes
from config import DIFFICULTY_LEVELS, IMAGE_STYLES
from utils.file_operations import save_story_to_google_drive
from models.comic_image_generator import ComicImageGenerator

# Global variable to store saved stories
saved_stories = []

def list_saved_stories():
    """List all saved stories from the Story Sessions directory"""
    stories = []
    story_dir = "Story Sessions"

    if os.path.exists(story_dir):
        files = os.listdir(story_dir)
        session_files = [f for f in files if f.endswith("_story_session.json")]

        for session_file in session_files:
            try:
                # Extract the base filename (without _story_session.json)
                base_name = session_file.replace("_story_session.json", "")

                # Try to make the name more readable by replacing underscores with spaces
                display_name = base_name.split("_")[0].replace("_", " ")
                if display_name:
                    # Add timestamp from the filename for uniqueness
                    timestamp_part = "_".join(base_name.split("_")[-2:]) if len(base_name.split("_")) > 1 else ""
                    display_name = f"{display_name} ({timestamp_part})"
                else:
                    display_name = base_name

                stories.append((display_name, base_name))
            except Exception as e:
                print(f"Error processing story file {session_file}: {str(e)}")

    # Sort stories by timestamp (newest first)
    stories.sort(key=lambda x: x[1].split("_")[-1] if "_" in x[1] else "", reverse=True)

    return stories

def load_saved_story(base_name):
    """Load a saved story from the Story Sessions directory"""
    story_dir = "Story Sessions"
    session_file = os.path.join(story_dir, f"{base_name}_story_session.json")
    story_file = os.path.join(story_dir, f"{base_name}_story_data.json")
    image_dir = os.path.join(story_dir, f"{base_name}_images")

    story_session = {}
    story_data = {}

    try:
        if os.path.exists(session_file):
            with open(session_file, "r", encoding="utf-8") as f:
                story_session = json.load(f)

                # Initialize scene_images if it doesn't exist
                if "scene_images" not in story_session:
                    story_session["scene_images"] = {}

                # If there's an images folder for this story, load images as file paths directly
                if os.path.exists(image_dir):
                    scene_images = {}
                    for file in os.listdir(image_dir):
                        if file.startswith("scene_") and file.endswith(".png"):
                            scene_num = file.replace("scene_", "").replace(".png", "")
                            image_path = os.path.join(image_dir, file)
                            # Use file path directly
                            if os.path.exists(image_path):
                                scene_images[scene_num] = image_path

                    # Update the session with file paths
                    if scene_images:
                        story_session["scene_images"] = scene_images

                # Ensure all session keys exist for continuity
                for key in ["chat_history", "identified_details", "scene_responses", "completed_scenes", "key_points"]:
                    if key not in story_session:
                        if key in ["chat_history", "identified_details", "scene_responses"]:
                            story_session[key] = {}
                        elif key == "completed_scenes":
                            story_session[key] = []
                        elif key == "key_points":
                            story_session[key] = {}

        if os.path.exists(story_file):
            with open(story_file, "r", encoding="utf-8") as f:
                story_data = json.load(f)

        # Determine starting scene - use the first incomplete scene if possible
        current_scene = 1
        if "completed_scenes" in story_session and story_session["completed_scenes"]:
            completed = [int(s) for s in story_session["completed_scenes"]]
            if completed and story_data and "scenes" in story_data:
                # Find the first incomplete scene
                for i in range(1, len(story_data["scenes"]) + 1):
                    if i not in completed:
                        current_scene = i
                        break
                # If all scenes are completed, go to the last scene
                if all(i in completed for i in range(1, len(story_data["scenes"]) + 1)):
                    current_scene = len(story_data["scenes"])

        # Return the loaded story session and data
        return story_session, story_data, current_scene
    except Exception as e:
        print(f"Error loading story: {str(e)}")
        return {}, {}, 1

def create_story_tab():
    """Create the UI components for the Story Sequence Generator tab"""

    # Add modern CSS styling for the story interface
    custom_css = """
    /* Story Interface Specific Styles */
    .story-container {
        background: var(--bg-card);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        border: 1px solid var(--border-color);
        transition: all 0.3s ease;
    }

    .story-container:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 40px rgba(102, 126, 234, 0.2);
        border-color: var(--primary-color);
    }

    .story-header {
        text-align: center;
        padding: 2rem 1rem;
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        color: white;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
    }

    #story-chatbot {
        border-radius: 16px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        background: var(--bg-card);
        border: 1px solid var(--border-color);
    }

    #story-chatbot .message {
        margin: 12px 0;
        padding: 16px 20px;
        border-radius: 16px;
        max-width: 85%;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }

    #story-chatbot .message.user {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        color: white;
        margin-left: auto;
        margin-right: 0;
    }

    #story-chatbot .message.assistant {
        background: linear-gradient(135deg, var(--accent-color) 0%, var(--success-color) 100%);
        color: white;
        margin-left: 0;
        margin-right: auto;
    }

    #latest-feedback {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 16px;
        margin-top: 15px;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    .story-stats {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }

    .stat-card {
        background: var(--bg-card);
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        border: 1px solid var(--border-color);
        transition: all 0.3s ease;
    }

    .stat-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.2);
    }
    """

    # Initialize global variable
    global saved_stories
    saved_stories = list_saved_stories()

    # Define refresh function early
    def refresh_stories_list():
        """Reload the list of saved stories from the directory"""
        global saved_stories  # Access the global variable to update it

        # Re-scan the stories directory
        saved_stories = list_saved_stories()

        # Extract display names for the dropdown
        choices = [name for name, _ in saved_stories] if saved_stories else []

        # Return dropdown update with no selection
        return gr.update(choices=choices, value=None)

    # State variables
    story_session = gr.State({})
    story_data = gr.State({})
    current_scene = gr.State(1)

    # Get the list of saved stories from the global variable
    story_choices = [name for name, _ in saved_stories] if saved_stories else []

    # Main vertical layout
    with gr.Column():
        # Header Section
        with gr.Column(elem_classes="story-header"):
            gr.Markdown("# 📚 Comic Story Generator")
            gr.Markdown("""
            **Create engaging visual narratives for enhanced learning**

            Generate single comic images with multiple panels that tell compelling stories.
            Perfect for teaching narrative understanding, sequencing concepts, and social communication
            through consistent characters and engaging visual storytelling.
            """)

        # Quick Stats Dashboard
        with gr.Row(elem_classes="story-stats"):
            with gr.Column(elem_classes="stat-card"):
                gr.Markdown("### 🎨 Generated\n**0** Comics")
            with gr.Column(elem_classes="stat-card"):
                gr.Markdown("### 📖 Current Story\n**None**")
            with gr.Column(elem_classes="stat-card"):
                gr.Markdown("### 🎯 Progress\n**0%** Complete")

        # Story control section
        with gr.Row():
            # Sidebar for saved stories
            with gr.Column(scale=1, elem_classes="story-container"):
                gr.Markdown("## 📖 Story Library")
                gr.Markdown("**Access previously created stories and templates**")
                story_sidebar = gr.Dropdown(
                    label="🔍 Load Saved Story",
                    choices=story_choices,
                    value=None,
                    interactive=True,
                    info="Select a saved story to continue working or use as template"
                )
                refresh_stories_btn = gr.Button(
                    "🔄 Refresh Library",
                    elem_classes="primary-btn"
                )

        # Comic settings section
        with gr.Column(elem_classes="story-container"):
            gr.Markdown("## ⚙️ Comic Generation Settings")
            gr.Markdown("**Configure parameters for personalized story creation**")

            with gr.Row():
                age_input = gr.Textbox(
                    label="👶 Child's Age",
                    placeholder="Enter age (e.g., 3, 5, 8)...",
                    value="3",
                    elem_classes="modern-input"
                )
                autism_level_dropdown = gr.Dropdown(
                    label="🧩 Autism Support Level",
                    choices=["Level 1", "Level 2", "Level 3"],
                    value="Level 1",
                    info="Determines narrative complexity and social elements"
                )

            with gr.Row():
                image_style_dropdown = gr.Dropdown(
                    label="🎨 Visual Style",
                    choices=IMAGE_STYLES,
                    value="Modern Digital Comic",
                    info="Choose the artistic approach for your story panels"
                )

            with gr.Row():
                attempt_limit = gr.Slider(
                    label="🔁 Attempt Limit",
                    minimum=1,
                    maximum=10,
                    value=3,
                    step=1,
                    info="Number of interaction attempts per scene."
                )

            story_prompt_input = gr.Textbox(
                label="📝 Story Concept",
                placeholder="Describe your story idea (e.g., 'A young wizard learning magic at an enchanted school', 'A little girl making her first friend at a new school', 'A family preparing for a fun day at the beach')...",
                lines=4,
                elem_classes="modern-input",
                info="Be descriptive to help create engaging, educational content"
            )

            with gr.Row():
                generation_status = gr.Markdown("")
                with gr.Row():
                    generate_24_scenes_button = gr.Button(
                        "✨ Create Comic Story",
                        elem_classes="primary-btn",
                        variant="primary",
                        size="lg"
                    )

        # Story interaction section
        with gr.Column(elem_classes="story-container"):
            gr.Markdown("## 📊 Story Details & Progress")

            # Comic information section
            story_info_box = gr.Markdown("""
                ### 📖 Story Overview

                **Ready to create your comic story!**

                Generate a comic to see detailed story information, character descriptions, and narrative flow.
                """,
                elem_classes="story-container"
            )

            scene_navigation = gr.HTML("""
                <div class="story-container" style="text-align: center; padding: 1.5rem;">
                    <div class="status-badge status-warning">
                        <span>🎬 Ready to Generate Story</span>
                    </div>
                    <p style="margin-top: 1rem; color: var(--text-secondary);">
                        Create your comic story to enable scene navigation
                    </p>
                </div>
            """)

        # Scene display and interaction section
        with gr.Row():
            with gr.Column(scale=2, elem_classes="story-container"):
                gr.Markdown("## 🎬 Comic Story Display")
                gr.Markdown("**Your generated comic story will appear here**")
                # Use type="filepath" to prevent path too long errors on Windows
                scene_image = gr.Image(
                    label="🖼️ Comic Story Image",
                    type="filepath",
                    elem_classes="modern-card"
                )
                scene_description = gr.Markdown("""
                    **📝 Scene Description**

                    Generate a comic story to see detailed scene descriptions and narrative elements.
                    """)

            with gr.Column(scale=1):
                # Details to identify section
                with gr.Column(elem_classes="story-container"):
                    gr.Markdown("## 🎯 Learning Objectives")
                    gr.Markdown("**Help the child identify these story elements:**")
                    checklist_html = gr.HTML("""
                        <div class="progress-container">
                            <div style="text-align: center; padding: 2rem;">
                                <div class="loading-spinner" style="margin: 0 auto 1rem;"></div>
                                <p style="color: var(--text-secondary);">Generate a story to see learning objectives</p>
                            </div>
                        </div>
                    """)

                with gr.Column(elem_classes="story-container"):
                    gr.Markdown("## 📊 Session Progress")
                    attempt_counter_html = gr.HTML(
                        """
                            <div class="status-badge status-warning" style="display:none;">
                                <span>🔄 Attempts: 0/3</span>
                            </div>
                        """,
                        visible=False
                    )

                    progress_html = gr.HTML("""
                        <div class="progress-container">
                            <div style="text-align: center; padding: 1.5rem;">
                                <p style="color: var(--text-secondary);">Ready to start story session</p>
                                <div class="progress-bar">
                                    <div class="progress-fill" style="width: 0%"></div>
                                </div>
                                <small style="color: var(--text-secondary);">Progress: 0%</small>
                            </div>
                        </div>
                    """)

        # Key points section
        with gr.Column(elem_classes="story-container"):
            gr.Markdown("## 🔑 Key Learning Points")
            gr.Markdown("**Educational insights and narrative elements to focus on**")
            key_points_display = gr.Markdown("""
                *Generate your comic story to see key learning points and educational objectives*
                """,
                elem_id="key-points-display"
            )

        # Session details section
        with gr.Column(elem_classes="story-container"):
            gr.Markdown("## 📋 Session Analytics")
            gr.Markdown("**Detailed progress tracking and therapeutic insights**")
            session_details_output = gr.JSON(
                label="📊 Comprehensive Session Data",
                value={},
                elem_classes="modern-card"
            )

        # Scene extraction section
        with gr.Column(elem_classes="story-container"):
            gr.Markdown("## 🖼️ Panel Analysis Tools")
            gr.Markdown("""
                **Extract and analyze individual comic panels**

                Break down your multi-panel comic into individual scenes for focused learning and detailed discussion.
                Perfect for step-by-step narrative analysis and comprehension building.
            """)
            # Button removed from UI – kept invisible for backward compatibility
            extract_scenes_btn = gr.Button(
                "🔍 Extract Individual Panels",
                elem_classes="primary-btn",
                visible=False
            )

            # Display area for individual scene navigation
            with gr.Column(visible=False, elem_classes="modern-card") as scene_viewer_container:
                gr.Markdown("### 🎬 Individual Panel Viewer")
                with gr.Row():
                    prev_scene_btn_viewer = gr.Button(
                        "← Previous Panel",
                        elem_classes="primary-btn"
                    )
                    scene_counter = gr.Markdown(
                        "**Panel 1 of 1**",
                        elem_classes="status-badge"
                    )
                    next_scene_btn_viewer = gr.Button(
                        "Next Panel →",
                        elem_classes="primary-btn"
                    )
                individual_scene_image = gr.Image(
                    label="🎭 Current Panel Focus",
                    type="filepath",
                    height=512,
                    interactive=False,
                    elem_classes="modern-card"
                )

        # Child interaction section (moved beneath split images)
        with gr.Column(elem_classes="story-container"):
            gr.Markdown("## 💬 Interactive Story Discussion")
            gr.Markdown("""
                **Engage in meaningful conversation about the story**

                After generating a comic, encourage the child to describe what they observe.
                The AI provides personalized, supportive feedback and tracks progress in narrative
                understanding, character recognition, and sequential storytelling skills.
            """)

            # Full Story mode checkbox
            full_story_mode = gr.Checkbox(
                label="📚 Full Story Analysis Mode",
                value=False,
                info="✅ Full Story: Child describes the entire narrative | ❌ Panel Mode: Child describes individual panels separately",
                elem_classes="modern-input"
            )

            # Main chat interface - using Chatbot component like the single image interface
            chatbot = gr.Chatbot(
                label="💬 Story Discussion History",
                type="messages",
                height=450,
                show_label=True,
                elem_id="story-chatbot",
                show_copy_button=True,
                elem_classes="modern-card"
            )

            # Input area with send button
            with gr.Row():
                user_description_input = gr.Textbox(
                    label="Child's Story Response",
                    placeholder="Type what the child describes about the story or scene...",
                    show_label=False,
                    scale=4,
                    container=False,
                    elem_id="chat-input",
                    elem_classes="modern-input",
                    lines=2
                )
                submit_description_btn = gr.Button(
                    "📤 Share Response",
                    elem_classes="primary-btn",
                    scale=1,
                    size="lg"
                )

            # Latest feedback display
            feedback_display = gr.Markdown("", visible=False, elem_id="latest-feedback")

        # Save comic section with both buttons
        with gr.Column():
            gr.Markdown("## Save Comic Story")
            story_name_input = gr.Textbox(
                label="Comic Story Name",
                placeholder="Enter the name of the comic story...",
                lines=1
            )
            with gr.Row():
                save_local_btn = gr.Button("💾 Save Story Locally")
                save_google_drive_btn = gr.Button("☁️ Save to Google Drive")
            save_result = gr.Textbox(label="Save Result", interactive=False)

        # -------------------- Automatic Scene Extraction --------------------
        # State objects for the individual panel viewer
        scene_paths = gr.State([])
        current_scene_index = gr.State(0)
        scene_viewer_visible = gr.State(False)

        def auto_init_scene_viewer(story_session):
            """Automatically split the freshly-generated comic into individual
            panels.  This replaces the manual *Extract Individual Panels* button
            to streamline the user workflow."""
            comic_path = story_session.get("comic_image_path")
            num_scenes = story_session.get("num_scenes", 3)

            if not comic_path:
                # Nothing to split yet
                return [], 0, False, None, "No story comic generated yet"

            # Util returns the list of filepaths for the extracted panels
            scene_paths_list, _ = extract_comic_scenes(comic_path, num_scenes)
            if not scene_paths_list:
                return [], 0, False, None, "Failed to extract scenes"

            # Start the viewer at the first panel
            return (
                scene_paths_list,
                0,
                True,
                scene_paths_list[0],
                f"Panel 1 of {len(scene_paths_list)}"
            )

        # --------------------------------------------------------------------

        # Event handlers
        def generate_story_with_24_scenes(age, autism_level, story_prompt, image_style, attempt_limit):
            """Helper to call the generator with a fixed scene count."""
            # This now correctly calls the generator which yields updates
            gen = generate_comic_story_sequence(age, autism_level, story_prompt, image_style, 16, attempt_limit)
            for output in gen:
                yield output

        generate_24_scenes_button.click(
            fn=lambda: "Generating comic story... this may take a minute...",
            inputs=None,
            outputs=generation_status
        ).then(
            generate_story_with_24_scenes,
            inputs=[
                age_input,
                autism_level_dropdown,
                story_prompt_input,
                image_style_dropdown,
                attempt_limit
            ],
            outputs=[
                story_session, story_data, current_scene, scene_image,
                scene_description, story_info_box, scene_navigation, generation_status
            ]
        ).then(
            # Initialize the chat display for the first scene
            lambda session: convert_session_to_messages(session, 1, False),
            inputs=[story_session],
            outputs=[chatbot]
        ).then(
            update_session_details,
            inputs=[story_session, story_data],
            outputs=[session_details_output]
        ).then(
            format_key_points,
            inputs=[story_session, story_data],
            outputs=[key_points_display]
        ).then(
            # Update checklist, attempt counter, and progress display
            lambda session, scene: (
                update_story_checklist_html(session, scene),
                update_story_attempt_counter(session, scene),
                update_story_progress_html(session, scene)
            ),
            inputs=[story_session, current_scene],
            outputs=[checklist_html, attempt_counter_html, progress_html]
        ).then(
            auto_init_scene_viewer,
            inputs=[story_session],
            outputs=[scene_paths, current_scene_index, scene_viewer_visible, individual_scene_image, scene_counter]
        ).then(
            fn=lambda x: gr.update(visible=x),
            inputs=[scene_viewer_visible],
            outputs=[scene_viewer_container]
        )

        def chat_submit_wrapper(user_message, session, data, scene, full_mode):
            """Wrapper function for chat submission that returns proper chatbot format"""
            if not user_message.strip():
                return [], "", session, ""

            # Import the enhanced function
            from utils.story_management import submit_story_description_enhanced

            # Call the enhanced function which returns: input_clear, chat_messages, updated_session, feedback, new_image
            input_clear, chat_messages, updated_session, feedback, new_image = submit_story_description_enhanced(
                user_message, session, data, scene, full_mode
            )

            return chat_messages, input_clear, updated_session, feedback, new_image

        # Chat submission handlers (both button click and Enter key)
        chat_inputs = [
            user_description_input,
            story_session,
            story_data,
            current_scene,
            full_story_mode
        ]

        chat_outputs = [
            chatbot,
            user_description_input,
            story_session,
            feedback_display,
            scene_image
        ]

        # Define the shared update chain
        def create_update_chain(trigger):
            return trigger.then(
                # Update the key points display to show newly identified details
                format_key_points,
                inputs=[story_session, story_data],
                outputs=[key_points_display]
            ).then(
                # Update session details to reflect changes
                update_session_details,
                inputs=[story_session, story_data],
                outputs=[session_details_output]
            ).then(
                # Update checklist, attempt counter, and progress display
                lambda session, scene: (
                    update_story_checklist_html(session, scene),
                    update_story_attempt_counter(session, scene),
                    update_story_progress_html(session, scene)
                ),
                inputs=[story_session, current_scene],
                outputs=[checklist_html, attempt_counter_html, progress_html]
            )

        # Apply the update chain to both triggers
        create_update_chain(
            submit_description_btn.click(
                chat_submit_wrapper,
                inputs=chat_inputs,
                outputs=chat_outputs
            )
        )

        create_update_chain(
            user_description_input.submit(
                chat_submit_wrapper,
                inputs=chat_inputs,
                outputs=chat_outputs
            )
        )

        # Navigation handlers removed - only dropdown navigation remains for main comic view

        # -------------------- Panel Navigation (auto-extracted) --------------------
        def update_scene_display(scene_paths, current_index):
            if not scene_paths:
                return None, "Panel 0 of 0"

            # Clamp index to valid range
            index = max(0, min(current_index, len(scene_paths) - 1))
            return scene_paths[index], f"Panel {index + 1} of {len(scene_paths)}"

        # Previous / Next panel controls
        prev_scene_btn_viewer.click(
            fn=lambda paths, idx: (paths, max(0, idx - 1)),
            inputs=[scene_paths, current_scene_index],
            outputs=[scene_paths, current_scene_index]
        ).then(
            fn=update_scene_display,
            inputs=[scene_paths, current_scene_index],
            outputs=[individual_scene_image, scene_counter]
        )

        next_scene_btn_viewer.click(
            fn=lambda paths, idx: (paths, min(len(paths) - 1, idx + 1) if paths else 0),
            inputs=[scene_paths, current_scene_index],
            outputs=[scene_paths, current_scene_index]
        ).then(
            fn=update_scene_display,
            inputs=[scene_paths, current_scene_index],
            outputs=[individual_scene_image, scene_counter]
        )

        # Define save functions after refresh_stories_list is defined
        def save_and_refresh_local(story_session, story_data, story_name):
            """Save story locally and refresh the story list"""
            result = save_story_locally_handler(story_session, story_data, story_name)

            # Use the refresh function to update the global variable
            refresh_stories_list()

            # Return save result
            return result

        def save_and_refresh_gdrive(story_session, story_data, story_name):
            """Save story to Google Drive and refresh the story list"""
            result = save_story_data_handler(story_session, story_data, story_name)

            # Use the refresh function to update the global variable
            refresh_stories_list()

            # Return result
            return result

        # Update save buttons handlers
        save_local_btn.click(
            save_and_refresh_local,
            inputs=[story_session, story_data, story_name_input],
            outputs=[save_result]
        ).then(
            # After saving, refresh the dropdown
            refresh_stories_list,
            inputs=[],
            outputs=[story_sidebar]
        )

        save_google_drive_btn.click(
            save_and_refresh_gdrive,
            inputs=[story_session, story_data, story_name_input],
            outputs=[save_result]
        ).then(
            # After saving, refresh the dropdown
            refresh_stories_list,
            inputs=[],
            outputs=[story_sidebar]
        )

        # Sidebar event handlers
        def load_story_handler(story_name):
            # Handle invalid input
            if not story_name:
                return {}, {}, 1, None, "No story selected", "", "", "", "", "", []

            # Find the base_name for the selected story
            base_name = None
            for display_name, base in saved_stories:
                if display_name == story_name:
                    base_name = base
                    break

            # Handle story not found
            if not base_name:
                return {}, {}, 1, None, "Story not found", "", "", "", "", "", []

            try:
                # Load the story with enhanced session restoration
                session, data, scene = load_saved_story(base_name)

                # Get the current scene image - now directly using file path
                scene_image = None
                if "scene_images" in session and str(scene) in session["scene_images"]:
                    scene_image = session["scene_images"][str(scene)]
                    # File paths will be used directly by Gradio Image with type="filepath"

                # Get the scene description - safely access keys with fallback values
                scene_description = ""
                if "scenes" in data and len(data["scenes"]) >= scene:
                    scene_data = data["scenes"][scene-1]
                    scene_title = scene_data.get("title", f"Scene {scene}")
                    scene_desc = scene_data.get("description", "No description available")
                    scene_description = f"## {scene_title}\n\n{scene_desc}"

                # Add previously submitted description and feedback if available
                if "scene_responses" in session and str(scene) in session["scene_responses"]:
                    scene_response = session["scene_responses"][str(scene)]
                    if "evaluation" in scene_response:
                        eval_data = scene_response["evaluation"]
                        feedback_text = eval_data.get("feedback", "")
                        hint = eval_data.get("hint", "")
                        question = eval_data.get("question_prompt", "")
                        scene_description += f"\n\n### Previous Feedback\n{feedback_text}\n{'**Hint:** ' + hint if hint else ''}\n{'**Question to consider:** ' + question if question else ''}"

                # Update story info
                story_title = data.get('title', 'Loaded Story')
                story_info = f"### {story_title}\n\n{data.get('premise', '')}"
                if "educational_focus" in data:
                    story_info += f"\n\n**Educational Focus:** {data['educational_focus']}"
                if "completed_scenes" in session:
                    completed = len(session["completed_scenes"])
                    total = len(data.get("scenes", []))
                    story_info += f"\n\n**Progress:** {completed}/{total} scenes completed"

                # Create scene navigation HTML
                num_scenes = len(data.get('scenes', []))
                scene_nav_html = create_scene_navigation_html(num_scenes, scene)

                # Update scene selector - ensure at least Scene 1 is available
                scene_choices = [f"Scene {i+1}" for i in range(num_scenes)]
                if not scene_choices:
                    scene_choices = ["Scene 1"]

                # Extract the story name from the base_name
                story_name_value = base_name.split('_')[0].replace('_', ' ')

                # Get previously saved user description
                user_description = ""
                if "scene_responses" in session and str(scene) in session["scene_responses"]:
                    user_description = session["scene_responses"][str(scene)].get("user_description", "")

                # Get feedback from the previous submission
                feedback = ""
                if "scene_responses" in session and str(scene) in session["scene_responses"]:
                    scene_response = session["scene_responses"][str(scene)]
                    if "evaluation" in scene_response:
                        eval_data = scene_response["evaluation"]
                        feedback_text = eval_data.get("feedback", "")
                        hint = eval_data.get("hint", "")
                        question = eval_data.get("question_prompt", "")
                        feedback = f"""### Previous Feedback
                        {feedback_text}
                        {"**Hint:** " + hint if hint else ""}
                        {"**Question to consider:** " + question if question else ""}
                        """

                # Get chat history for this scene (always panel mode when loading)
                chat_history = convert_session_to_messages(session, scene, False)

                return session, data, scene, scene_image, scene_description, story_info, scene_nav_html, story_name_value, user_description, feedback, chat_history

            except Exception as e:
                print(f"Error in load_story_handler: {e}")
                # Return default values on error (removed scene_selector_update)
                return {}, {}, 1, None, f"Error loading story: {str(e)}", "", "", "", "", "", []

        # Load story event handlers
        story_sidebar.change(
            load_story_handler,
            inputs=[story_sidebar],
            outputs=[
                story_session,
                story_data,
                current_scene,
                scene_image,
                scene_description,
                story_info_box,
                scene_navigation,
                story_name_input,
                user_description_input,
                feedback_display,
                chatbot
            ]
        ).then(
            update_session_details,
            inputs=[story_session, story_data],
            outputs=[session_details_output]
        ).then(
            format_key_points,
            inputs=[story_session, story_data],
            outputs=[key_points_display]
        )

        # Full story mode checkbox change handler
        full_story_mode.change(
            lambda mode: gr.update(
                placeholder="Describe the entire comic story - what happens from beginning to end, who are the characters, and what is the main message?" if mode
                else "Type what the child says about this scene/panel...",
                label="Child's Full Story Description" if mode else "Child's Description"
            ),
            inputs=[full_story_mode],
            outputs=[user_description_input]
        ).then(
            # Update chat history when mode changes
            lambda session, scene, mode: convert_session_to_messages(session, scene, mode),
            inputs=[story_session, current_scene, full_story_mode],
            outputs=[chatbot]
        )

        # Then update the button click handler to not need input:
        refresh_stories_btn.click(
            refresh_stories_list,
            inputs=[],  # No input needed
            outputs=[story_sidebar]
        )

def create_scene_navigation_html(num_scenes, current_scene):
    """Create HTML for scene navigation buttons"""
    html = "<div style='display: flex; justify-content: center; gap: 10px; padding: 10px;'>"

    for i in range(1, num_scenes + 1):
        if i == current_scene:
            # Current scene - highlighted
            html += f"<button style='background-color: #2196F3; color: white; border: none; padding: 8px 12px; border-radius: 4px; cursor: pointer;'>{i}</button>"
        else:
            # Other scenes
            html += f"<button style='background-color: #e0e0e0; color: black; border: none; padding: 8px 12px; border-radius: 4px; cursor: pointer;'>{i}</button>"

    html += "</div>"
    return html

def update_session_details(story_session, story_data=None):
    """Update the session details display"""
    # Filter out large data like images
    filtered_session = {}
    for key, value in story_session.items():
        if key not in ["scene_images", "scene_prompts"]:
            filtered_session[key] = value

    # Add a summary of chat history for each scene
    if "chat_history" in story_session:
        chat_summary = {}
        for scene_num, chats in story_session["chat_history"].items():
            chat_summary[f"Scene {scene_num} Chat"] = [
                {"speaker": speaker, "message": message[:100] + "..." if len(message) > 100 else message}
                for speaker, message in chats
            ]
        filtered_session["chat_summary"] = chat_summary

    # Add a summary of identified details for each scene
    if "identified_details" in story_session:
        details_summary = {}
        for scene_num, details in story_session["identified_details"].items():
            scene_info = story_data.get("scenes", [])[int(scene_num)-1] if story_data and "scenes" in story_data else {}
            all_key_elements = scene_info.get("key_elements", [])

            details_summary[f"Scene {scene_num} Details"] = {
                "identified": details,
                "total": len(all_key_elements),
                "percentage": f"{(len(details) / len(all_key_elements) * 100) if all_key_elements else 0:.1f}%"
            }
        filtered_session["details_summary"] = details_summary

    return filtered_session

def format_key_points(story_session, story_data=None):
    """Format the key points for display in the UI with a progress meter"""
    if not story_session or "key_points" not in story_session:
        return "Generate a story to see key learning points."

    key_points = story_session.get("key_points", {})
    identified_details = story_session.get("identified_details", {})

    # Start with a header
    formatted_points = "### Key Points to Guide Learning\n\n"

    # Format educational points
    if "educational_points" in key_points and key_points["educational_points"]:
        formatted_points += "#### Educational Concepts\n"
        for point in key_points["educational_points"]:
            formatted_points += f"- {point}\n"
        formatted_points += "\n"

    if "character_points" in key_points and key_points["character_points"]:
        formatted_points += "#### Character Observations\n"
        for point in key_points["character_points"]:
            formatted_points += f"- {point}\n"
        formatted_points += "\n"

    if "plot_points" in key_points and key_points["plot_points"]:
        formatted_points += "#### Story Events\n"
        for point in key_points["plot_points"]:
            formatted_points += f"- {point}\n"
        formatted_points += "\n"

    if "emotional_points" in key_points and key_points["emotional_points"]:
        formatted_points += "#### Emotional Understanding\n"
        for point in key_points["emotional_points"]:
            formatted_points += f"- {point}\n"
        formatted_points += "\n"

    if "cause_effect_points" in key_points and key_points["cause_effect_points"]:
        formatted_points += "#### Cause and Effect\n"
        for point in key_points["cause_effect_points"]:
            formatted_points += f"- {point}\n"
        formatted_points += "\n"

    if "visual_details_points" in key_points and key_points["visual_details_points"]:
        formatted_points += "#### Visual Details\n"
        for point in key_points["visual_details_points"]:
            formatted_points += f"- {point}\n"
        formatted_points += "\n"

    if "questions" in key_points and key_points["questions"]:
        formatted_points += "#### Guiding Questions\n"
        for question in key_points["questions"]:
            formatted_points += f"- {question}\n"
        formatted_points += "\n"

    # Add progress meter and identified details section
    if identified_details:
        formatted_points += "\n## Progress Tracker\n\n"

        # Calculate overall progress
        total_details_identified = sum(len(details) for details in identified_details.values())

        # Get total possible details from story data if available
        total_possible_details = 0
        if story_data and "scenes" in story_data:
            for scene in story_data["scenes"]:
                total_possible_details += len(scene.get("key_elements", []))
        else:
            # Estimate total possible details if story data not provided
            for scene_num, details in identified_details.items():
                if len(details) > 0:
                    # Assume we need about 5 details per scene if not specified
                    total_possible_details = len(identified_details) * 5
                    break

        if total_possible_details > 0:
            progress_percentage = min(100, int((total_details_identified / total_possible_details) * 100))

            # Visual progress bar using Unicode block characters
            progress_bar_width = 30  # characters wide
            filled_blocks = int((progress_percentage / 100) * progress_bar_width)
            empty_blocks = progress_bar_width - filled_blocks

            progress_bar = "█" * filled_blocks + "░" * empty_blocks

            formatted_points += f"### Overall Progress: {progress_percentage}%\n"
            formatted_points += f"{progress_bar} {progress_percentage}/100\n\n"

            # Win condition text
            if progress_percentage >= 80:
                formatted_points += "🏆 **Great job!** You've identified most of the key details in the story!\n\n"
            elif progress_percentage >= 50:
                formatted_points += "👍 **Good progress!** Keep identifying more details to complete the story.\n\n"
            else:
                formatted_points += "🔍 **Keep exploring!** Try to find more details in each scene.\n\n"

        # Add per-scene progress details
        formatted_points += "### Identified Details by Scene\n\n"

        for scene_num in sorted(identified_details.keys(), key=lambda x: int(x)):
            details = identified_details[scene_num]

            # Get total key elements for this scene if available
            scene_total_elements = 0
            if story_data and "scenes" in story_data and int(scene_num) <= len(story_data["scenes"]):
                scene_data = story_data["scenes"][int(scene_num)-1]
                scene_total_elements = len(scene_data.get("key_elements", []))
            else:
                scene_total_elements = max(5, len(details))  # Assume at least 5 elements

            # Calculate scene progress percentage
            scene_percentage = min(100, int((len(details) / scene_total_elements) * 100))

            # Scene title if available
            scene_title = ""
            if story_data and "scenes" in story_data and int(scene_num) <= len(story_data["scenes"]):
                scene_data = story_data["scenes"][int(scene_num)-1]
                scene_title = scene_data.get("title", f"Scene {scene_num}")
                if scene_title != f"Scene {scene_num}":
                    scene_title = f"Scene {scene_num}: {scene_title}"
                else:
                    scene_title = f"Scene {scene_num}"
            else:
                scene_title = f"Scene {scene_num}"

            # Scene progress header with percentage
            formatted_points += f"#### {scene_title} - {scene_percentage}% Complete\n"

            # Mini progress bar for scene
            mini_bar_width = 15
            mini_filled = int((scene_percentage / 100) * mini_bar_width)
            mini_empty = mini_bar_width - mini_filled
            mini_bar = "█" * mini_filled + "░" * mini_empty

            formatted_points += f"{mini_bar} ({len(details)}/{scene_total_elements} details)\n\n"

            # List identified details with checkmarks
            if details:
                for detail in details:
                    formatted_points += f"- ✅ {detail}\n"
            else:
                formatted_points += "*No details identified yet*\n"

            formatted_points += "\n"

    return formatted_points

def _parse_scene_selection(choice, current):
    """Safely parse the scene selection and return the offset from current scene"""
    if not choice:
        return 0

    try:
        # Try to extract the scene number
        choice_str = str(choice).strip()
        if ' ' in choice_str:
            # Format is "Scene X"
            scene_num = int(choice_str.split()[1])
            return scene_num - int(current)
        elif choice_str.isdigit():
            # Just a number
            scene_num = int(choice_str)
            return scene_num - int(current)
        else:
            # Unknown format
            return 0
    except (IndexError, ValueError, TypeError):
        # Any error, return 0 (stay on current scene)
        return 0

def convert_session_to_messages(story_session, current_scene, full_story_mode=False):
    """Convert session chat history to Gradio Chatbot messages format"""
    if not story_session or "chat_history" not in story_session:
        return []

    if full_story_mode:
        # Get full story chat history
        scene_chat = story_session.get("chat_history", {}).get("full_story", [])
    else:
        # Get the current scene number as a string
        scene_num = str(current_scene)
        # Get chat history for this scene
        scene_chat = story_session.get("chat_history", {}).get(scene_num, [])

    # Convert to Gradio Chatbot messages format
    messages = []
    for speaker, message in scene_chat:
        if speaker == "Child":
            # User message
            messages.append({"role": "user", "content": message})
        else:
            # Assistant/Teacher message
            messages.append({"role": "assistant", "content": message})

    return messages

def format_chat_history(story_session, current_scene, full_story_mode=False):
    """Legacy function - kept for compatibility but converts to messages format"""
    messages = convert_session_to_messages(story_session, current_scene, full_story_mode)

    if not messages:
        if full_story_mode:
            return "No full story conversation history yet."
        else:
            return "No conversation history for this panel yet."

    # For backwards compatibility, create a simple text format
    title = "Full Story Conversation" if full_story_mode else f"Panel {current_scene} Conversation"

    chat_text = f"### {title}\n\n"
    for msg in messages:
        role = "Child" if msg["role"] == "user" else "Teacher"
        chat_text += f"**{role}:** {msg['content']}\n\n"

    return chat_text

def update_story_checklist_html(story_session, current_scene):
    """Update the checklist HTML for the story interface"""
    if not story_session or "key_details" not in story_session:
        return """
        <div id="checklist-container" style="background-color: #000000; color: #ffffff; padding: 15px; border-radius: 8px;">
            <p>Generate a comic story to see details to identify.</p>
        </div>
        """

    key_details = story_session.get("key_details", [])
    identified_details = story_session.get("identified_details_by_scene", {}).get(str(current_scene), [])

    html = """
    <div id="checklist-container" style="background-color: #000000; color: #ffffff; padding: 15px; border-radius: 8px;">
        <h4 style="margin-top: 0; color: #ffffff;">🔍 Find These Details:</h4>
    """

    for i, detail in enumerate(key_details):
        is_identified = detail in identified_details
        status_icon = "✅" if is_identified else "❌"
        color = "#4CAF50" if is_identified else "#ffffff"

        html += f"""
        <div style="margin: 8px 0; padding: 8px; border-radius: 5px; background-color: {'#2d5a2d' if is_identified else '#333333'};">
            <span style="color: {color};">{status_icon} {detail}</span>
        </div>
        """

    html += "</div>"
    return html

def update_story_attempt_counter(story_session, current_scene):
    """Update the attempt counter for the current scene"""
    if not story_session:
        return """
        <div id="attempt-counter" style="margin-top: 10px; padding: 10px; background-color: #000000; color: #ffffff; border-radius: 5px; border: 1px solid #444;">
            <p style="margin: 0; font-weight: bold;">Attempts: 0/3</p>
        </div>
        """

    attempt_count = story_session.get("attempt_count_by_scene", {}).get(str(current_scene), 0)
    attempt_limit = story_session.get("attempt_limit", 3)

    return f"""
    <div id="attempt-counter" style="margin-top: 10px; padding: 10px; background-color: #000000; color: #ffffff; border-radius: 5px; border: 1px solid #444;">
        <p style="margin: 0; font-weight: bold;">Attempts: {attempt_count}/{attempt_limit}</p>
    </div>
    """

def update_story_progress_html(story_session, current_scene):
    """Update the progress HTML for the story interface"""
    if not story_session or "key_details" not in story_session:
        return """
        <div id="progress-container" style="background-color: #000000; color: #ffffff; padding: 15px; border-radius: 8px;">
            <p>No active session.</p>
        </div>
        """

    key_details = story_session.get("key_details", [])
    identified_details = story_session.get("identified_details_by_scene", {}).get(str(current_scene), [])

    total_details = len(key_details)
    identified_count = len(identified_details)

    if total_details == 0:
        progress_percentage = 0
    else:
        progress_percentage = int((identified_count / total_details) * 100)

    # Create progress bar
    bar_width = 20
    filled_chars = int((progress_percentage / 100) * bar_width)
    empty_chars = bar_width - filled_chars
    progress_bar = "█" * filled_chars + "░" * empty_chars

    return f"""
    <div id="progress-container" style="background-color: #000000; color: #ffffff; padding: 15px; border-radius: 8px;">
        <h4 style="margin-top: 0; color: #ffffff;">📊 Progress</h4>
        <p style="margin: 5px 0;">Scene {current_scene}: {identified_count}/{total_details} details found</p>
        <div style="font-family: monospace; font-size: 14px; margin: 10px 0;">
            {progress_bar} {progress_percentage}%
        </div>
        <p style="margin: 5px 0; font-size: 12px;">
            {'🎉 Great job! Keep exploring!' if progress_percentage > 70 else '🔍 Keep looking for more details!'}
        </p>
    </div>
    """
