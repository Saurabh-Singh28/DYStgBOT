#!/usr/bin/env python3
"""
Telegram Bot with AI Chat and Admin Features

Features:
- Basic commands: /start, /help, /contact
- AI Chat mode with /chat command
- Hidden admin commands
- File-based storage for user data and chat history
- User mention in group chats
"""

import os
import json
import logging
import random
import time
import asyncio
import pytz
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Set, Any
from enum import Enum
from dotenv import load_dotenv
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    ReplyKeyboardMarkup, ReplyKeyboardRemove, InputMediaPhoto
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters,
    ContextTypes, CallbackContext, CallbackQueryHandler,
    JobQueue, Job, ConversationHandler
)

# Load environment variables
load_dotenv()

# Conversation states for profile management
PROFILE, EDIT_CHOICE, EDIT_VALUE = range(3)

# Enums
class UserRole(Enum):
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"

# Configuration from environment variables
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
ADMIN_IDS = [int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]
MODERATOR_IDS = [int(x.strip()) for x in os.getenv("MODERATOR_IDS", "").split(",") if x.strip()]

# AI Configuration
AI_ENABLED = os.getenv("AI_ENABLED", "True").lower() == "true"
AI_PROVIDER = os.getenv("AI_PROVIDER", "openai")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
AI_MODEL = os.getenv("AI_MODEL", "gpt-3.5-turbo")
AI_TEMPERATURE = float(os.getenv("AI_TEMPERATURE", "0.7"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "1000"))

# Import AI modules if enabled
openai_client = None
if AI_ENABLED and AI_PROVIDER == "openai":
    try:
        from openai import OpenAI
        if OPENAI_API_KEY:
            openai_client = OpenAI(api_key=OPENAI_API_KEY)
        else:
            print("Warning: OPENAI_API_KEY not set. AI features will be disabled.")
            AI_ENABLED = False
    except ImportError:
        print("Warning: openai package not installed. Install with: pip install openai"
              "\nAI features will be disabled.")
        AI_ENABLED = False

DATA_DIR = os.getenv("DATA_DIR", "data")
USERS_FILE = os.path.join(DATA_DIR, "users.json")
CHAT_HISTORY_FILE = os.path.join(DATA_DIR, "chat_history.txt")
COMMAND_LOGS = os.path.join(DATA_DIR, "command_logs.txt")
FEEDBACK_FILE = os.path.join(DATA_DIR, "feedback.json")
REMINDERS_FILE = os.path.join(DATA_DIR, "reminders.json")
BROADCASTS_FILE = os.path.join(DATA_DIR, "broadcasts.json")

# Rate limiting
RATE_LIMIT = {
    'default': {'limit': int(os.getenv("RATE_LIMIT_DEFAULT", "10")), 
                'per_seconds': int(os.getenv("RATE_LIMIT_WINDOW", "60"))},
    'admin': {'limit': int(os.getenv("RATE_LIMIT_ADMIN", "30")), 
              'per_seconds': int(os.getenv("RATE_LIMIT_WINDOW", "60"))},
}

# Supported languages with their respective translations
LANGUAGES = {
    'en': {
        'welcome': '👋 Hello {}! Welcome to our bot!',
        'help': '🤖 *Available Commands:*',
        'admin_commands': '👑 *Admin Commands:*',
        'moderator_commands': '🔧 *Moderator Commands:*',
        'user_commands': '👤 *User Commands:*',
    },
    'es': {
        'welcome': '👋 ¡Hola {}! ¡Bienvenido a nuestro bot!',
        'help': '🤖 *Comandos disponibles:*',
        'admin_commands': '👑 *Comandos de administrador:*',
        'moderator_commands': '🔧 *Comandos de moderador:*',
        'user_commands': '👤 *Comandos de usuario:*',
    },
    # Add more languages as needed
}

# Default language
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "en")

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Ensure data directory and files exist
os.makedirs(DATA_DIR, exist_ok=True)
for file_path in [USERS_FILE, CHAT_HISTORY_FILE, COMMAND_LOGS, FEEDBACK_FILE, REMINDERS_FILE, BROADCASTS_FILE]:
    if not os.path.exists(file_path):
        with open(file_path, 'w', encoding='utf-8') as f:
            if file_path.endswith('.json'):
                if 'reminders' in file_path or 'broadcasts' in file_path:
                    json.dump([], f, ensure_ascii=False, indent=2)
                else:
                    json.dump({}, f, ensure_ascii=False, indent=2)
            else:
                f.write('')

def get_ai_response(user_input: str, user_id: int) -> str:
    """
    Get a response from the configured AI provider.
    
    Args:
        user_input (str): The user's input message
        user_id (int): Telegram user ID for context
        
    Returns:
        str: The AI's response
    """
    if not AI_ENABLED:
        return "⚠️ AI features are currently disabled. Please contact the bot administrator."
    
    user_data = get_user_data(user_id)
    
    try:
        if AI_PROVIDER == "openai":
            # Get user context for more personalized responses
            user_context = (
                f"You are chatting with {user_data.get('profile', {}).get('full_name', 'a user')}. "
                f"Their interests include: {', '.join(user_data.get('profile', {}).get('interests', [])) or 'not specified'}. "
                f"They are from {user_data.get('profile', {}).get('location', 'an unknown location')}."
            )
            
            # Create messages with context
            messages = [
                {"role": "system", "content": "You are a helpful AI assistant in a Telegram bot. "
                                           "Be concise, friendly, and helpful in your responses."},
                {"role": "system", "content": user_context},
                {"role": "user", "content": user_input}
            ]
            
            # Call the OpenAI API using new client
            response = openai_client.chat.completions.create(
                model=AI_MODEL,
                messages=messages,
                temperature=AI_TEMPERATURE,
                max_tokens=MAX_TOKENS
            )
            
            # Extract and return the response
            return response.choices[0].message.content.strip()
            
        elif AI_PROVIDER == "custom":
            # Add your custom AI provider integration here
            return "🤖 Custom AI integration not yet implemented."
            
        else:
            return "⚠️ Invalid AI provider configured."
            
    except Exception as e:
        logger.error(f"Error in get_ai_response: {str(e)}")
        return "⚠️ Sorry, I encountered an error processing your request. Please try again later."

