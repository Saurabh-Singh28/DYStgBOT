# AI-Powered Telegram Bot

A feature-rich Telegram bot built with python-telegram-bot that includes AI chat functionality, user management, and admin features.

## Features

- **Basic Commands**: /start, /help, /contact, /profile
- **AI Chat Mode**: /chat to start a conversation with the AI (OpenAI GPT integration)
- **User Management**: Tracks user interactions, profiles, and chat history
- **Admin Commands**: Hidden commands for bot administration
- **Moderator System**: Role-based access control (User, Moderator, Admin)
- **File-based Storage**: All data is stored locally in JSON and text files
- **Rate Limiting**: Prevents spam and abuse
- **Multi-language Support**: English and Spanish (extensible)
- **Reminders**: Set reminders with natural language
- **Broadcast**: Send announcements to all users (admin only)
- **Error Handling**: Robust error handling and logging
- **Secure Configuration**: Environment variables for sensitive data

## Prerequisites

- Python 3.8 or higher
- A Telegram bot token from [@BotFather](https://t.me/botfather)
- (Optional) OpenAI API key for AI chat features

## Installation

1. Clone this repository or download the files

2. Install the required packages:

```bash
pip install -r requirements.txt
```

3. Configure the bot:
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Edit `.env` and fill in your credentials:
     - `TELEGRAM_BOT_TOKEN`: Your bot token from BotFather
     - `ADMIN_IDS`: Your Telegram user ID (comma-separated for multiple admins)
     - `OPENAI_API_KEY`: Your OpenAI API key (if using AI features)
     - Adjust other settings as needed

4. (Optional) Initialize sample data:
```bash
python init_data.py
```

## Running the Bot

```bash
python bot.py
```

The bot will start and begin responding to commands. Use /start in a chat with your bot to begin.

## Security Best Practices

⚠️ **IMPORTANT**: Never commit your `.env` file to version control!

- The `.env` file contains sensitive credentials and is already in `.gitignore`
- Always use environment variables for API keys and tokens
- Regularly rotate your API keys
- Keep your dependencies updated: `pip install -r requirements.txt --upgrade`

## Available Commands

### User Commands
- `/start` - Start the bot and see welcome message
- `/help` - Show available commands
- `/contact` - Get contact information
- `/profile` - View and edit your profile
- `/chat` - Enter AI chat mode
- `/endchat` - Exit AI chat mode
- `/feedback` - Send feedback to admins
- `/language` - Change language preference
- `/remindme` - Set a reminder
- `/myinfo` - Show your user information

### Moderator Commands
- `/broadcast` - Send message to all users
- `/userinfo` - Get user information

### Admin Commands
- `/owner` - Show owner commands
- `/status` - Show bot status
- `/users` - List all users with statistics
- `/promote` - Promote user to moderator/admin
- `/demote` - Demote user to regular user
- `/stats` - Show detailed bot statistics
- `/export` - Export user data
- `/announce` - Make an announcement

## Data Storage

The bot stores data in the following files:
- `data/users.json` - User data, profiles, and preferences
- `data/chat_history.txt` - Chat history logs
- `data/command_logs.txt` - Command usage logs
- `data/feedback.json` - User feedback submissions
- `data/reminders.json` - Scheduled reminders
- `data/broadcasts.json` - Broadcast history

All data files are automatically created on first run.

## Configuration Options

Edit your `.env` file to customize:

- **AI Settings**: Model, temperature, max tokens
- **Rate Limiting**: Messages per minute for users and admins
- **Language**: Default language for new users
- **Data Directory**: Where to store data files

## Getting Your Telegram User ID

To set yourself as an admin, you need your Telegram user ID:

1. Start a chat with [@userinfobot](https://t.me/userinfobot)
2. It will reply with your user ID
3. Add this ID to `ADMIN_IDS` in your `.env` file

## Customization

### Adding New Languages

Edit the `LANGUAGES` dictionary in `bot.py`:

```python
LANGUAGES = {
    'en': {...},
    'es': {...},
    'fr': {  # Add French
        'welcome': '👋 Bonjour {}! Bienvenue!',
        'help': '🤖 *Commandes disponibles:*',
        ...
    }
}
```

### Adding New Commands

1. Create a new async function with the command logic:
   ```python
   async def my_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
       await update.message.reply_text("Hello!")
   ```

2. Add a command handler in the `main()` function:
   ```python
   application.add_handler(CommandHandler("mycommand", my_command))
   ```

3. Update the help text in `help_command()` if it's a public command

### Switching AI Providers

The bot supports OpenAI by default. To add a custom AI provider:

1. Set `AI_PROVIDER=custom` in `.env`
2. Modify the `get_ai_response()` function in `bot.py` to integrate your AI service

## License

This project is open source and available under the MIT License.
