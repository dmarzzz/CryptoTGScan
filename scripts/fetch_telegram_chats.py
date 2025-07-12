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
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

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
        Returns (is_accessible, error_message, chat_name, recent_message)
        """
        try:
            from telethon.sync import TelegramClient
            
            # Create a temporary client for this verification
            with TelegramClient(
                "temp_session",
                self.api_id,
                self.api_hash
            ) as client:
                logger.info(f"Attempting to connect to chat ID: {chat_id}")
                
                # Try to get chat information
                chat = client.get_entity(chat_id)
                chat_name = getattr(chat, 'title', None) or getattr(chat, 'first_name', None) or f"Chat {chat_id}"
                
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
                    logger.warning(f"Could not fetch recent message for chat {chat_id}: {e}")
                    recent_message = "Could not fetch recent message"
                
                return True, "Accessible", chat_name, recent_message
                
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

class HTMLReportGenerator:
    """Modular class for generating HTML verification reports."""
    
    def __init__(self, output_dir: str = "website"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def generate_verification_report(self, verification_results: Dict[int, Dict[str, any]]) -> str:
        """Generate HTML report for chat verification results."""
        
        # Generate table rows
        table_rows = ""
        for chat_id, result in verification_results.items():
            status = "Yes" if result['accessible'] else "No"
            status_class = "success" if result['accessible'] else "error"
            chat_name = result.get('chat_name', 'Unknown')
            recent_message = result.get('recent_message', 'No recent messages')
            
            # Truncate recent message for display
            display_message = recent_message[:100] + "..." if len(recent_message) > 100 else recent_message
            
            table_rows += f"""
                <tr>
                    <td>{chat_id}</td>
                    <td>{chat_name}</td>
                    <td class="{status_class}">{status}</td>
                    <td>{result['message']}</td>
                    <td class="recent-message" title="{recent_message}">{display_message}</td>
                    <td>{result['verified_at']}</td>
                </tr>"""
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Telegram Chat Verification Results</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            font-size: 14px;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
            vertical-align: top;
        }}
        th {{
            background-color: #f8f9fa;
            font-weight: bold;
        }}
        .success {{
            color: #28a745;
            font-weight: bold;
        }}
        .error {{
            color: #dc3545;
            font-weight: bold;
        }}
        .summary {{
            margin-top: 30px;
            padding: 20px;
            background-color: #e9ecef;
            border-radius: 5px;
        }}
        .timestamp {{
            text-align: center;
            color: #666;
            margin-top: 20px;
            font-size: 14px;
        }}
        .api-info {{
            background-color: #d1ecf1;
            border: 1px solid #bee5eb;
            border-radius: 5px;
            padding: 15px;
            margin-bottom: 20px;
        }}
        .recent-message {{
            max-width: 200px;
            word-wrap: break-word;
            font-style: italic;
            color: #666;
        }}
        .chat-name {{
            font-weight: bold;
            color: #333;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Telegram Chat Verification Results</h1>
        
        <div class="api-info">
            <h3>API Configuration</h3>
            <p><strong>Method:</strong> API ID and Hash (No Bot Token Required)</p>
            <p><strong>Environment Variables:</strong> TELEGRAM_API_ID, TELEGRAM_API_HASH</p>
            <p><strong>Status:</strong> Real API calls using telethon (Official Telegram Client)</p>
        </div>
        
        <div class="summary">
            <h3>Summary</h3>
            <p>Total chats verified: {len(verification_results)}</p>
            <p>Accessible: {sum(1 for r in verification_results.values() if r['accessible'])}</p>
            <p>Not accessible: {sum(1 for r in verification_results.values() if not r['accessible'])}</p>
        </div>
        
        <table>
            <thead>
                <tr>
                    <th>Chat ID</th>
                    <th>Chat Name</th>
                    <th>Accessible</th>
                    <th>Message</th>
                    <th>Recent Message</th>
                    <th>Verified At</th>
                </tr>
            </thead>
            <tbody>
                {table_rows}
            </tbody>
        </table>
        
        <div class="timestamp">
            Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
        </div>
    </div>
</body>
</html>"""
        
        return html_content
    
    def save_report(self, verification_results: Dict[int, Dict[str, any]], filename: str = None) -> str:
        """Save the verification report to a file."""
        html_content = self.generate_verification_report(verification_results)
        
        # Generate filename with date if not provided
        if filename is None:
            current_date = datetime.now().strftime('%Y-%m-%d')
            filename = f"output_{current_date}.html"
        
        output_file = self.output_dir / filename
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"Verification report saved to: {output_file}")
        return str(output_file)

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