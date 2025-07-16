#!/usr/bin/env python3
"""
Telegram Activity Summary Generator
Scans the database for messages in the last hour and generates an HTML summary.
"""

import os
import sys
from datetime import datetime, timedelta
from supabase import create_client, Client
from jinja2 import Template
import json

# Initialize Supabase client
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

if not supabase_url or not supabase_key:
    print("Error: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY environment variables are required")
    sys.exit(1)

supabase: Client = create_client(supabase_url, supabase_key)

def get_recent_messages(hours=1):
    """Get messages from the last N hours"""
    cutoff_time = datetime.now() - timedelta(hours=hours)
    
    response = supabase.table('messages_v1').select(
        '*, users_v1!messages_v1_from_user_id_fkey(*), chats_v1!messages_v1_chat_id_fkey(*), forum_topics_v1(*)'
    ).gte('date', cutoff_time.isoformat()).order('date', desc=True).execute()
    
    return response.data

def get_chat_summary(chat_id):
    """Get summary statistics for a specific chat"""
    cutoff_time = datetime.now() - timedelta(hours=1)
    
    # Get message count
    messages_response = supabase.table('messages_v1').select(
        'id, from_user_id, message_type, date'
    ).eq('chat_id', chat_id).gte('date', cutoff_time.isoformat()).execute()
    
    messages = messages_response.data
    
    # Get unique users
    unique_users = set(msg['from_user_id'] for msg in messages if msg['from_user_id'])
    
    # Get message types
    message_types = {}
    for msg in messages:
        msg_type = msg.get('message_type', 'unknown')
        message_types[msg_type] = message_types.get(msg_type, 0) + 1
    
    return {
        'message_count': len(messages),
        'unique_users': len(unique_users),
        'message_types': message_types,
        'last_message': max([msg['date'] for msg in messages]) if messages else None
    }

def get_forum_topics(chat_id):
    """Get forum topics for a chat"""
    response = supabase.table('forum_topics_v1').select('*').eq('chat_id', chat_id).execute()
    return response.data

def get_topic_messages(chat_id, topic_id):
    """Get messages for a specific forum topic in the last hour"""
    cutoff_time = datetime.now() - timedelta(hours=1)
    
    response = supabase.table('messages_v1').select(
        'id, from_user_id, text, date, users_v1!messages_v1_from_user_id_fkey(first_name, username)'
    ).eq('chat_id', chat_id).eq('message_thread_id', topic_id).gte('date', cutoff_time.isoformat()).execute()
    
    return response.data

