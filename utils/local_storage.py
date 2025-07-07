import json
import time
import base64
from datetime import datetime

def save_state_to_local_storage(state_data):
    """
    Convert the state data to a JSON string and save it to localStorage using gradio's LocalStorage

    Args:
        state_data (dict): A dictionary containing the current state (active_session and saved_sessions)
    """
    try:
        # Convert datetime objects to strings for JSON serialization if needed
        state_json = json.dumps(state_data)
        return state_json
    except Exception as e:
        print(f"Error saving state to local storage: {str(e)}")
        return None

def load_state_from_local_storage(state_json):
    """
    Load and parse the state data from localStorage

    Args:
        state_json (str): JSON string containing the saved state

    Returns:
        dict: The parsed state data or None if there was an error
    """
    try:
        if not state_json:
            return None

        state_data = json.loads(state_json)
        return state_data
    except Exception as e:
        print(f"Error loading state from local storage: {str(e)}")
        return None

def list_saved_states(all_saved_states_json):
    """
    Parse and return a list of all saved states with their metadata

    Args:
        all_saved_states_json (str): JSON string containing all saved states

    Returns:
        list: A list of dictionaries with metadata about each saved state
    """
    try:
        if not all_saved_states_json:
            return []

        all_states = json.loads(all_saved_states_json)

        # Create a list of metadata for each state (timestamp, difficulty, etc.)
        state_list = []
        for state_id, state in all_states.items():
            # Extract key metadata
            active_session = state.get('active_session', {})
            saved_sessions = state.get('saved_sessions', [])

            difficulty = active_session.get('difficulty', 'Unknown')
            timestamp = state.get('timestamp', 'Unknown')

            # Count total sessions
            total_sessions = len(saved_sessions)
            if active_session and active_session.get('prompt'):
                total_sessions += 1

            state_list.append({
                'id': state_id,
                'timestamp': timestamp,
                'difficulty': difficulty,
                'total_sessions': total_sessions,
                'display_name': f"{timestamp} - {difficulty} ({total_sessions} sessions)"
            })

        return sorted(state_list, key=lambda x: x['timestamp'], reverse=True)
    except Exception as e:
        print(f"Error listing saved states: {str(e)}")
        return []

def create_new_state_entry(active_session, saved_sessions):
    """
    Create a new state entry with the current timestamp

    Args:
        active_session (dict): The current active session
        saved_sessions (list): The list of saved sessions

    Returns:
        dict: A new state entry with timestamp
    """
    return {
        'active_session': active_session,
        'saved_sessions': saved_sessions,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
