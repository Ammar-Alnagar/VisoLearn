def migrate_chat_history_format(chat_history):
    """
    Migrate old tuple-based chat history to new dictionary format.

    Args:
        chat_history: List of chat messages in old tuple format or new dict format

    Returns:
        list: Chat history in new dictionary format with 'role' and 'content' keys
    """
    if not chat_history:
        return []

    migrated_history = []
    for message in chat_history:
        if isinstance(message, tuple) and len(message) == 2:
            # Old format: ("Child", "message") or ("Teacher", "message")
            role_old, content = message
            if role_old == "Child":
                role_new = "user"
            elif role_old == "Teacher":
                role_new = "assistant"
            elif role_old == "System":
                role_new = "system"
            else:
                role_new = "assistant"  # Default fallback

            migrated_history.append({"role": role_new, "content": content})
        elif isinstance(message, dict) and "role" in message and "content" in message:
            # Already in new format
            migrated_history.append(message)
        else:
            # Unexpected format, skip or handle gracefully
            print(f"Warning: Unexpected chat message format: {message}")
            continue

    return migrated_history
