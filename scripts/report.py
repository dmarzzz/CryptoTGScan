#!/usr/bin/env python3
"""
HTML Report Generation Module
Part of the Telegram Chat Summarization System.

This module provides functionality for generating HTML reports
from chat verification results and other data.
"""

from pathlib import Path
from typing import Dict, List
from datetime import datetime
import logging
import html

logger = logging.getLogger(__name__)

class HTMLReportGenerator:
    """Modular class for generating HTML verification reports."""
    
    def __init__(self, output_dir: str = "website", template_path: str = "assets/template.html"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.template_path = Path(template_path)
    
    def load_template(self) -> str:
        """Load HTML template from file."""
        try:
            with open(self.template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            logger.warning(f"Template file {self.template_path} not found. Using fallback template.")
            return self._get_fallback_template()
    
    def _get_fallback_template(self) -> str:
        """Fallback template if template.html is not found."""
        return """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>{{TITLE}}</title></head>
<body>{{CONTENT}}</body></html>"""
    
    def _generate_messages_dropdown(self, chat_id: int, messages: List[Dict]) -> str:
        """Generate HTML for messages dropdown."""
        if not messages or not isinstance(messages, list):
            return "No messages available"
        
        dropdown_html = f"""
        <div class="messages-dropdown">
            <button class="dropdown-btn" onclick="toggleDropdown({chat_id})">
                View Messages <span class="messages-count">({len(messages)} messages)</span>
            </button>
            <div id="dropdown-{chat_id}" class="dropdown-content">"""
        
        for msg in messages:
            if isinstance(msg, dict):
                sender = html.escape(str(msg.get('sender', 'Unknown')))
                timestamp = msg.get('timestamp', 'Unknown')
                content = html.escape(str(msg.get('content', 'No content')))
                
                # Format timestamp
                try:
                    if timestamp != 'Unknown' and timestamp != 'N/A':
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        formatted_time = timestamp
                except:
                    formatted_time = timestamp
                
                dropdown_html += f"""
                <div class="message-item">
                    <div class="message-header">
                        <span class="message-sender">{sender}</span>
                        <span class="message-timestamp">{formatted_time}</span>
                    </div>
                    <div class="message-content">{content}</div>
                </div>"""
        
        dropdown_html += """
            </div>
        </div>"""
        
        return dropdown_html
    
    def generate_verification_report(self, verification_results: Dict[int, Dict[str, any]]) -> str:
        """Generate HTML report for chat verification results."""
        
        # Generate table rows
        table_rows = ""
        for chat_id, result in verification_results.items():
            status = "Yes" if result['accessible'] else "No"
            status_class = "success" if result['accessible'] else "error"
            chat_name = html.escape(result.get('chat_name', 'Unknown'))
            recent_messages = result.get('recent_messages', [])
            
            # Generate messages dropdown
            messages_dropdown = self._generate_messages_dropdown(chat_id, recent_messages)
            
            table_rows += f"""
                <tr>
                    <td>{chat_id}</td>
                    <td class="chat-name">{chat_name}</td>
                    <td class="{status_class}">{status}</td>
                    <td>{html.escape(result['message'])}</td>
                    <td>{messages_dropdown}</td>
                    <td>{result['verified_at']}</td>
                </tr>"""
        
        # Generate content for template
        content = f"""
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
                    <th>Messages</th>
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
        """
        
        # Load template and replace placeholders
        template = self.load_template()
        html_content = template.replace('{{TITLE}}', 'Telegram Chat Verification Results')
        html_content = html_content.replace('{{CONTENT}}', content)
        
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