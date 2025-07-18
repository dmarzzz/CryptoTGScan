#!/usr/bin/env python3
"""
Wartime Milady CEO - GitHub Data Generator
Generates repository data from GitHub config for the intelligence platform.
"""

import json
import os
import sys
import requests
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_github_credentials():
    """Check if GitHub credentials are properly configured"""
    github_token = os.getenv('GITHUB_TOKEN')
    if not github_token:
        raise ValueError("GITHUB_TOKEN environment variable is not set. Please set it to access GitHub API.")
    
    # Test the token by making a simple API call
    headers = {
        'Authorization': f'token {github_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    try:
        response = requests.get('https://api.github.com/user', headers=headers)
        if response.status_code == 401:
            raise ValueError("Invalid GitHub token. Please check your GITHUB_TOKEN.")
        elif response.status_code != 200:
            raise ValueError(f"GitHub API error: {response.status_code}")
        
        print(f"✅ GitHub API authenticated as: {response.json().get('login', 'Unknown')}")
        return headers
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Failed to connect to GitHub API: {e}")

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
        print("💡 Add repository URLs to the 'repositories' array in the config file.")
        return default_config
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print(f"📊 Loaded GitHub config with {len(config.get('repositories', []))} repository URLs")
        return config
    except Exception as e:
        print(f"❌ Error loading GitHub config: {e}")
        return None

def fetch_repository_data(repo_url, headers):
    """Fetch repository data from GitHub API"""
    # Extract owner and repo from URL
    if repo_url.startswith('https://github.com/'):
        parts = repo_url.replace('https://github.com/', '').split('/')
        if len(parts) >= 2:
            owner, repo = parts[0], parts[1]
        else:
            raise ValueError(f"Invalid GitHub URL format: {repo_url}")
    else:
        raise ValueError(f"Invalid GitHub URL: {repo_url}")
    
    # Fetch repository data
    api_url = f"https://api.github.com/repos/{owner}/{repo}"
    response = requests.get(api_url, headers=headers)
    
    if response.status_code == 404:
        raise ValueError(f"Repository not found: {owner}/{repo}")
    elif response.status_code != 200:
        raise ValueError(f"GitHub API error for {owner}/{repo}: {response.status_code}")
    
    repo_data = response.json()
    
    # Fetch recent commits (last 7 days)
    commits_url = f"{api_url}/commits"
    commits_params = {
        'since': (datetime.utcnow() - timedelta(days=7)).isoformat() + 'Z',
        'per_page': 100
    }
    
    commits_response = requests.get(commits_url, headers=headers, params=commits_params)
    commits_data = commits_response.json() if commits_response.status_code == 200 else []
    
    # Count unique contributors in the last 7 days
    contributors = set()
    for commit in commits_data:
        if commit.get('author') and commit['author'].get('login'):
            contributors.add(commit['author']['login'])
    
    # Fetch pull requests count
    prs_url = f"{api_url}/pulls"
    prs_params = {'state': 'open', 'per_page': 1}
    prs_response = requests.get(prs_url, headers=headers, params=prs_params)
    prs_count = 0
    if prs_response.status_code == 200:
        # Get total count from Link header if available
        link_header = prs_response.headers.get('Link', '')
        if 'rel="last"' in link_header:
            # Extract the page number from the last link
            import re
            match = re.search(r'page=(\d+)>; rel="last"', link_header)
            if match:
                prs_count = int(match.group(1))
        else:
            prs_count = len(prs_response.json())
    
    # Fetch issues count
    issues_url = f"{api_url}/issues"
    issues_params = {'state': 'open', 'per_page': 1}
    issues_response = requests.get(issues_url, headers=headers, params=issues_params)
    issues_count = 0
    if issues_response.status_code == 200:
        # Get total count from Link header if available
        link_header = issues_response.headers.get('Link', '')
        if 'rel="last"' in link_header:
            import re
            match = re.search(r'page=(\d+)>; rel="last"', link_header)
            if match:
                issues_count = int(match.group(1))
        else:
            issues_count = len(issues_response.json())
    
    # Get appropriate icon based on repository name and language
    repo_name = repo_data['name']
    language = repo_data.get('language', '')
    icon = get_repository_icon(repo_name, language)
    
    return {
        "id": f"{owner}/{repo}",
        "name": repo_data['name'],
        "full_name": repo_data['full_name'],
        "description": repo_data.get('description', ''),
        "icon": icon,
        "language": language,
        "stars": repo_data['stargazers_count'],
        "forks": repo_data['forks_count'],
        "last_update": repo_data['updated_at'],
        "stats": {
            "commits_7d": len(commits_data),
            "contributors_7d": len(contributors),
            "pull_requests": prs_count,
            "issues": issues_count
        }
    }

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

def main():
    """Main function to generate GitHub data"""
    print("🚀 Generating GitHub Intelligence Data...")
    
    try:
        # Check GitHub credentials first
        headers = check_github_credentials()
        
        # Load config
        config = load_github_config()
        if not config:
            print("❌ Failed to load GitHub config")
            return
        
        repository_urls = config.get('repositories', [])
        if not repository_urls:
            print("⚠️  No repository URLs found in config. Please add repository URLs to data/github_config.json")
            print("Example format:")
            print('  "repositories": [')
            print('    "https://github.com/ethereum/go-ethereum",')
            print('    "https://github.com/ethereum/solidity"')
            print('  ]')
            return
        
        print(f"📊 Fetching data for {len(repository_urls)} repositories...")
        
        repositories = []
        for i, repo_url in enumerate(repository_urls, 1):
            try:
                print(f"📄 Fetching data for repository {i}/{len(repository_urls)}: {repo_url}")
                repo_data = fetch_repository_data(repo_url, headers)
                repositories.append(repo_data)
                print(f"✅ Successfully fetched data for {repo_data['name']}")
            except Exception as e:
                print(f"❌ Error fetching data for {repo_url}: {e}")
                continue
        
        if not repositories:
            print("❌ No repositories were successfully fetched")
            return
        
        # Create the final data structure
        data = {
            "generated_at": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
            "total_repositories": len(repositories),
            "repositories": repositories
        }
        
        # Save the data
        output_file = Path('data/github_repositories.json')
        output_file.parent.mkdir(exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Generated GitHub data for {len(repositories)} repositories")
        print(f"📁 Saved to: {output_file}")
        
        return data
        
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("\n📋 Setup instructions:")
        print("1. Create a GitHub personal access token at https://github.com/settings/tokens")
        print("2. Set the GITHUB_TOKEN environment variable:")
        print("   export GITHUB_TOKEN=your_token_here")
        print("3. Add repository URLs to data/github_config.json")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 