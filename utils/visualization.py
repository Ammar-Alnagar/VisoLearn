import math

def update_difficulty_label(active_session):
    if hasattr(active_session, 'value'):  # Check if it's a State object
        active_session = active_session.value
    return f"**Current Difficulty:** {active_session.get('difficulty', 'Very Simple')}"

def update_checklist_html(checklist):
    # Add this check at the beginning to handle State object
    if hasattr(checklist, 'value'):  # Check if it's a State object
        checklist = checklist.value

    if not checklist:
        return """
            <div id="checklist-container" style="background-color: #000000; color: #ffffff; padding: 15px; border-radius: 8px;">
                <p>Generate an image to see details to identify.</p>
            </div>
        """

    html_content = """
        <div id="checklist-container" style="background-color: #000000; color: #ffffff; padding: 15px; border-radius: 8px;">
            <style>
                .checklist-item {
                    display: flex;
                    align-items: center;
                    margin-bottom: 10px;
                    padding: 8px;
                    border-radius: 5px;
                    transition: background-color 0.3s;
                }
                .identified {
                    background-color: #1e4620;
                    text-decoration: line-through;
                    color: #7fff7f;
                }
                .not-identified {
                    background-color: #222222;
                    color: #ffffff;
                }
                .checkmark {
                    margin-right: 10px;
                    font-size: 1.2em;
                }
            </style>
    """

    for item in checklist:
        detail = item["detail"]
        identified = item["identified"]
        css_class = "identified" if identified else "not-identified"
        checkmark = "✅" if identified else "❌"
        html_content += f"""
            <div class="checklist-item {css_class}">
                <span class="checkmark">{checkmark}</span>
                <span>{detail}</span>
            </div>
        """

    html_content += """
        </div>
    """
    return html_content

def update_progress_html(checklist, active_session):
    # Add this check at the beginning to handle State object
    if hasattr(checklist, 'value'):  # Check if it's a State object
        checklist = checklist.value

    if hasattr(active_session, 'value'):  # Check if it's a State object
        active_session = active_session.value

    if not checklist:
        return """
            <div id="progress-container" style="background-color: #000000; color: #ffffff; padding: 15px; border-radius: 8px;">
                <p>No active session.</p>
            </div>
        """

    total_items = len(checklist)
    identified_items = sum(1 for item in checklist if item["identified"])
    percentage = (identified_items / total_items) * 100 if total_items > 0 else 0
    progress_bar_width = f"{percentage}%"

    # Calculate threshold
    details_threshold = active_session.get("details_threshold", 0.7)
    threshold_count = math.ceil(total_items * details_threshold)
    threshold_percentage = (threshold_count / total_items) * 100

    html_content = f"""
        <div id="progress-container" style="background-color: #000000; color: #ffffff; padding: 15px; border-radius: 8px;">
            <h3>Progress: {identified_items} / {total_items} details</h3>
            <div style="width: 100%; background-color: #333333; border-radius: 5px; margin-bottom: 10px; position: relative;">
                <div style="width: {progress_bar_width}; height: 24px; background-color: #4CAF50; border-radius: 5px;"></div>
                <div style="position: absolute; top: 0; bottom: 0; left: {threshold_percentage}%; width: 2px; background-color: #ff6b6b;"></div>
                <div style="position: absolute; top: -15px; left: {threshold_percentage - 5}%; color: #ff6b6b; font-weight: bold;">⚠️</div>
            </div>
            <p style="font-size: 14px; text-align: center; color: #dddddd;">
                Need to identify at least {threshold_count} details ({int(details_threshold*100)}%) to advance
            </p>
            <p style="font-size: 16px; font-weight: bold; text-align: center; color: #ffffff;">
    """

    if identified_items >= threshold_count:
        html_content += "🎉 Threshold reached! Ready to advance! 🎉"
    elif percentage >= 75:
        html_content += "Almost there! Keep going!"
    elif percentage >= 50:
        html_content += "Halfway there! You're doing great!"
    elif percentage >= 25:
        html_content += "Good start! Keep looking!"
    else:
        html_content += "Let's find more details!"

    html_content += """
            </p>
        </div>
    """
    return html_content

def update_attempt_counter(active_session):
    if hasattr(active_session, 'value'):  # Check if it's a State object
        active_session = active_session.value
    current_count = active_session.get("attempt_count", 0)
    limit = active_session.get("attempt_limit", 3)
    return f"""
        <div id="attempt-counter" style="margin-top: 10px; padding: 10px; background-color: #000000; color: #ffffff; border-radius: 5px; border: 1px solid #444;">
            <p style="margin: 0; font-weight: bold; text-align: center;">Attempts: {current_count}/{limit}</p>
        </div>
    """
