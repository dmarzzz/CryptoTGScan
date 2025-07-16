#!/usr/bin/env python3
"""
Check Webhook Status
Simple script to check if the webhook is set up correctly.
"""

import requests
import json

def check_webhook():
    """Check webhook status"""
    print("🔍 Checking Webhook Status")
    print("=" * 40)
    
    # Get bot token from user
    bot_token = input("Enter your Telegram bot token: ").strip()
    if not bot_token:
        print("❌ Bot token is required")
        return
    
    # Check webhook info
    print("\n📡 Checking webhook info...")
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
                print("\n🔧 To fix this, run: python scripts/setup_webhook.py")
        else:
            print(f"❌ Failed to get webhook info: {result.get('description', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Error checking webhook: {e}")

if __name__ == "__main__":
    check_webhook() 