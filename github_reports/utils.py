import requests
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from collections import defaultdict

def issue_resolution_time_data(issues):
    """Return a list of resolution times (in days) for closed issues."""
    times = []
    for issue in issues:
        if issue.get('closed_at'):
            created = datetime.strptime(issue['created_at'], '%Y-%m-%dT%H:%M:%SZ')
            closed = datetime.strptime(issue['closed_at'], '%Y-%m-%dT%H:%M:%SZ')
            times.append((closed - created).days + (closed - created).seconds/86400)
    return times

def plot_issue_resolution_time(times, output, chart_type='hist'): 
    plt.figure(figsize=(10,6))
    if chart_type == 'hist':
        plt.hist(times, bins=20, color='skyblue', edgecolor='black')
        plt.title('Issue Resolution Time Histogram')
        plt.xlabel('Days to Close')
        plt.ylabel('Number of Issues')
    else:
        plt.boxplot(times, vert=False)
        plt.title('Issue Resolution Time Boxplot')
        plt.xlabel('Days to Close')
    plt.tight_layout()
    plt.savefig(output)
def fetch_pull_requests(repo, token, state='all'):
    """Fetch all pull requests from a GitHub repo."""
    prs = []
    page = 1
    while True:
        url = f'https://api.github.com/repos/{repo}/pulls'
        params = {'state': state, 'per_page': 100, 'page': page}
        batch = github_api_get(url, token, params)
        if not batch:
            break
        prs.extend(batch)
        page += 1
    return prs

def pr_activity_timeline_data(prs):
    """Return weekly counts of PRs opened, closed, and merged."""
    opened = defaultdict(int)
    closed = defaultdict(int)
    merged = defaultdict(int)
    weeks = set()
    for pr in prs:
        if 'created_at' in pr:
            week = datetime.strptime(pr['created_at'], '%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%W')
            opened[week] += 1
            weeks.add(week)
        if pr.get('closed_at'):
            week = datetime.strptime(pr['closed_at'], '%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%W')
            closed[week] += 1
            weeks.add(week)
        if pr.get('merged_at'):
            week = datetime.strptime(pr['merged_at'], '%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%W')
            merged[week] += 1
            weeks.add(week)
    week_list = sorted(list(weeks))
    opened_counts = [opened[w] for w in week_list]
    closed_counts = [closed[w] for w in week_list]
    merged_counts = [merged[w] for w in week_list]
    return week_list, opened_counts, closed_counts, merged_counts

def plot_pr_activity_timeline(week_list, opened_counts, closed_counts, merged_counts, output):
    plt.figure(figsize=(12,7))
    plt.plot(week_list, opened_counts, label='Opened PRs')
    plt.plot(week_list, closed_counts, label='Closed PRs')
    plt.plot(week_list, merged_counts, label='Merged PRs')
    plt.xlabel('Week')
    plt.ylabel('Count')
    plt.title('PR Activity Timeline')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output)
def issue_type_breakdown_data(issues):
    """Return a Counter of issue labels for type breakdown."""
    from collections import Counter
    labels = []
    for issue in issues:
        labels.extend([l['name'] for l in issue.get('labels', [])])
    return Counter(labels)

def plot_issue_type_breakdown(counter, output, chart_type='pie'):
    plt.figure(figsize=(8,8))
    labels = list(counter.keys())
    counts = list(counter.values())
    if chart_type == 'pie':
        plt.pie(counts, labels=labels, autopct='%1.1f%%', startangle=140)
        plt.title('Issue Type Breakdown (by Label)')
    else:
        plt.bar(labels, counts)
        plt.title('Issue Type Breakdown (by Label)')
        plt.ylabel('Count')
        plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output)

# Utility functions for GitHub API interaction and charting
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
