import gradio as gr
import os
import json
import time  # Import the time module
import logging
import tempfile
import base64

from utils.visualization import update_difficulty_label, update_checklist_html, update_progress_html, update_attempt_counter
from utils.state_management import generate_image_and_reset_chat, chat_respond, update_sessions, load_checklist_from_session
from utils.file_operations import (
    save_all_session_images, save_session_log, save_to_google_drive,
    save_session_to_filesystem, list_saved_filesystem_sessions,
    load_session_from_filesystem, delete_filesystem_session
)
from utils.local_storage import save_state_to_local_storage, load_state_from_local_storage, list_saved_states, create_new_state_entry
from config import DEFAULT_SESSION, IMAGE_STYLES

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("visolearn")


def safe_get_data(data):
    """
    Safely handle different types of data that might be passed from Gradio components

    Args:
        data: The data to process, which might be a State object, string, dict, etc.

    Returns:
        dict or list: The processed data in Python data structure form
    """
    try:
        # Handle State objects
        if hasattr(data, 'value'):
            data = data.value

        # Convert string to Python object if needed
        if isinstance(data, str) and data:
            try:
                return json.loads(data)
            except:
                return {}
        elif isinstance(data, (dict, list)):
            return data
        else:
            return {} if isinstance(data, dict) else []
    except Exception as e:
        print(f"Error processing data: {e}")
        return {} if isinstance(data, dict) else []

def generate_saved_states_html(all_states):
    """Generate HTML for the saved states list"""
    try:
        # Ensure we have a dictionary
        if isinstance(all_states, str):
            try:
                all_states = json.loads(all_states)
            except:
                return "<div>Error parsing saved sessions data.</div>"

        if not all_states:
            return "<div>No saved sessions found.</div>"

        html = "<div class='saved-states-container'>"

        # Sort states by timestamp (newest first)
        sorted_states = []
        for state_id, state in all_states.items():
            timestamp = state.get('timestamp', '')
            display_name = state.get('display_name', timestamp)
            active_session = state.get('active_session', {})
            saved_sessions = state.get('saved_sessions', [])

            # Get some metadata to display
            difficulty = active_session.get('difficulty', 'Unknown')
            total_sessions = len(saved_sessions)
            if active_session and active_session.get('prompt'):
                total_sessions += 1

            sorted_states.append({
                'id': state_id,
                'timestamp': timestamp,
                'display_name': display_name,
                'difficulty': difficulty,
                'total_sessions': total_sessions
            })

        # Sort by timestamp (newest first)
        sorted_states.sort(key=lambda x: x['timestamp'], reverse=True)

        # Generate HTML for each state
        for state in sorted_states:
            html += f"""
            <div class='saved-state-item' onclick='loadState("{state['id']}")'>
                <strong>{state['display_name'] or state['timestamp']}</strong><br>
                <span>Difficulty: {state['difficulty']} - {state['total_sessions']} sessions</span>
                <span class='delete-button' onclick='event.stopPropagation(); deleteState("{state['id']}")'>🗑️</span>
            </div>
            """

        html += """
        <script>
            function loadState(stateId) {
                // Use Gradio's built-in function to trigger an event
                document.dispatchEvent(new CustomEvent('load-state', {
                    detail: { stateId: stateId }
                }));
            }

            function deleteState(stateId) {
                if (confirm('Are you sure you want to delete this saved session?')) {
                    document.dispatchEvent(new CustomEvent('delete-state', {
                        detail: { stateId: stateId }
                    }));
                }
            }

            // Add event listeners for custom events
            document.addEventListener('load-state', function(e) {
                const gradioEl = document.querySelector('#load-state-trigger');
                if (gradioEl) {
                    gradioEl.value = e.detail.stateId;
                    gradioEl.dispatchEvent(new Event('input'));
                }
            });

            document.addEventListener('delete-state', function(e) {
                const gradioEl = document.querySelector('#delete-state-trigger');
                if (gradioEl) {
                    gradioEl.value = e.detail.stateId;
                    gradioEl.dispatchEvent(new Event('input'));
                }
            });
        </script>
        """

        html += "</div>"
        return html
    except Exception as e:
        print(f"Error generating saved states HTML: {e}")
        return f"<div>Error displaying saved sessions: {str(e)}</div>"

