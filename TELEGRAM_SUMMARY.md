# Telegram Activity Summary Generator

## 📊 Overview

This GitHub Action automatically generates hourly HTML summaries of Telegram activity by scanning the Supabase database for recent messages and creating beautiful, detailed reports.

## 🚀 Features

### **Hourly Reports**
- Runs every hour at minute 0 (cron: `0 * * * *`)
- Can be triggered manually via GitHub Actions
- Generates HTML files with date in the filename in the `website/` directory

### **Comprehensive Data**
- **Message Statistics**: Total messages, users, and activity per chat
- **Chat Information**: Title, type, member count, forum status
- **Recent Messages**: Last 10 messages with sender and content
- **Forum Topics**: Special handling for supergroups with forum mode
- **User Activity**: Track unique users and message types

### **Beautiful HTML Reports**
- Modern, responsive design
- Color-coded statistics cards
- Collapsible message lists
- Forum topic sections with activity
- Mobile-friendly layout

## 📁 Generated Files

Reports are saved as:
```
website/telegram_summary_YYYY-MM-DD.html
```

Example: `website/telegram_summary_2025-01-13.html`

## 🔧 Setup

### 1. GitHub Secrets

Add these secrets to your GitHub repository:

| Secret Name | Description |
|-------------|-------------|
| `SUPABASE_URL` | Your Supabase project URL |
| `SUPABASE_SERVICE_ROLE_KEY` | Your Supabase service role key |

#### How to Find These Values

##### **Step 1: Get Your Supabase URL**
1. Go to your Supabase dashboard: https://supabase.com/dashboard/project/hrfiaxcjknmswdirgczm
2. Navigate to **Settings** → **API**
3. Copy the **Project URL** (it looks like: `https://hrfiaxcjknmswdirgczm.supabase.co`)

##### **Step 2: Get Your Service Role Key**
1. In the same **Settings** → **API** page
2. Scroll down to **Project API keys**
3. Copy the **service_role** key (starts with `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`)
4. **Important**: Use the `service_role` key, NOT the `anon` key

#### How to Set Up GitHub Secrets

##### **Step 1: Go to Repository Settings**
1. Navigate to your GitHub repository
2. Click on **Settings** tab
3. In the left sidebar, click **Secrets and variables** → **Actions**

##### **Step 2: Add the Secrets**
1. Click **New repository secret**
2. Add each secret:

| Secret Name | Secret Value |
|-------------|--------------|
| `SUPABASE_URL` | `https://hrfiaxcjknmswdirgczm.supabase.co` |
| `SUPABASE_SERVICE_ROLE_KEY` | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` (your actual key) |

##### **Step 3: Verify Setup**
1. Go to **Actions** tab in your repository
2. Select **Telegram Activity Summary Generator**
3. Click **Run workflow** to test manually

### 2. Environment Variables

The action uses the same environment variables as your bot:
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_SERVICE_ROLE_KEY`: Your Supabase service role key

## 📊 Report Content

### **Summary Statistics**
- **Active Chats**: Number of chats with recent activity
- **Total Messages**: All messages in the last hour
- **Active Users**: Unique users who sent messages
- **Forum Chats**: Supergroups with forum mode enabled

### **Per-Chat Details**
For each active chat, the report shows:

#### **Chat Header**
- Chat title and type (private/group/supergroup/channel)
- Member count and description

#### **Activity Statistics**
- Message count in the last hour
- Number of unique users
- Recent message count
- Forum topics count (if applicable)

#### **Recent Messages**
- Last 10 messages with:
  - Sender name and username
  - Message content (truncated to 100 characters)
  - Timestamp
  - Message type (text, photo, video, etc.)

#### **Forum Topics** (Supergroups Only)
- Topic names and status (open/closed)
- Recent activity in each topic
- Sample messages from topics

## 🎨 HTML Features

### **Responsive Design**
- Works on desktop, tablet, and mobile
- Grid-based layout that adapts to screen size
- Scrollable message lists

