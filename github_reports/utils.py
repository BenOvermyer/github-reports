
# Utility functions for GitHub API interaction and charting
import requests
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

def github_api_get(url, token, params=None):
    if token is None or token.strip() == "":
        raise RuntimeError(
            "GitHub token is missing. Please provide a valid personal access token."
        )
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(url, headers=headers, params=params)
    try:
        response.raise_for_status()
    except requests.HTTPError as e:
        if response.status_code == 404:
            raise RuntimeError(
                f"Repository not found or access denied. "
                f"Check that the repository name is correct and that your token has access to private repositories (scope: 'repo')."
            ) from e
        elif response.status_code == 401:
            raise RuntimeError(
                f"Unauthorized. Your token may be invalid or missing required scopes. "
                f"Check your token permissions and try again."
            ) from e
        elif response.status_code == 403:
            raise RuntimeError(
                f"Forbidden. You may not have permission to access this resource, or you have hit a rate limit. "
                f"Check your token permissions and GitHub API rate limits."
            ) from e
        else:
            raise RuntimeError(f"GitHub API error: {response.status_code} {response.reason}") from e
    return response.json()

def fetch_all_issues(repo, token):
    """Fetch all issues (open and closed) from a GitHub repo."""
    issues = []
    page = 1
    while True:
        url = f'https://api.github.com/repos/{repo}/issues'
        params = {'state': 'all', 'per_page': 100, 'page': page}
        batch = github_api_get(url, token, params)
        if not batch:
            break
        issues.extend(batch)
        page += 1
    return issues

def fetch_commits(repo, token, since):
    """Fetch commits since a given date from a GitHub repo."""
    commits = []
    page = 1
    while True:
        url = f'https://api.github.com/repos/{repo}/commits'
        params = {'since': since.isoformat(), 'per_page': 100, 'page': page}
        batch = github_api_get(url, token, params)
        if not batch:
            break
        commits.extend(batch)
        page += 1
    return commits

def burndown_data_from_issues(issues):
    """Return daily open/closed issue counts for burndown chart."""
    if not issues:
        return [], [], []
    created_dates = [datetime.strptime(i['created_at'], '%Y-%m-%dT%H:%M:%SZ') for i in issues]
    closed_dates = [datetime.strptime(i['closed_at'], '%Y-%m-%dT%H:%M:%SZ') for i in issues if i.get('closed_at')]
    start = min(created_dates)
    end = max(created_dates + closed_dates) if closed_dates else max(created_dates)
    days = (end - start).days + 1
    date_range = [start + timedelta(days=i) for i in range(days)]
    open_counts = []
    closed_counts = []
    for d in date_range:
        # Cumulative sum of issues opened up to and including this date
        open_count = sum(1 for i in issues if datetime.strptime(i['created_at'], '%Y-%m-%dT%H:%M:%SZ') <= d)
        closed_count = sum(1 for i in issues if i.get('closed_at') and datetime.strptime(i['closed_at'], '%Y-%m-%dT%H:%M:%SZ') <= d)
        open_counts.append(open_count)
        closed_counts.append(closed_count)
    return date_range, open_counts, closed_counts

def plot_burndown(date_range, open_counts, closed_counts, output):
    plt.figure(figsize=(10,6))
    plt.plot(date_range, open_counts, label='Open Issues')
    plt.plot(date_range, closed_counts, label='Closed Issues')
    plt.xlabel('Date')
    plt.ylabel('Issue Count')
    plt.title('Burndown Chart')
    plt.legend()
    plt.tight_layout()
    plt.savefig(output)


def commit_summary_weekly_data(commits):
    """Return weekly commit counts per user as a dict: {user: [week1, week2, ...]} and week labels."""
    from collections import defaultdict
    if not commits:
        return {}, []
    # Find date range
    dates = [datetime.strptime(c['commit']['author']['date'], '%Y-%m-%dT%H:%M:%SZ') for c in commits if c.get('commit') and c['commit'].get('author')]
    if not dates:
        return {}, []
    start = min(dates)
    end = max(dates)
    # Build week bins
    week_starts = []
    current = start - timedelta(days=start.weekday())  # start from Monday
    while current <= end:
        week_starts.append(current)
        current += timedelta(days=7)
    week_labels = [ws.strftime('%Y-%m-%d') for ws in week_starts]
    user_week_counts = defaultdict(lambda: [0]*len(week_starts))
    for c in commits:
        if not (c.get('commit') and c['commit'].get('author')):
            continue
        author = c['commit']['author']['name']
        date = datetime.strptime(c['commit']['author']['date'], '%Y-%m-%dT%H:%M:%SZ')
        for i, ws in enumerate(week_starts):
            we = ws + timedelta(days=7)
            if ws <= date < we:
                user_week_counts[author][i] += 1
                break
    return user_week_counts, week_labels


def plot_commit_summary_weekly(user_week_counts, week_labels, output):
    import numpy as np
    users = list(user_week_counts.keys())
    weeks = len(week_labels)
    x = np.arange(weeks)
    plt.figure(figsize=(12,7))
    bottom = np.zeros(weeks)
    for user in users:
        counts = user_week_counts[user]
        plt.bar(x, counts, bottom=bottom, label=user)
        bottom += np.array(counts)
    plt.xlabel('Week Starting')
    plt.ylabel('Commits')
    plt.title('Weekly Commit Summary per User')
    plt.xticks(x, week_labels, rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output)