def log_command(user_id: int, command: str) -> None:
    """Log command usage."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(COMMAND_LOGS, 'a', encoding='utf-8') as f:
        f.write(f"{timestamp} - User {user_id} used command: {command}\n")

def save_chat_history(user_id: int, username: str, message: str, is_bot: bool = False) -> None:
    """Save chat history to file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sender = "Bot" if is_bot else f"User {username} ({user_id})"
    with open(CHAT_HISTORY_FILE, 'a', encoding='utf-8') as f:
        f.write(f"[{timestamp}] {sender}: {message}\n")

def get_user_data(user_id: int) -> dict:
    """Get user data from storage with default values."""
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            users = json.load(f)
        
        user_id_str = str(user_id)
        if user_id_str not in users:
            users[user_id_str] = {
                "chat_mode": False,
                "first_seen": datetime.now().isoformat(),
                "last_seen": datetime.now().isoformat(),
                "message_count": 0,
                "language": DEFAULT_LANGUAGE,
                "role": UserRole.ADMIN.value if user_id in ADMIN_IDS 
                         else UserRole.MODERATOR.value if user_id in MODERATOR_IDS 
                         else UserRole.USER.value,
                "profile": {
                    "full_name": "",
                    "username": "",
                    "bio": "",
                    "location": "",
                    "interests": [],
                    "preferred_topics": [],
                    "last_activity": datetime.now().isoformat()
                },
                "settings": {
                    "notifications": True,
                    "daily_digest": False,
                    "privacy": {
                        "show_last_seen": True,
                        "show_join_date": True,
                        "show_activity_stats": True
                    },
                    "theme": "system"  # system/light/dark
                },
                "stats": {
                    "commands_used": 0,
                    "messages_sent": 0,
                    "media_sent": 0,
                    "stickers_sent": 0,
                    "voice_messages": 0,
                    "active_days": 1,
                    "last_command": None,
                    "last_command_time": None,
                    "favorite_commands": {}
                },
                "rate_limit": {
                    "count": 0,
                    "last_reset": time.time()
                },
                "achievements": {
                    "welcome": False,
                    "early_adopter": False,
                    "active_user": False,
                    "feedback_provider": False,
                    "power_user": False
                },
                "metadata": {
                    "referral_code": "",
                    "referred_by": "",
                    "devices": [],
                    "timezone": "UTC"
                }
            }
            save_all_users(users)
        
        return users[user_id_str]
    except Exception as e:
        logger.error(f"Error reading user data: {e}")
        return {
            "chat_mode": False,
            "first_seen": datetime.now().isoformat(),
            "last_seen": datetime.now().isoformat(),
            "message_count": 0,
            "language": DEFAULT_LANGUAGE,
            "role": UserRole.USER.value,
            "settings": {"notifications": True, "daily_digest": False},
            "stats": {"commands_used": 0, "messages_sent": 0, "last_command": None, "last_command_time": None},
            "rate_limit": {"count": 0, "last_reset": time.time()}
        }

def save_all_users(users_data: dict) -> None:
    """Save all users data to storage."""
    try:
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users_data, f, indent=4, ensure_ascii=False, default=str)
    except Exception as e:
        logger.error(f"Error saving all users data: {e}")

def save_user_data(user_id: int, data: dict) -> None:
    """Save user data to storage."""
    try:
        with open(USERS_FILE, 'r+', encoding='utf-8') as f:
            users = json.load(f)
            users[str(user_id)] = data
            save_all_users(users)
    except Exception as e:
        logger.error(f"Error saving user data: {e}")

def get_all_users() -> dict:
    """Get all users data."""
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error getting all users: {e}")
        return {}

def is_admin(user_id: int) -> bool:
    """Check if user is an admin."""
    user_data = get_user_data(user_id)
    return user_data.get('role') == UserRole.ADMIN.value or user_id in ADMIN_IDS

def is_moderator(user_id: int) -> bool:
    """Check if user is a moderator or admin."""
    user_data = get_user_data(user_id)
    return (user_data.get('role') in [UserRole.MODERATOR.value, UserRole.ADMIN.value] or 
            user_id in MODERATOR_IDS or 
            user_id in ADMIN_IDS)

def check_rate_limit(user_id: int) -> bool:
    """Check if user has exceeded rate limit."""
    user_data = get_user_data(user_id)
    role = 'admin' if is_admin(user_id) else 'default'
    limit = RATE_LIMIT[role]['limit']
    per_seconds = RATE_LIMIT[role]['per_seconds']
    
    now = time.time()
    rate_data = user_data.get('rate_limit', {'count': 0, 'last_reset': now})
    
    # Reset counter if time window has passed
    if now - rate_data['last_reset'] > per_seconds:
        rate_data['count'] = 0
        rate_data['last_reset'] = now
    
    # Check rate limit
    if rate_data['count'] >= limit:
        return False
    
    # Increment counter
    rate_data['count'] += 1
    user_data['rate_limit'] = rate_data
    save_user_data(user_id, user_data)
    return True

