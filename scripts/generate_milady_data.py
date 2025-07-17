#!/usr/bin/env python3
"""
Generate channels.json data for Wartime Milady CEO Intelligence Platform
Extracts data from Supabase database and formats it for the static site generator.
"""

import os
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path
from supabase import create_client, Client

# Initialize Supabase client
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

if not supabase_url or not supabase_key:
    print("Error: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY environment variables are required")
    sys.exit(1)

supabase: Client = create_client(supabase_url, supabase_key)

def get_chat_activity_24h(chat_id):
    """
    Get 24-hour activity statistics for a chat
    """
    cutoff_time = datetime.now() - timedelta(hours=24)    # Get messages from last 24 hours
    messages_response = supabase.table('messages_v1').select(
        "id,from_user_id, date"
    ).eq('chat_id', chat_id).gte('date', cutoff_time.isoformat()).execute()
    
    messages = messages_response.data
    
    # Get unique participants
    unique_users = set(msg['from_user_id'] for msg in messages if msg['from_user_id'])    # Get previous 24 hours for comparison
    prev_cutoff = cutoff_time - timedelta(hours=24)
    prev_messages_response = supabase.table('messages_v1').select(
        "id,from_user_id, date"
    ).eq('chat_id', chat_id).gte('date', prev_cutoff.isoformat()).lt('date', cutoff_time.isoformat()).execute()
    
    prev_messages = prev_messages_response.data
    prev_unique_users = set(msg['from_user_id'] for msg in prev_messages if msg['from_user_id'])
    
    # Calculate change percentages
    current_count = len(messages)
    prev_count = len(prev_messages)
    
    if prev_count > 0:
        message_change = ((current_count - prev_count) / prev_count) * 100
    else:
        message_change = 100 if current_count > 0 else 0
    current_users = len(unique_users)
    prev_users = len(prev_unique_users)
    
    if prev_users > 0:
        user_change = ((current_users - prev_users) / prev_users) * 100
    else:
        user_change = 100 if current_users > 0 else 0
    
    # Determine trend based on message count
    trend = "up" if message_change > 0 else "down"
    
    return {
        "messages_24h": current_count,
        "participants_24h": current_users,
        "change_percent": round(message_change, 1),
        "trend": trend
    }

def get_chat_icon(chat_type, title):
    """
    Get appropriate icon for chat type
    """
    title_lower = title.lower()
    
    # Channel-specific icons
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
    
    # Default icons based on chat type
    if chat_type == "channel":
        return "📢"
    elif chat_type == "supergroup":
        return "👥"
    elif chat_type == "group":
        return "👥"
    else:
        return "💬"

def get_active_chats():
    """
    Get all active chats with recent activity
    """
    # Get chats that have had messages in the last 7 days
    cutoff_time = datetime.now() - timedelta(days=7)
    
    # Get unique chat IDs from recent messages
    messages_response = supabase.table('messages_v1').select(
      "chat_id"
    ).gte('date', cutoff_time.isoformat()).execute()
    
    chat_ids = set(msg['chat_id'] for msg in messages_response.data if msg['chat_id'])
    
    if not chat_ids:
        return []
    # Get chat details - use select('*') like the working script
    chats_response = supabase.table('chats_v1').select('*').in_('chat_id', list(chat_ids)).execute()
    
    return chats_response.data

def generate_channels_data():
    """
    Generate the channels.json data structure
    """
    print("🔍 Fetching active chats from database...")
    active_chats = get_active_chats()
    
    if not active_chats:
        print("⚠️  No active chats found in the last 7 days")
        return None
    
    print(f"📊 Found {len(active_chats)} active chats")
    
    channels = []
    now = datetime.now()
    
    for chat in active_chats:
        print(f"📈 Processing chat: {chat.get('title', 'Unknown')}")
        
        # Get 24-hour activity stats
        activity = get_chat_activity_24h(chat['chat_id'])
        
        # Skip chats with no recent activity
        if activity['messages_24h'] == 0:
            continue
        
        # Create channel entry
        channel = {
          "id": str(chat['chat_id']),
            "name": chat.get('title', 'Unknown Chat'),
           "icon": get_chat_icon(chat.get('chat_type'), chat.get('title')),
            "last_update": now.strftime('%Y-%m-%dT%H:%M:%SZ'),
            "stats": activity
        }
        
        channels.append(channel)
    
    # Sort by message count (most active first)
    channels.sort(key=lambda x: x['stats']['messages_24h'], reverse=True)
    
    # Limit to top 12 channels
    channels = channels[:12]
    data = {
        "generated_at": now.strftime('%Y-%m-%dT%H:%M:%SZ'),
        "total_channels": len(channels),
        "channels": channels
    }
    
    return data

def save_channels_data(data, output_path='data/channels.json'):
    """
    Save the channels data to JSON file
    """
    output_file = Path(output_path)
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Saved channels data to {output_file}")
    return output_file

def main():
    """
    Main function
    """
    print("🚀 Generating Wartime Milady CEO channels data...")
    
    try:
        # Generate the data
        data = generate_channels_data()
        
        if not data:
            print("❌ No data generated")
            return False
        
        # Save to file
        output_file = save_channels_data(data)
        
        # Print summary
        print(f"\n✅ Successfully generated data for {data['total_channels']} channels:")
        for channel in data['channels']:
            print(f"  • {channel['name']}: {channel['stats']['messages_24h']} messages, {channel['stats']['participants_24h']} users")
        
        print(f"\n📁 Data saved to: {output_file.absolute()}")
        return True       
    except Exception as e:
        print(f"❌ Error generating channels data: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 