#!/usr/bin/env python3
"""
Setup Telegram Webhook
Script to configure the Telegram webhook for the bot.
"""

import os
import sys
import requests
import json

def setup_webhook():
    """Set up the Telegram webhook"""
    print("🔧 Setting up Telegram Webhook")
    print("=" * 40)
    
    # Get bot token from user
    bot_token = input("Enter your Telegram bot token: ").strip()
    if not bot_token:
        print("❌ Bot token is required")
        return
    
    # Webhook URL components
    project_ref = "hrfiaxcjknmswdirgczm"  # From your Supabase project
    function_secret = "03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4"
    
    webhook_url = f"https://{project_ref}.supabase.co/functions/v1/telegram-bot?secret={function_secret}"
    
    print(f"\n📡 Webhook URL: {webhook_url}")
    
    # Set webhook
    set_webhook_url = f"https://api.telegram.org/bot{bot_token}/setWebhook"
    payload = {
        "url": webhook_url,
        "allowed_updates": ["message", "channel_post", "edited_message", "edited_channel_post"]
    }
    
    print("\n🚀 Setting webhook...")
    try:
        response = requests.post(set_webhook_url, json=payload)
        result = response.json()
        
        if result.get("ok"):
            print("✅ Webhook set successfully!")
            print(f"   URL: {result.get('result', {}).get('url', 'N/A')}")
            print(f"   Pending updates: {result.get('result', {}).get('pending_update_count', 0)}")
        else:
            print(f"❌ Failed to set webhook: {result.get('description', 'Unknown error')}")
            return
            
    except Exception as e:
        print(f"❌ Error setting webhook: {e}")
        return
    
    # Verify webhook
    print("\n🔍 Verifying webhook...")
    try:
        get_webhook_url = f"https://api.telegram.org/bot{bot_token}/getWebhookInfo"
        response = requests.get(get_webhook_url)
        result = response.json()
        
        if result.get("ok"):
            webhook_info = result.get("result", {})
            print("✅ Webhook verification:")
            print(f"   URL: {webhook_info.get('url', 'N/A')}")
            print(f"   Has custom certificate: {webhook_info.get('has_custom_certificate', False)}")
            print(f"   Pending updates: {webhook_info.get('pending_update_count', 0)}")
            print(f"   Last error date: {webhook_info.get('last_error_date', 'N/A')}")
            print(f"   Last error message: {webhook_info.get('last_error_message', 'N/A')}")
            
            if webhook_info.get('last_error_message'):
                print(f"⚠️  Warning: There was an error: {webhook_info.get('last_error_message')}")
        else:
            print(f"❌ Failed to get webhook info: {result.get('description', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Error verifying webhook: {e}")
    
    print("\n🎉 Setup complete!")
    print("Try sending a message to your bot to test it.")

if __name__ == "__main__":
    setup_webhook() 