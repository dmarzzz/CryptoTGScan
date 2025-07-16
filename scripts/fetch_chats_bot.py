#!/usr/bin/env python3
"""
Telegram Chat Fetching and Verification Script
Part of Milestone 1 for the Telegram Chat Summarization System.

This script:
- Reads chat IDs from chat_ids.yaml
- Connects to Telegram API using telethon with bot token
- Verifies bot access to configured chats
- Shows sample messages the bot receives
"""

import os
import yaml
import logging
from typing import Dict, List, Tuple
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TelegramChatVerifier:
    """Modular class for Telegram chat verification using bot token."""
    
    def __init__(self):
        self.api_id = os.getenv('TELEGRAM_API_ID')
        self.api_hash = os.getenv('TELEGRAM_API_HASH')
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.verification_results = {}
        
        # Define the output directory for reports
        self.reports_dir = "website"
        Path(self.reports_dir).mkdir(exist_ok=True)
        
    def load_chat_ids(self, config_path: str = "chat_ids.yaml") -> List[int]:
        """Load chat IDs from YAML configuration file."""
        try:
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
                chat_ids = config.get('telegram_chat_ids', [])
                logger.info(f"Loaded {len(chat_ids)} chat IDs from configuration")
                return chat_ids
        except FileNotFoundError:
            logger.error(f"Configuration file {config_path} not found")
            return []
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML configuration: {e}")
            return []
    
    def verify_api_credentials(self) -> bool:
        """Verify that required API credentials are available."""
        if not self.bot_token:
            logger.error("TELEGRAM_BOT_TOKEN is required")
            return False
        
        if not self.api_id or not self.api_hash:
            logger.error("Bot token authentication requires both TELEGRAM_API_ID and TELEGRAM_API_HASH")
            return False
        
        logger.info("Using bot token authentication")
        return True
    
    def create_client(self):
        """Create telethon client with bot token authentication."""
        from telethon.sync import TelegramClient
        return TelegramClient("bot_session", self.api_id, self.api_hash).start(bot_token=self.bot_token)
    
    def list_bot_info(self):
        """List bot information and recent messages."""
        try:
            from telethon.sync import TelegramClient
            
            with self.create_client() as client:
                logger.info("Listing bot information:")
                logger.info("=" * 50)
                
                # Get bot info
                bot_info = client.get_me()
                logger.info(f"Bot: @{bot_info.username} (ID: {bot_info.id})")
                logger.info("Bot is active and ready to verify chat access")
                logger.info("Note: Bots cannot fetch message history due to Telegram API restrictions")
                logger.info("=" * 50)
                
        except Exception as e:
            logger.error(f"Error listing bot info: {e}")
    
    def fetch_chat_messages(self, chat_id: int) -> Tuple[bool, str, str, list]:
        """
        Attempt to fetch latest messages from a specific Telegram chat.
        Returns (is_accessible, error_message, chat_name, recent_messages_list)
        """
        try:
            from telethon.sync import TelegramClient
            from telethon.tl.types import Channel, Chat, User
            
            with self.create_client() as client:
                logger.info(f"Attempting to fetch messages from chat ID: {chat_id}")
                
                # Get chat information first
                try:
                    chat = client.get_entity(chat_id)
                    
                    # Determine chat name and type based on entity type
                    if isinstance(chat, Channel):
                        chat_name = chat.title or f"Channel {chat_id}"
                        entity_type = "Channel/Megagroup"
                    elif isinstance(chat, Chat):
                        chat_name = chat.title or f"Group {chat_id}"
                        entity_type = "Group"
                    elif isinstance(chat, User):
                        chat_name = f"{chat.first_name or ''} {chat.last_name or ''}".strip() or f"User {chat_id}"
                        entity_type = "User"
                    else:
                        chat_name = f"Chat {chat_id}"
                        entity_type = "Unknown"
                    
                    logger.info(f"Found {entity_type}: {chat_name}")
                    
                    # Try to fetch recent messages
                    try:
                        logger.info("Attempting to fetch recent messages...")
                        messages = client.get_messages(chat_id, limit=10)
                        
                        recent_messages = []
                        for msg in messages:
                            if msg and hasattr(msg, 'text') and msg.text:
                                sender = "Unknown"
                                if hasattr(msg, 'sender_id') and msg.sender_id:
                                    try:
                                        sender_entity = client.get_entity(msg.sender_id)
                                        if hasattr(sender_entity, 'first_name'):
                                            sender = sender_entity.first_name
                                        elif hasattr(sender_entity, 'title'):
                                            sender = sender_entity.title
                                        elif hasattr(sender_entity, 'username'):
                                            sender = f"@{sender_entity.username}"
                                    except:
                                        sender = f"User {msg.sender_id}"
                                
                                content = msg.text or msg.message or "[Media message]" if msg.media else "[No text]"
                                recent_messages.append({
                                    'timestamp': msg.date.isoformat() if msg.date else 'N/A',
                                    'sender': sender,
                                    'content': content,
                                    'message_id': msg.id
                                })
                                
                                if len(recent_messages) >= 5:  # Limit to 5 messages
                                    break
                        
                        if recent_messages:
                            logger.info(f"Successfully fetched {len(recent_messages)} messages from {chat_name}")
                            return True, f"Messages fetched successfully", chat_name, recent_messages
                        else:
                            logger.info(f"No text messages found in {chat_name}")
                            return True, f"No text messages available", chat_name, []
                            
                    except Exception as e:
                        error_msg = str(e)
                        if "The API access for bot users is restricted" in error_msg or "GetHistoryRequest" in error_msg:
                            logger.warning(f"Bot cannot fetch message history from {chat_name}: {error_msg}")
                            return True, f"Bot access confirmed (no message history due to API restrictions)", chat_name, [
                                {
                                    'timestamp': 'N/A',
                                    'sender': 'System',
                                    'content': 'Bot access confirmed but cannot fetch message history due to Telegram API restrictions',
                                    'message_id': 0
                                }
                            ]
                        else:
                            logger.error(f"Error fetching messages from {chat_name}: {error_msg}")
                            return False, f"Error fetching messages: {error_msg}", chat_name, []
                    
                except Exception as e:
                    error_msg = str(e)
                    if "Peer id invalid" in error_msg:
                        logger.error(f"Chat ID {chat_id} is invalid or bot doesn't have access")
                        return False, f"Invalid chat ID or no access: {error_msg}", "Unknown", []
                    elif "CHAT_WRITE_FORBIDDEN" in error_msg:
                        logger.error(f"Bot doesn't have permission to access chat {chat_id}")
                        return False, f"Bot lacks permission: {error_msg}", "Unknown", []
                    else:
                        logger.error(f"Could not get chat {chat_id}: {e}")
                        return False, f"Error: {error_msg}", "Unknown", []
                
        except Exception as e:
            logger.error(f"Error processing chat {chat_id}: {e}")
            return False, f"Error: {str(e)}", "Unknown", [{'timestamp': 'N/A', 'sender': 'Error', 'content': f"Error: {str(e)}", 'message_id': 0}]
    
    def verify_all_chats(self) -> Dict[int, Dict[str, any]]:
        """Verify bot access to all configured chat IDs."""
        if not self.verify_api_credentials():
            return {}
        
        # First, list bot info and recent messages
        self.list_bot_info()
        
        chat_ids = self.load_chat_ids()
        results = {}
        
        for chat_id in chat_ids:
            logger.info(f"Fetching messages from chat ID: {chat_id}")
            is_accessible, message, chat_name, recent_messages = self.fetch_chat_messages(chat_id)
            
            results[chat_id] = {
                'accessible': is_accessible,
                'message': message,
                'chat_name': chat_name,
                'recent_messages': recent_messages,
                'verified_at': datetime.now().isoformat()
            }
            
            status = "✅ Yes" if is_accessible else "❌ No"
            logger.info(f"Chat {chat_id} ({chat_name}): {status} - {message}")
        
        self.verification_results = results
        return results


def main():
    """Main function to run the Telegram chat verification process."""
    logger.info("Starting Telegram bot chat verification process")
    
    # Initialize verifier
    verifier = TelegramChatVerifier()
    
    # Verify all chats
    results = verifier.verify_all_chats()
    
    if not results:
        logger.error("No verification results to report")
        return
    
    # Generate and save HTML report
    from report import HTMLReportGenerator
    report_generator = HTMLReportGenerator()
    report_file = report_generator.save_report(results)
    
    logger.info(f"Verification process completed. Report saved to: {report_file}")
    
    # Print summary
    accessible_count = sum(1 for r in results.values() if r['accessible'])
    total_count = len(results)
    logger.info(f"Summary: {accessible_count}/{total_count} chats are accessible")
    
    # Print detailed results
    logger.info("Detailed verification results:")
    for chat_id, result in results.items():
        logger.info(f"  Chat {chat_id} ({result['chat_name']}): {result['message']}")

if __name__ == "__main__":
    main() 