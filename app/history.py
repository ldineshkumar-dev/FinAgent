import json
import os
from datetime import datetime

HISTORY_FILE = os.path.join('data', 'chat_history.json')
MAX_HISTORY_SIZE = 5

def load_chat_history():
    """Loads the chat history from the JSON file."""
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        # If file is corrupted or unreadable, return empty list
        return []

def save_chat_history(all_chats, current_messages):
    """Saves the current chat to the history file if it's a meaningful conversation."""
    # A "meaningful" conversation has more than the initial AI welcome message
    if len(current_messages) > 1:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Prepend the new chat to the beginning of the list
        all_chats.insert(0, {"timestamp": timestamp, "messages": current_messages})

        # Trim the history to the maximum size
        if len(all_chats) > MAX_HISTORY_SIZE:
            all_chats = all_chats[:MAX_HISTORY_SIZE]

        try:
            with open(HISTORY_FILE, 'w') as f:
                json.dump(all_chats, f, indent=4)
        except IOError as e:
            print(f"Error saving chat history: {e}")
    
    return all_chats
