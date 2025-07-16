# Environment Variables Setup

## 🔧 Required Environment Variables

Set these environment variables in your Supabase project dashboard:

### 1. Go to Supabase Dashboard
- Visit: https://supabase.com/dashboard/project/hrfiaxcjknmswdirgczm
- Navigate to **Settings** → **Edge Functions**

### 2. Add Environment Variables

| Variable Name | Description | Example |
|---------------|-------------|---------|
| `TELEGRAM_BOT_TOKEN` | Your Telegram bot token from @BotFather | `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz` |
| `SUPABASE_URL` | Your Supabase project URL | `https://hrfiaxcjknmswdirgczm.supabase.co` |
| `SUPABASE_SERVICE_ROLE_KEY` | Your Supabase service role key | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` |
| `FUNCTION_SECRET` | Random secret for webhook security | `your-random-secret-string` |

### 3. How to Get These Values

#### Telegram Bot Token
1. Message @BotFather on Telegram
2. Use `/newbot` command
3. Follow instructions to create bot
4. Copy the token provided

#### Supabase URL & Service Role Key
1. Go to your Supabase project dashboard
2. Navigate to **Settings** → **API**
3. Copy the **Project URL** and **service_role** key

#### Function Secret
Generate a random string for security:
```bash
# Generate a random secret
openssl rand -base64 32
```

## 🚀 Verification

After setting the environment variables:

1. **Test the bot**: Send a message to your bot
2. **Check logs**: Go to Edge Functions → telegram-bot → Logs
3. **Verify database**: Check the tables in your Supabase dashboard

## 📊 Database Tables Created

The bot will automatically populate these tables:
- `users_v1` - Telegram user information
- `chats_v1` - Chat/group/channel information  
- `messages_v1` - All messages with metadata
- `forum_topics_v1` - Forum topics (if applicable)

## 🔍 Troubleshooting

### Common Issues

1. **"not allowed" error**: Check your `FUNCTION_SECRET`
2. **Database connection errors**: Verify `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY`
3. **Bot not responding**: Check `TELEGRAM_BOT_TOKEN`
4. **Permission denied**: Ensure service role key has proper permissions

### Debug Commands

```bash
# Check function status
supabase functions list

# View function logs
# (Check in Supabase dashboard: Edge Functions → telegram-bot → Logs)

# Redeploy function
supabase functions deploy telegram-bot --no-verify-jwt
```

## 🔒 Security Notes

- **Never commit** environment variables to version control
- **Use service role key** only in server-side code
- **Rotate secrets** periodically
- **Monitor logs** for unusual activity 