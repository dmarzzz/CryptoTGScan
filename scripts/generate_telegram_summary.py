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
    
    # Get messages without relationships to avoid the foreign key issue
    response = supabase.table('messages_v1').select(
        'id, telegram_message_id, chat_id, from_user_id, message_thread_id, date, edit_date, text, message_type, reply_to_message_id, reply_to_chat_id, is_deleted'
    ).gte('date', cutoff_time.isoformat()).order('date', desc=True).execute()
    
    return response.data

def get_users_data(user_ids):
    """Get user data for the given user IDs"""
    if not user_ids:
        return {}
    
    response = supabase.table('users_v1').select('*').in_('user_id', list(user_ids)).execute()
    users = {}
    for user in response.data:
        users[user['user_id']] = user
    return users

def get_chats_data(chat_ids):
    """Get chat data for the given chat IDs"""
    if not chat_ids:
        return {}
    
    response = supabase.table('chats_v1').select('*').in_('chat_id', list(chat_ids)).execute()
    chats = {}
    for chat in response.data:
        chats[chat['chat_id']] = chat
    return chats

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
    """Get forum topics with recent message counts for a chat"""
    cutoff_time = datetime.now() - timedelta(hours=1)
    
    # Get forum topics for this chat
    topics_response = supabase.table('forum_topics_v1').select('*').eq('chat_id', chat_id).execute()
    topics = topics_response.data
    
    # For each topic, get recent messages
    for topic in topics:
        messages_response = supabase.table('messages_v1').select(
            'id, from_user_id, text, date'
        ).eq('chat_id', chat_id).eq('message_thread_id', topic['topic_id']).gte('date', cutoff_time.isoformat()).execute()
        
        topic['recent_messages'] = messages_response.data
        topic['message_count'] = len(messages_response.data)
    
    return topics

def get_topic_messages(chat_id, topic_id):
    """Get messages for a specific forum topic in the last hour"""
    cutoff_time = datetime.now() - timedelta(hours=1)
    
    response = supabase.table('messages_v1').select(
        'id, from_user_id, text, date'
    ).eq('chat_id', chat_id).eq('message_thread_id', topic_id).gte('date', cutoff_time.isoformat()).execute()
    
    return response.data