# Command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message when the command /start is issued."""
    user = update.effective_user
    user_data = get_user_data(user.id)
    
    if not user_data.get('first_seen'):
        user_data['first_seen'] = datetime.now().isoformat()
        save_user_data(user.id, user_data)
    
    welcome_text = (
        f"👋 Hello {user.mention_markdown_v2()}!\n\n"
        "I'm your friendly AI bot! Here's what I can do:\n"
        "• Use /help to see available commands\n"
        "• Use /chat to start AI chat mode\n"
        "• Use /contact to get in touch"
    )
    
    await update.message.reply_markdown_v2(welcome_text)
    log_command(user.id, "/start")

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show user profile and edit options."""
    user = update.effective_user
    user_data = get_user_data(user.id)
    
    # Update user's profile with current Telegram info if empty
    if not user_data['profile']['full_name']:
        user_data['profile'].update({
            'full_name': f"{user.first_name} {user.last_name or ''}".strip(),
            'username': user.username or "",
            'last_activity': datetime.now().isoformat()
        })
        save_user_data(user.id, user_data)
    
    # Format profile information
    profile_text = (
        f"👤 *{user_data['profile']['full_name']}*"
        f"{f' (@{user_data['profile']['username']})' if user_data['profile']['username'] else ''}\n\n"
        f"🆔 User ID: `{user.id}`\n"
        f"📅 Member since: {datetime.fromisoformat(user_data['first_seen']).strftime('%Y-%m-%d %H:%M')}\n"
        f"🌐 Language: {user_data['language'].upper()}\n"
        f"📝 Bio: {user_data['profile']['bio'] or 'Not set'}\n"
        f"📍 Location: {user_data['profile']['location'] or 'Not set'}\n"
        f"🎯 Interests: {', '.join(user_data['profile']['interests']) or 'None'}\n"
        f"📊 Messages sent: {user_data['stats']['messages_sent']}\n"
        f"📱 Last seen: {datetime.fromisoformat(user_data['last_seen']).strftime('%Y-%m-%d %H:%M')}"
    )
    
    # Create inline keyboard for profile actions
    keyboard = [
        [InlineKeyboardButton("✏️ Edit Profile", callback_data="edit_profile")],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            profile_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            profile_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    return PROFILE

async def edit_profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show edit profile options."""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("📝 Bio", callback_data="edit_bio")],
        [InlineKeyboardButton("📍 Location", callback_data="edit_location")],
        [InlineKeyboardButton("🎯 Interests", callback_data="edit_interests")],
        [InlineKeyboardButton("🔙 Back to Profile", callback_data="back_to_profile")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "What would you like to edit?",
        reply_markup=reply_markup
    )
    
    return EDIT_CHOICE

async def handle_edit_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle the user's choice of what to edit."""
    query = update.callback_query
    await query.answer()
    
    choice = query.data
    
    if choice == "edit_bio":
        await query.edit_message_text("✏️ Please enter your new bio (max 500 characters):")
        context.user_data['editing'] = 'bio'
    elif choice == "edit_location":
        await query.edit_message_text("📍 Please enter your location (e.g., City, Country):")
        context.user_data['editing'] = 'location'
    elif choice == "edit_interests":
        await query.edit_message_text("🎯 Please enter your interests, separated by commas (e.g., music, sports, reading):")
        context.user_data['editing'] = 'interests'
    elif choice == "back_to_profile":
        await profile(update, context)
        return PROFILE
    
    return EDIT_VALUE

