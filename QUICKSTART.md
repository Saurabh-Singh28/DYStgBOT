# Quick Start Guide

Get your Telegram bot up and running in 5 minutes!

## Step 1: Create Your Bot

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot` command
3. Follow the prompts to name your bot
4. Copy the bot token (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

## Step 2: Get Your User ID

1. Search for [@userinfobot](https://t.me/userinfobot) on Telegram
2. Start a chat with it
3. Copy your user ID (a number like: `123456789`)

## Step 3: Setup the Bot

### Option A: Using the Setup Script (Recommended)

```bash
python setup.py
```

Follow the interactive prompts to configure your bot.

### Option B: Manual Setup

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your credentials:
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   ADMIN_IDS=your_user_id_here
   ```

## Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 5: Run the Bot

```bash
python bot.py
```

You should see: `🤖 Bot is running. Press Ctrl+C to stop.`

## Step 6: Test Your Bot

1. Open Telegram and search for your bot by username
2. Send `/start` command
3. Try other commands like `/help`, `/profile`, etc.

## Optional: Enable AI Chat

To enable AI chat features:

1. Get an OpenAI API key from [platform.openai.com](https://platform.openai.com/api-keys)
2. Add it to your `.env` file:
   ```
   OPENAI_API_KEY=sk-...your_key_here
   AI_ENABLED=True
   ```
3. Restart the bot
4. Use `/chat` command to start chatting with AI

## Troubleshooting

### Bot doesn't respond
- Check that the bot token is correct in `.env`
- Make sure the bot is running (check terminal)
- Verify you started a chat with the bot on Telegram

### AI chat not working
- Verify `OPENAI_API_KEY` is set in `.env`
- Check that `AI_ENABLED=True` in `.env`
- Ensure you have OpenAI credits available

### Permission errors
- Make sure your user ID is in `ADMIN_IDS` in `.env`
- Restart the bot after changing `.env`

## Next Steps

- Read the full [README.md](README.md) for all features
- Customize the bot by editing `bot.py`
- Add more languages in the `LANGUAGES` dictionary
- Deploy to a server for 24/7 operation

## Need Help?

- Check [README.md](README.md) for detailed documentation
- Review [CHANGELOG.md](CHANGELOG.md) for recent changes
- Contact: sanataniking280@gmail.com
