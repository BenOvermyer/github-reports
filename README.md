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

All commands accept a comma-separated list for `--repo` to aggregate data across multiple repositories.

### Burndown Chart
Generate a burndown chart of open/closed issues over time:
```sh
github-reports burndown --repo octocat/Hello-World --token <your_token> --output burndown.png
github-reports burndown --repo octocat/Hello-World,psf/requests --token <your_token> --output burndown.png
```

### Commit Summary
Generate a weekly commit count summary per user:
```sh
github-reports commit-summary --repo octocat/Hello-World --token <your_token> --months 3 --output commits.png
github-reports commit-summary --repo octocat/Hello-World,psf/requests --token <your_token> --months 6 --output commits.png
```

### Issue Type Breakdown
Pie or bar chart of issue labels:
```sh
github-reports issue-type-breakdown --repo octocat/Hello-World --token <your_token> --output labels.png --chart-type pie
github-reports issue-type-breakdown --repo octocat/Hello-World,psf/requests --token <your_token> --output labels.png --chart-type bar
```

### PR Activity Timeline
Line chart of PRs opened/closed/merged per week:
```sh
github-reports pr-activity-timeline --repo octocat/Hello-World --token <your_token> --output pr_timeline.png
github-reports pr-activity-timeline --repo octocat/Hello-World,psf/requests --token <your_token> --output pr_timeline.png
```

### Issue Resolution Time
Histogram or boxplot of time taken to close issues:
```sh
github-reports issue-resolution-time --repo octocat/Hello-World --token <your_token> --output resolution.png --chart-type hist
github-reports issue-resolution-time --repo octocat/Hello-World,psf/requests --token <your_token> --output resolution.png --chart-type box
```

## Popular Repository Examples

- `octocat/Hello-World` (GitHub's sample repo)
- `psf/requests` (Popular Python HTTP library)
- `django/django` (Popular Python web framework)

You can aggregate across any combination:
```sh
github-reports burndown --repo octocat/Hello-World,django/django,psf/requests --token <your_token> --output burndown.png
```

## Development
- All dependencies are managed with `uv`.
- CLI entry point: `github_reports/cli.py`
- Utility functions: `github_reports/utils.py`

## License
MIT
