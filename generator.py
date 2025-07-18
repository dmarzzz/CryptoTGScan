#!/usr/bin/env python3
"""
Wartime Milady CEO Intelligence Platform - Static Site Generator
Milestone 1: Foundation & Homepage Structure
"""
import json
import shutil
from datetime import datetime
from pathlib import Path

class MiladySiteGenerator:
    def __init__(self, data_dir='data', output_dir='website'):
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.static_dir = Path('static')
        self.data_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)

    def load_channel_data(self):
        data_file = self.data_dir / 'channels.json'
        if not data_file.exists():
            sample = self._create_sample_data()
            with open(data_file, 'w') as f:
                json.dump(sample, f, indent=2)
            return sample
        with open(data_file, 'r') as f:
            return json.load(f)

    def _create_sample_data(self):
        now = datetime.utcnow()
        return {
            "generated_at": now.strftime('%Y-%m-%dT%H:%M:%SZ'),
            "total_channels": 8,
            "channels": [
                {
                    "id": "ethereum-core-devs",
                    "name": "Ethereum Core Devs",
                    "icon": "⚡",
                    "last_update": now.strftime('%Y-%m-%dT%H:%M:%SZ'),
                    "stats": {
                        "messages_24h": 156,
                        "participants_24h": 23,
                        "change_percent": 15.5,
                        "trend": "up"
                    }
                },
                {
                    "id": "ethresearch",
                    "name": "Ethereum Research",
                    "icon": "🔬",
                    "last_update": now.strftime('%Y-%m-%dT%H:%M:%SZ'),
                    "stats": {
                        "messages_24h": 89,
                        "participants_24h": 17,
                        "change_percent": -5.2,
                        "trend": "down"
                    }
                },
                {
                    "id": "defi-protocols",
                    "name": "DeFi Protocols",
                    "icon": "💸",
                    "last_update": now.strftime('%Y-%m-%dT%H:%M:%SZ'),
                    "stats": {
                        "messages_24h": 234,
                        "participants_24h": 45,
                        "change_percent": 28.7,
                        "trend": "up"
                    }
                },
                {
                    "id": "layer2-scaling",
                    "name": "Layer 2 Scaling",
                    "icon": "🛣️",
                    "last_update": now.strftime('%Y-%m-%dT%H:%M:%SZ'),
                    "stats": {
                        "messages_24h": 67,
                        "participants_24h": 12,
                        "change_percent": -2.1,
                        "trend": "down"
                    }
                },
                {
                    "id": "nft-ecosystem",
                    "name": "NFT Ecosystem",
                    "icon": "🖼️",
                    "last_update": now.strftime('%Y-%m-%dT%H:%M:%SZ'),
                    "stats": {
                        "messages_24h": 189,
                        "participants_24h": 34,
                        "change_percent": 42.3,
                        "trend": "up"
                    }
                },
                {
                    "id": "governance",
                    "name": "DAO Governance",
                    "icon": "🏛️",
                    "last_update": now.strftime('%Y-%m-%dT%H:%M:%SZ'),
                    "stats": {
                        "messages_24h": 45,
                        "participants_24h": 8,
                        "change_percent": 12.8,
                        "trend": "up"
                    }
                },
                {
                    "id": "security-audits",
                    "name": "Security Audits",
                    "icon": "🛡️",
                    "last_update": now.strftime('%Y-%m-%dT%H:%M:%SZ'),
                    "stats": {
                        "messages_24h": 78,
                        "participants_24h": 15,
                        "change_percent": -8.9,
                        "trend": "down"
                    }
                },
                {
                    "id": "developer-tools",
                    "name": "Developer Tools",
                    "icon": "🛠️",
                    "last_update": now.strftime('%Y-%m-%dT%H:%M:%SZ'),
                    "stats": {
                        "messages_24h": 123,
                        "participants_24h": 28,
                        "change_percent": 19.4,
                        "trend": "up"
                    }
                }
            ]
        }

    def format_military_time(self, timestamp):
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return dt.strftime('%Y-%m-%d %H%MZ')
        except Exception:
            return timestamp

    def generate_homepage(self, data):
        current_time = datetime.utcnow().strftime('%Y-%m-%d %H%MZ')
        channel_cards = []
        for channel in data['channels']:
            # Create safe filename for the report link - handle negative Telegram chat IDs
            channel_id = str(channel['id'])
            safe_filename = channel_id.replace('-', '')  # Remove minus sign for filename
            card_html = f'''
            <a href="reports/report_{safe_filename}.html" class="channel-card" tabindex="0" aria-label="{channel['name']} channel card">
                <div class="channel-header">
                    <div class="channel-icon">{channel['icon']}</div>
                    <div class="channel-info">
                        <h3 class="channel-name">{channel['name']}</h3>
                        <div class="channel-meta">
                            <span class="last-update">Last: {self.format_military_time(channel['last_update'])}</span>
                        </div>
                    </div>
                </div>
                <div class="channel-stats">
                    <div class="stat-row">
                        <div class="stat-item">
                            <span class="stat-label">Messages</span>
                            <span class="stat-value">{channel['stats']['messages_24h']}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Participants</span>
                            <span class="stat-value">{channel['stats']['participants_24h']}</span>
                        </div>
                    </div>
                </div>
            </a>
            '''
            channel_cards.append(card_html)
        # Use the static wartimemiladyceo.jpg for the avatar
        avatar_html = '''
            <img src="assets/wartimemiladyceo.jpg" alt="Wartime Milady CEO avatar" class="avatar-img" width="120" height="120" loading="lazy" style="display:block; border-radius:50%; object-fit:cover; background:#222;" onerror="this.style.display='none';this.parentNode.querySelector('.avatar-fallback').style.display='flex';">
            <div class="avatar-fallback" style="display:none; width:120px; height:120px; align-items:center; justify-content:center; border-radius:50%; background:linear-gradient(45deg,#FF006E,#00F5FF); font-size:3rem; border:3px solid #00FF00; box-shadow:0 0 20px #FF006E,0 0 20px #00FF00;">👾</div>
        '''
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Wartime Milady CEO - Ethereum Intelligence Command</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Inter:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
{self._get_css()}
    </style>
