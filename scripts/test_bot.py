#!/usr/bin/env python3
"""
Test Bot Functionality
Script to test if the bot is working correctly.
"""

import os
import sys
import requests
import json
from supabase import create_client, Client

def test_bot():
    """Test bot functionality"""
    print("🤖 Testing Bot Functionality")
    print("=" * 40)
    
    # Get bot token
    bot_token = input("Enter your Telegram bot token: ").strip()
    if not bot_token:
        print("❌ Bot token is required")
        return
    
    # Test 1: Check bot info
    print("\n📋 Test 1: Checking bot info...")
    try:
        response = requests.get(f"https://api.telegram.org/bot{bot_token}/getMe")
        result = response.json()
        
        if result.get("ok"):
            bot_info = result.get("result", {})
            print("✅ Bot info retrieved:")
            print(f"   Name: {bot_info.get('first_name', 'N/A')}")
            print(f"   Username: @{bot_info.get('username', 'N/A')}")
            print(f"   ID: {bot_info.get('id', 'N/A')}")
            print(f"   Can join groups: {bot_info.get('can_join_groups', False)}")
            print(f"   Can read all group messages: {bot_info.get('can_read_all_group_messages', False)}")
        else:
            print(f"❌ Failed to get bot info: {result.get('description', 'Unknown error')}")
            return
    except Exception as e:
        print(f"❌ Error getting bot info: {e}")
        return
    
    # Test 2: Check webhook status
    print("\n🔗 Test 2: Checking webhook status...")
    try:
        response = requests.get(f"https://api.telegram.org/bot{bot_token}/getWebhookInfo")
        result = response.json()
        
        if result.get("ok"):
            webhook_info = result.get("result", {})
            print("✅ Webhook status:")
            print(f"   URL: {webhook_info.get('url', 'Not set')}")
            print(f"   Has custom certificate: {webhook_info.get('has_custom_certificate', False)}")
            print(f"   Pending updates: {webhook_info.get('pending_update_count', 0)}")
            
            if webhook_info.get('last_error_date'):
                print(f"   ⚠️  Last error: {webhook_info.get('last_error_message', 'Unknown error')}")
            elif webhook_info.get('url'):
                print("   ✅ Webhook is set and working")
            else:
                print("   ❌ Webhook is not set")
        else:
            print(f"❌ Failed to get webhook info: {result.get('description', 'Unknown error')}")
    except Exception as e:
        print(f"❌ Error checking webhook: {e}")
    
    # Test 3: Check Supabase connection
    print("\n🗄️ Test 3: Checking Supabase connection...")
    try:
        supabase_url = "https://hrfiaxcjknmswdirgczm.supabase.co"
        supabase_key = input("Enter your Supabase service role key: ").strip()
        
        if not supabase_key:
            print("❌ Supabase key is required")
            return
        
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # Test database connection
        result = supabase.table('chats_v1').select('count', count='exact').execute()
        print("✅ Supabase connection successful")
        print(f"   Total chats in database: {result.count}")
        
    except Exception as e:
        print(f"❌ Error connecting to Supabase: {e}")
    
    # Test 4: Test function endpoint
    print("\n🌐 Test 4: Testing function endpoint...")
    try:
        function_url = "https://hrfiaxcjknmswdirgczm.supabase.co/functions/v1/telegram-bot"
        secret = "03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4"
        
        response = requests.post(
            f"{function_url}?secret={secret}",
            headers={"Content-Type": "application/json"},
            json={"test": "ping"}
        )
        
        print(f"✅ Function endpoint response: {response.status_code}")
        if response.status_code == 401:
            print("   This is expected - the endpoint requires proper Telegram webhook format")
        elif response.status_code == 200:
            print("   Function is responding correctly")
        else:
            print(f"   Unexpected response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing function endpoint: {e}")
    
    print("\n🎉 Testing complete!")
    print("\n📝 Next steps:")
    print("1. Run the webhook setup script: python scripts/setup_webhook.py")
    print("2. Send a message to your bot to test it")
    print("3. Check the Supabase dashboard for logs")

if __name__ == "__main__":
    test_bot() 