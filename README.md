# GitHub Reports CLI

A Python CLI tool to generate project management charts (burndown, commit summaries, and more) from GitHub repositories using the GitHub REST API.

## Features
- **Burndown Chart**: Visualize open/closed issues over time.
- **Commit Summary**: See commit counts per user for the last X months.
- **Extensible**: Add more charts as needed.


## Requirements
- Python 3.12+
- [uv (Astral)](https://github.com/astral-sh/uv) for dependency management and running
- A GitHub personal access token (PAT)

### Required GitHub PAT Permissions
Your personal access token must have the following scopes:

- `repo` (Full control of private repositories)
   - Required to read issues and commits from private repositories
- `public_repo` (Access public repositories)
   - Sufficient for public repositories only

For most use cases, the `repo` scope is recommended. You can generate a PAT at https://github.com/settings/tokens

## Installation

1. Install [uv](https://github.com/astral-sh/uv):
   ```sh
   curl -Ls https://astral.sh/uv/install.sh | sh
   # or see uv docs for your OS
   ```

2. Install dependencies:
   ```sh
   uv sync
   ```

3. (Optional) Install as CLI:
   ```sh
   uv pip install -e .
   ```

## Usage

### Burndown Chart
```sh
github-reports burndown --repo owner/repo --token <your_token> --output burndown.png
```

### Commit Summary
```sh
github-reports commit-summary --repo owner/repo --token <your_token> --months 3 --output commits.png
```

## Development
- All dependencies are managed with `uv`.
- CLI entry point: `github_reports/cli.py`
- Utility functions: `github_reports/utils.py`

## License
MIT
