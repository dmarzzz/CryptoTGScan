#!/usr/bin/env python3
"""
HTML Report Generation Module
Part of the Telegram Chat Summarization System.

This module provides functionality for generating HTML reports
from chat verification results and other data.
"""

from pathlib import Path
from typing import Dict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

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