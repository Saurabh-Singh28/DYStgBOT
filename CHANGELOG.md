# Changelog

All notable changes to this project will be documented in this file.

## [2.0.0] - 2025-10-02

### 🔒 Security Improvements
- **Environment Variables**: Migrated all sensitive configuration to `.env` file
- **Secure Credentials**: No more hardcoded API keys or tokens in source code
- **gitignore**: Added comprehensive `.gitignore` to prevent credential leaks
- **Best Practices**: Updated README with security guidelines

### ✨ New Features
- **Profile Management**: Users can view and edit their profiles
- **Language Selection**: Multi-language support with `/language` command
- **User Info**: `/myinfo` command to view detailed user information
- **User Management**: Admin commands `/promote` and `/demote` for role management
- **User Listing**: `/users` command for admins to view all users
- **Reminder System**: Enhanced reminder functionality with natural language parsing
- **Daily Statistics**: Automated daily stats sent to admins

### 🔧 Technical Improvements
- **OpenAI API Update**: Migrated from deprecated API to new client-based approach (v1.12.0)
- **Error Handler**: Properly registered error handler in main()
- **Missing Functions**: Implemented all referenced but missing functions
- **Data Structure**: Aligned data structures between init_data.py and bot.py
- **Code Organization**: Removed duplicate initialization code
- **Dependencies**: Updated to latest stable versions with pinned versions

### 📦 Dependencies Updated
- `python-telegram-bot`: 20.7
- `openai`: 1.12.0 (with new client API)
- `python-dotenv`: 1.0.0
- `typing-extensions`: 4.9.0
- `python-dateutil`: 2.8.2
- `pytz`: 2024.1

### 📝 Documentation
- **README**: Comprehensive update with security section
- **Setup Script**: Added interactive setup.py for easy configuration
- **.env.example**: Template for environment variables
- **CHANGELOG**: This file to track changes

### 🐛 Bug Fixes
- Fixed OpenAI API deprecation warnings
- Fixed missing function implementations
- Fixed error handler not being registered
- Fixed data file initialization logic
- Fixed rate limiting data structure
- Fixed daily stats message count calculation

### 🗑️ Removed
- Hardcoded credentials from source code
- Duplicate data initialization code
- Deprecated OpenAI API calls

## [1.0.0] - Initial Release

### Features
- Basic bot commands (/start, /help, /contact)
- AI chat mode with OpenAI integration
- User tracking and chat history
- Admin commands
- File-based storage