def generate_html_summary():
    """Generate the HTML summary report"""
    
    # Get recent messages
    recent_messages = get_recent_messages(1)
    
    if not recent_messages:
        print("No recent messages found")
        return
    
    # Extract user_ids and chat_ids from messages
    user_ids = set(msg['from_user_id'] for msg in recent_messages if msg['from_user_id'])
    chat_ids = set(msg['chat_id'] for msg in recent_messages if msg['chat_id'])
    
    # Get user data
    users_data = get_users_data(user_ids)
    
    # Get chat data
    chats_data = get_chats_data(chat_ids)
    
    # Group messages by chat
    chats = {}
    for msg in recent_messages:
        chat_id = msg['chat_id']
        if chat_id not in chats:
            chats[chat_id] = {
                'chat_info': chats_data.get(chat_id),
                'messages': [],
                'summary': get_chat_summary(chat_id),
                'forum_topics': []
            }
        chats[chat_id]['messages'].append(msg)
    
    # Get forum topics for each chat
    for chat_id, chat_data in chats.items():
        if chat_data['chat_info'] and chat_data['chat_info'].get('is_forum'):
            chat_data['forum_topics'] = get_forum_topics(chat_id)
    
    # Generate HTML
    html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Telegram Activity Summary - {{ generation_time }}</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            line-height: 1.6;
            color: #2d3748;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 24px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
            color: white;
            padding: 40px;
            text-align: center;
            position: relative;
            overflow: hidden;
        }
        
        .header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="white" opacity="0.1"/><circle cx="75" cy="75" r="1" fill="white" opacity="0.1"/><circle cx="50" cy="10" r="0.5" fill="white" opacity="0.1"/><circle cx="10" cy="60" r="0.5" fill="white" opacity="0.1"/><circle cx="90" cy="40" r="0.5" fill="white" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
            opacity: 0.3;
        }
        
        .header h1 {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 10px;
            position: relative;
            z-index: 1;
        }
        
        .header .subtitle {
            font-size: 1.1rem;
            opacity: 0.9;
            font-weight: 400;
            position: relative;
            z-index: 1;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 24px;
            padding: 40px;
            background: #f8fafc;
        }
        
        .stat-card {
            background: white;
            padding: 32px 24px;
            border-radius: 16px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            border: 1px solid #e2e8f0;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .stat-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #3b82f6, #8b5cf6, #ec4899);
        }
        
        .stat-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
        }
        
        .stat-number {
            font-size: 2.5rem;
            font-weight: 700;
            color: #1e293b;
            margin-bottom: 8px;
            display: block;
        }
        
        .stat-label {
            font-size: 0.9rem;
            color: #64748b;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .content {
            padding: 40px;
        }
        
        .chat-section {
            margin: 32px 0;
            background: white;
            border-radius: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            border: 1px solid #e2e8f0;
            overflow: hidden;
            transition: all 0.3s ease;
        }
        
        .chat-section:hover {
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
        }
        
        .chat-header {
            background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
            padding: 24px 32px;
            border-bottom: 1px solid #e2e8f0;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 16px;
        }
        
        .chat-title {
            font-size: 1.4rem;
            font-weight: 600;
            color: #1e293b;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .chat-icon {
            width: 24px;
            height: 24px;
            background: #3b82f6;
            border-radius: 6px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 12px;
            font-weight: 600;
        }
        
        .chat-type {
            background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            box-shadow: 0 2px 4px rgba(59, 130, 246, 0.3);
        }
        
        .chat-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 16px;
            padding: 24px 32px;
            background: #f8fafc;
            border-bottom: 1px solid #e2e8f0;
        }
        
        .chat-stat {
            text-align: center;
            padding: 16px;
            background: white;
            border-radius: 12px;
            border: 1px solid #e2e8f0;
        }
        
        .chat-stat-number {
            font-size: 1.8rem;
            font-weight: 700;
            color: #1e293b;
            margin-bottom: 4px;
            display: block;
        }
        
        .chat-stat-label {
            font-size: 0.8rem;
            color: #64748b;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .chat-content {
            padding: 32px;
        }
        
        .section-title {
            font-size: 1.2rem;
            font-weight: 600;
            color: #1e293b;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .section-icon {
            width: 20px;
            height: 20px;
            background: #3b82f6;
            border-radius: 4px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 10px;
            font-weight: 600;
        }
        
        .message-list {
            max-height: 400px;
            overflow-y: auto;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            background: #f8fafc;
        }
        
        .message-item {
            padding: 16px 20px;
            border-bottom: 1px solid #e2e8f0;
            background: white;
            transition: background-color 0.2s ease;
        }
        
        .message-item:last-child {
            border-bottom: none;
        }
        
        .message-item:hover {
            background: #f1f5f9;
        }
        
        .message-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }
        
        .message-sender {
            font-weight: 600;
            color: #1e293b;
            font-size: 0.9rem;
        }
        
        .message-time {
            color: #64748b;
            font-size: 0.8rem;
            font-weight: 500;
        }
        
        .message-text {
            color: #374151;
            line-height: 1.5;
            word-wrap: break-word;
        }
        
        .topic-section {
            margin: 20px 0;
            padding: 20px;
            background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
            border-radius: 12px;
            border-left: 4px solid #f59e0b;
        }
        
        .topic-header {
            font-weight: 600;
            color: #92400e;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .topic-icon {
            width: 16px;
            height: 16px;
            background: #f59e0b;
            border-radius: 3px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 8px;
            font-weight: 600;
        }
        
        .topic-content {
            color: #78350f;
            font-size: 0.9rem;
            line-height: 1.5;
        }
        
        .footer {
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
            padding: 32px 40px;
            text-align: center;
            border-top: 1px solid #e2e8f0;
        }
        
        .timestamp {
            color: #64748b;
            font-size: 0.9rem;
            font-weight: 500;
        }
        
        .no-activity {
            text-align: center;
            color: #64748b;
            font-style: italic;
            padding: 60px 20px;
            background: #f8fafc;
            border-radius: 12px;
            margin: 20px 0;
        }
        
        .no-activity-icon {
            font-size: 3rem;
            margin-bottom: 16px;
            opacity: 0.5;
        }
        
        /* Scrollbar styling */
        .message-list::-webkit-scrollbar {
            width: 8px;
        }
        
        .message-list::-webkit-scrollbar-track {
            background: #f1f5f9;
            border-radius: 4px;
        }
        
        .message-list::-webkit-scrollbar-thumb {
            background: #cbd5e1;
            border-radius: 4px;
        }
        
        .message-list::-webkit-scrollbar-thumb:hover {
            background: #94a3b8;
        }
        
        /* Responsive design */
        @media (max-width: 768px) {
            body {
                padding: 10px;
            }
            
            .header {
                padding: 30px 20px;
            }
            
            .header h1 {
                font-size: 2rem;
            }
            
            .stats-grid {
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 16px;
                padding: 24px;
            }
            
            .content {
                padding: 24px;
            }
            
            .chat-header {
                padding: 20px;
                flex-direction: column;
                align-items: flex-start;
            }
            
            .chat-stats {
                grid-template-columns: repeat(2, 1fr);
                gap: 12px;
                padding: 20px;
            }
            
            .chat-content {
                padding: 20px;
            }
        }
        
        /* Animation */
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .chat-section {
            animation: fadeInUp 0.6s ease-out;
        }
        
        .stat-card {
            animation: fadeInUp 0.6s ease-out;
        }
        
        .stat-card:nth-child(1) { animation-delay: 0.1s; }
        .stat-card:nth-child(2) { animation-delay: 0.2s; }
        .stat-card:nth-child(3) { animation-delay: 0.3s; }
        .stat-card:nth-child(4) { animation-delay: 0.4s; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📱 Telegram Activity Summary</h1>
            <div class="subtitle">Real-time insights from your Telegram channels</div>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <span class="stat-number">{{ total_chats }}</span>
                <div class="stat-label">Active Chats</div>
            </div>
            <div class="stat-card">
                <span class="stat-number">{{ total_messages }}</span>
                <div class="stat-label">Total Messages</div>
            </div>
            <div class="stat-card">
                <span class="stat-number">{{ total_users }}</span>
                <div class="stat-label">Active Users</div>
            </div>
            <div class="stat-card">
                <span class="stat-number">{{ forum_chats }}</span>
                <div class="stat-label">Forum Chats</div>
            </div>
        </div>

        <div class="content">
            {% for chat_id, chat_data in chats.items() %}
            <div class="chat-section">
                <div class="chat-header">
                    <div class="chat-title">
                        <div class="chat-icon">💬</div>
                        {% if chat_data.chat_info and chat_data.chat_info.title %}
                            {{ chat_data.chat_info.title }}
                        {% else %}
                            Chat {{ chat_id }}
                        {% endif %}
                    </div>
                    <div class="chat-type">{{ chat_data.chat_info.chat_type if chat_data.chat_info else 'Unknown' }}</div>
                </div>
                
                <div class="chat-stats">
                    <div class="chat-stat">
                        <span class="chat-stat-number">{{ chat_data.summary.message_count }}</span>
                        <div class="chat-stat-label">Messages</div>
                    </div>
                    <div class="chat-stat">
                        <span class="chat-stat-number">{{ chat_data.summary.unique_users }}</span>
                        <div class="chat-stat-label">Users</div>
                    </div>
                    <div class="chat-stat">
                        <span class="chat-stat-number">{{ chat_data.messages|length }}</span>
                        <div class="chat-stat-label">Recent</div>
                    </div>
                    {% if chat_data.chat_info and chat_data.chat_info.is_forum %}
                    <div class="chat-stat">
                        <span class="chat-stat-number">{{ chat_data.forum_topics|length }}</span>
                        <div class="chat-stat-label">Topics</div>
                    </div>
                    {% endif %}
                </div>

                <div class="chat-content">
                    {% if chat_data.messages %}
                    <div class="section-title">
                        <div class="section-icon">📝</div>
                        Recent Messages
                    </div>
                    <div class="message-list">
                        {% for msg in chat_data.messages[:10] %}
                        <div class="message-item">
                            <div class="message-header">
                                <div class="message-sender">
                                    {% if msg.from_user_id in users_data %}
                                        {{ users_data[msg.from_user_id].first_name }}
                                        {% if users_data[msg.from_user_id].username %}
                                            (@{{ users_data[msg.from_user_id].username }})
                                        {% endif %}
                                    {% else %}
                                        Unknown User
                                    {% endif %}
                                </div>
                                <div class="message-time">
                                    {{ msg.date.split('T')[1][:5] }}
                                </div>
                            </div>
                            <div class="message-text">
                                {% if msg.text %}
                                    {{ msg.text[:100] }}{% if msg.text|length > 100 %}...{% endif %}
                                {% else %}
                                    <em>[{{ msg.message_type }} message]</em>
                                {% endif %}
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                    {% endif %}

                    {% if chat_data.chat_info and chat_data.chat_info.is_forum and chat_data.forum_topics %}
                    <div class="section-title" style="margin-top: 32px;">
                        <div class="section-icon">🏷️</div>
                        Forum Topics
                    </div>
                    {% for topic in chat_data.forum_topics %}
                    <div class="topic-section">
                        <div class="topic-header">
                            <div class="topic-icon">📌</div>
                            {{ topic.name }}
                            {% if topic.is_closed %}
                                <span style="color: #dc2626;">(Closed)</span>
                            {% endif %}
                        </div>
                        {% if topic.recent_messages %}
                        <div class="topic-content">
                            <strong>{{ topic.recent_messages|length }} recent messages:</strong><br>
                            {% for msg in topic.recent_messages[:3] %}
                                {% if msg.from_user_id in users_data %}
                                    <strong>{{ users_data[msg.from_user_id].first_name }}</strong>: {{ msg.text[:50] }}{% if msg.text|length > 50 %}...{% endif %}
                                {% endif %}
                                {% if not loop.last %}<br>{% endif %}
                            {% endfor %}
                        </div>
                        {% else %}
                        <div class="topic-content" style="font-style: italic;">No recent activity</div>
                        {% endif %}
                    </div>
                    {% endfor %}
                    {% endif %}
                </div>
            </div>
            {% endfor %}

            {% if not chats %}
            <div class="no-activity">
                <div class="no-activity-icon">📭</div>
                <h3>No Recent Activity</h3>
                <p>No messages were found in the last hour.</p>
            </div>
            {% endif %}
        </div>

        <div class="footer">
            <div class="timestamp">
                📊 Report generated on: {{ generation_time }}<br>
                ⏰ Data covers the last hour ({{ start_time }} to {{ end_time }})
            </div>
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
    forum_chats = sum(1 for chat in chats.values() if chat['chat_info'] and chat['chat_info'].get('is_forum'))
    
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
        end_time=end_time,
        users_data=users_data,
        chats_data=chats_data
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