async def save_profile_edit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Save the edited profile information."""
    user = update.effective_user
    user_data = get_user_data(user.id)
    field = context.user_data.get('editing')
    value = update.message.text.strip()
    
    if field == 'bio':
        if len(value) > 500:
            await update.message.reply_text("❌ Bio is too long! Maximum 500 characters.")
            return EDIT_VALUE
        user_data['profile']['bio'] = value
        await update.message.reply_text("✅ Bio updated successfully!")
    elif field == 'location':
        if len(value) > 100:
            await update.message.reply_text("❌ Location is too long! Maximum 100 characters.")
            return EDIT_VALUE
        user_data['profile']['location'] = value
        await update.message.reply_text("📍 Location updated successfully!")
    elif field == 'interests':
        interests = [i.strip() for i in value.split(',') if i.strip()]
        if len(interests) > 10:
            await update.message.reply_text("❌ You can have a maximum of 10 interests.")
            return EDIT_VALUE
        if any(len(interest) > 30 for interest in interests):
            await update.message.reply_text("❌ Each interest must be 30 characters or less.")
            return EDIT_VALUE
        user_data['profile']['interests'] = interests
        await update.message.reply_text(f"🎯 Updated {len(interests)} interests!")
    
    # Update last activity
    user_data['profile']['last_activity'] = datetime.now().isoformat()
    
    # Save the updated profile
    save_user_data(user.id, user_data)
    
    # Show the updated profile
    await profile(update, context)
    return PROFILE

async def cancel_profile_edit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the profile editing process."""
    await update.message.reply_text("❌ Profile editing cancelled.")
    return await profile(update, context)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    user = update.effective_user
    user_data = get_user_data(user.id)
    lang = user_data.get('language', DEFAULT_LANGUAGE)
    
    # Base commands available to all users
    help_text = f"{LANGUAGES.get(lang, LANGUAGES[DEFAULT_LANGUAGE])['help']}\n\n"
    help_text += "• /start - Show welcome message\n"
    help_text += "• /help - Show this help message\n"
    help_text += "• /profile - View and edit your profile\n"
    help_text += "• /chat - Start AI chat mode\n"
    help_text += "• /contact - Contact information\n"
    help_text += "• /feedback - Send us your feedback\n"
    help_text += "• /language - Change language\n"
    help_text += "• /remindme - Set a reminder\n"
    help_text += "• /myinfo - Show your information\n"
    
    # Add moderator commands if user is moderator
    if is_moderator(user.id):
        help_text += f"\n{LANGUAGES.get(lang, LANGUAGES[DEFAULT_LANGUAGE])['moderator_commands']}\n"
        help_text += "• /broadcast - Send message to all users\n"
        help_text += "• /userinfo - Get user information\n"
    
    # Add admin commands if user is admin
    if is_admin(user.id):
        help_text += f"\n{LANGUAGES.get(lang, LANGUAGES[DEFAULT_LANGUAGE])['admin_commands']}\n"
        help_text += "• /stats - Show bot statistics\n"
        help_text += "• /export - Export user data\n"
        help_text += "• /announce - Make an announcement\n"
    
    # Create keyboard with quick actions
    keyboard = [
        [InlineKeyboardButton("💬 Start Chat", callback_data="start_chat"),
         InlineKeyboardButton("📝 Feedback", callback_data="give_feedback")],
        [InlineKeyboardButton("⚙️ Settings", callback_data="settings")]
    ]
    
    if is_moderator(user.id):
        keyboard.append([InlineKeyboardButton("👥 User Management", callback_data="user_management")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        help_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    log_command(user.id, "/help")

async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send contact information."""
    contact_info = (
        "📧 *Contact Information*\n\n"
        "For support or questions, please contact:\n"
        "• Email: sanataniking280@gmail.com\n"
        "• Telegram: tg://user?id=5239347550"
    )
    
    await update.message.reply_markdown_v2(contact_info)
    log_command(update.effective_user.id, "/contact")

async def chat_mode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Enable AI chat mode for the user."""
    user = update.effective_user
    user_data = get_user_data(user.id)
    user_data['chat_mode'] = True
    save_user_data(user.id, user_data)
    
    await update.message.reply_text(
        "💬 *AI Chat Mode Activated*\n\n"
        "You're now chatting with the AI! Send any message and I'll respond.\n"
        "Type /endchat to exit chat mode.",
        parse_mode='Markdown'
    )
    log_command(user.id, "/chat")

async def end_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Disable AI chat mode for the user."""
    user = update.effective_user
    user_data = get_user_data(user.id)
    user_data['chat_mode'] = False
    save_user_data(user.id, user_data)
    
    await update.message.reply_text(
        "👋 *AI Chat Mode Deactivated*\n\n"
        "You've exited chat mode. Type /chat to start again.",
        parse_mode='Markdown'
    )
    log_command(user.id, "/endchat")

# Hidden commands (not shown in /help)
async def owner(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Hidden command to show bot owner information."""
    user = update.effective_user
    if user.id in ADMIN_IDS:
        await update.message.reply_text(
            "👑 *Bot Owner Commands*\n\n"
            "• /status - Show bot status\n"
            "• /users - Show user statistics",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text("🔒 You don't have permission to use this command.")
    log_command(user.id, "/owner (hidden)")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show bot status (admin only)."""
    user = update.effective_user
    if user.id in ADMIN_IDS:
        try:
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                users = json.load(f)
            total_users = len(users)
            
            with open(COMMAND_LOGS, 'r', encoding='utf-8') as f:
                total_commands = len(f.readlines())
                
            status_text = (
                "📊 *Bot Status*\n\n"
                f"• Total Users: {total_users}\n"
                f"• Commands Processed: {total_commands}\n"
                f"• Uptime: {get_uptime()}"
            )
            await update.message.reply_markdown_v2(status_text)
        except Exception as e:
            await update.message.reply_text(f"❌ Error getting status: {str(e)}")
    else:
        await update.message.reply_text("🔒 You don't have permission to use this command.")
    log_command(user.id, "/status (hidden)")

def get_uptime() -> str:
    """Get bot uptime."""
    if not hasattr(get_uptime, 'start_time'):
        get_uptime.start_time = datetime.now()
    
    uptime = datetime.now() - get_uptime.start_time
    days, seconds = uptime.days, uptime.seconds
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    
    return f"{days}d {hours}h {minutes}m {seconds}s"

# Message handler for AI chat mode
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle incoming messages and process them based on context.
    
    This function handles both regular messages and AI chat mode messages.
    In chat mode, it sends messages to the AI and returns responses.
    """
    user = update.effective_user
    chat = update.effective_chat
    message_text = update.message.text
    
    # Skip if message is empty or from a channel
    if not message_text or chat.type == 'channel':
        return
    
    # Update user's last seen and message count
    user_data = get_user_data(user.id)
    user_data['last_seen'] = datetime.now().isoformat()
    user_data['stats'] = user_data.get('stats', {})
    user_data['stats']['messages_sent'] = user_data['stats'].get('messages_sent', 0) + 1
    save_user_data(user.id, user_data)
    
    # Check rate limiting
    if not check_rate_limit(user.id):
        await update.message.reply_text(
            "⚠️ You're sending messages too fast! Please slow down."
        )
        return
    
    # Log the message
    save_chat_history(user.id, user.username or f"user_{user.id}", message_text)
    
    # Check if user is in chat mode
    if user_data.get('chat_mode'):
        # Show typing action
        await context.bot.send_chat_action(
            chat_id=chat.id,
            action="typing"
        )
        
        try:
            # Get AI response
            ai_response = get_ai_response(message_text, user.id)
            
            # Send the response with markdown parsing
            await update.message.reply_text(ai_response, parse_mode='Markdown')
            
            # Log the bot's response
            save_chat_history(user.id, "Bot", ai_response, is_bot=True)
            
        except Exception as e:
            logger.error(f"Error in AI chat: {str(e)}")
            await update.message.reply_text(
                "⚠️ Sorry, I encountered an error processing your message. "
                "Please try again later or contact support if the issue persists."
            )
    
    # Check for bot mention in group chats
    elif chat.type in ['group', 'supergroup']:
        if f"@{context.bot.username}" in message_text:
            # Bot was mentioned in a group
            response = (
                f"👋 Hi {user.mention_markdown_v2()}! I'm {context.bot.first_name}.\n"
                "Here's what I can do:\n"
                "• Use /help to see available commands\n"
                "• Use /chat to start a conversation with me\n"
                "• Use /profile to view or edit your profile"
            )
            await update.message.reply_markdown_v2(response)
    
    # Handle direct messages
    elif chat.type == 'private':
        # Check if user is in feedback mode
        if user_data.get('waiting_for_feedback'):
            await handle_feedback(update, context)
            return
            
        # Check if user is setting a reminder
        if user_data.get('setting_reminder'):
            await handle_reminder(update, context)
            return
            
        # Suggest using /chat if message doesn't start with a command
        if not message_text.startswith('/'):
            await update.message.reply_text(
                "🤖 I'm not in chat mode. Type /chat to start a conversation with me!\n\n"
                "Or use /help to see what else I can do!"
            )
            return

# Error handler
async def error_handler(update: object, context: CallbackContext) -> None:
    """Log errors and handle them gracefully."""
    logger.error("Exception while handling an update:", exc_info=context.error)
    
    # Try to notify the user about the error
    if update and hasattr(update, 'message'):
        try:
            await update.message.reply_text(
                "❌ An error occurred while processing your request. "
                "The developers have been notified."
            )
        except Exception as e:
            logger.error(f"Failed to send error message: {e}")

# New command handlers
async def feedback_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /feedback command."""
    user = update.effective_user
    user_data = get_user_data(user.id)
    user_data['waiting_for_feedback'] = True
    save_user_data(user.id, user_data)
    
    await update.message.reply_text(
        "💬 Please share your feedback. What would you like to tell us?"
    )
    log_command(user.id, "/feedback")

async def handle_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Process user feedback."""
    user = update.effective_user
    feedback_text = update.message.text
    
    # Save feedback
    feedback = {
        'user_id': user.id,
        'username': user.username or f"{user.first_name} {user.last_name or ''}".strip(),
        'text': feedback_text,
        'timestamp': datetime.now().isoformat()
    }
    
    try:
        with open(FEEDBACK_FILE, 'r+', encoding='utf-8') as f:
            feedbacks = json.load(f)
            feedbacks[str(datetime.now().timestamp())] = feedback
            f.seek(0)
            json.dump(feedbacks, f, indent=4, ensure_ascii=False)
            f.truncate()
    except Exception as e:
        logger.error(f"Error saving feedback: {e}")
    
    # Reset feedback flag
    user_data = get_user_data(user.id)
    user_data['waiting_for_feedback'] = False
    save_user_data(user.id, user_data)
    
    # Notify admins
    admin_message = (
        f"📝 *New Feedback*\n\n"
        f"From: {user.mention_markdown_v2()}"
        f" ({user.id if user.id != user.username else ''})\n"
        f"Text: {feedback_text}"
    )
    
    await notify_admins(context, admin_message)
    
    # Thank user
    await update.message.reply_text(
        "🙏 Thank you for your feedback! We appreciate your input."
    )

async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle language selection."""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    lang = query.data.replace("set_lang_", "")
    
    if lang in LANGUAGES:
        user_data = get_user_data(user.id)
        user_data['language'] = lang
        save_user_data(user.id, user_data)
        
        await query.edit_message_text(
            f"✅ Language set to {lang.upper()}"
        )
    else:
        await query.edit_message_text(
            "❌ Invalid language selection."
        )

async def remind_me(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /remindme command."""
    user = update.effective_user
    user_data = get_user_data(user.id)
    
    if context.args:
        try:
            # Parse time and message from command
            time_str = context.args[0]
            message = ' '.join(context.args[1:]) if len(context.args) > 1 else "Reminder!"
            
            # Parse time (e.g., "in 5 minutes" or "tomorrow at 14:30")
            reminder_time = parse_time(time_str)
            
            if reminder_time > datetime.now():
                # Schedule reminder
                job_context = {
                    'chat_id': update.effective_chat.id,
                    'message': message,
                    'user_id': user.id
                }
                
                # Calculate delay in seconds
                delay = (reminder_time - datetime.now()).total_seconds()
                
                # Schedule the job
                context.job_queue.run_once(
                    send_reminder,
                    delay,
                    data=job_context,
                    name=f"reminder_{user.id}_{int(time.time())}"
                )
                
                await update.message.reply_text(
                    f"⏰ I'll remind you at {reminder_time.strftime('%Y-%m-%d %H:%M')}:\n{message}"
                )
                
                # Save reminder
                save_reminder(user.id, reminder_time, message)
                
            else:
                await update.message.reply_text(
                    "Please specify a future time for the reminder."
                )
                
        except (ValueError, IndexError):
            await update.message.reply_text(
                "Invalid format. Use: /remindme [time] [message]\n"
                "Example: /remindme in 30 minutes Call mom"
            )
    else:
        # Show reminder setup help
        await update.message.reply_text(
            "⏰ *Set a Reminder*\n\n"
            "Usage: /remindme [time] [message]\n\n"
            "Examples:\n"
            "• /remindme in 30 minutes Take the pizza out of the oven\n"
            "• /remindme tomorrow at 9am Team meeting\n"
            "• /remindme next monday at 14:00 Submit report",
            parse_mode='Markdown'
        )

async def send_reminder(context: CallbackContext) -> None:
    """Send reminder to user."""
    job = context.job
    await context.bot.send_message(
        job.data['chat_id'],
        f"🔔 *Reminder*: {job.data['message']}",
        parse_mode='Markdown'
    )

def save_reminder(user_id: int, reminder_time: datetime, message: str) -> None:
    """Save reminder to file."""
    try:
        with open(REMINDERS_FILE, 'r+', encoding='utf-8') as f:
            reminders = json.load(f)
            
            reminder = {
                'user_id': user_id,
                'time': reminder_time.isoformat(),
                'message': message,
                'created_at': datetime.now().isoformat()
            }
            
            reminders.append(reminder)
            f.seek(0)
            json.dump(reminders, f, indent=4, ensure_ascii=False, default=str)
            f.truncate()
    except Exception as e:
        logger.error(f"Error saving reminder: {e}")

def parse_time(time_str: str) -> datetime:
    """Parse natural language time string to datetime."""
    # This is a simplified version - you might want to use a library like dateparser for production
    now = datetime.now()
    
    # Handle "in X minutes/hours/days"
    if time_str.startswith('in '):
        parts = time_str[3:].split()
        if len(parts) >= 2:
            try:
                amount = int(parts[0])
                unit = parts[1].lower()
                
                if 'minute' in unit:
                    return now + timedelta(minutes=amount)
                elif 'hour' in unit:
                    return now + timedelta(hours=amount)
                elif 'day' in unit:
                    return now + timedelta(days=amount)
                elif 'week' in unit:
                    return now + timedelta(weeks=amount)
            except (ValueError, IndexError):
                pass
    
    # Handle specific times like "at 14:30"
    elif time_str.startswith('at '):
        time_part = time_str[3:].strip()
        try:
            # Try to parse time in format HH:MM
            hours, minutes = map(int, time_part.split(':'))
            reminder_time = now.replace(hour=hours, minute=minutes, second=0, microsecond=0)
            
            # If the time has already passed today, set it for tomorrow
            if reminder_time < now:
                reminder_time += timedelta(days=1)
                
            return reminder_time
        except (ValueError, IndexError):
            pass
    
    # Default: add 1 hour
    return now + timedelta(hours=1)

async def broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Broadcast a message to all users (admin only)."""
    user = update.effective_user
    
    if not is_admin(user.id):
        await update.message.reply_text("❌ This command is for administrators only.")
        return
    
    if not context.args:
        await update.message.reply_text(
            "📢 *Broadcast a Message*\n\n"
            "Usage: /broadcast [message]\n\n"
            "Example: /broadcast Hello everyone! We'll have maintenance tomorrow at 2 AM UTC.",
            parse_mode='Markdown'
        )
        return
    
    message = ' '.join(context.args)
    users = get_all_users()
    total = len(users)
    success = 0
    failed = 0
    
    # Send broadcast to all users
    for user_id_str in users:
        try:
            await context.bot.send_message(
                chat_id=user_id_str,
                text=f"📢 *Announcement*\n\n{message}",
                parse_mode='Markdown'
            )
            success += 1
            # Small delay to avoid hitting rate limits
            await asyncio.sleep(0.1)
        except Exception as e:
            logger.error(f"Failed to send broadcast to {user_id_str}: {e}")
            failed += 1
    
    # Save broadcast record
    save_broadcast(user.id, message, total, success, failed)
    
    # Send report to admin
    await update.message.reply_text(
        f"📢 *Broadcast Sent*\n\n"
        f"• Total recipients: {total}\n"
        f"• Successfully sent: {success}\n"
        f"• Failed: {failed}\n\n"
        f"Message: {message[:100]}{'...' if len(message) > 100 else ''}",
        parse_mode='Markdown'
    )

def save_broadcast(admin_id: int, message: str, total: int, success: int, failed: int) -> None:
    """Save broadcast record to file."""
    try:
        with open(BROADCASTS_FILE, 'r+', encoding='utf-8') as f:
            try:
                broadcasts = json.load(f)
            except json.JSONDecodeError:
                broadcasts = []
            
            broadcast = {
                'admin_id': admin_id,
                'timestamp': datetime.now().isoformat(),
                'message': message,
                'total_recipients': total,
                'successful': success,
                'failed': failed
            }
            
            broadcasts.append(broadcast)
            f.seek(0)
            json.dump(broadcasts, f, indent=4, ensure_ascii=False, default=str)
            f.truncate()
    except Exception as e:
        logger.error(f"Error saving broadcast: {e}")

async def notify_admins(context: CallbackContext, message: str) -> None:
    """Send a message to all admins."""
    for admin_id in ADMIN_IDS:
        try:
            await context.bot.send_message(
                chat_id=admin_id,
                text=message,
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Failed to notify admin {admin_id}: {e}")

# Button callbacks
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button callbacks."""
    query = update.callback_query
    await query.answer()
    
    if query.data == "start_chat":
        await chat_mode(update, context)
    elif query.data == "give_feedback":
        await feedback_command(update, context)
    elif query.data.startswith("set_lang_"):
        await set_language(update, context)
    # Add more button handlers as needed

# Add this to main()
def main() -> None:
    """Start the bot."""
    if not TOKEN:
        print("ERROR: Please set TELEGRAM_BOT_TOKEN in your .env file")
        print("Copy .env.example to .env and fill in your credentials")
        return
    
    # Create the Application with persistence
    application = Application.builder().token(TOKEN).build()
    
    # Add conversation handler for profile management
    profile_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("profile", profile)],
        states={
            PROFILE: [
                CallbackQueryHandler(edit_profile, pattern="^edit_profile$"),
                CallbackQueryHandler(help_command, pattern="^back_to_menu$")
            ],
            EDIT_CHOICE: [
                CallbackQueryHandler(handle_edit_choice, pattern="^edit_"),
                CallbackQueryHandler(profile, pattern="^back_to_profile$")
            ],
            EDIT_VALUE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, save_profile_edit)
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel_profile_edit)],
    )
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("contact", contact))
    application.add_handler(CommandHandler("chat", chat_mode))
    application.add_handler(CommandHandler("endchat", end_chat))
    application.add_handler(CommandHandler("feedback", feedback_command))
    application.add_handler(CommandHandler("remindme", remind_me))
    application.add_handler(CommandHandler("broadcast", broadcast_message))
    application.add_handler(CommandHandler("language", language_command))
    application.add_handler(CommandHandler("setlanguage", set_language))
    application.add_handler(CommandHandler("myinfo", my_info))
    application.add_handler(profile_conv_handler)
    
    # Add hidden command handlers
    application.add_handler(CommandHandler("owner", owner))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("users", list_users))
    application.add_handler(CommandHandler("promote", promote_user))
    application.add_handler(CommandHandler("demote", demote_user))
    
    # Update callback query handler to exclude profile patterns
    application.add_handler(CallbackQueryHandler(button_callback, pattern="^(?!edit_|back_to_)"))
    
    # Add message handler (must be after command handlers)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Start the bot
    print("🤖 Bot is running. Press Ctrl+C to stop.")
    
    # Start the job queue
    job_queue = application.job_queue
    
    # Add daily stats job
    job_queue.run_daily(send_daily_stats, time=datetime.time(hour=0, minute=0))
    
    # Start the bot
    application.run_polling()

