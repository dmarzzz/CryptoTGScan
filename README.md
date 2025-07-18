# Wartime Milady CEO Intelligence Platform

A cyberpunk/military-styled static site generator for monitoring Telegram channels and GitHub repositories with automated intelligence reports.

## Features

- **Multi-Platform Intelligence**: Monitor both Telegram channels and GitHub repositories
- **Automated Reports**: Daily reports for the last 7 days with detailed statistics
- **Cyberpunk UI**: Military-styled interface with animations and effects
- **Static Site Generation**: Fully static HTML/CSS/JS for easy deployment
- **GitHub Actions Integration**: Automated updates every 6 hours

## Setup

### Prerequisites

- Python 3.11+
- GitHub Personal Access Token
- Supabase database (for Telegram data)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/CryptoTGScan.git
cd CryptoTGScan
```

2. Install Python dependencies:
```bash
pip install requests python-dotenv supabase psycopg2-binary
```

3. Set up environment variables:
```bash
# For GitHub API access
export GITHUB_TOKEN=your_github_personal_access_token

# For Telegram data (if using Supabase)
export SUPABASE_URL=your_supabase_url
export SUPABASE_SERVICE_ROLE_KEY=your_supabase_key
```

### GitHub Token Setup

1. Go to [GitHub Settings > Personal Access Tokens](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Give it a name like "Wartime Milady CEO Intelligence"
4. Select scopes:
   - `public_repo` (for public repositories)
   - `repo` (for private repositories, if needed)
5. Copy the token and set it as the `GITHUB_TOKEN` environment variable

### Configuration

#### GitHub Repositories

Edit `data/github_config.json` to add repository URLs:

```json
{
  "generated_at": "2025-01-17T12:00:00Z",
  "total_repositories": 0,
  "repositories": [
    "https://github.com/ethereum/go-ethereum",
    "https://github.com/ethereum/solidity",
    "https://github.com/ethereum/EIPs"
  ]
}
```

#### Telegram Channels

Edit `data/channels.json` to configure Telegram channels (or let the system generate from database).

### Usage

#### Local Development

1. Generate the site:
```bash
python generator.py
```

2. Open `website/index.html` in your browser

#### GitHub Actions (Automated)

The platform automatically updates every 6 hours via GitHub Actions. To enable:

1. Add the following secrets to your GitHub repository:
   - `GITHUB_TOKEN`: Your GitHub personal access token
   - `SUPABASE_URL`: Your Supabase URL (for Telegram data)
   - `SUPABASE_SERVICE_ROLE_KEY`: Your Supabase service role key

2. The workflow will automatically:
   - Fetch GitHub repository data
   - Generate Telegram channel data
   - Create daily reports
   - Update the static site

## File Structure

```
├── data/
│   ├── channels.json          # Telegram channel configuration
│   ├── github_config.json     # GitHub repository URLs
│   └── github_repositories.json # Generated GitHub data
├── scripts/
│   ├── generate_milady_data.py    # Generate Telegram data
│   ├── generate_github_data.py    # Fetch GitHub repository data
│   ├── generate_report_pages.py   # Generate Telegram reports
│   └── generate_github_reports.py # Generate GitHub reports
├── website/
│   ├── index.html             # Homepage
│   ├── telegram.html          # Telegram intelligence page
│   ├── github.html            # GitHub intelligence page
│   ├── reports/               # Telegram reports
│   └── github_reports/        # GitHub reports
└── generator.py               # Main site generator
```

## Intelligence Reports

### Telegram Reports
- Message counts and participant statistics
- Daily activity summaries
- Channel-specific insights

### GitHub Reports
- Commit activity (last 7 days)
- Contributor statistics
- Pull request and issue counts
- Repository metadata (stars, forks, language)

## Styling

The platform uses a cyberpunk/military aesthetic with:
- Neon color scheme (pink, cyan, green)
- Scan line animations
- Matrix-style effects
- Terminal-style typography
- Responsive design

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally with `python generator.py`
5. Submit a pull request

## License

MIT License - see LICENSE file for details.