</head>
<body>
    <div class="scan-lines"></div>
    <header class="site-header">
        <div class="header-content">
            <div class="milady-avatar">
                {avatar_html}
            </div>
            <div class="header-text">
                <h1 class="site-title">Wartime Milady CEO</h1>
                <p class="site-subtitle">Monitoring {data['total_channels']} channels across the frontlines</p>
                <div class="status-bar">
                    <span class="timestamp">{current_time}</span>
                    <span class="status-indicator" aria-live="polite">SYSTEMS ONLINE</span>
                </div>
            </div>
        </div>
    </header>
    <main class="main-content">
        <div class="channel-grid">
            {''.join(channel_cards)}
        </div>
    </main>
    <footer class="site-footer">
        <p>Generated by Wartime Milady CEO Intelligence Platform</p>
        <p>Data updated: {self.format_military_time(data['generated_at'])}</p>
    </footer>
</body>
</html>'''
        return html

    def _get_css(self):
        return '''
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Inter:wght@400;500;700&display=swap');
:root {
  --color-primary: #FF006E;
  --color-secondary: #00F5FF;
  --color-accent: #00FF00;
  --color-bg: #0A0A0A;
  --color-surface: #1A1A1A;
  --color-text: #F0F0F0;
  --font-mono: 'Space Mono', monospace;
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}
body {
  font-family: var(--font-sans);
  color: var(--color-text);
  background:
    radial-gradient(ellipse at top left, rgba(255,0,110,0.1) 0%, transparent 50%),
    radial-gradient(ellipse at bottom right, rgba(0,245,255,0.1) 0%, transparent 50%),
    #0A0A0A;
  min-height: 100vh;
  margin: 0;
  animation: flicker 10s infinite;
}
body::after {
  content: '';
  position: fixed;
  top: 0; left: 0;
  width: 100vw; height: 100vh;
  background-image:
    linear-gradient(rgba(255,0,110,0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,0,110,0.03) 1px, transparent 1px);
  background-size: 50px 50px;
  pointer-events: none;
  z-index: 1;
}
body::before {
  content: '';
  position: fixed;
  top: -5%; left: -5%;
  width: 110%; height: 110%;
  border-radius: 10%;
  box-shadow: inset 0 0 100px rgba(0,0,0,0.5);
  pointer-events: none;
  z-index: 999;
}
@keyframes flicker {
  0%, 100% { opacity: 1; }
  95% { opacity: 0.98; }
}
h1.site-title {
  font-family: 'Space Mono', monospace;
  font-size: clamp(2rem, 5vw, 3.5rem);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  background: linear-gradient(45deg, #FF006E, #00F5FF, #00FF00);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-shadow: 0 0 30px rgba(255,0,110,0.5);
  margin: 0;
}
.site-subtitle {
  font-family: 'Space Mono', monospace;
  opacity: 0.8;
  letter-spacing: 0.1em;
}
.avatar-img {
  width: 200px !important;
  height: 200px !important;
  border-radius: 50% !important;
  border: 3px solid #FF006E !important;
  box-shadow:
    0 0 30px rgba(255,0,110,0.8),
    0 0 60px rgba(255,0,110,0.4),
    inset 0 0 30px rgba(255,0,110,0.2) !important;
  animation: float 3s ease-in-out infinite !important;
  object-fit: cover !important;
}
.avatar-fallback {
  width: 200px !important;
  height: 200px !important;
  border-radius: 50% !important;
  border: 3px solid #FF006E !important;
  box-shadow:
    0 0 30px rgba(255,0,110,0.8),
    0 0 60px rgba(255,0,110,0.4),
    inset 0 0 30px rgba(255,0,110,0.2) !important;
  animation: float 3s ease-in-out infinite !important;
  font-size: 4em !important;
  display: flex;
  align-items: center;
  justify-content: center;
}
@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}
.status-indicator {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1.5rem;
  background: rgba(0,255,0,0.1);
  border: 2px solid #00FF00;
  border-radius: 20px;
  font-family: 'Space Mono', monospace;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  font-weight: 700;
  box-shadow:
    inset 0 0 20px rgba(0,255,0,0.3),
    0 0 20px rgba(0,255,0,0.5);
  position: relative;
}
.status-indicator::before {
  content: '';
  display: inline-block;
  width: 10px; height: 10px;
  background: #00FF00;
  border-radius: 50%;
  margin-right: 0.5em;
  animation: blink 1s infinite;
  box-shadow: 0 0 10px #00FF00;
}
@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}
.site-header {
  position: relative;
  padding: 2rem;
  margin-bottom: 3rem;
  background: linear-gradient(180deg, rgba(26,26,26,0.8) 0%, transparent 100%);
  border: 2px solid #FF006E;
  border-radius: 12px;
  overflow: hidden;
}
.site-header::before {
  content: 'WARTIME MILADY CEO v1.337';
  position: absolute;
  top: 0.5rem;
  left: 0.5rem;
  font-family: 'Space Mono', monospace;
  font-size: 0.75rem;
  color: #FF006E;
  opacity: 0.5;
  letter-spacing: 0.1em;
}
.site-header::after {
  content: '';
  position: absolute;
  top: 0; right: 0;
  width: 50px; height: 50px;
  background: linear-gradient(45deg, transparent 50%, #FF006E 50%);
  opacity: 0.3;
}

/* Add terminal-style decoration to header */
.header-container::before {
  content: ' * ]';
  position: absolute;
  top: 1rem;
  right: 1rem;
  font-family: 'Space Mono', monospace;
  color: #00FF00;
  opacity: 0.6;
  animation: blink 2s infinite;
}

/* Add matrix-rain effect with pseudo elements (very lightweight) */
.header-container::after {
  content: ' 10111 11101 11110 11011110011001';
  position: absolute;
  bottom: 0.5em;
  left: 1rem;
  font-size: 0.7rem;
  font-family: monospace;
  color: #00F5FF;
  opacity: 0.2;
  letter-spacing: 0.2em;
}

.scan-lines::before {
  content: '';
  position: fixed;
  top: -100vh;
  left: 0;
  width: 100vw;
  height: 200vh;
  background: repeating-linear-gradient(
    0deg,
    transparent,
    transparent 2px,
    rgba(255,0,110,0.06) 2px,
    rgba(255,0,110,0.06) 4px
  );
  animation: scan-lines 8s linear infinite;
  pointer-events: none;
  z-index: 1000;
}
.scan-lines::after {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, #FF006E, transparent);
  animation: scan-horizontal 4s linear infinite;
  z-index: 1001;
}
@keyframes scan-horizontal {
  0% { transform: translateY(-100vh); }
  100% { transform: translateY(100vh); }
}
@keyframes scan-lines {
  0% { transform: translateY(0); }
  100% { transform: translateY(100vh); }
}
.channel-card {
  background: linear-gradient(135deg, #1A1A1A 0%, #0F0F0F 100%);
  border: 2px solid #FF006E;
  border-radius: 12px;
  padding: 1.5rem;
  position: relative;
  overflow: hidden;
  transition: box-shadow 0.2s, border-color 0.2s, transform 0.2s;
  cursor: pointer;
  text-decoration: none;
  color: inherit;
  display: block;
}
.channel-card:hover {
  transform: translateY(-2px);
  border-color: #00F5FF;
  box-shadow: 0 4px 24px rgba(0,245,255,0.15);
}
.stat-value {
  font-family: 'Space Mono', monospace;
  font-weight: 700;
  font-size: 2rem;
  color: #00F5FF;
  text-shadow:
    0 0 10px #00F5FF,
    0 0 20px #00F5FF,
    0 0 30px #00F5FF;
  letter-spacing: 0.1em;
  background: rgba(0,245,255,0.1);
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  display: inline-block;
}
.stat-label {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  opacity: 0.7;
  margin-top: 0.25rem;
  font-family: 'Space Mono', monospace;
}
.timestamp {
  font-family: 'Space Mono', monospace;
  background: rgba(0,245,255,0.1);
  border: 1px solid #00F5FF;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  letter-spacing: 0.1em;
  display: inline-block;
  position: relative;
  overflow: hidden;
}
.timestamp::before {
  content: '';
  position: absolute;
  top: 0; left: -100%;
  width: 100%; height: 100%;
  background: linear-gradient(90deg, transparent, rgba(0,245,255,0.3), transparent);
  animation: sweep 3s infinite;
}
@keyframes sweep {
  0% { left: -100%; }
  100% { left: 100%; }
}
::selection {
  background: #FF006E;
  color: #0A0A0A;
}
.site-footer {
  margin-top: 4rem;
  padding: 2rem;
  text-align: center;
  font-family: 'Space Mono', monospace;
  font-size: 0.875rem;
  opacity: 0.6;
  letter-spacing: 0.1em;
  border-top: 1px solid rgba(255,0,110,0.3);
}
.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
  display: flex;
  align-items: center;
  gap: 2rem;
  position: relative;
  z-index: 1;
}
.milady-avatar {
  flex-shrink: 0;
}
.header-text {
  flex: 1;
}
.status-bar {
  display: flex;
  align-items: center;
  gap: 2rem;
  margin-top: 1rem;
}
.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 3rem 2rem;
  position: relative;
  z-index: 2;
}
.channel-grid {
  display: grid;
  gap: 1.5rem;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
}
.channel-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}
.channel-icon {
  font-size: 2em;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255,0,110,0.1);
  border: 1px solid var(--color-primary);
  border-radius: 8px;
}
.channel-name {
  font-size: 1.3rem;
  color: var(--color-text);
  margin-bottom: 0.25rem;
  font-family: 'Space Mono', monospace;
}
.channel-meta {
  font-size: 0.85em;
  color: #888;
}
.channel-stats {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
}
.stat-row {
  display: flex;
  gap: 1.5em;
}
.stat-item {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}
@media (max-width: 1024px) {
  .site-title { font-size: 2rem; }
  .header-content { flex-direction: column; text-align: center; gap: 1.5rem; }
  .avatar-img, .avatar-fallback { width: 150px !important; height: 150px !important; }
  .channel-grid { grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); }
}
@media (max-width: 768px) {
  .site-title { font-size: 1.5rem; }
  .header-content { padding: 0 1em; }
  .main-content { padding: 2rem 1rem; }
  .channel-grid { grid-template-columns: 1fr; gap: 1.5rem; }
  .channel-card { padding: 1rem; }
  .stat-row { gap: 1rem; }
  .status-bar { flex-direction: column; gap: 1rem; align-items: flex-start; }
}
@media (max-width: 480px) {
  .site-title { font-size: 1.25rem; }
  .avatar-img, .avatar-fallback { width: 120px !important; height: 120px !important; }
  .channel-header { flex-direction: column; text-align: center; gap: 0.75rem; }
  .channel-stats { flex-direction: column; gap: 1rem; align-items: center; }
  .stat-row { justify-content: center; }
}
@media (prefers-reduced-motion: reduce) {
  * { animation-duration: 0.01ms !important; animation-iteration-count: 1 !important; transition-duration: 0.1s !important; }
}
.channel-card:focus {
  outline: 2px solid var(--color-secondary);
  outline-offset: 2px;
}
@media (prefers-contrast: high) {
  :root { --color-bg: #000; --color-surface: #111111; --color-text: #ffffff; }
}
'''

    def copy_static_assets(self):
        static_output = self.output_dir / 'static'
        if self.static_dir.exists():
            static_output.mkdir(exist_ok=True)
            for item in self.static_dir.iterdir():
                if item.is_file():
                    shutil.copy2(item, static_output)
                elif item.is_dir():
                    shutil.copytree(item, static_output / item.name, dirs_exist_ok=True)
        
        # Also copy assets folder for the avatar image
        assets_dir = Path('assets')
        if assets_dir.exists():
            assets_output = self.output_dir / 'assets'
            assets_output.mkdir(exist_ok=True)
            for item in assets_dir.iterdir():
                if item.is_file():
                    shutil.copy2(item, assets_output)
                elif item.is_dir():
                    shutil.copytree(item, assets_output / item.name, dirs_exist_ok=True)

    def generate_report_pages(self, data):
        """Generate individual report pages for each channel"""
        print("📊 Generating individual report pages...")
        
        # Create reports directory
        reports_dir = self.output_dir / 'reports'
        reports_dir.mkdir(exist_ok=True)
        
        for channel in data['channels']:
            try:
                self._generate_single_report(channel, reports_dir)
            except Exception as e:
                print(f"⚠️  Error generating report for {channel['name']}: {e}")
        
        print(f"✅ Generated {len(data['channels'])} report pages")

    def _generate_single_report(self, channel, reports_dir):
        """Generate a single report page for a channel"""
        # This is a simplified version - in production, this would fetch real data
        current_time = datetime.utcnow().strftime('%Y-%m-%d %H%MZ')
        
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Wartime Milady CEO - {channel['name']} Report</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Inter:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
{self._get_report_css()}
    </style>
</head>
<body>
    <div class="scan-lines"></div>
    <header class="site-header">
        <div class="header-content">
            <div class="chat-icon">
                {channel['icon']}
            </div>
            <div class="header-text">
                <h1 class="site-title">{channel['name']}</h1>
                <p class="site-subtitle">Detailed Intelligence Report - Last 24 Hours</p>
                <div class="status-bar">
                    <span class="timestamp">{current_time}</span>
                    <span class="status-indicator" aria-live="polite">SYSTEMS ONLINE</span>
                </div>
            </div>
        </div>
    </header>
    
    <main class="main-content">
        <a href="../index.html" class="back-link">← BACK TO COMMAND CENTER</a>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{channel['stats']['messages_24h']}</div>
                <div class="stat-label">Total Messages</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{channel['stats']['participants_24h']}</div>
                <div class="stat-label">Active Participants</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">3</div>
                <div class="stat-label">Message Types</div>
            </div>
        </div>
        
        <div class="messages-section">
            <h2 class="section-title">Recent Messages</h2>
            <div class="message-list">
                <div class="message-item">
                    <div class="message-header">
                        <span class="message-author">Sample User</span>
                        <span class="message-time">{current_time}</span>
                    </div>
                    <div class="message-text">This is a sample message from the {channel['name']} channel. In production, this would show real messages from the database.</div>
                    <span class="message-type-badge">text</span>
                </div>
                <div class="message-item">
                    <div class="message-header">
                        <span class="message-author">Another User</span>
                        <span class="message-time">{current_time}</span>
                    </div>
                    <div class="message-text">Another sample message showing the report page functionality.</div>
                    <span class="message-type-badge">text</span>
                </div>
            </div>
        </div>
    </main>
    
    <footer class="site-footer">
        <p>Generated by Wartime Milady CEO Intelligence Platform</p>
        <p>Report generated: {current_time}</p>
    </footer>
</body>
</html>'''
        
        # Write to file
        safe_filename = channel['id'].replace('-', '')  # Remove minus sign for filename
        output_file = reports_dir / f"report_{safe_filename}.html"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"📄 Generated report: {output_file}")

    def _get_report_css(self):
        """Get CSS for report pages"""
        return '''
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Inter:wght@400;500;700&display=swap');
:root {
  --color-primary: #FF006E;
  --color-secondary: #00F5FF;
  --color-accent: #00FF00;
  --color-bg: #0A0A0A;
  --color-surface: #1A1A1A;
  --color-text: #F0F0F0;
  --font-mono: 'Space Mono', monospace;
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

body {
  font-family: var(--font-sans);
  color: var(--color-text);
  background:
    radial-gradient(ellipse at top left, rgba(255,0,110,0.1) 0%, transparent 50%),
    radial-gradient(ellipse at bottom right, rgba(0,245,255,0.1) 0%, transparent 50%),
    #0A0A0A;
  min-height: 100vh;
  margin: 0;
  animation: flicker 10s infinite;
}

body::after {
  content: '';
  position: fixed;
  top: 0; left: 0;
  width: 100vw; height: 100vh;
  background-image:
    linear-gradient(rgba(255,0,110,0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,0,110,0.03) 1px, transparent 1px);
  background-size: 50px 50px;
  pointer-events: none;
  z-index: 1;
}

@keyframes flicker {
  0%, 100% { opacity: 1; }
  95% { opacity: 0.98; }
}

h1.site-title {
  font-family: 'Space Mono', monospace;
  font-size: clamp(2rem, 5vw, 3.5rem);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  background: linear-gradient(45deg, #FF006E, #00F5FF, #00FF00);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-shadow: 0 0 30px rgba(255,0,110,0.5);
  margin: 0;
}

.site-header {
  position: relative;
  padding: 2rem;
  margin-bottom: 3rem;
  background: linear-gradient(180deg, rgba(26,26,26,0.8) 0%, transparent 100%);
  border: 2px solid #FF006E;
  border-radius: 12px;
  overflow: hidden;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
  display: flex;
  align-items: center;
  gap: 2rem;
  position: relative;
  z-index: 1;
}

.chat-icon {
  font-size: 4em;
  width: 120px;
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255,0,110,0.1);
  border: 2px solid var(--color-primary);
  border-radius: 12px;
  flex-shrink: 0;
}

.header-text {
  flex: 1;
}

.status-bar {
  display: flex;
  align-items: center;
  gap: 2rem;
  margin-top: 1rem;
}

.timestamp {
  font-family: 'Space Mono', monospace;
  background: rgba(0,245,255,0.1);
  border: 1px solid #00F5FF;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  letter-spacing: 0.1em;
  display: inline-block;
}

.status-indicator {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1.5rem;
  background: rgba(0,255,0,0.1);
  border: 2px solid #00FF00;
  border-radius: 20px;
  font-family: 'Space Mono', monospace;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  font-weight: 700;
  box-shadow:
    inset 0 0 20px rgba(0,255,0,0.3),
    0 0 20px rgba(0,255,0,0.5);
  position: relative;
}

.status-indicator::before {
  content: '';
  display: inline-block;
  width: 10px; height: 10px;
  background: #00FF00;
  border-radius: 50%;
  margin-right: 0.5em;
  animation: blink 1s infinite;
  box-shadow: 0 0 10px #00FF00;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}

.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 3rem 2rem;
  position: relative;
  z-index: 2;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 3rem;
}

.stat-card {
  background: linear-gradient(135deg, #1A1A1A 0%, #0F0F0F 100%);
  border: 2px solid #FF006E;
  border-radius: 12px;
  padding: 1.5rem;
  text-align: center;
  transition: all 0.2s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  border-color: #00F5FF;
  box-shadow: 0 4px 24px rgba(0,245,255,0.15);
}

.stat-value {
  font-family: 'Space Mono', monospace;
  font-weight: 700;
  font-size: 2.5rem;
  color: #00F5FF;
  text-shadow:
    0 0 10px #00F5FF,
    0 0 20px #00F5FF,
    0 0 30px #00F5FF;
  letter-spacing: 0.1em;
  margin-bottom: 0.5rem;
}

.stat-label {
  font-size: 0.875rem;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  opacity: 0.7;
  font-family: 'Space Mono', monospace;
}

.messages-section {
  background: linear-gradient(135deg, #1A1A1A 0%, #0F0F0F 100%);
  border: 2px solid #FF006E;
  border-radius: 12px;
  padding: 2rem;
  margin-bottom: 2rem;
}

.section-title {
  font-family: 'Space Mono', monospace;
  font-size: 1.5rem;
  color: var(--color-text);
  margin-bottom: 1.5rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.message-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.message-item {
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,0,110,0.2);
  border-radius: 8px;
  padding: 1rem;
  transition: all 0.2s ease;
}

.message-item:hover {
  background: rgba(255,255,255,0.08);
  border-color: rgba(255,0,110,0.4);
  transform: translateX(4px);
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.message-author {
  font-family: 'Space Mono', monospace;
  font-weight: 700;
  color: #00F5FF;
  font-size: 0.9rem;
}

.message-time {
  font-family: 'Space Mono', monospace;
  font-size: 0.8rem;
  color: #888;
}

.message-text {
  color: var(--color-text);
  line-height: 1.5;
  word-wrap: break-word;
}

.message-type-badge {
  display: inline-block;
  padding: 0.2rem 0.5rem;
  background: rgba(0,255,0,0.1);
  border: 1px solid #00FF00;
  border-radius: 4px;
  font-size: 0.7rem;
  font-family: 'Space Mono', monospace;
  color: #00FF00;
  margin-left: 0.5rem;
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: rgba(255,0,110,0.1);
  border: 2px solid #FF006E;
  border-radius: 8px;
  color: #FF006E;
  text-decoration: none;
  font-family: 'Space Mono', monospace;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  transition: all 0.2s ease;
  margin-bottom: 2rem;
}

.back-link:hover {
  background: rgba(255,0,110,0.2);
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(255,0,110,0.3);
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    text-align: center;
    gap: 1.5rem;
  }
  
  .chat-icon {
    width: 80px;
    height: 80px;
    font-size: 2.5em;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .status-bar {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
}
'''

    def generate_site(self):
        print("🚀 Generating Wartime Milady CEO Intelligence Platform...")
        data = self.load_channel_data()
        print(f"📊 Loaded data for {data['total_channels']} channels")
        homepage_html = self.generate_homepage(data)
        homepage_path = self.output_dir / 'index.html'
        with open(homepage_path, 'w', encoding='utf-8') as f:
            f.write(homepage_html)
        print(f"📄 Generated homepage: {homepage_path}")
        
        # Generate report pages
        self.generate_report_pages(data)
        
        self.copy_static_assets()
        print("📁 Copied static assets")
        print("✅ Site generation complete!")
        print(f"📂 Output directory: {self.output_dir.absolute()}")
        return True

def main():
    generator = MiladySiteGenerator()
    generator.generate_site()

if __name__ == "__main__":
    main() 