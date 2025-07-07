import gradio as gr
import os
from utils.visualization import update_difficulty_label, update_checklist_html, update_progress_html, update_attempt_counter
from utils.state_management import generate_image_and_reset_chat, chat_respond, update_sessions
from utils.file_operations import save_all_session_images, save_session_log
from config import DEFAULT_SESSION, IMAGE_STYLES
from ui.story_interface import create_story_tab

def create_interface():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(current_dir, "Compumacy-Logo-Trans2.png")

    with gr.Blocks(css="""
        /* Modern Color Palette */
        :root {
            --primary-color: #667eea;
            --primary-dark: #5a6fd8;
            --secondary-color: #f093fb;
            --accent-color: #4ecdc4;
            --success-color: #10b981;
            --warning-color: #f59e0b;
            --error-color: #ef4444;
            --bg-primary: #0f172a;
            --bg-secondary: #1e293b;
            --bg-card: #334155;
            --text-primary: #f8fafc;
            --text-secondary: #cbd5e1;
            --border-color: #475569;
        }

        /* Global Styles */
        .gradio-container {
            background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
            color: var(--text-primary);
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }

        /* Logo Section */
        #logo-row {
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 2rem 1rem;
            background: linear-gradient(135deg, #000000 0%, #1a1a2e 50%, #16213e 100%);
            border-bottom: 2px solid var(--primary-color);
            box-shadow: 0 4px 20px rgba(102, 126, 234, 0.1);
        }

        #logo-row img {
            max-width: 320px;
            object-fit: contain;
            filter: drop-shadow(0 4px 12px rgba(102, 126, 234, 0.3));
            transition: transform 0.3s ease;
        }

        #logo-row img:hover {
            transform: scale(1.05);
        }

        /* Tab Styling */
        .tab-nav {
            background: var(--bg-card);
            border-radius: 12px 12px 0 0;
            padding: 0.5rem;
            margin-bottom: 0;
        }

        /* Card Components */
        .modern-card {
            background: var(--bg-card);
            border-radius: 16px;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            border: 1px solid var(--border-color);
            transition: all 0.3s ease;
        }

        .modern-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 12px 40px rgba(102, 126, 234, 0.2);
            border-color: var(--primary-color);
        }

        /* Button Enhancements */
        .primary-btn {
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            border: none;
            border-radius: 12px;
            padding: 12px 24px;
            color: white;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }

        .primary-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
        }

        /* Input Field Enhancements */
        .modern-input {
            background: var(--bg-secondary);
            border: 2px solid var(--border-color);
            border-radius: 12px;
            padding: 12px 16px;
            color: var(--text-primary);
            transition: all 0.3s ease;
        }

        .modern-input:focus {
            border-color: var(--primary-color);
            box-shadow: 0 0 20px rgba(102, 126, 234, 0.3);
            outline: none;
        }

        /* Progress Indicators */
        .progress-container {
            background: var(--bg-card);
            border-radius: 12px;
            padding: 1.5rem;
            border: 1px solid var(--border-color);
        }

        .progress-bar {
            height: 8px;
            background: var(--bg-secondary);
            border-radius: 4px;
            overflow: hidden;
            margin: 1rem 0;
        }

        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, var(--primary-color), var(--accent-color));
            border-radius: 4px;
            transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
        }

        /* Status Badges */
        .status-badge {
            display: inline-flex;
            align-items: center;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-size: 0.875rem;
            font-weight: 600;
            margin: 0.25rem;
        }

        .status-success {
            background: rgba(16, 185, 129, 0.2);
            color: var(--success-color);
            border: 1px solid var(--success-color);
        }

        .status-warning {
            background: rgba(245, 158, 11, 0.2);
            color: var(--warning-color);
            border: 1px solid var(--warning-color);
        }

        .status-error {
            background: rgba(239, 68, 68, 0.2);
            color: var(--error-color);
            border: 1px solid var(--error-color);
        }

        /* Responsive Design */
        @media (max-width: 768px) {
            .modern-card {
                padding: 1rem;
                margin: 0.5rem 0;
            }

            #logo-row {
                padding: 1rem;
            }

            #logo-row img {
                max-width: 250px;
            }
        }

        /* Animations */
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .fade-in-up {
            animation: fadeInUp 0.6s ease-out;
        }

        /* Loading States */
        .loading-spinner {
            border: 3px solid var(--bg-secondary);
            border-top: 3px solid var(--primary-color);
            border-radius: 50%;
            width: 24px;
            height: 24px;
            animation: spin 1s linear infinite;
            display: inline-block;
            margin-right: 8px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    """) as demo:
        active_session = gr.State(DEFAULT_SESSION)
        saved_sessions = gr.State([])
        checklist_state = gr.State([])

        with gr.Row(elem_id="logo-row"):
            gr.Image(value=logo_path, show_label=False, container=False, height=100)

        with gr.Tabs(selected=0) as tabs:
            with gr.TabItem("📚 Story Sequence Generator"):
                with gr.Column(elem_classes="fade-in-up"):
                    create_story_tab()

            with gr.TabItem("🎨 Image Description Practice", visible=False):
                # Header Section
                with gr.Row(elem_classes="fade-in-up"):
                    with gr.Column():
                        gr.Markdown("""
                        # 🧩 Autism Education Image Description Tool

                        **Empowering communication through visual learning**

                        This interactive tool helps children with autism develop descriptive language skills through structured image analysis and supportive feedback.
                        """)

                # Status Dashboard
                with gr.Row(elem_classes="modern-card fade-in-up"):
                    with gr.Column(scale=1):
                        difficulty_label = gr.Markdown("### 🎯 Current Difficulty: Very Simple")
                    with gr.Column(scale=1):
                        session_status = gr.Markdown("### 📊 Session Status: Ready")
                    with gr.Column(scale=1):
                        completion_rate = gr.Markdown("### ✨ Progress: 0%")

                with gr.Row():
                    with gr.Column(scale=2):
                        with gr.Column(elem_classes="modern-card"):
                            gr.Markdown("## 🖼️ Image Generation")
                            gr.Markdown("**Configure learning parameters to generate personalized educational content**")
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
                                    info="Level 1: Requiring support | Level 2: Substantial support | Level 3: Very substantial support"
                                )
                            topic_focus_input = gr.Textbox(
                                label="🎯 Learning Focus",
                                placeholder="Enter learning objectives (e.g., 'animals', 'emotions', 'daily routines', 'social situations')...",
                                lines=1,
                                elem_classes="modern-input",
                                info="Specify the educational theme for targeted learning"
                            )
                            treatment_plan_input = gr.Textbox(
                                label="📋 Therapeutic Goals",
                                placeholder="Describe specific therapeutic objectives and communication goals...",
                                lines=2,
                                elem_classes="modern-input",
                                info="Guide the AI to create content aligned with therapy objectives"
                            )
                            with gr.Row():
                                attempt_limit_input = gr.Number(
                                    label="🔢 Allowed Attempts",
                                    value=3,
                                    precision=0,
                                    minimum=1,
                                    maximum=100,
                                    info="Number of attempts before moving to next level"
                                )
                            with gr.Row():
                                image_style_dropdown = gr.Dropdown(
                                    label="🎨 Visual Style",
                                    choices=IMAGE_STYLES,
                                    value="Modern Digital Comic",
                                    info="Choose the artistic style that best suits the learning objective"
                                )
                                voice_options = ["en-US-JennyNeural", "en-US-GuyNeural", "en-GB-SoniaNeural", "en-AU-NatashaNeural"]
                                voice_dropdown = gr.Dropdown(
                                    label="🔊 Voice Assistant",
                                    choices=voice_options,
                                    value="en-US-JennyNeural",
                                    info="Select preferred voice for audio feedback"
                                )

                            generate_btn = gr.Button(
                                "✨ Generate Learning Image",
                                elem_classes="primary-btn",
                                size="lg"
                            )
                            img_output = gr.Image(
                                label="🖼️ Generated Learning Image",
                                elem_classes="modern-card"
                            )

                        with gr.Column(elem_classes="modern-card"):
                            gr.Markdown("## 💬 Interactive Learning Session")
                            gr.Markdown("""
                                **How it works:**
                                1. 🖼️ Generate an educational image tailored to the child's needs
                                2. 👀 Encourage the child to observe and describe what they see
                                3. 💭 Type their responses in the chat below
                                4. 🎉 Receive immediate, supportive feedback and progress tracking

                                *The AI provides gentle guidance and celebrates every effort!*
                            """)
                            chatbot = gr.Chatbot(
                                label="💬 Learning Conversation",
                                type="messages",
                                height=400,
                                elem_classes="modern-card",
                                show_copy_button=True
                            )
                            with gr.Row():
                                chat_input = gr.Textbox(
                                    label="Child's Response",
                                    placeholder="Type what the child describes about the image...",
                                    show_label=True,
                                    elem_classes="modern-input",
                                    lines=2
                                )
                                send_btn = gr.Button(
                                    "📤 Send",
                                    elem_classes="primary-btn",
                                    size="lg"
                                )
                    with gr.Column(scale=1):
                        with gr.Column(elem_classes="modern-card"):
                            gr.Markdown("## 🎯 Learning Objectives")
                            gr.Markdown("**Help the child identify these key elements:**")
                            checklist_html = gr.HTML("""
                                <div class="progress-container">
                                    <div style="text-align: center; padding: 2rem;">
                                        <div class="loading-spinner" style="margin: 0 auto 1rem;"></div>
                                        <p style="color: var(--text-secondary);">Generate an image to see learning objectives</p>
                                    </div>
                                </div>
                            """)

                        with gr.Column(elem_classes="modern-card"):
                            gr.Markdown("## 📊 Session Progress")
                            attempt_counter_html = gr.HTML("""
                                <div class="status-badge status-warning">
                                    <span>🔄 Attempts: 0/3</span>
                                </div>
                            """)

                            progress_html = gr.HTML("""
                                <div class="progress-container">
                                    <div style="text-align: center; padding: 1.5rem;">
                                        <p style="color: var(--text-secondary);">Ready to start learning session</p>
                                        <div class="progress-bar">
                                            <div class="progress-fill" style="width: 0%"></div>
                                        </div>
                                        <small style="color: var(--text-secondary);">Progress: 0%</small>
                                    </div>
                                </div>
                            """)

                with gr.Row(elem_classes="modern-card fade-in-up"):
                    with gr.Column():
                        gr.Markdown("## 📈 Progress Analytics")
                        gr.Markdown("""
                            **Comprehensive learning insights and session tracking**

                            Track the child's communication development across multiple sessions.
                            View detailed analytics including difficulty progression, response quality,
                            and therapeutic goal achievements.
                        """)
                        sessions_output = gr.JSON(
                            label="📋 Detailed Session Data",
                            value={},
                            elem_classes="modern-card"
                        )
                # Export and Save Section
                with gr.Row(elem_classes="modern-card fade-in-up"):
                    with gr.Column():
                        gr.Markdown("## 💾 Export & Save Options")
                        gr.Markdown("**Preserve learning progress and therapeutic insights**")

                        filename_input = gr.Textbox(
                            label="📝 Custom Filename",
                            placeholder="Enter custom filename or leave blank for auto-generated name",
                            info="Files will be saved with timestamps and appropriate extensions",
                            elem_classes="modern-input"
                        )

                with gr.Row():
                    with gr.Column(scale=1, elem_classes="modern-card"):
                        gr.Markdown("### 🖼️ Save Images")
                        gr.Markdown("Export all generated learning images for offline use and portfolio documentation.")
                        save_images_btn = gr.Button(
                            "💾 Export All Images",
                            elem_classes="primary-btn"
                        )
                        save_result = gr.Textbox(
                            label="Export Status",
                            interactive=False,
                            elem_classes="modern-input"
                        )

                    with gr.Column(scale=1, elem_classes="modern-card"):
                        gr.Markdown("### 📊 Save Session Data")
                        gr.Markdown("Export comprehensive session logs including conversations, progress metrics, and therapeutic insights.")
                        save_log_btn = gr.Button(
                            "📝 Export Session Data",
                            elem_classes="primary-btn"
                        )
                        save_log_result = gr.Textbox(
                            label="Export Status",
                            interactive=False,
                            elem_classes="modern-input"
                        )

                    with gr.Column(scale=1, elem_classes="modern-card"):
                        gr.Markdown("### ☁️ Cloud Backup")
                        gr.Markdown("Securely backup all session data and images to Google Drive for easy access and sharing.")
                        save_drive_btn = gr.Button(
                            "☁️ Backup to Cloud",
                            elem_classes="primary-btn"
                        )
                        save_drive_result = gr.Textbox(
                            label="Backup Status",
                            interactive=False,
                            elem_classes="modern-input"
                        )

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
                    lambda sessions, active: "This function has been moved to the Story Sequence Generator tab.",
                    inputs=[saved_sessions, active_session],
                    outputs=[save_drive_result]
                )

                generate_btn.click(
                    generate_image_and_reset_chat,
                    inputs=[age_input, autism_level_dropdown, topic_focus_input, treatment_plan_input,
                            attempt_limit_input, active_session, saved_sessions, image_style_dropdown],
                    outputs=[img_output, active_session, saved_sessions, checklist_state]
                )

                checklist_state.change(
                    update_progress_html,
                    inputs=[checklist_state, active_session],
                    outputs=[progress_html]
                )

                def chat_respond_wrapper(user_message, active_session, saved_sessions, checklist, voice):
                    """Wrapper function that handles voice selection and chat response"""
                    # Set the voice preference for TTS
                    set_voice(voice)

                    # Call the original chat_respond function
                    return chat_respond(user_message, active_session, saved_sessions, checklist)

                # Modify your button click handlers to use the wrapper:
                send_btn.click(
                    chat_respond_wrapper,
                    inputs=[chat_input, active_session, saved_sessions, checklist_state, voice_dropdown],
                    outputs=[chat_input, chatbot, saved_sessions, active_session, checklist_state, img_output]
                )

                chat_input.submit(
                    chat_respond_wrapper,
                    inputs=[chat_input, active_session, saved_sessions, checklist_state, voice_dropdown],
                    outputs=[chat_input, chatbot, saved_sessions, active_session, checklist_state, img_output]
                )
                checklist_state.change(
                    update_checklist_html,
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



    return demo

def set_voice(voice):
    """
    Sets the voice for text-to-speech. This is a no-op placeholder since we're not using
    the text-to-speech functionality.

    Args:
        voice: The voice identifier (not used)
    """
    # This is intentionally left empty since we're not using text-to-speech
    pass