def generate_html_summary():
    """Generate the HTML summary report"""
    
    # Get recent messages
    recent_messages = get_recent_messages(1)
    
    if not recent_messages:
        print("No recent messages found")
        return
    
    # Group messages by chat
    chats = {}
    for msg in recent_messages:
        chat_id = msg['chat_id']
        if chat_id not in chats:
            chats[chat_id] = {
                'chat_info': msg['chats_v1!messages_v1_chat_id_fkey'],
                'messages': [],
                'summary': get_chat_summary(chat_id),
                'forum_topics': []
            }
        chats[chat_id]['messages'].append(msg)
    
    # Get forum topics for supergroups
    for chat_id, chat_data in chats.items():
        if chat_data['chat_info'].get('is_forum'):
            chat_data['forum_topics'] = get_forum_topics(chat_id)
            
            # Get topic activity
            for topic in chat_data['forum_topics']:
                topic['recent_messages'] = get_topic_messages(chat_id, topic['topic_id'])
    
    # Generate HTML
    html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Telegram Activity Summary - {{ generation_time }}</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f7fa;
            line-height: 1.6;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background-color: white;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.2em;
            border-bottom: 3px solid #3498db;
            padding-bottom: 15px;
        }
        h2 {
            color: #34495e;
            margin-top: 30px;
            margin-bottom: 15px;
            border-left: 4px solid #3498db;
            padding-left: 15px;
        }
        h3 {
            color: #2980b9;
            margin-bottom: 10px;
        }
        .summary-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }
        .stat-number {
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 5px;
        }
        .chat-section {
            margin: 30px 0;
            padding: 20px;
            border: 1px solid #ecf0f1;
            border-radius: 10px;
            background-color: #fafbfc;
        }
        .chat-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        .chat-title {
            font-size: 1.3em;
            font-weight: bold;
            color: #2c3e50;
        }
        .chat-type {
            background: #3498db;
            color: white;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 0.8em;
        }
        .chat-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin: 15px 0;
        }
        .chat-stat {
            background: white;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            border-left: 4px solid #3498db;
        }
        .message-list {
            max-height: 300px;
            overflow-y: auto;
            border: 1px solid #ecf0f1;
            border-radius: 8px;
            background: white;
        }
        .message-item {
            padding: 10px 15px;
            border-bottom: 1px solid #f1f3f4;
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
        }
        .message-item:last-child {
            border-bottom: none;
        }
        .message-content {
            flex: 1;
            margin-right: 15px;
        }
        .message-sender {
            font-weight: bold;
            color: #2980b9;
            margin-bottom: 5px;
        }
        .message-text {
            color: #2c3e50;
            word-wrap: break-word;
        }
        .message-time {
            color: #7f8c8d;
            font-size: 0.8em;
            white-space: nowrap;
        }
        .topic-section {
            margin: 15px 0;
            padding: 15px;
            background: white;
            border-radius: 8px;
            border-left: 4px solid #e74c3c;
        }
        .topic-header {
            font-weight: bold;
            color: #e74c3c;
            margin-bottom: 10px;
        }
        .timestamp {
            text-align: center;
            color: #7f8c8d;
            margin-top: 30px;
            font-size: 14px;
            padding: 15px;
            background-color: #ecf0f1;
            border-radius: 8px;
        }
        .no-activity {
            text-align: center;
            color: #7f8c8d;
            font-style: italic;
            padding: 40px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📱 Telegram Activity Summary</h1>
        
        <div class="summary-stats">
            <div class="stat-card">
                <div class="stat-number">{{ total_chats }}</div>
                <div>Active Chats</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ total_messages }}</div>
                <div>Total Messages</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ total_users }}</div>
                <div>Active Users</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ forum_chats }}</div>
                <div>Forum Chats</div>
            </div>
        </div>

        {% for chat_id, chat_data in chats.items() %}
        <div class="chat-section">
            <div class="chat-header">
                <div class="chat-title">
                    {% if chat_data.chat_info.title %}
                        {{ chat_data.chat_info.title }}
                    {% else %}
                        Chat {{ chat_id }}
                    {% endif %}
                </div>
                <div class="chat-type">{{ chat_data.chat_info.chat_type }}</div>
            </div>
            
            <div class="chat-stats">
                <div class="chat-stat">
                    <div style="font-size: 1.5em; font-weight: bold; color: #3498db;">
                        {{ chat_data.summary.message_count }}
                    </div>
                    <div>Messages</div>
                </div>
                <div class="chat-stat">
                    <div style="font-size: 1.5em; font-weight: bold; color: #e74c3c;">
                        {{ chat_data.summary.unique_users }}
                    </div>
                    <div>Users</div>
                </div>
                <div class="chat-stat">
                    <div style="font-size: 1.5em; font-weight: bold; color: #f39c12;">
                        {{ chat_data.messages|length }}
                    </div>
                    <div>Recent</div>
                </div>
                {% if chat_data.chat_info.is_forum %}
                <div class="chat-stat">
                    <div style="font-size: 1.5em; font-weight: bold; color: #9b59b6;">
                        {{ chat_data.forum_topics|length }}
                    </div>
                    <div>Topics</div>
                </div>
                {% endif %}
            </div>

            {% if chat_data.messages %}
            <h3>📝 Recent Messages</h3>
            <div class="message-list">
                {% for msg in chat_data.messages[:10] %}
                <div class="message-item">
                    <div class="message-content">
                        <div class="message-sender">
                            {% if msg.users_v1!messages_v1_from_user_id_fkey %}
                                {{ msg.users_v1!messages_v1_from_user_id_fkey.first_name }}
                                {% if msg.users_v1!messages_v1_from_user_id_fkey.username %}
                                    (@{{ msg.users_v1!messages_v1_from_user_id_fkey.username }})
                                {% endif %}
                            {% else %}
                                Unknown User
                            {% endif %}
                        </div>
                        <div class="message-text">
                            {% if msg.text %}
                                {{ msg.text[:100] }}{% if msg.text|length > 100 %}...{% endif %}
                            {% else %}
                                <em>[{{ msg.message_type }} message]</em>
                            {% endif %}
                        </div>
                    </div>
                    <div class="message-time">
                        {{ msg.date.split('T')[1][:5] }}
                    </div>
                </div>
                {% endfor %}
            </div>
            {% endif %}

            {% if chat_data.chat_info.is_forum and chat_data.forum_topics %}
            <h3>🏷️ Forum Topics</h3>
            {% for topic in chat_data.forum_topics %}
            <div class="topic-section">
                <div class="topic-header">
                    {{ topic.name }}
                    {% if topic.is_closed %}
                        <span style="color: #e74c3c;">(Closed)</span>
                    {% endif %}
                </div>
                {% if topic.recent_messages %}
                <div style="margin-top: 10px;">
                    <strong>{{ topic.recent_messages|length }} recent messages:</strong>
                    <div style="margin-top: 5px; font-size: 0.9em; color: #7f8c8d;">
                        {% for msg in topic.recent_messages[:3] %}
                            {% if msg.users_v1!messages_v1_from_user_id_fkey %}
                                {{ msg.users_v1!messages_v1_from_user_id_fkey.first_name }}: {{ msg.text[:50] }}{% if msg.text|length > 50 %}...{% endif %}
                            {% endif %}
                            {% if not loop.last %}<br>{% endif %}
                        {% endfor %}
                    </div>
                </div>
                {% else %}
                <div style="color: #7f8c8d; font-style: italic;">No recent activity</div>
                {% endif %}
            </div>
            {% endfor %}
            {% endif %}
        </div>
        {% endfor %}

        <div class="timestamp">
            Report generated on: {{ generation_time }}<br>
            Data covers the last hour ({{ start_time }} to {{ end_time }})
        </div>
    </div>
