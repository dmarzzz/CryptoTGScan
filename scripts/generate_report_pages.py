#!/usr/bin/env python3
"""
Wartime Milady CEO - Individual Report Page Generator
Generates detailed report pages for each monitored Telegram chat.
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from supabase import create_client, Client
import json

# Initialize Supabase client
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

if not supabase_url or not supabase_key:
    print("Error: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY environment variables are required")
    sys.exit(1)

supabase: Client = create_client(supabase_url, supabase_key)

def get_chat_messages(chat_id, start_date, end_date, limit=100):
    """Get messages from a specific chat within a date range"""
    response = supabase.table('messages_v1').select(
        'id, telegram_message_id, from_user_id, date, text, message_type, reply_to_message_id'
    ).eq('chat_id', chat_id).gte('date', start_date.isoformat()).lt('date', end_date.isoformat()).order('date', desc=True).limit(limit).execute()
    
    return response.data

def get_chat_info(chat_id):
    """Get chat information"""
    response = supabase.table('chats_v1').select('*').eq('chat_id', chat_id).execute()
    return response.data[0] if response.data else None

def get_users_data(user_ids):
    """Get user data for the given user IDs"""
    if not user_ids:
        return {}
    
    response = supabase.table('users_v1').select('*').in_('user_id', list(user_ids)).execute()
    users = {}
    for user in response.data:
        users[user['user_id']] = user
    return users

def get_chat_stats(chat_id, start_date, end_date):
    """Get comprehensive statistics for a chat within a date range"""
    # Get messages
    messages_response = supabase.table('messages_v1').select(
        'id, from_user_id, message_type, date'
    ).eq('chat_id', chat_id).gte('date', start_date.isoformat()).lt('date', end_date.isoformat()).execute()
    
    messages = messages_response.data
    
    # Calculate stats
    unique_users = set(msg['from_user_id'] for msg in messages if msg['from_user_id'])
    message_types = {}
    hourly_activity = {}
    
    for msg in messages:
        # Message types
        msg_type = msg.get('message_type', 'text')
        message_types[msg_type] = message_types.get(msg_type, 0) + 1
        
        # Hourly activity
        msg_time = datetime.fromisoformat(msg['date'].replace('Z', '+00:00'))
        hour = msg_time.strftime('%H')
        hourly_activity[hour] = hourly_activity.get(hour, 0) + 1
    
    return {
        'total_messages': len(messages),
        'unique_participants': len(unique_users),
        'message_types': message_types,
        'hourly_activity': hourly_activity,
        'last_message': max([msg['date'] for msg in messages]) if messages else None
    }

def format_military_time(timestamp):
    """Format timestamp in military time"""
    try:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H%MZ')
    except Exception:
        return timestamp

def get_chat_icon(chat_type, title):
    """Get appropriate icon for chat type"""
    title_lower = (title or '').lower()
    
    if "ethereum" in title_lower and "core" in title_lower:
        return "⚡"
    elif "research" in title_lower:
        return "🔬"
    elif "defi" in title_lower or "protocol" in title_lower:
        return "💸"
    elif "layer" in title_lower and "2" in title_lower:
        return "🛣️"
    elif "nft" in title_lower:
        return "🖼️"
    elif "governance" in title_lower or "dao" in title_lower:
        return "🏛️"
    elif "security" in title_lower or "audit" in title_lower:
        return "🛡️"
    elif "developer" in title_lower or "tool" in title_lower:
        return "🛠️"
    elif "crypto" in title_lower or "bitcoin" in title_lower:
        return "₿"
    elif "trading" in title_lower:
        return "📈"
    elif "news" in title_lower:
        return "📰"
    
    if chat_type == "channel":
        return "📢"
    elif chat_type == "supergroup":
        return "👥"
    elif chat_type == "group":
        return "👥"
    else:
        return "💬"

def generate_report_css():
    """Generate the CSS for report pages"""
    return '''
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Inter:wght@400;500;700&display=swap');
:root {
  --color-primary: #FF006E;
  --color-secondary: #00F5FF;
  --color-accent: #00FF00;
  --color-bg: #0A0A0A;
  --color-surface: #1A1A1A;
  --color-text: #F0F0F0;
  --font-mono: 'Space Mono', monospace;
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

body {
  font-family: var(--font-sans);
  color: var(--color-text);
  background:
    radial-gradient(ellipse at top left, rgba(255,0,110,0.1) 0%, transparent 50%),
    radial-gradient(ellipse at bottom right, rgba(0,245,255,0.1) 0%, transparent 50%),
    #0A0A0A;
  min-height: 100vh;
  margin: 0;
  animation: flicker 10s infinite;
}

body::after {
  content: '';
  position: fixed;
  top: 0; left: 0;
  width: 100vw; height: 100vh;
  background-image:
    linear-gradient(rgba(255,0,110,0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,0,110,0.03) 1px, transparent 1px);
  background-size: 50px 50px;
  pointer-events: none;
  z-index: 1;
}

@keyframes flicker {
  0%, 100% { opacity: 1; }
  95% { opacity: 0.98; }
}

h1.site-title {
  font-family: 'Space Mono', monospace;
  font-size: clamp(2rem, 5vw, 3.5rem);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  background: linear-gradient(45deg, #FF006E, #00F5FF, #00FF00);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-shadow: 0 0 30px rgba(255,0,110,0.5);
  margin: 0;
}

.site-header {
  position: relative;
  padding: 2rem;
  margin-bottom: 3rem;
  background: linear-gradient(180deg, rgba(26,26,26,0.8) 0%, transparent 100%);
  border: 2px solid #FF006E;
  border-radius: 12px;
  overflow: hidden;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
  display: flex;
  align-items: center;
  gap: 2rem;
  position: relative;
  z-index: 1;
}

.chat-icon {
  font-size: 4em;
  width: 120px;
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255,0,110,0.1);
  border: 2px solid var(--color-primary);
  border-radius: 12px;
  flex-shrink: 0;
}

.header-text {
  flex: 1;
}

.status-bar {
  display: flex;
  align-items: center;
  gap: 2rem;
  margin-top: 1rem;
}

.timestamp {
  font-family: 'Space Mono', monospace;
  background: rgba(0,245,255,0.1);
  border: 1px solid #00F5FF;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  letter-spacing: 0.1em;
  display: inline-block;
}

.status-indicator {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1.5rem;
  background: rgba(0,255,0,0.1);
  border: 2px solid #00FF00;
  border-radius: 20px;
  font-family: 'Space Mono', monospace;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  font-weight: 700;
  box-shadow:
    inset 0 0 20px rgba(0,255,0,0.3),
    0 0 20px rgba(0,255,0,0.5);
  position: relative;
}

.status-indicator::before {
  content: '';
  display: inline-block;
  width: 10px; height: 10px;
  background: #00FF00;
  border-radius: 50%;
  margin-right: 0.5em;
  animation: blink 1s infinite;
  box-shadow: 0 0 10px #00FF00;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}

.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 3rem 2rem;
  position: relative;
  z-index: 2;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 3rem;
}

.stat-card {
  background: linear-gradient(135deg, #1A1A1A 0%, #0F0F0F 100%);
  border: 2px solid #FF006E;
  border-radius: 12px;
  padding: 1.5rem;
  text-align: center;
  transition: all 0.2s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  border-color: #00F5FF;
  box-shadow: 0 4px 24px rgba(0,245,255,0.15);
}

.stat-value {
  font-family: 'Space Mono', monospace;
  font-weight: 700;
  font-size: 2.5rem;
  color: #00F5FF;
  text-shadow:
    0 0 10px #00F5FF,
    0 0 20px #00F5FF,
    0 0 30px #00F5FF;
  letter-spacing: 0.1em;
  margin-bottom: 0.5rem;
}

.stat-label {
  font-size: 0.875rem;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  opacity: 0.7;
  font-family: 'Space Mono', monospace;
}

.messages-section {
  background: linear-gradient(135deg, #1A1A1A 0%, #0F0F0F 100%);
  border: 2px solid #FF006E;
  border-radius: 12px;
  padding: 2rem;
  margin-bottom: 2rem;
}

.section-title {
  font-family: 'Space Mono', monospace;
  font-size: 1.5rem;
  color: var(--color-text);
  margin-bottom: 1.5rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.message-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.message-item {
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,0,110,0.2);
  border-radius: 8px;
  padding: 1rem;
  transition: all 0.2s ease;
}

.message-item:hover {
  background: rgba(255,255,255,0.08);
  border-color: rgba(255,0,110,0.4);
  transform: translateX(4px);
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.message-author {
  font-family: 'Space Mono', monospace;
  font-weight: 700;
  color: #00F5FF;
  font-size: 0.9rem;
}

.message-time {
  font-family: 'Space Mono', monospace;
  font-size: 0.8rem;
  color: #888;
}

.message-text {
  color: var(--color-text);
  line-height: 1.5;
  word-wrap: break-word;
}

.message-type-badge {
  display: inline-block;
  padding: 0.2rem 0.5rem;
  background: rgba(0,255,0,0.1);
  border: 1px solid #00FF00;
  border-radius: 4px;
  font-size: 0.7rem;
  font-family: 'Space Mono', monospace;
  color: #00FF00;
  margin-left: 0.5rem;
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: rgba(255,0,110,0.1);
  border: 2px solid #FF006E;
  border-radius: 8px;
  color: #FF006E;
  text-decoration: none;
  font-family: 'Space Mono', monospace;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  transition: all 0.2s ease;
  margin-bottom: 2rem;
}

.back-link:hover {
  background: rgba(255,0,110,0.2);
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(255,0,110,0.3);
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    text-align: center;
    gap: 1.5rem;
  }
  
  .chat-icon {
    width: 80px;
    height: 80px;
    font-size: 2.5em;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .status-bar {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
}
'''

def generate_report_page(chat_id, start_date, end_date, output_dir='website/reports'):
    """Generate a detailed report page for a specific chat and date range"""
    
    # Get chat data
    chat_info = get_chat_info(chat_id)
    if not chat_info:
        print(f"Chat {chat_id} not found")
        return
    
    # Get messages
    messages = get_chat_messages(chat_id, start_date, end_date, limit=50)
    
    # Get user data
    user_ids = set(msg['from_user_id'] for msg in messages if msg['from_user_id'])
    users_data = get_users_data(user_ids)
    
    # Get statistics
    stats = get_chat_stats(chat_id, start_date, end_date)
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Generate HTML
    current_time = datetime.utcnow().strftime('%Y-%m-%d %H%MZ')
    chat_icon = get_chat_icon(chat_info.get('chat_type'), chat_info.get('title'))
    
    # Format date range for display
    date_range = f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Wartime Milady CEO - {chat_info.get('title', 'Unknown Chat')} Report ({date_range})</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Inter:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
{generate_report_css()}
    </style>
</head>
<body>
    <div class="scan-lines"></div>
    <header class="site-header">
        <div class="header-content">
            <div class="chat-icon">
                {chat_icon}
            </div>
            <div class="header-text">
                <h1 class="site-title">{chat_info.get('title', 'Unknown Chat')}</h1>
                <p class="site-subtitle">Intelligence Report - {date_range}</p>
                <div class="status-bar">
                    <span class="timestamp">{current_time}</span>
                    <span class="status-indicator" aria-live="polite">SYSTEMS ONLINE</span>
                </div>
            </div>
        </div>
    </header>
    
    <main class="main-content">
        <a href="../index.html" class="back-link">← BACK TO COMMAND CENTER</a>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{stats['total_messages']}</div>
                <div class="stat-label">Total Messages</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{stats['unique_participants']}</div>
                <div class="stat-label">Active Participants</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{len(stats['message_types'])}</div>
                <div class="stat-label">Message Types</div>
            </div>
        </div>
        
        <div class="messages-section">
            <h2 class="section-title">Recent Messages</h2>
            <div class="message-list">
'''
    
    # Add messages
    for msg in messages:
        user = users_data.get(msg['from_user_id'], {})
        author_name = user.get('first_name', 'Unknown User')
        if user.get('last_name'):
            author_name += f" {user['last_name']}"
        
        message_time = format_military_time(msg['date'])
        message_text = msg.get('text', '[No text content]')
        message_type = msg.get('message_type', 'text')
        
        html += f'''
                <div class="message-item">
                    <div class="message-header">
                        <span class="message-author">{author_name}</span>
                        <span class="message-time">{message_time}</span>
                    </div>
                    <div class="message-text">{message_text}</div>
                    <span class="message-type-badge">{message_type}</span>
                </div>
'''
    
    html += '''
            </div>
        </div>
    </main>
    
    <footer class="site-footer">
        <p>Generated by Wartime Milady CEO Intelligence Platform</p>
        <p>Report generated: ''' + current_time + '''</p>
    </footer>
</body>
</html>'''
    
    # Write to file with date-based filename
    safe_filename = str(chat_id).replace('-', '')  # Remove minus sign for filename
    date_suffix = start_date.strftime('%Y%m%d')
    output_file = output_path / f"report_{safe_filename}_{date_suffix}.html"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"Generated report: {output_file}")
    return output_file

def generate_daily_reports_for_chat(chat_id, days_back=7):
    """Generate daily reports for the last N days for a specific chat"""
    reports = []
    
    for i in range(days_back):
        # Calculate date range for this day
        end_date = datetime.now() - timedelta(days=i)
        start_date = end_date - timedelta(days=1)
        
        # Generate report for this day
        report_file = generate_report_page(chat_id, start_date, end_date)
        if report_file:
            reports.append({
                'date': start_date.strftime('%Y-%m-%d'),
                'filename': report_file.name,
                'start_date': start_date,
                'end_date': end_date
            })
    
    return reports

def generate_all_reports():
    """Generate daily report pages for all monitored chats"""
    # Read channels data from the JSON file generated by the main script
    channels_file = Path('data/channels.json')
    
    if not channels_file.exists():
        print("Error: channels.json not found. Run generate_milady_data.py first.")
        return
    
    try:
        with open(channels_file, 'r', encoding='utf-8') as f:
            channels_data = json.load(f)
        
        print(f"📊 Generating daily reports for {len(channels_data['channels'])} channels...")
        
        all_reports = {}
        
        for channel in channels_data['channels']:
            try:
                chat_id = int(channel['id'])  # Convert string ID back to int
                print(f"📄 Generating daily reports for {channel['name']} (ID: {chat_id})")
                
                # Generate daily reports for this chat
                reports = generate_daily_reports_for_chat(chat_id, days_back=7)
                all_reports[chat_id] = {
                    'name': channel['name'],
                    'reports': reports
                }
                
            except Exception as e:
                print(f"Error generating reports for chat {channel['name']} (ID: {channel['id']}): {e}")
        
        # Save reports metadata for the popup interface
        metadata_file = Path('website/reports/metadata.json')
        metadata_file.parent.mkdir(exist_ok=True)
        
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(all_reports, f, indent=2, default=str)
        
        print(f"✅ Generated daily reports for {len(channels_data['channels'])} channels")
        print(f"📁 Reports metadata saved to: {metadata_file}")
        
    except Exception as e:
        print(f"Error reading channels data: {e}")
        return

if __name__ == "__main__":
    generate_all_reports() 