def generate_filesystem_sessions_html(sessions_list):
    """Generate HTML for the filesystem saved sessions list"""
    try:
        if not sessions_list:
            return "<div>No saved sessions found in 'Sessions History' directory.</div>"

        html = "<div class='filesystem-sessions-container'>"

        # Generate HTML for each session
        for session in sessions_list:
            session_id = session.get('id', '')
            display_name = session.get('display_name', session.get('id', 'Unknown'))
            timestamp = session.get('timestamp', 'Unknown')
            sessions_count = session.get('sessions_count', 0)

            html += f"""
            <div class='saved-state-item' onclick='loadFilesystemSession("{session_id}")'>
                <strong>{display_name}</strong><br>
                <span>Created: {timestamp} - {sessions_count} sessions</span>
                <span class='delete-button' onclick='event.stopPropagation(); deleteFilesystemSession("{session_id}")'>🗑️</span>
            </div>
            """

        html += """
        <script>
            function loadFilesystemSession(sessionId) {
                console.log("Loading filesystem session:", sessionId);
                // Use a direct approach to trigger Gradio events
                const loadTrigger = document.getElementById('load-filesystem-trigger');
                if (loadTrigger) {
                    loadTrigger.value = sessionId;
                    const event = new Event('input', { bubbles: true });
                    loadTrigger.dispatchEvent(event);
                } else {
                    console.error("Could not find load trigger element");
                }
            }

            function deleteFilesystemSession(sessionId) {
                if (confirm('Are you sure you want to delete this saved session from disk?')) {
                    console.log("Deleting filesystem session:", sessionId);
                    const deleteTrigger = document.getElementById('delete-filesystem-trigger');
                    if (deleteTrigger) {
                        deleteTrigger.value = sessionId;
                        const event = new Event('input', { bubbles: true });
                        deleteTrigger.dispatchEvent(event);
                    } else {
                        console.error("Could not find delete trigger element");
                    }
                }
            }
        </script>
        """

        html += "</div>"
        return html
    except Exception as e:
        print(f"Error generating filesystem sessions HTML: {e}")
        return f"<div>Error generating session list: {str(e)}</div>"


