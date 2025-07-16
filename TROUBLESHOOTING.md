# Troubleshooting Guide

## Bot Token Issues

### "Peer id invalid" Error
**Problem:** Bot cannot access the specified chat ID.

**Solutions:**
1. **Add the bot to the chat:**
   - Add your bot to the Telegram chat/channel you want to monitor
   - For groups: Add the bot as a member
   - For channels: Add the bot as an admin

2. **Check bot permissions:**
   - Make sure the bot has permission to read messages
   - For channels, the bot needs admin rights with read permissions

3. **Verify chat ID:**
   - Double-check the chat ID in `chat_ids.yaml`
   - Use a tool like @userinfobot to get the correct chat ID

### "CHAT_WRITE_FORBIDDEN" or "CHAT_READ_FORBIDDEN" Error
**Problem:** Bot lacks permission to read messages from the chat.

**Solutions:**
1. **For Groups:**
   - Make sure the bot is added to the group
   - Check group privacy settings (some groups may restrict bot access)

2. **For Channels:**
   - Add the bot as an admin to the channel
   - Grant the bot "Read Messages" permission
   - Make sure the channel allows admin bots

3. **For Private Chats:**
   - Bots cannot access private chats unless they're specifically designed for it
   - Consider using API ID/hash authentication instead

### "The API key is required for new authorizations" Error
**Problem:** Invalid or missing bot token.

**Solutions:**
1. **Get a valid bot token:**
   - Message @BotFather on Telegram
   - Use `/newbot` command
   - Follow the instructions to create your bot
   - Copy the bot token (starts with `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

2. **Set the environment variables:**
   ```bash
   export TELEGRAM_API_ID=your_api_id
   export TELEGRAM_API_HASH=your_api_hash
   export TELEGRAM_BOT_TOKEN=your_bot_token_here
   ```

3. **Add to GitHub Secrets:**
   - Go to your repository Settings → Secrets and variables → Actions
   - Add `TELEGRAM_API_ID`, `TELEGRAM_API_HASH`, and `TELEGRAM_BOT_TOKEN`

**Note:** Bot tokens with telethon still require API ID and hash for authentication.

### "The API access for bot users is restricted" Error
**Problem:** Bot cannot fetch message history due to Telegram API restrictions.

**Solutions:**
1. **This is a Telegram API limitation:**
   - Bots cannot access message history using `GetHistoryRequest`
   - This is a security feature by Telegram, not a configuration issue
   - The script will automatically detect bot usage and provide limited access

2. **For full message history access:**
   - Use API ID and hash authentication (user account) instead of bot token
   - User accounts can fetch full message history
   - Bot tokens can only verify chat access and get basic information

3. **Bot capabilities:**
   - Bots can verify they have access to a chat
   - Bots can get basic chat information (title, type, etc.)
   - Bots cannot fetch message history or read messages
   - This is a Telegram security restriction, not a bug

**Note:** The script automatically handles this limitation by providing different functionality for bots vs user accounts.

## API ID/Hash Issues

### "Missing required environment variables" Error
**Problem:** API credentials not set.

**Solutions:**
1. **Get API credentials:**
   - Go to https://my.telegram.org
   - Log in with your phone number
   - Create a new application
   - Copy the API ID and API Hash

2. **Set environment variables:**
   ```bash
   export TELEGRAM_API_ID=your_api_id
   export TELEGRAM_API_HASH=your_api_hash
   ```

3. **Add to GitHub Secrets:**
   - Go to your repository Settings → Secrets and variables → Actions
   - Add `TELEGRAM_API_ID` and `TELEGRAM_API_HASH`

## Chat ID Issues

### Finding Correct Chat IDs
1. **For Groups:**
   - Add @userinfobot to the group
   - Send any message in the group
   - The bot will show the group ID

2. **For Channels:**
   - Forward a message from the channel to @userinfobot
   - The bot will show the channel ID

3. **For Private Chats:**
   - Use API ID/hash authentication instead of bot token
   - The chat ID will be the user's ID

### Common Chat ID Formats
- **Groups:** Usually negative numbers (e.g., `-1001234567890`)
- **Channels:** Usually negative numbers starting with -100 (e.g., `-1001234567890`)
- **Users:** Positive numbers (e.g., `123456789`)

## GitHub Action Issues

### "No changes to commit" Message
**Problem:** The workflow runs but doesn't commit changes.

**Solutions:**
1. **Check if reports were generated:**
   - Look in the `website/` directory for HTML files
   - Check the workflow logs for any errors

2. **Verify file permissions:**
   - Make sure the workflow has write permissions
   - Check that the `website/` directory exists

### Workflow Not Running
**Problem:** GitHub Action doesn't trigger.

**Solutions:**
1. **Check cron schedule:**
   - The workflow runs daily at 12:00 UTC
   - You can manually trigger it from the Actions tab

2. **Verify environment:**
   - Make sure the "test" environment is configured
   - Check that secrets are properly set

## Performance Issues

### Slow Message Fetching
**Problem:** Script takes a long time to fetch messages.

**Solutions:**
1. **Reduce message limit:**
   - Edit `scripts/fetch_chats.py`
   - Change `self.message_limit = 2000` to a smaller value (e.g., 500)

2. **Reduce date range:**
   - Change `self.days_to_fetch = 7` to a smaller value (e.g., 3)

3. **Install TgCrypto for speed:**
   ```bash
   pip install TgCrypto
   ```

## Getting Help

If you're still having issues:

1. **Check the logs:** Look at the detailed error messages in the script output
2. **Verify credentials:** Make sure your bot token or API credentials are correct
3. **Test locally:** Run the script locally with your credentials to debug
4. **Check Telegram limits:** Be aware of Telegram's rate limits and API restrictions

## Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| "Peer id invalid" | Bot not added to chat | Add bot to the chat |
| "CHAT_WRITE_FORBIDDEN" | Bot lacks permissions | Grant bot admin rights |
| "Missing required environment variables" | No credentials set | Set TELEGRAM_BOT_TOKEN or API credentials |
| "The API key is required" | Invalid bot token | Get valid token from @BotFather |
| "No changes to commit" | No reports generated | Check for errors in logs | 