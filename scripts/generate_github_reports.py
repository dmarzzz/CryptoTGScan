#!/usr/bin/env python3
"""
Wartime Milady CEO - GitHub Repository Report Generator
Generates detailed report pages for each monitored GitHub repository.
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
import json

def get_repository_icon(repo_name, language):
    """Get appropriate icon for repository type"""
    repo_lower = repo_name.lower()
    language_lower = language.lower() if language else ""
    
    if "ethereum" in repo_lower and "go" in repo_lower:
        return "⚡"
    elif "solidity" in repo_lower:
        return "🔧"
    elif "eip" in repo_lower or "improvement" in repo_lower:
        return "📋"
    elif "consensus" in repo_lower or "spec" in repo_lower:
        return "🔐"
    elif "js" in repo_lower or "javascript" in repo_lower:
        return "🟨"
    elif "core" in repo_lower:
        return "⚙️"
    elif "research" in repo_lower:
        return "🔬"
    elif "security" in repo_lower:
        return "🛡️"
    elif "test" in repo_lower:
        return "🧪"
    elif "docs" in repo_lower or "documentation" in repo_lower:
        return "📚"
    
    # Language-based icons
    if language_lower == "go":
        return "🐹"
    elif language_lower == "python":
        return "🐍"
    elif language_lower == "javascript" or language_lower == "typescript":
        return "🟨"
    elif language_lower == "rust":
        return "🦀"
    elif language_lower == "c++":
        return "🔧"
    elif language_lower == "markdown":
        return "📝"
    else:
        return "💻"

def generate_github_report_css():
    """Generate the CSS for GitHub report pages"""
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

.repo-icon {
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

.repo-info-section {
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

.repo-description {
  color: var(--color-text);
  line-height: 1.6;
  font-size: 1.1rem;
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,0,110,0.2);
  border-radius: 8px;
}

.repo-meta {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
  margin-top: 1.5rem;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,0,110,0.2);
  border-radius: 6px;
}

.meta-label {
  font-family: 'Space Mono', monospace;
  font-size: 0.8rem;
  text-transform: uppercase;
  opacity: 0.7;
}

.meta-value {
  font-weight: 700;
  color: #00F5FF;
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
  
  .repo-icon {
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
  
  .repo-meta {
    grid-template-columns: 1fr;
  }
}
'''

def generate_github_report_page(repo_data, start_date, end_date, output_dir='website/github_reports'):
    """Generate a detailed report page for a specific GitHub repository"""
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Generate HTML
    current_time = datetime.utcnow().strftime('%Y-%m-%d %H%MZ')
    repo_icon = get_repository_icon(repo_data['name'], repo_data.get('language', ''))
    
    # Format date range for display
    date_range = f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Wartime Milady CEO - {repo_data['name']} Report ({date_range})</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Inter:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
{generate_github_report_css()}
    </style>
</head>
<body>
    <div class="scan-lines"></div>
    <header class="site-header">
        <div class="header-content">
            <div class="repo-icon">
                {repo_icon}
            </div>
            <div class="header-text">
                <h1 class="site-title">{repo_data['name']}</h1>
                <p class="site-subtitle">GitHub Intelligence Report - {date_range}</p>
                <div class="status-bar">
                    <span class="timestamp">{current_time}</span>
                    <span class="status-indicator" aria-live="polite">SYSTEMS ONLINE</span>
                </div>
            </div>
        </div>
    </header>
    
    <main class="main-content">
        <a href="../github.html" class="back-link">← BACK TO GITHUB INTELLIGENCE</a>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{repo_data['stats']['commits_7d']}</div>
                <div class="stat-label">Commits (7d)</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{repo_data['stats']['contributors_7d']}</div>
                <div class="stat-label">Contributors (7d)</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{repo_data['stats']['pull_requests']}</div>
                <div class="stat-label">Pull Requests</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{repo_data['stats']['issues']}</div>
                <div class="stat-label">Open Issues</div>
            </div>
        </div>
        
        <div class="repo-info-section">
            <h2 class="section-title">Repository Information</h2>
            <div class="repo-description">{repo_data.get('description', 'No description available')}</div>
            
            <div class="repo-meta">
                <div class="meta-item">
                    <span class="meta-label">Language:</span>
                    <span class="meta-value">{repo_data.get('language', 'Unknown')}</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">Stars:</span>
                    <span class="meta-value">{repo_data.get('stars', 0):,}</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">Forks:</span>
                    <span class="meta-value">{repo_data.get('forks', 0):,}</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">Full Name:</span>
                    <span class="meta-value">{repo_data.get('full_name', repo_data['name'])}</span>
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
    
    # Write to file with date-based filename
    safe_filename = repo_data['id'].replace('/', '_').replace('-', '_')
    date_suffix = start_date.strftime('%Y%m%d')
    output_file = output_path / f"report_{safe_filename}_{date_suffix}.html"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"Generated GitHub report: {output_file}")
    return output_file

def generate_daily_github_reports_for_repo(repo_data, days_back=7):
    """Generate daily reports for the last N days for a specific repository"""
    reports = []
    
    for i in range(days_back):
        # Calculate date range for this day
        end_date = datetime.now() - timedelta(days=i)
        start_date = end_date - timedelta(days=1)
        
        # Generate report for this day
        report_file = generate_github_report_page(repo_data, start_date, end_date)
        if report_file:
            reports.append({
                'date': start_date.strftime('%Y-%m-%d'),
                'filename': report_file.name,
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'commits': repo_data['stats']['commits_7d'],
                'contributors': repo_data['stats']['contributors_7d']
            })
    
    return reports

def generate_all_github_reports():
    """Generate daily report pages for all monitored GitHub repositories"""
    # Read repositories data from the JSON file
    repos_file = Path('data/github_repositories.json')
    
    if not repos_file.exists():
        print("Error: github_repositories.json not found. Run generate_github_data.py first.")
        return
    
    try:
        with open(repos_file, 'r', encoding='utf-8') as f:
            repos_data = json.load(f)
        
        print(f"📊 Generating daily reports for {len(repos_data['repositories'])} repositories...")
        
        all_reports = {}
        
        for repo in repos_data['repositories']:
            try:
                print(f"📄 Generating daily reports for {repo['name']} (ID: {repo['id']})")
                
                # Generate daily reports for this repository
                reports = generate_daily_github_reports_for_repo(repo, days_back=7)
                # Use the repo ID as the metadata key
                metadata_key = repo['id'].replace('/', '_')
                all_reports[metadata_key] = {
                    'name': repo['name'],
                    'reports': reports
                }
                
            except Exception as e:
                print(f"Error generating reports for repo {repo['name']} (ID: {repo['id']}): {e}")
        
        # Save reports metadata for the popup interface
        metadata_file = Path('website/github_reports/metadata.json')
        metadata_file.parent.mkdir(exist_ok=True)
        
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(all_reports, f, indent=2, default=str)
        
        print(f"✅ Generated daily reports for {len(repos_data['repositories'])} repositories")
        print(f"📁 Reports metadata saved to: {metadata_file}")
        
    except Exception as e:
        print(f"Error reading repositories data: {e}")
        return

if __name__ == "__main__":
    generate_all_github_reports() 