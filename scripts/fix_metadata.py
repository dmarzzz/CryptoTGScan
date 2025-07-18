#!/usr/bin/env python3
"""
Fix metadata.json by extracting real data from existing report files
"""

import json
import re
from pathlib import Path
from datetime import datetime

def extract_stats_from_report(report_file):
    """Extract total_messages and unique_participants from a report HTML file"""
    try:
        with open(report_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract total messages from the section note
        total_messages_match = re.search(r'Total messages: (\d+)', content)
        total_messages = int(total_messages_match.group(1)) if total_messages_match else 0
        
        # Extract unique participants from the stat card
        participants_match = re.search(r'<div class="stat-value">(\d+)</div>\s*<div class="stat-label">Active Participants</div>', content)
        unique_participants = int(participants_match.group(1)) if participants_match else 0
        
        return total_messages, unique_participants
    except Exception as e:
        print(f"Error reading {report_file}: {e}")
        return 0, 0

def regenerate_metadata():
    """Regenerate metadata.json from existing report files"""
    reports_dir = Path('website/reports')
    metadata = {}
    
    # Find all report files
    report_files = list(reports_dir.glob('report_*.html'))
    
    for report_file in report_files:
        # Parse filename to get chat_id and date
        # Format: report_1002009589709_20250717.html
        filename = report_file.name
        match = re.match(r'report_(\d+)_(\d{8})\.html', filename)
        
        if match:
            chat_id = match.group(1)
            date_str = match.group(2)
            
            # Convert date format from YYYYMMDD to YYYY-MM-DD
            date_formatted = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
            
            # Extract stats from the report file
            total_messages, unique_participants = extract_stats_from_report(report_file)
            
            # Initialize chat entry if not exists
            if chat_id not in metadata:
                metadata[chat_id] = {
                    'name': '',  # We'll get this from the first report
                    'reports': []
                }
            
            # Add report entry
            report_entry = {
                'date': date_formatted,
                'filename': filename,
                'start_date': f"{date_formatted} 00:00:00",
                'end_date': f"{date_formatted} 23:59:59",
                'total_messages': total_messages,
                'unique_participants': unique_participants
            }
            
            metadata[chat_id]['reports'].append(report_entry)
    
    # Sort reports by date for each chat
    for chat_id in metadata:
        metadata[chat_id]['reports'].sort(key=lambda x: x['date'], reverse=True)
        
        # Get chat name from the first report if available
        if metadata[chat_id]['reports']:
            first_report = metadata[chat_id]['reports'][0]
            try:
                with open(reports_dir / first_report['filename'], 'r', encoding='utf-8') as f:
                    content = f.read()
                    title_match = re.search(r'<title>.*? - (.*?) Report', content)
                    if title_match:
                        metadata[chat_id]['name'] = title_match.group(1)
            except:
                pass
    
    # Write the regenerated metadata
    metadata_file = reports_dir / 'metadata.json'
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"✅ Regenerated metadata.json with real data from {len(report_files)} report files")
    print(f"📁 Metadata saved to: {metadata_file}")
    
    # Print summary
    for chat_id, chat_data in metadata.items():
        print(f"\n📊 {chat_data['name']} (ID: {chat_id}):")
        for report in chat_data['reports']:
            print(f"  {report['date']}: {report['total_messages']} messages, {report['unique_participants']} participants")

if __name__ == "__main__":
    regenerate_metadata() 