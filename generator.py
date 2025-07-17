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
            trend_arrow = '↗' if channel['stats']['trend'] == 'up' else '↘'
            trend_class = 'trend-up' if channel['stats']['trend'] == 'up' else 'trend-down'
            card_html = f'''
            <div class="channel-card" tabindex="0" aria-label="{channel['name']} channel card">
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
                            <span class="stat-label">Users</span>
                            <span class="stat-value">{channel['stats']['participants_24h']}</span>
                        </div>
                    </div>
                    <div class="activity-badge {trend_class}">
                        <span class="trend-arrow">{trend_arrow}</span>
                        <span class="change-percent">{abs(channel['stats']['change_percent'])}%</span>
                    </div>
                </div>
            </div>
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
    <link href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Inter:wght@300;400;600&display=swap" rel="stylesheet">
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
                <h1 class="site-title">ETHEREUM INTELLIGENCE COMMAND</h1>
                <p class="site-subtitle">Monitoring {data['total_channels']} channels across the frontlines</p>
                <div class="status-bar">
                    <span class="timestamp">{current_time}</span>
                    <span class="status-indicator" aria-live="polite">● SYSTEMS ONLINE</span>
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
        # (CSS omitted for brevity, will be included in actual file)
        return """
:root {
  --color-primary: #FF006E;
  --color-secondary: #00F5FF;
  --color-accent: #00FF00;
  --color-bg: #0A0A0A;
  --color-surface: #1A1A1A;
  --color-text: #F0F0F0;
  --font-mono: 'Space Mono', 'Courier New', monospace;
  --font-sans: -apple-system, BlinkMacSystemFont, 'Inter', sans-serif;
}
body { font-family: var(--font-sans); background: var(--color-bg); color: var(--color-text); line-height: 1.6; }
.scan-lines { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; pointer-events: none; z-index: 100; }
.scan-lines::before { content: ''; position: fixed; top: -100vh; left: 0; width: 100vw; height: 200vh; background: repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(255,0,110,0.03) 2px, rgba(255,0,110,0.03) 4px); animation: scan-lines 8s linear infinite; pointer-events: none; z-index: 100; }
@keyframes scan-lines { 0% { transform: translateY(0); } 100% { transform: translateY(100vh); } }
.site-header { background: linear-gradient(135deg, var(--color-surface), rgba(26,26,26,0.9)); border-bottom: 2px solid var(--color-primary); padding: 2rem 0; position: relative; overflow: hidden; }
.header-content { max-width: 1200px; margin: 0 auto; padding: 0 2rem; display: flex; align-items: center; gap: 2rem; position: relative; z-index: 1; }
.milady-avatar { flex-shrink: 0; }
.avatar-placeholder { width: 120px; height: 120px; border-radius: 50%; background: linear-gradient(45deg, var(--color-primary), var(--color-secondary)); display: flex; align-items: center; justify-content: center; font-size: 3rem; border: 3px solid var(--color-accent); box-shadow: 0 0 20px var(--color-primary), 0 0 20px var(--color-accent); animation: pulse 2s ease-in-out infinite alternate; }
@keyframes pulse { 0% { transform: scale(1); } 100% { transform: scale(1.05); } }
.header-text { flex: 1; }
.site-title { font-size: 2.5rem; font-family: var(--font-mono); background: linear-gradient(45deg, var(--color-primary), var(--color-secondary)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; text-shadow: 0 0 30px var(--color-primary); margin-bottom: 0.5rem; }
.site-subtitle { font-size: 1.1rem; color: #888; margin-bottom: 1rem; }
.status-bar { display: flex; align-items: center; gap: 2rem; margin-top: 1rem; }
.timestamp { font-family: var(--font-mono); font-size: 0.9rem; color: var(--color-secondary); background: rgba(0,245,255,0.1); padding: 0.5rem 1rem; border: 1px solid var(--color-secondary); border-radius: 4px; }
.status-indicator { font-family: var(--font-mono); font-size: 0.9rem; color: var(--color-accent); display: flex; align-items: center; gap: 0.5em; }
.status-indicator::before { content: '●'; color: var(--color-accent); animation: blink 1s ease-in-out infinite alternate; margin-right: 0.5em; }
@keyframes blink { 0% { opacity: 1; } 100% { opacity: 0.3; } }
.main-content { max-width: 1200px; margin: 0 auto; padding: 3rem 2rem; }
.channel-grid { display: grid; gap: 1.5rem; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); }
.channel-card { background: var(--color-surface); border: 1px solid var(--color-primary); border-radius: 8px; padding: 1.5rem; transition: all 0.3s ease; cursor: pointer; position: relative; overflow: hidden; outline: none; }
.channel-card:hover, .channel-card:focus { transform: translateY(-2px) scale(1.02); box-shadow: 0 0 20px rgba(255,0,110,0.5), 0 0 40px rgba(255,0,110,0.3), inset 0 0 20px rgba(255,0,110,0.1); border-color: var(--color-accent); }
.channel-header { display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem; }
.channel-icon { font-size: 2rem; width: 60px; height: 60px; display: flex; align-items: center; justify-content: center; background: rgba(255,0,110,0.1); border: 1px solid var(--color-primary); border-radius: 8px; }
.channel-name { font-size: 1.3rem; color: var(--color-text); margin-bottom: 0.25rem; font-family: var(--font-mono); }
.channel-meta { font-size: 0.85rem; color: #888; }
.channel-stats { display: flex; justify-content: space-between; align-items: flex-end; }
.stat-row { display: flex; gap: 1.5rem; }
.stat-item { display: flex; flex-direction: column; align-items: flex-start; }
.stat-label { font-size: 0.75rem; color: #888; font-family: var(--font-mono); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.25em; }
.stat-value { font-size: 1.5rem; font-weight: 600; font-family: var(--font-mono); color: var(--color-secondary); }
.activity-badge { display: inline-flex; align-items: center; gap: 0.25rem; padding: 0.25rem 0.5rem; background: rgba(0,255,0,0.1); border: 1px solid var(--color-accent); border-radius: 4px; font-size: 0.75rem; font-family: var(--font-mono); }
.activity-badge.trend-up { background: rgba(0,255,0,0.1); border-color: var(--color-accent); color: var(--color-accent); }
.activity-badge.trend-down { background: rgba(255,0,110,0.1); border-color: var(--color-primary); color: var(--color-primary); }
.trend-arrow { font-size: 1rem; }
.site-footer { background: var(--color-surface); border-top: 1px solid var(--color-primary); padding: 2rem; text-align: center; color: #888; font-size: 0.9rem; }
@media (max-width: 1024px) { .site-title { font-size: 2rem; } .header-content { flex-direction: column; text-align: center; gap: 1.5rem; } .avatar-placeholder { width: 100px; height: 100px; font-size: 2.5rem; } .channel-grid { grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); } }
@media (max-width: 768px) { .site-title { font-size: 1.5rem; } .header-content { padding: 0 1em; } .main-content { padding: 2rem 1rem; } .channel-grid { grid-template-columns: 1fr; gap: 1.5rem; } .channel-card { padding: 1rem; } .stat-row { gap: 1rem; } .status-bar { flex-direction: column; gap: 1rem; align-items: flex-start; } }
@media (max-width: 480px) { .site-title { font-size: 1.25rem; } .avatar-placeholder { width: 80px; height: 80px; font-size: 2rem; } .channel-header { flex-direction: column; text-align: center; gap: 0.75rem; } .channel-stats { flex-direction: column; gap: 1rem; align-items: center; } .stat-row { justify-content: center; } }
@media (prefers-reduced-motion: reduce) { * { animation-duration: 0.01ms !important; animation-iteration-count: 1 !important; transition-duration: 0.1s !important; } }
.channel-card:focus { outline: 2px solid var(--color-secondary); outline-offset: 2px; }
@media (prefers-contrast: high) { :root { --color-bg: #000; --color-surface: #111111; --color-text: #ffffff; } }
        """

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

    def generate_site(self):
        print("🚀 Generating Wartime Milady CEO Intelligence Platform...")
        data = self.load_channel_data()
        print(f"📊 Loaded data for {data['total_channels']} channels")
        homepage_html = self.generate_homepage(data)
        homepage_path = self.output_dir / 'index.html'
        with open(homepage_path, 'w', encoding='utf-8') as f:
            f.write(homepage_html)
        print(f"📄 Generated homepage: {homepage_path}")
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