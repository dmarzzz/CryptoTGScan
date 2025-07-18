#!/usr/bin/env python3
"""
Wartime Milady CEO - GitHub Data Generator
Generates repository data from GitHub config for the intelligence platform.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

def load_github_config():
    """Load GitHub repository configuration"""
    config_file = Path('data/github_config.json')
    
    if not config_file.exists():
        # Create default config if it doesn't exist
        default_config = {
            "generated_at": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
            "total_repositories": 0,
            "repositories": []
        }
        
        config_file.parent.mkdir(exist_ok=True)
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=2)
        
        print(f"📁 Created default GitHub config: {config_file}")
        return default_config
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print(f"📊 Loaded GitHub config with {config.get('total_repositories', 0)} repositories")
        return config
    except Exception as e:
        print(f"❌ Error loading GitHub config: {e}")
        return None

def generate_sample_github_data():
    """Generate sample GitHub repository data for demonstration"""
    now = datetime.utcnow()
    
    sample_repositories = [
        {
            "id": "ethereum/go-ethereum",
            "name": "Go Ethereum",
            "full_name": "ethereum/go-ethereum",
            "description": "Official Go implementation of the Ethereum protocol",
            "icon": "⚡",
            "language": "Go",
            "stars": 44500,
            "forks": 19500,
            "last_update": now.strftime('%Y-%m-%dT%H:%M:%SZ'),
            "stats": {
                "commits_7d": 45,
                "contributors_7d": 12,
                "pull_requests": 23,
                "issues": 156
            }
        },
        {
            "id": "ethereum/solidity",
            "name": "Solidity",
            "full_name": "ethereum/solidity",
            "description": "Solidity, the Smart Contract Programming Language",
            "icon": "🔧",
            "language": "C++",
            "stars": 21500,
            "forks": 5800,
            "last_update": now.strftime('%Y-%m-%dT%H:%M:%SZ'),
            "stats": {
                "commits_7d": 28,
                "contributors_7d": 8,
                "pull_requests": 15,
                "issues": 89
            }
        },
        {
            "id": "ethereum/EIPs",
            "name": "Ethereum Improvement Proposals",
            "full_name": "ethereum/EIPs",
            "description": "The Ethereum Improvement Proposal repository",
            "icon": "📋",
            "language": "Markdown",
            "stars": 12500,
            "forks": 4800,
            "last_update": now.strftime('%Y-%m-%dT%H:%M:%SZ'),
            "stats": {
                "commits_7d": 12,
                "contributors_7d": 5,
                "pull_requests": 8,
                "issues": 34
            }
        },
        {
            "id": "ethereum/ethereum-js",
            "name": "Ethereum.js",
            "full_name": "ethereum/ethereum.js",
            "description": "Ethereum JavaScript implementation",
            "icon": "🟨",
            "language": "TypeScript",
            "stars": 8900,
            "forks": 3200,
            "last_update": now.strftime('%Y-%m-%dT%H:%M:%SZ'),
            "stats": {
                "commits_7d": 31,
                "contributors_7d": 9,
                "pull_requests": 18,
                "issues": 67
            }
        },
        {
            "id": "ethereum/consensus-specs",
            "name": "Consensus Specs",
            "full_name": "ethereum/consensus-specs",
            "description": "Ethereum Proof of Stake consensus specifications",
            "icon": "🔐",
            "language": "Python",
            "stars": 3400,
            "forks": 1200,
            "last_update": now.strftime('%Y-%m-%dT%H:%M:%SZ'),
            "stats": {
                "commits_7d": 19,
                "contributors_7d": 6,
                "pull_requests": 11,
                "issues": 42
            }
        }
    ]
    
    return {
        "generated_at": now.strftime('%Y-%m-%dT%H:%M:%SZ'),
        "total_repositories": len(sample_repositories),
        "repositories": sample_repositories
    }

def main():
    """Main function to generate GitHub data"""
    print("🚀 Generating GitHub Intelligence Data...")
    
    # Load existing config or create sample data
    config = load_github_config()
    
    if not config or config.get('total_repositories', 0) == 0:
        print("📝 No repositories configured, generating sample data...")
        data = generate_sample_github_data()
    else:
        print("📊 Using existing GitHub configuration...")
        data = config
    
    # Save the data
    output_file = Path('data/github_repositories.json')
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    
    print(f"✅ Generated GitHub data for {data['total_repositories']} repositories")
    print(f"📁 Saved to: {output_file}")
    
    return data

if __name__ == "__main__":
    main() 