### **Visual Elements**
- **Gradient Cards**: Summary statistics with blue-purple gradients
- **Color-Coded Stats**: Different colors for different metrics
- **Topic Sections**: Red-bordered sections for forum topics
- **Message Lists**: Clean, readable message display

### **Navigation**
- Date-based reports for historical tracking
- Clear generation time and data coverage period
- Easy to browse multiple reports

## 🔄 Workflow

### **Automatic Execution**
1. **Hourly Trigger**: Runs every hour at minute 0
2. **Database Query**: Scans messages from the last hour
3. **Data Processing**: Groups by chat, calculates statistics
4. **HTML Generation**: Creates beautiful report with Jinja2 templates
5. **File Storage**: Saves to `website/` directory with date in filename
6. **Git Commit**: Automatically commits and pushes changes

### **Manual Trigger**
- Go to GitHub Actions tab
- Select "Telegram Activity Summary Generator"
- Click "Run workflow"

## 📈 Example Report Structure

```html
📱 Telegram Activity Summary
┌─────────────────────────────────────┐
│ Active Chats │ Total Messages │     │
│     5        │      127       │     │
│ Active Users │ Forum Chats    │     │
│     23       │      2         │     │
└─────────────────────────────────────┘

┌─ Chat: Crypto Discussion Group ─────┐
│ Type: supergroup │ Members: 1,234   │
│ Messages: 45 │ Users: 12 │ Recent: 8 │
│ Topics: 3                           │
│                                     │
│ 📝 Recent Messages:                  │
│ • John (@john): Bitcoin is mooning! │
│ • Alice: What do you think about... │
│ • Bob: I'm bullish on ETH           │
│                                     │
│ 🏷️ Forum Topics:                    │
│ • General Discussion (3 messages)   │
│ • Trading Signals (2 messages)      │
│ • News & Updates (1 message)        │
└─────────────────────────────────────┘
```

## 🔍 Troubleshooting

### **Common Issues**

1. **No reports generated**
   - Check GitHub Actions logs
   - Verify Supabase credentials
   - Ensure bot is collecting data

2. **Empty reports**
   - No recent activity in the last hour
   - Check if bot is properly logging messages
   - Verify database tables exist

3. **Missing forum topics**
   - Only supergroups with forum mode enabled
   - Topics must be created in the chat
   - Recent activity required

4. **GitHub Action fails**
   - Verify both secrets are set correctly
   - Check that service role key has proper permissions
   - Ensure Supabase URL is correct

### **Debug Commands**

```bash
# Test the script locally
cd scripts
python generate_telegram_summary.py

# Check GitHub Actions
# Go to Actions tab in your repository
```

### **Verification Steps**

1. **Check Secrets**: Go to Settings → Secrets and variables → Actions
2. **Test Manually**: Run the workflow manually from Actions tab
3. **Check Logs**: View the workflow logs for any error messages
4. **Verify Database**: Ensure your bot is logging messages to Supabase

## 🔒 Security

- Uses service role key for database access
- No sensitive data in HTML reports
- Environment variables are encrypted
- Reports are public (in website directory)

## 📝 Customization

### **Modify Report Period**
Change the `hours=1` parameter in `get_recent_messages()` to adjust the time window.

### **Add New Statistics**
Extend the `get_chat_summary()` function to include additional metrics.

### **Custom Styling**
Modify the CSS in the HTML template for different visual themes.

### **Additional Data**
Add more database queries to include other information like:
- Media file statistics
- Reply chain analysis
- User engagement metrics
- Message sentiment (future)

## 🚀 Future Enhancements

- **Real-time Updates**: WebSocket-based live updates
- **Analytics Dashboard**: Interactive charts and graphs
- **Export Options**: PDF, CSV, JSON formats
- **Email Notifications**: Send reports via email
- **Custom Filters**: Filter by chat type, user, or time period
- **Trend Analysis**: Compare activity across time periods 