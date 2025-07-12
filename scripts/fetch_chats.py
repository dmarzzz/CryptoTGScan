#!/usr/bin/env python3
"""
Telegram Chat Fetching and Verification Script
Part of Milestone 1 for the Telegram Chat Summarization System.

This script:
- Reads chat IDs from chat_ids.yaml
- Connects to Telegram API using API ID and hash (no bot token)
- Verifies access and basic retrieval capability for each listed chat
- Outputs verification results with chat names and recent messages
"""

import os
import yaml
import logging
from typing import Dict, List, Tuple
from datetime import datetime
from report import HTMLReportGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TelegramChatVerifier:
    """Modular class for Telegram chat verification using API ID and hash."""
    
    def __init__(self):
        self.api_id = os.getenv('TELEGRAM_API_ID')
        self.api_hash = os.getenv('TELEGRAM_API_HASH')
        self.verification_results = {}
        
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
        required_vars = ['TELEGRAM_API_ID', 'TELEGRAM_API_HASH']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            logger.error(f"Missing required environment variables: {missing_vars}")
            return False
        
        logger.info("All required API credentials are available")
        return True
    
    def verify_chat_access(self, chat_id: int) -> Tuple[bool, str, str, str]:
        """
        Verify access to a specific Telegram chat using real API calls with telethon.
        Handles both regular chats and channels/megagroups.
        Returns (is_accessible, error_message, chat_name, recent_message)
        """
        try:
            from telethon.sync import TelegramClient
            from telethon.tl.types import Channel, Chat, User
            
            # Create a temporary client for this verification
            with TelegramClient(
                "temp_session",
                self.api_id,
                self.api_hash
            ) as client:
                logger.info(f"Attempting to connect to chat ID: {chat_id}")
                
                # Try to get chat information
                try:
                    chat = client.get_entity(chat_id)
                except Exception as e:
                    logger.error(f"Could not get entity for chat {chat_id}: {e}")
                    return False, f"Error: {str(e)}", "Unknown", "No recent messages"
                
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
                
                # Try to get the most recent message
                recent_message = "No recent messages found"
                try:
                    # Get the most recent message (limit=1)
                    messages = client.get_messages(chat_id, limit=1)
                    if messages:
                        message = messages[0]
                        if message.text:
                            recent_message = message.text
                        elif message.caption:
                            recent_message = message.caption
                        else:
                            recent_message = f"[{message.media.__class__.__name__ if message.media else 'Text'}] Media message"
                except Exception as e:
                    logger.warning(f"Could not fetch recent message for {entity_type} {chat_id}: {e}")
                    recent_message = f"Could not fetch recent message ({entity_type})"
                
                return True, f"Accessible ({entity_type})", chat_name, recent_message
                
        except Exception as e:
            logger.error(f"Error verifying chat {chat_id}: {e}")
            return False, f"Error: {str(e)}", "Unknown", "No recent messages"
    
    def verify_all_chats(self) -> Dict[int, Dict[str, any]]:
        """Verify access to all configured chat IDs."""
        if not self.verify_api_credentials():
            return {}
        
        chat_ids = self.load_chat_ids()
        results = {}
        
        for chat_id in chat_ids:
            logger.info(f"Verifying access to chat ID: {chat_id}")
            is_accessible, message, chat_name, recent_message = self.verify_chat_access(chat_id)
            
            results[chat_id] = {
                'accessible': is_accessible,
                'message': message,
                'chat_name': chat_name,
                'recent_message': recent_message,
                'verified_at': datetime.now().isoformat()
            }
            
            status = "✅ Yes" if is_accessible else "❌ No"
            logger.info(f"Chat {chat_id} ({chat_name}): {status} - {message}")
            if is_accessible and recent_message:
                logger.info(f"Recent message: {recent_message[:100]}...")
        
        self.verification_results = results
        return results


def main():
    """Main function to run the Telegram chat verification process."""
    logger.info("Starting Telegram chat verification process")
    
    # Initialize verifier
    verifier = TelegramChatVerifier()
    
    # Verify all chats
    results = verifier.verify_all_chats()
    
    if not results:
        logger.error("No verification results to report")
        return
    
    # Generate and save HTML report
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