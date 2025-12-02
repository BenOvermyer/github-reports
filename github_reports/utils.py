import matplotlib.pyplot as plt
import textwrap
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


def plot_issue_resolution_time(times, output, chart_type='hist', repo_name=None): 
    plt.figure(figsize=(10,6))
    title = 'Issue Resolution Time Histogram' if chart_type == 'hist' else 'Issue Resolution Time Boxplot'
    if repo_name:
        title += f' - {repo_name}'
    title = "\n".join(textwrap.wrap(title, width=60))
    
    if chart_type == 'hist':
        plt.hist(times, bins=20, color='skyblue', edgecolor='black')
        plt.title(title)
        plt.xlabel('Days to Close')
        plt.ylabel('Number of Issues')
    else:
        plt.boxplot(times, vert=False)
        plt.title(title)
        plt.xlabel('Days to Close')
    plt.tight_layout()
    plt.savefig(output)


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


def plot_pr_activity_timeline(week_list, opened_counts, closed_counts, merged_counts, output, repo_name=None):
    plt.figure(figsize=(12,7))
    plt.plot(week_list, opened_counts, label='Opened PRs')
    plt.plot(week_list, closed_counts, label='Closed PRs')
    plt.plot(week_list, merged_counts, label='Merged PRs')
    plt.xlabel('Week')
    plt.ylabel('Count')
    title = 'PR Activity Timeline'
    if repo_name:
        title += f' - {repo_name}'
    plt.title("\n".join(textwrap.wrap(title, width=60)))
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


def plot_issue_type_breakdown(counter, output, chart_type='pie', repo_name=None):
    plt.figure(figsize=(8,8))
    labels = list(counter.keys())
    counts = list(counter.values())
    title = 'Issue Type Breakdown (by Label)'
    if repo_name:
        title += f' - {repo_name}'
    title = "\n".join(textwrap.wrap(title, width=60))

    if chart_type == 'pie':
        plt.pie(counts, labels=labels, autopct='%1.1f%%', startangle=140)
        plt.title(title)
    else:
        plt.bar(labels, counts)
        plt.title(title)
        plt.ylabel('Count')
        plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output)


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
    total_issues = len(issues)
    closed_so_far = 0
    for d in date_range:
        closed_on_day = sum(1 for i in issues if i.get('closed_at') and datetime.strptime(i['closed_at'], '%Y-%m-%dT%H:%M:%SZ').date() == d.date())
        closed_so_far += closed_on_day
        open_count = total_issues - closed_so_far  # Remaining open issues
        open_counts.append(open_count)
        closed_counts.append(closed_on_day)
    return date_range, open_counts, closed_counts


def plot_burndown(date_range, open_counts, closed_counts, output, repo_name=None):
    plt.figure(figsize=(10,6))
    # Actual work line: remaining open issues per day
    plt.plot(date_range, open_counts, label='Actual Work (Remaining Open Issues)', color='blue')

    # Ideal line: straight line from initial total to zero
    initial_total = open_counts[0] if open_counts else 0
    ideal_line = [initial_total - (initial_total * i / (len(date_range)-1)) for i in range(len(date_range))] if len(date_range) > 1 else [initial_total]
    plt.plot(date_range, ideal_line, label='Ideal (To Zero)', color='red', linestyle='dotted')

    plt.xlabel('Date')
    plt.ylabel('Remaining Issues')
    title = 'Burndown Chart'
    if repo_name:
        title += f' - {repo_name}'
    plt.title("\n".join(textwrap.wrap(title, width=60)))
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


def plot_commit_summary_weekly(user_week_counts, week_labels, output, repo_name=None):
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
    title = 'Weekly Commit Summary per User'
    if repo_name:
        title += f' - {repo_name}'
    plt.title("\n".join(textwrap.wrap(title, width=60)))
    plt.xticks(x, week_labels, rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output)