# Daily stats function
# Missing function implementations
async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /language command - show language selection."""
    user = update.effective_user
    user_data = get_user_data(user.id)
    current_lang = user_data.get('language', DEFAULT_LANGUAGE)
    
    # Create language selection keyboard
    keyboard = []
    for lang_code, lang_data in LANGUAGES.items():
        flag = "🇺🇸" if lang_code == 'en' else "🇪🇸" if lang_code == 'es' else "🌐"
        status = "✅" if lang_code == current_lang else ""
        keyboard.append([InlineKeyboardButton(
            f"{flag} {lang_code.upper()} {status}",
            callback_data=f"set_lang_{lang_code}"
        )])
    
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="back_to_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🌐 *Select Language*\n\nChoose your preferred language:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    log_command(user.id, "/language")

async def my_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /myinfo command - show user information."""
    user = update.effective_user
    user_data = get_user_data(user.id)
    
    # Update user's profile with current Telegram info if empty
    if not user_data['profile']['full_name']:
        user_data['profile'].update({
            'full_name': f"{user.first_name} {user.last_name or ''}".strip(),
            'username': user.username or "",
            'last_activity': datetime.now().isoformat()
        })
        save_user_data(user.id, user_data)
    
    info_text = (
        f"👤 *Your Information*\n\n"
        f"🆔 User ID: `{user.id}`\n"
        f"👤 Full Name: {user_data['profile']['full_name']}\n"
        f"🔖 Username: @{user_data['profile']['username'] if user_data['profile']['username'] else 'Not set'}\n"
        f"📅 Member since: {datetime.fromisoformat(user_data['first_seen']).strftime('%Y-%m-%d %H:%M')}\n"
        f"🌐 Language: {user_data['language'].upper()}\n"
        f"📊 Messages sent: {user_data['stats']['messages_sent']}\n"
        f"📱 Last seen: {datetime.fromisoformat(user_data['last_seen']).strftime('%Y-%m-%d %H:%M')}\n"
        f"📝 Bio: {user_data['profile']['bio'] or 'Not set'}\n"
        f"📍 Location: {user_data['profile']['location'] or 'Not set'}\n"
        f"🎯 Interests: {', '.join(user_data['profile']['interests']) or 'None'}"
    )
    
    await update.message.reply_text(info_text, parse_mode='Markdown')
    log_command(user.id, "/myinfo")