def create_interface():
    # Get the current directory path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Assuming the logo is named 'logo.png' - adjust the filename as needed
    logo_path = os.path.join(current_dir, "Compumacy-Logo-Trans2.png")

    css = """
        #logo-row {
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 1rem;
            background-color: black;
        }
        #logo-row img {
            max-width: 300px;
            object-fit: contain;
        }
        .saved-state-item {
            padding: 10px;
            margin: 5px 0;
            border-radius: 5px;
            background-color: #333333;
            color: #ffffff;
            cursor: pointer;
            transition: background-color 0.2s;
            border: 1px solid #444;
        }
        .saved-state-item:hover {
            background-color: #444444;
        }
        .delete-button {
            color: #ff6b6b;
            margin-left: 10px;
            float: right;
            font-weight: bold;
        }
        .filesystem-sessions-container {
            max-height: 400px;
            overflow-y: auto;
            padding: 5px;
            border: 1px solid #444;
            border-radius: 5px;
            background-color: #222222;
        }
        /* Highlight effect when clicking */
        .saved-state-item:active {
            background-color: #555555;
        }
    """

    with gr.Blocks(css=css) as demo:
        active_session = gr.State(DEFAULT_SESSION)
        saved_sessions = gr.State([])
        checklist_state = gr.State([])

        # Local Storage States
        local_storage = gr.State({})
        current_state_id = gr.State(None)

        # Add logo at the top
        with gr.Row(elem_id="logo-row"):
            gr.Image(value=logo_path, show_label=False, container=False, height=100)

        with gr.Row():
            with gr.Column(scale=2):
                gr.Markdown("# Autism Education Image Description Tool")
                difficulty_label = gr.Markdown("**Current Difficulty:** Very Simple")

                # Add Local Storage UI elements
                with gr.Accordion("Session Management", open=False):
                    with gr.Tabs() as session_tabs:
                        with gr.TabItem("Browser Storage"):
                            gr.Markdown("## Save & Load Sessions in Browser")
                            gr.Markdown("Save your current session or load a previously saved one from browser storage.")

                            with gr.Row():
                                save_state_name = gr.Textbox(
                                    label="Session Name (optional)",
                                    placeholder="Enter a name for this session save",
                                    info="If left blank, the current timestamp will be used"
                                )
                                save_state_btn = gr.Button("💾 Save to Browser")

                            saved_states_list = gr.HTML(
                                label="Browser Saved Sessions",
                                value="<div>No saved sessions found.</div>"
                            )

                            local_storage_status = gr.Markdown("")

                        with gr.TabItem("File System"):
                            gr.Markdown("## Save & Load Sessions from Disk")
                            gr.Markdown("Save your current session or load a previously saved one from the 'Sessions History' folder.")

                            with gr.Row():
                                save_fs_name = gr.Textbox(
                                    label="Session Name (optional)",
                                    placeholder="Enter a name for this session save",
                                    info="If left blank, the current timestamp will be used"
                                )
                                save_fs_btn = gr.Button("💾 Save to Disk")
                                refresh_fs_btn = gr.Button("🔄 Refresh List")

                            # Add dropdown menu for filesystem sessions
                            filesystem_sessions_dropdown = gr.Dropdown(
                                label="Select a session to load",
                                choices=[],
                                interactive=True,
                                elem_id="filesystem-sessions-dropdown"
                            )

                            load_fs_btn = gr.Button("📂 Load Selected Session")
                            delete_fs_btn = gr.Button("🗑️ Delete Selected Session")

                            filesystem_sessions_list = gr.HTML(
                                label="Filesystem Saved Sessions",
                                value="<div>Loading saved sessions from disk...</div>"
                            )

                            filesystem_status = gr.Markdown("")

                with gr.Column():
                    gr.Markdown("## Generate Image")
                    gr.Markdown("Enter the child's details to generate an appropriate educational image.")
                    with gr.Row():
                        age_input = gr.Textbox(label="Child's Age", placeholder="Enter age...", value="3")
                        autism_level_dropdown = gr.Dropdown(label="Autism Level", choices=["Level 1", "Level 2", "Level 3"], value="Level 1")
                    topic_focus_input = gr.Textbox(
                        label="Topic Focus",
                        placeholder="Enter a specific topic or detail to focus on (e.g., 'animals', 'emotions', 'daily routines')...",
                        lines=1
                    )
                    treatment_plan_input = gr.Textbox(
                        label="Treatment Plan",
                        placeholder="Enter the treatment plan to guide the image generation...",
                        lines=2
                    )
                    with gr.Row():
                        attempt_limit_input = gr.Number(label="Allowed Attempts", value=3, precision=0)
                        details_threshold_input = gr.Slider(
                            label="Details Threshold (%)",
                            minimum=10,
                            maximum=100,
                            value=70,
                            step=5,
                            info="Percentage of details needed to advance difficulty"
                        )
                    image_style_dropdown = gr.Dropdown(
                        label="Image Style",
                        choices=IMAGE_STYLES,
                        value="Realistic",
                        info="Select the visual style for the generated image"
                    )
                    generate_btn = gr.Button("Generate Image")
                    img_output = gr.Image(label="Generated Image")
                with gr.Column():
                    gr.Markdown("## Image Description Practice")
                    gr.Markdown(
                        "After generating an image, ask the child to describe what they see. "
                        "Type their description in the box below. The system will provide supportive feedback "
                        "and track their progress in identifying details."
                    )
                    chatbot = gr.Chatbot(label="Conversation History", type='messages')
                    with gr.Row():
                        chat_input = gr.Textbox(label="Child's Description", placeholder="Type what the child says about the image...", show_label=True)
                        send_btn = gr.Button("Submit")
            with gr.Column(scale=1):
                gr.Markdown("## Details to Identify")
                gr.Markdown("The child should try to identify these elements in the image:")
                checklist_html = gr.HTML("""
                    <div id="checklist-container" style="background-color: #000000; color: #ffffff; padding: 15px; border-radius: 8px;">
                        <p>Generate an image to see details to identify.</p>
                    </div>
                """)
                attempt_counter_html = gr.HTML("""
                    <div id="attempt-counter" style="margin-top: 10px; padding: 10px; background-color: #000000; color: #ffffff; border-radius: 5px; border: 1px solid #444;">
                        <p style="margin: 0; font-weight: bold;">Attempts: 0/3</p>
                    </div>
                """)

                progress_html = gr.HTML("""
                    <div id="progress-container" style="background-color: #000000; color: #ffffff; padding: 15px; border-radius: 8px;">
                        <p>No active session.</p>
                    </div>
                """)

        with gr.Row():
            with gr.Column():
                gr.Markdown("## Progress Tracking")
                gr.Markdown(
                    "This section tracks the child's progress across sessions. "
                    "Each session includes the difficulty level, identified details, "
                    "and the full conversation history."
                )
                sessions_output = gr.JSON(label="Session Details", value={})
        with gr.Row():
            with gr.Column():
                gr.Markdown("## Save Options")
                filename_input = gr.Textbox(
                    label="Custom Filename (optional)",
                    placeholder="Enter custom filename or leave blank for default timestamp-based name",
                    info="Files will be saved with this name plus appropriate extensions"
                )

            with gr.Column(scale=1):
                gr.Markdown("## Save Images")
                gr.Markdown("Click the button below to save all images from all sessions to disk.")
                save_images_btn = gr.Button("💾 Save All Session Images")
                save_result = gr.Textbox(label="Save Result", interactive=False)

            with gr.Column(scale=1):
                gr.Markdown("## Save Session Log")
                gr.Markdown("Click the button below to save the complete session log as a JSON file.")
                save_log_btn = gr.Button("📝 Save Session Log")
                save_log_result = gr.Textbox(label="Save Log Result", interactive=False)

            with gr.Column(scale=1):
                gr.Markdown("## Save to Google Drive")
                gr.Markdown("Click to save all sessions and images to Google Drive.")
                save_drive_btn = gr.Button("☁️ Save to Google Drive")
                save_drive_result = gr.Textbox(label="Google Drive Save Result", interactive=False)

        # Hidden localStorage components for Gradio
        localStorage_component = gr.JSON(label="Local Storage Data", visible=False)
        allStatesStorage_component = gr.JSON(label="All States Storage", visible=False)

        # Hidden triggers for filesystem operations
        load_filesystem_trigger = gr.Textbox(
            label="Load Filesystem Session ID",
            elem_id="load-filesystem-trigger",
            visible=False
        )
        delete_filesystem_trigger = gr.Textbox(
            label="Delete Filesystem Session ID",
            elem_id="delete-filesystem-trigger",
            visible=False
        )

        def update_saved_states_display(x):
            """Handle both string and dictionary inputs for generating saved states HTML"""
            try:
                # If x is already a dictionary, use it directly
                if isinstance(x, dict):
                    return generate_saved_states_html(x)
                # If x is a string, try to parse it as JSON
                elif isinstance(x, str) and x:
                    return generate_saved_states_html(json.loads(x))
                # Otherwise, return empty state
                else:
                    return generate_saved_states_html({})
            except Exception as e:
                print(f"Error updating saved states display: {e}")
                return "<div>Error displaying saved sessions. Please try again.</div>"

        def save_current_state(save_name, active_session, saved_sessions, all_states_json):
            """Save the current state to localStorage"""
            try:
                # Handle State objects by extracting their values
                if hasattr(active_session, 'value'):
                    active_session = active_session.value
                if hasattr(saved_sessions, 'value'):
                    saved_sessions = saved_sessions.value
                if hasattr(all_states_json, 'value'):
                    all_states_json = all_states_json.value

                # Load existing states or create new dict
                if isinstance(all_states_json, dict):
                    all_states = all_states_json
                elif isinstance(all_states_json, str) and all_states_json:
                    all_states = json.loads(all_states_json)
                else:
                    all_states = {}

                # Create a unique ID for this state
                import time
                state_id = f"{save_name or 'session'}_{int(time.time())}"

                # Create the state entry
                state_entry = create_new_state_entry(active_session, saved_sessions)

                # Add custom name if provided
                if save_name:
                    state_entry['display_name'] = save_name

                # Add to all states
                all_states[state_id] = state_entry

                # Save back to localStorage - ensure it's a JSON string
                all_states_json = json.dumps(all_states)

                # Generate HTML for the saved states list
                saved_states_html = generate_saved_states_html(all_states)

                return (
                    all_states_json,
                    saved_states_html,
                    "✅ Session saved successfully!",
                    ""  # Clear the name input
                )
            except Exception as e:
                print(f"Error saving state: {e}")
                # Try to generate HTML safely
                try:
                    if isinstance(all_states_json, dict):
                        html = generate_saved_states_html(all_states)
                    elif isinstance(all_states_json, str) and all_states_json:
                        html = generate_saved_states_html(json.loads(all_states_json))
                    else:
                        html = generate_saved_states_html({})
                except:
                    html = "<div>Error displaying saved sessions.</div>"

                return (
                    all_states_json,
                    html,
                    f"❌ Error saving session: {str(e)}",
                    save_name
                )

        def load_saved_state(state_id, all_states_json):
            """Load a saved state by ID"""
            try:
                # Handle State objects
                if hasattr(state_id, 'value'):
                    state_id = state_id.value
                if hasattr(all_states_json, 'value'):
                    all_states_json = all_states_json.value

                # Handle different input types
                if isinstance(all_states_json, dict):
                    all_states = all_states_json
                elif isinstance(all_states_json, str) and all_states_json:
                    all_states = json.loads(all_states_json)
                else:
                    return DEFAULT_SESSION, [], state_id, "❌ No saved states found."

                if state_id not in all_states:
                    return DEFAULT_SESSION, [], None, f"❌ State with ID {state_id} not found."

                state = all_states[state_id]
                active_sess = state.get('active_session', DEFAULT_SESSION)
                saved_sess = state.get('saved_sessions', [])

                # Create HTML for checklist based on active session
                new_checklist = []
                if active_sess and active_sess.get('key_details'):
                    for i, detail in enumerate(active_sess.get('key_details', [])):
                        identified = detail in active_sess.get('identified_details', [])
                        new_checklist.append({"detail": detail, "identified": identified, "id": i})

                # Return the loaded state
                return active_sess, saved_sess, state_id, f"✅ Loaded session from {state.get('timestamp', 'unknown date')}"
            except Exception as e:
                print(f"Error loading state: {e}")
                return DEFAULT_SESSION, [], None, f"❌ Error loading state: {str(e)}"

        def delete_saved_state(state_id, all_states_json):
            """Delete a saved state by ID"""
            try:
                # Handle State objects
                if hasattr(state_id, 'value'):
                    state_id = state_id.value
                if hasattr(all_states_json, 'value'):
                    all_states_json = all_states_json.value

                # Handle different input types
                if isinstance(all_states_json, dict):
                    all_states = all_states_json
                elif isinstance(all_states_json, str) and all_states_json:
                    all_states = json.loads(all_states_json)
                else:
                    return all_states_json, "<div>No saved sessions found.</div>", "❌ No saved states found."

                if state_id not in all_states:
                    return json.dumps(all_states), generate_saved_states_html(all_states), f"❌ State with ID {state_id} not found."

                # Remove the state
                del all_states[state_id]

                # Save back to localStorage
                all_states_json = json.dumps(all_states)

                # Generate HTML for the saved states list
                saved_states_html = generate_saved_states_html(all_states)

                return all_states_json, saved_states_html, "✅ Session deleted successfully!"
            except Exception as e:
                print(f"Error deleting state: {e}")
                return all_states_json, "<div>Error displaying saved sessions.</div>", f"❌ Error deleting session: {str(e)}"

        def auto_save_state(active_session, saved_sessions, current_id, all_states_json):
            try:
                # Handle State objects
                if hasattr(active_session, 'value'):
                    active_session = active_session.value
                if hasattr(saved_sessions, 'value'):
                    saved_sessions = saved_sessions.value
                if hasattr(current_id, 'value'):
                    current_id = current_id.value
                if hasattr(all_states_json, 'value'):
                    all_states_json = all_states_json.value

                # Only save if we have a valid state with an active session
                if not active_session or not active_session.get('prompt'):
                    return all_states_json

                # Handle different input types
                if isinstance(all_states_json, dict):
                    all_states = all_states_json
                elif isinstance(all_states_json, str) and all_states_json:
                    all_states = json.loads(all_states_json)
                else:
                    all_states = {}

                import time
                # Use existing ID or create a new one
                state_id = current_id or f"autosave_{int(time.time())}"

                # Create the state entry
                state_entry = create_new_state_entry(active_session, saved_sessions)
                state_entry['autosave'] = True

                # Add to all states
                all_states[state_id] = state_entry

                # Save back to localStorage - ensure it's a JSON string
                return json.dumps(all_states)
            except Exception as e:
                # On error, don't change the existing storage
                print(f"Auto-save error: {e}")
                return all_states_json

        def load_most_recent_session(all_states_json):
            try:
                # Handle State objects
                if hasattr(all_states_json, 'value'):
                    all_states_json = all_states_json.value

                # Handle different input types
                if isinstance(all_states_json, dict):
                    all_states = all_states_json
                elif isinstance(all_states_json, str) and all_states_json:
                    all_states = json.loads(all_states_json)
                else:
                    return DEFAULT_SESSION, [], None, None

                if not all_states:
                    return DEFAULT_SESSION, [], None, None

                # Find the most recent state
                most_recent = None
                most_recent_time = ""
                most_recent_id = None

                for state_id, state in all_states.items():
                    timestamp = state.get('timestamp', '')
                    if not most_recent or timestamp > most_recent_time:
                        most_recent = state
                        most_recent_time = timestamp
                        most_recent_id = state_id

                if most_recent:
                    active_sess = most_recent.get('active_session', DEFAULT_SESSION)
                    saved_sess = most_recent.get('saved_sessions', [])
                    return active_sess, saved_sess, most_recent_id, most_recent_id

                return DEFAULT_SESSION, [], None, None
            except Exception as e:
                print(f"Error loading recent session: {e}")
                return DEFAULT_SESSION, [], None, None

        def update_filesystem_sessions_dropdown():
            """Update the filesystem sessions dropdown with the latest sessions"""
            sessions_list = list_saved_filesystem_sessions()
            dropdown_choices = []

            for session in sessions_list:
                display_name = session['display_name']
                session_id = session['id']
                dropdown_choices.append((f"{display_name} ({session['sessions_count']} sessions)", session_id))

            return gr.update(choices=dropdown_choices)

        def load_session_and_update_ui(session_id):
            logger.info(f"Loading session ID: {session_id}")
            if not session_id:
                return None, [], "No session ID provided", [], [], None

            # Load the session
            loaded_session_data = load_session_from_filesystem(session_id)
            if not loaded_session_data:
                return DEFAULT_SESSION, [], f"Error loading session from disk with ID: {session_id}", [], [], None

            # Unpack all 4 values returned by load_session_from_filesystem
            active_session_data, saved_sessions_data, message, checklist_items = loaded_session_data

            # Extract chat history
            chat_history = []
            if active_session_data and "chat" in active_session_data:
                chat_history = active_session_data.get("chat", [])

            # Get image - handle path to local file instead of data URL
            image = None
            if active_session_data and "image_file" in active_session_data:
                # Use the direct path to the image file
                image_path = os.path.join("Sessions History", session_id, active_session_data.get("image_file"))
                if os.path.exists(image_path):
                    image = image_path

            return active_session_data, saved_sessions_data, message, checklist_items, chat_history, image

        # Add hidden components to trigger state loading and deletion
        load_state_trigger = gr.Textbox(elem_id="load-state-trigger", visible=False)
        delete_state_trigger = gr.Textbox(elem_id="delete-state-trigger", visible=False)

        # Event handlers for file operations
        save_log_btn.click(
            save_session_log,
            inputs=[saved_sessions, active_session, filename_input],
            outputs=[save_log_result]
        )

        save_images_btn.click(
            save_all_session_images,
            inputs=[saved_sessions, active_session, filename_input],
            outputs=[save_result]
        )

        save_drive_btn.click(
            save_to_google_drive,
            inputs=[saved_sessions, active_session, filename_input],
            outputs=[save_drive_result]
        )

        # Event handlers for local storage
        save_state_btn.click(
            save_current_state,
            inputs=[save_state_name, active_session, saved_sessions, allStatesStorage_component],
            outputs=[allStatesStorage_component, saved_states_list, local_storage_status, save_state_name]
        )

        load_state_trigger.change(
            load_saved_state,
            inputs=[load_state_trigger, allStatesStorage_component],
            outputs=[active_session, saved_sessions, current_state_id, local_storage_status]
        )

        delete_state_trigger.change(
            delete_saved_state,
            inputs=[delete_state_trigger, allStatesStorage_component],
            outputs=[allStatesStorage_component, saved_states_list, local_storage_status]
        )

        # Event handlers for filesystem storage
        save_fs_btn.click(
            save_session_to_filesystem,
            inputs=[active_session, saved_sessions, save_fs_name],
            outputs=[filesystem_status]
        ).then(
            lambda: (update_filesystem_sessions_dropdown(), list_saved_filesystem_sessions(), ""),
            inputs=[],
            outputs=[filesystem_sessions_dropdown, filesystem_sessions_list, save_fs_name]
        )

        refresh_fs_btn.click(
            lambda: (update_filesystem_sessions_dropdown(), generate_filesystem_sessions_html(list_saved_filesystem_sessions()), ""),
            inputs=[],
            outputs=[filesystem_sessions_dropdown, filesystem_sessions_list, filesystem_status]
        )

        # New event handler for the dropdown and load button
        load_fs_btn.click(
            lambda session_id: load_session_and_update_ui(session_id),
            inputs=[filesystem_sessions_dropdown],
            outputs=[active_session, saved_sessions, filesystem_status, checklist_state, chatbot, img_output]
        ).then(
            update_difficulty_label,
            inputs=[active_session],
            outputs=[difficulty_label]
        ).then(
            update_attempt_counter,
            inputs=[active_session],
            outputs=[attempt_counter_html]
        ).then(
            update_checklist_html,
            inputs=[checklist_state],
            outputs=[checklist_html]
        ).then(
            update_progress_html,
            inputs=[checklist_state, active_session],
            outputs=[progress_html]
        )

        # Delete session using dropdown selection
        delete_fs_btn.click(
            lambda session_id: (delete_filesystem_session(session_id), update_filesystem_sessions_dropdown(), generate_filesystem_sessions_html(list_saved_filesystem_sessions())),
            inputs=[filesystem_sessions_dropdown],
            outputs=[filesystem_status, filesystem_sessions_dropdown, filesystem_sessions_list]
        )

        # Handle load and delete from the HTML list also
        load_filesystem_trigger.change(
            load_session_and_update_ui,
            inputs=[load_filesystem_trigger],
            outputs=[active_session, saved_sessions, filesystem_status, checklist_state, chatbot, img_output]
        ).then(
            update_difficulty_label,
            inputs=[active_session],
            outputs=[difficulty_label]
        ).then(
            update_attempt_counter,
            inputs=[active_session],
            outputs=[attempt_counter_html]
        ).then(
            update_checklist_html,
            inputs=[checklist_state],
            outputs=[checklist_html]
        ).then(
            update_progress_html,
            inputs=[checklist_state, active_session],
            outputs=[progress_html]
        )

        delete_filesystem_trigger.change(
            lambda session_id: (delete_filesystem_session(session_id), update_filesystem_sessions_dropdown(), generate_filesystem_sessions_html(list_saved_filesystem_sessions())),
            inputs=[delete_filesystem_trigger],
            outputs=[filesystem_status, filesystem_sessions_dropdown, filesystem_sessions_list]
        )

        # Update saved states display when the component changes
        allStatesStorage_component.change(
            update_saved_states_display,
            inputs=[allStatesStorage_component],
            outputs=[saved_states_list]
        )

        # Load filesystem sessions list and dropdown on startup
        demo.load(
            lambda: (update_filesystem_sessions_dropdown(), generate_filesystem_sessions_html(list_saved_filesystem_sessions())),
            inputs=[],
            outputs=[filesystem_sessions_dropdown, filesystem_sessions_list]
        )

        # Main app functionality
        generate_btn.click(
            generate_image_and_reset_chat,
            inputs=[age_input, autism_level_dropdown, topic_focus_input, treatment_plan_input,
                    attempt_limit_input, details_threshold_input, active_session, saved_sessions, image_style_dropdown],
            outputs=[img_output, active_session, saved_sessions, checklist_state, chatbot]
        ).then(
            lambda active_session: active_session.get("chat", []),
            inputs=[active_session],
            outputs=[chatbot]
        )

        checklist_state.change(
            lambda checklist, active_session: update_progress_html(checklist, active_session),
            inputs=[checklist_state, active_session],
            outputs=[progress_html]
        )

        send_btn.click(
            chat_respond,
            inputs=[chat_input, active_session, saved_sessions, checklist_state],
            outputs=[chat_input, chatbot, saved_sessions, active_session, checklist_state, img_output]
        )
        chat_input.submit(
            chat_respond,
            inputs=[chat_input, active_session, saved_sessions, checklist_state],
            outputs=[chat_input, chatbot, saved_sessions, active_session, checklist_state, img_output]
        )

        checklist_state.change(
            lambda checklist: update_checklist_html(checklist),
            inputs=[checklist_state],
            outputs=[checklist_html]
        )

        active_session.change(
            update_difficulty_label,
            inputs=[active_session],
            outputs=[difficulty_label]
        )
        active_session.change(
            update_attempt_counter,
            inputs=[active_session],
            outputs=[attempt_counter_html]
        )
        active_session.change(
            update_sessions,
            inputs=[saved_sessions, active_session],
            outputs=sessions_output
        )
        saved_sessions.change(
            update_sessions,
            inputs=[saved_sessions, active_session],
            outputs=sessions_output
        )

        # Automatically save state when it changes
        active_session.change(
            auto_save_state,
            inputs=[active_session, saved_sessions, current_state_id, allStatesStorage_component],
            outputs=[allStatesStorage_component]
        )

        saved_sessions.change(
            auto_save_state,
            inputs=[active_session, saved_sessions, current_state_id, allStatesStorage_component],
            outputs=[allStatesStorage_component]
        )

        # Load the most recent session on startup
        demo.load(
            load_most_recent_session,
            inputs=[allStatesStorage_component],
            outputs=[active_session, saved_sessions, current_state_id, current_state_id]
        )

    return demo
