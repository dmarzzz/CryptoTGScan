# Telegram Bot Troubleshooting Guide

## 🚨 Bot Not Working? Let's Fix It!

If your bot is not responding, follow these steps to diagnose and fix the issue.

## 🔍 Quick Diagnosis

### 1. Check Bot Status
```bash
cd scripts
python test_bot.py
```

This will check:
- ✅ Bot token validity
- ✅ Webhook configuration
- ✅ Supabase connection
- ✅ Function endpoint

### 2. Check Webhook Setup
```bash
cd scripts
python setup_webhook.py
```

This will:
- 🔧 Set up the webhook URL
- 🔍 Verify webhook is working
- 📡 Configure allowed updates

## 🛠️ Common Issues & Solutions

### Issue 1: "Bot not responding to messages"

**Symptoms:**
- Bot deployed but not responding
- No error messages in logs
- Webhook URL not set

**Solution:**
1. Run the webhook setup script:
   ```bash
   python scripts/setup_webhook.py
   ```
2. Enter your bot token when prompted
3. Verify webhook is set correctly

### Issue 2: "Webhook error" or "Last error message"

**Symptoms:**
- Webhook info shows error messages
- Function returning 401/403 errors
- Bot not receiving updates

**Solutions:**
1. **Check function secret**: Ensure the secret in the webhook URL matches
2. **Verify HTTPS**: Webhook must use HTTPS
3. **Check function deployment**: Redeploy if needed
   ```bash
   cd bot
   supabase functions deploy telegram-bot --no-verify-jwt
   ```

### Issue 3: "Database connection errors"

**Symptoms:**
- Bot responds but doesn't store data
- Supabase connection failures
- Missing environment variables

**Solutions:**
1. **Check environment variables** in Supabase dashboard:
   - Go to Settings → Edge Functions
   - Verify all variables are set:
     - `TELEGRAM_BOT_TOKEN`
     - `SUPABASE_URL`
     - `SUPABASE_SERVICE_ROLE_KEY`
     - `FUNCTION_SECRET`

2. **Test database connection**:
   ```bash
   python scripts/test_bot.py
   ```

### Issue 4: "Function not deployed"

**Symptoms:**
- 404 errors when accessing function
- Function not listed in Supabase
- Deployment failures

**Solutions:**
1. **Check deployment status**:
   ```bash
   cd bot
   supabase functions list
   ```

2. **Redeploy function**:
   ```bash
   supabase functions deploy telegram-bot --no-verify-jwt
   ```

3. **Check for errors** in deployment logs

### Issue 5: "Bot token invalid"

**Symptoms:**
- 404 errors from Telegram API
- "Not Found" responses
- Bot info not retrievable

**Solutions:**
1. **Get new bot token** from @BotFather
2. **Update environment variable** in Supabase dashboard
3. **Redeploy function** after updating token

## 🔧 Manual Setup Steps

### Step 1: Get Bot Token
1. Message @BotFather on Telegram
2. Use `/newbot` command
3. Follow instructions
4. Copy the token

### Step 2: Set Environment Variables
1. Go to [Supabase Dashboard](https://supabase.com/dashboard/project/hrfiaxcjknmswdirgczm)
2. Navigate to **Settings** → **Edge Functions**
3. Add these variables:
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   SUPABASE_URL=https://hrfiaxcjknmswdirgczm.supabase.co
   SUPABASE_SERVICE_ROLE_KEY=your_service_key_here
   FUNCTION_SECRET=03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4
   ```

### Step 3: Deploy Function
```bash
cd bot
supabase functions deploy telegram-bot --no-verify-jwt
```

### Step 4: Set Webhook
```bash
cd scripts
python setup_webhook.py
```

### Step 5: Test Bot
1. Send a message to your bot
2. Check if it responds
3. Verify data is stored in Supabase

## 📊 Monitoring & Debugging

### Check Function Logs
1. Go to Supabase Dashboard
2. Navigate to **Edge Functions** → **telegram-bot**
3. Click on **Logs** tab
4. Look for errors or debug information

### Test Database
```bash
cd scripts
python test_forum_topics.py
```

### Check Webhook Status
```bash
curl "https://api.telegram.org/bot/YOUR_BOT_TOKEN/getWebhookInfo"
```

## 🚀 Advanced Troubleshooting

### Reset Everything
If nothing works, reset the entire setup:

1. **Delete webhook**:
   ```bash
   curl "https://api.telegram.org/bot/YOUR_BOT_TOKEN/deleteWebhook"
   ```

2. **Redeploy function**:
   ```bash
   cd bot
   supabase functions deploy telegram-bot --no-verify-jwt
   ```

3. **Set webhook again**:
   ```bash
   cd scripts
   python setup_webhook.py
   ```

### Check Bot Permissions
Ensure your bot has these permissions:
- ✅ Can join groups
- ✅ Can read all group messages
- ✅ Admin rights in groups (for forum topics)

### Verify HTTPS
- Webhook URL must use HTTPS
- Supabase Edge Functions provide HTTPS automatically
- No custom certificates needed

## 📞 Getting Help

If you're still having issues:

1. **Check the logs** in Supabase dashboard
2. **Run the test scripts** to identify the problem
3. **Verify all environment variables** are set correctly
4. **Check bot permissions** in Telegram groups

## 🔗 Useful Links

- [Supabase Dashboard](https://supabase.com/dashboard/project/hrfiaxcjknmswdirgczm)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Supabase Edge Functions](https://supabase.com/docs/guides/functions)

## 📝 Quick Commands Reference

```bash
# Test bot functionality
python scripts/test_bot.py

# Setup webhook
python scripts/setup_webhook.py

# Deploy function
cd bot && supabase functions deploy telegram-bot --no-verify-jwt

# Check function status
cd bot && supabase functions list

# Test forum topics
python scripts/test_forum_topics.py
``` 