async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List all users (admin only)."""
    user = update.effective_user
    
    if not is_admin(user.id):
        await update.message.reply_text("❌ This command is for administrators only.")
        return
    
    users = get_all_users()
    total_users = len(users)
    
    if total_users == 0:
        await update.message.reply_text("📝 No users found.")
        return
    
    # Group users by role
    admin_count = sum(1 for u in users.values() if u.get('role') == UserRole.ADMIN.value)
    mod_count = sum(1 for u in users.values() if u.get('role') == UserRole.MODERATOR.value)
    user_count = total_users - admin_count - mod_count
    
    users_text = f"👥 *User Statistics*\n\n"
    users_text += f"• Total Users: {total_users}\n"
    users_text += f"• Administrators: {admin_count}\n"
    users_text += f"• Moderators: {mod_count}\n"
    users_text += f"• Regular Users: {user_count}\n\n"
    
    # Show recent users (last 10)
    users_text += "🕐 *Recent Users:*\n"
    recent_users = sorted(users.items(), key=lambda x: x[1].get('first_seen', ''), reverse=True)[:10]
    
    for user_id, user_data in recent_users:
        first_seen = datetime.fromisoformat(user_data.get('first_seen', '2000-01-01')).strftime('%Y-%m-%d')
        role = user_data.get('role', 'user')
        username = user_data.get('profile', {}).get('username', 'N/A')
        users_text += f"• {first_seen} - {username} (ID: {user_id}) - {role}\n"
    
    await update.message.reply_text(users_text, parse_mode='Markdown')
    log_command(user.id, "/users")

async def promote_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Promote a user to moderator or admin (admin only)."""
    user = update.effective_user
    
    if not is_admin(user.id):
        await update.message.reply_text("❌ This command is for administrators only.")
        return
    
    if not context.args:
        await update.message.reply_text(
            "📈 *Promote User*\n\n"
            "Usage: /promote [user_id] [role]\n\n"
            "Roles: moderator, admin\n"
            "Example: /promote 123456789 moderator",
            parse_mode='Markdown'
        )
        return
    
    try:
        target_user_id = int(context.args[0])
        new_role = context.args[1].lower() if len(context.args) > 1 else 'moderator'
        
        if new_role not in ['moderator', 'admin']:
            await update.message.reply_text("❌ Invalid role. Use 'moderator' or 'admin'.")
            return
        
        target_user_data = get_user_data(target_user_id)
        if not target_user_data:
            await update.message.reply_text("❌ User not found.")
            return
        
        old_role = target_user_data.get('role', UserRole.USER.value)
        target_user_data['role'] = UserRole.MODERATOR.value if new_role == 'moderator' else UserRole.ADMIN.value
        save_user_data(target_user_id, target_user_data)
        
        await update.message.reply_text(
            f"✅ User {target_user_id} promoted from {old_role} to {new_role}."
        )
        
        # Notify the promoted user if possible
        try:
            await context.bot.send_message(
                chat_id=target_user_id,
                text=f"🎉 Congratulations! You've been promoted to {new_role}."
            )
        except:
            pass  # User might not have started the bot
            
    except (ValueError, IndexError):
        await update.message.reply_text("❌ Invalid format. Use: /promote [user_id] [role]")
    
    log_command(user.id, f"/promote {context.args[0] if context.args else 'N/A'}")

