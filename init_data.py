"""
Initialize data files with dummy data for the Telegram bot.
Run this script once to set up the initial data structure.
"""
import os
import json
from datetime import datetime, timedelta

# Configuration
DATA_DIR = "data"
USERS_FILE = os.path.join(DATA_DIR, "users.json")
CHAT_HISTORY_FILE = os.path.join(DATA_DIR, "chat_history.txt")
COMMAND_LOGS = os.path.join(DATA_DIR, "command_logs.txt")
FEEDBACK_FILE = os.path.join(DATA_DIR, "feedback.json")
REMINDERS_FILE = os.path.join(DATA_DIR, "reminders.json")
BROADCASTS_FILE = os.path.join(DATA_DIR, "broadcasts.json")

# Create data directory if it doesn't exist
os.makedirs(DATA_DIR, exist_ok=True)

def init_users():
    """Initialize users.json with dummy user data."""
    dummy_users = {
        "123456789": {
            "id": 123456789,
            "username": "john_doe",
            "first_name": "John",
            "last_name": "Doe",
            "is_bot": False,
            "language_code": "en",
            "is_premium": True,
            "added_to_attachment_menu": False,
            "can_join_groups": True,
            "can_read_all_group_messages": False,
            "supports_inline_queries": False,
            "role": "admin",
            "first_seen": "2025-09-15T10:30:00+05:30",
            "last_seen": datetime.now().isoformat(),
            "stats": {
                "messages_sent": 42,
                "commands_used": 15,
                "ai_interactions": 27
            },
            "profile": {
                "full_name": "John Doe",
                "username": "john_doe",
                "bio": "Tech enthusiast and bot developer",
                "location": "New York, USA",
                "interests": ["programming", "AI", "robotics"],
                "last_activity": datetime.now().isoformat()
            },
            "chat_mode": False,
            "language": "en",
            "settings": {
                "notifications": True,
                "privacy": {
                    "show_last_seen": True,
                    "show_join_date": True
                }
            },
            "rate_limit": {
                "last_message_time": datetime.now().timestamp(),
                "message_count": 1
            }
        },
        "987654321": {
            "id": 987654321,
            "username": "jane_smith",
            "first_name": "Jane",
            "last_name": "Smith",
            "is_bot": False,
            "language_code": "en",
            "is_premium": False,
            "added_to_attachment_menu": False,
            "can_join_groups": True,
            "can_read_all_group_messages": False,
            "supports_inline_queries": False,
            "role": "user",
            "first_seen": "2025-09-20T14:15:00+05:30",
            "last_seen": datetime.now().isoformat(),
            "stats": {
                "messages_sent": 18,
                "commands_used": 8,
                "ai_interactions": 10
            },
            "profile": {
                "full_name": "Jane Smith",
                "username": "jane_smith",
                "bio": "Digital artist and designer",
                "location": "London, UK",
                "interests": ["art", "design", "photography"],
                "last_activity": datetime.now().isoformat()
            },
            "chat_mode": True,
            "language": "en",
            "settings": {
                "notifications": True,
                "privacy": {
                    "show_last_seen": True,
                    "show_join_date": True
                }
            },
            "rate_limit": {
                "last_message_time": datetime.now().timestamp(),
                "message_count": 1
            }
        }
    }
    
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(dummy_users, f, indent=4, default=str)
    
    print(f"Initialized {USERS_FILE} with {len(dummy_users)} users")

def init_chat_history():
    """Initialize chat_history.txt with sample conversations."""
    sample_chats = [
        "[2025-09-25 10:15:23] User john_doe (123456789): Hello, bot!",
        "[2025-09-25 10:15:25] Bot: Hello John! How can I help you today?",
        "[2025-09-25 10:16:10] User john_doe (123456789): What's the weather like?",
        "[2025-09-25 10:16:15] Bot: I'm sorry, I don't have access to weather information. Is there anything else I can help you with?",
        "[2025-09-25 11:30:45] User jane_smith (987654321): Hi there!",
        "[2025-09-25 11:30:50] Bot: Hello Jane! Nice to see you again!"
    ]
    
    with open(CHAT_HISTORY_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(sample_chats))
    
    print(f"Initialized {CHAT_HISTORY_FILE} with sample conversations")

def init_command_logs():
    """Initialize command_logs.txt with sample command history."""
    sample_logs = [
        "2025-09-25 10:15:23 - User 123456789 used command: /start",
        "2025-09-25 10:15:45 - User 123456789 used command: /chat",
        "2025-09-25 10:16:10 - User 123456789 sent a message",
        "2025-09-25 11:30:45 - User 987654321 used command: /start",
        "2025-09-25 11:31:02 - User 987654321 used command: /profile"
    ]
    
    with open(COMMAND_LOGS, 'w', encoding='utf-8') as f:
        f.write('\n'.join(sample_logs))
    
    print(f"Initialized {COMMAND_LOGS} with sample command history")

def init_feedback():
    """Initialize feedback.json with sample feedback entries."""
    sample_feedback = [
        {
            "id": 1,
            "user_id": 123456789,
            "username": "john_doe",
            "message": "Great bot! Very helpful.",
            "rating": 5,
            "timestamp": "2025-09-25T10:20:00+05:30"
        },
        {
            "id": 2,
            "user_id": 987654321,
            "username": "jane_smith",
            "message": "Could use more features.",
            "rating": 3,
            "timestamp": "2025-09-25T11:35:00+05:30"
        }
    ]
    
    with open(FEEDBACK_FILE, 'w', encoding='utf-8') as f:
        json.dump(sample_feedback, f, indent=4)
    
    print(f"Initialized {FEEDBACK_FILE} with sample feedback")

def init_reminders():
    """Initialize reminders.json with sample reminders."""
    now = datetime.now()
    sample_reminders = [
        {
            "id": 1,
            "user_id": 123456789,
            "message": "Team meeting",
            "reminder_time": (now + timedelta(hours=2)).isoformat(),
            "created_at": now.isoformat(),
            "status": "pending"
        },
        {
            "id": 2,
            "user_id": 987654321,
            "message": "Call mom",
            "reminder_time": (now + timedelta(days=1)).isoformat(),
            "created_at": now.isoformat(),
            "status": "pending"
        }
    ]
    
    with open(REMINDERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(sample_reminders, f, indent=4, default=str)
    
    print(f"Initialized {REMINDERS_FILE} with sample reminders")

def init_broadcasts():
    """Initialize broadcasts.json with sample broadcast history."""
    sample_broadcasts = [
        {
            "id": 1,
            "admin_id": 123456789,
            "admin_username": "john_doe",
            "message": "Server maintenance tonight at 2 AM",
            "timestamp": "2025-09-24T20:00:00+05:30",
            "total_recipients": 2,
            "successful_deliveries": 2,
            "failed_deliveries": 0
        }
    ]
    
    with open(BROADCASTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(sample_broadcasts, f, indent=4, default=str)
    
    print(f"Initialized {BROADCASTS_FILE} with sample broadcast history")

if __name__ == "__main__":
    print("Initializing bot data files...\n")
    init_users()
    init_chat_history()
    init_command_logs()
    init_feedback()
    init_reminders()
    init_broadcasts()
    print("\nAll data files have been initialized successfully!")