</body>
</html>
    """
    
    # Calculate summary statistics
    total_chats = len(chats)
    total_messages = sum(chat['summary']['message_count'] for chat in chats.values())
    total_users = len(set(
        msg['from_user_id'] 
        for chat in chats.values() 
        for msg in chat['messages'] 
        if msg['from_user_id']
    ))
    forum_chats = sum(1 for chat in chats.values() if chat['chat_info'].get('is_forum'))
    
    # Generate timestamps
    generation_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
    start_time = (datetime.now() - timedelta(hours=1)).strftime('%H:%M')
    end_time = datetime.now().strftime('%H:%M')
    
    # Render template
    template = Template(html_template)
    html_content = template.render(
        chats=chats,
        total_chats=total_chats,
        total_messages=total_messages,
        total_users=total_users,
        forum_chats=forum_chats,
        generation_time=generation_time,
        start_time=start_time,
        end_time=end_time
    )
    
    # Ensure website directory exists
    os.makedirs('website', exist_ok=True)
    
    # Write HTML file with date in filename (following the same pattern as the existing cron job)
    current_date = datetime.now().strftime('%Y-%m-%d')
    filename = f'website/telegram_summary_{current_date}.html'
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Generated summary report: {filename}")
    print(f"Total chats: {total_chats}")
    print(f"Total messages: {total_messages}")
    print(f"Total users: {total_users}")
    print(f"Forum chats: {forum_chats}")

if __name__ == "__main__":
    generate_html_summary() 