async def demote_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Demote a user from moderator or admin to user (admin only)."""
    user = update.effective_user
    
    if not is_admin(user.id):
        await update.message.reply_text("❌ This command is for administrators only.")
        return
    
    if not context.args:
        await update.message.reply_text(
            "📉 *Demote User*\n\n"
            "Usage: /demote [user_id]\n\n"
            "Example: /demote 123456789",
            parse_mode='Markdown'
        )
        return
    
    try:
        target_user_id = int(context.args[0])
        
        target_user_data = get_user_data(target_user_id)
        if not target_user_data:
            await update.message.reply_text("❌ User not found.")
            return
        
        old_role = target_user_data.get('role', UserRole.USER.value)
        if old_role == UserRole.USER.value:
            await update.message.reply_text("❌ User is already a regular user.")
            return
        
        target_user_data['role'] = UserRole.USER.value
        save_user_data(target_user_id, target_user_data)
        
        await update.message.reply_text(
            f"✅ User {target_user_id} demoted from {old_role} to user."
        )
        
        # Notify the demoted user if possible
        try:
            await context.bot.send_message(
                chat_id=target_user_id,
                text=f"⚠️ You've been demoted to regular user."
            )
        except:
            pass  # User might not have started the bot
            
    except (ValueError, IndexError):
        await update.message.reply_text("❌ Invalid format. Use: /demote [user_id]")
    
    log_command(user.id, f"/demote {context.args[0] if context.args else 'N/A'}")

async def handle_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Process reminder setup from user message."""
    user = update.effective_user
    user_data = get_user_data(user.id)
    
    if not user_data.get('setting_reminder'):
        return
    
    reminder_text = update.message.text.strip()
    
    try:
        # Parse time and message from reminder text
        parts = reminder_text.split(' ', 2)
        if len(parts) < 2:
            await update.message.reply_text(
                "❌ Invalid format. Use: 'in [time] [message]'\n"
                "Example: 'in 30 minutes Take the pizza out of the oven'"
            )
            return
        
        time_str = f"in {parts[0]} {parts[1]}"
        message = parts[2] if len(parts) > 2 else "Reminder!"
        
        # Parse time
        reminder_time = parse_time(time_str)
        
        if reminder_time > datetime.now():
            # Schedule reminder
            job_context = {
                'chat_id': update.effective_chat.id,
                'message': message,
                'user_id': user.id
            }
            
            # Calculate delay in seconds
            delay = (reminder_time - datetime.now()).total_seconds()
            
            # Schedule the job
            context.job_queue.run_once(
                send_reminder,
                delay,
                data=job_context,
                name=f"reminder_{user.id}_{int(time.time())}"
            )
            
            await update.message.reply_text(
                f"⏰ I'll remind you at {reminder_time.strftime('%Y-%m-%d %H:%M')}:\n{message}"
            )
            
            # Save reminder
            save_reminder(user.id, reminder_time, message)
            
        else:
            await update.message.reply_text(
                "❌ Please specify a future time for the reminder."
            )
            
    except Exception as e:
        logger.error(f"Error setting reminder: {e}")
        await update.message.reply_text(
            "❌ Error setting reminder. Please try again."
        )
    
    # Reset reminder flag
    user_data['setting_reminder'] = False
    save_user_data(user.id, user_data)

async def send_daily_stats(context: CallbackContext) -> None:
    """Send daily statistics to admins."""
    users = get_all_users()
    today = datetime.now().date()
    
    new_users_today = sum(
        1 for user_data in users.values() 
        if datetime.fromisoformat(user_data.get('first_seen', '2000-01-01')).date() == today
    )
    
    active_users = sum(
        1 for user_data in users.values()
        if datetime.fromisoformat(user_data.get('last_seen', '2000-01-01')).date() == today
    )
    
    stats_message = (
        f"📊 *Daily Statistics*\n\n"
        f"• Total users: {len(users)}\n"
        f"• New users today: {new_users_today}\n"
        f"• Active users today: {active_users}\n"
        f"• Total messages today: {sum(u.get('stats', {}).get('messages_sent', 0) for u in users.values())}"
    )
    
    await notify_admins(context, stats_message)

if __name__ == "__main__":
    main()
 