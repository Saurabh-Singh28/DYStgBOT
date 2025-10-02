#!/usr/bin/env python3
"""
Setup script for the Telegram Bot
Helps users configure the bot for first-time use
"""
import os
import shutil
import sys

def main():
    print("=" * 60)
    print("Telegram Bot Setup")
    print("=" * 60)
    print()
    
    # Check if .env exists
    if os.path.exists('.env'):
        print("✅ .env file already exists")
        response = input("Do you want to overwrite it? (y/N): ").lower()
        if response != 'y':
            print("Setup cancelled. Using existing .env file.")
            return
    
    # Copy .env.example to .env
    if os.path.exists('.env.example'):
        shutil.copy('.env.example', '.env')
        print("✅ Created .env file from .env.example")
    else:
        print("❌ .env.example not found!")
        return
    
    print()
    print("Please configure your .env file with the following:")
    print()
    
    # Get Telegram Bot Token
    print("1. TELEGRAM_BOT_TOKEN")
    print("   Get this from @BotFather on Telegram")
    token = input("   Enter your bot token (or press Enter to skip): ").strip()
    
    # Get Admin IDs
    print()
    print("2. ADMIN_IDS")
    print("   Get your Telegram user ID from @userinfobot")
    admin_ids = input("   Enter admin user IDs (comma-separated, or press Enter to skip): ").strip()
    
    # Get OpenAI API Key
    print()
    print("3. OPENAI_API_KEY (optional)")
    print("   Get this from https://platform.openai.com/api-keys")
    openai_key = input("   Enter your OpenAI API key (or press Enter to skip): ").strip()
    
    # Update .env file
    if token or admin_ids or openai_key:
        with open('.env', 'r') as f:
            content = f.read()
        
        if token:
            content = content.replace('your_telegram_bot_token_here', token)
        if admin_ids:
            content = content.replace('123456789,987654321', admin_ids)
        if openai_key:
            content = content.replace('your_openai_api_key_here', openai_key)
        
        with open('.env', 'w') as f:
            f.write(content)
        
        print()
        print("✅ .env file updated with your configuration")
    
    # Check if data directory exists
    if not os.path.exists('data'):
        os.makedirs('data')
        print("✅ Created data directory")
    
    print()
    print("=" * 60)
    print("Setup Complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Review and edit .env file if needed")
    print("2. Install dependencies: pip install -r requirements.txt")
    print("3. (Optional) Initialize sample data: python init_data.py")
    print("4. Run the bot: python bot.py")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user.")
        sys.exit(0)
