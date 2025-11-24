import click
import utils
from datetime import datetime, timedelta


@click.group()
def main():
        """
        GitHub Reports CLI: Generate project management charts from GitHub data.

        Available commands:
            burndown                Generate a burndown chart from issues
            commit-summary          Generate a weekly commit count summary per user
            issue-type-breakdown    Generate an issue type breakdown chart (by label)
            pr-activity-timeline   Generate a PR activity timeline chart (opened/closed/merged per week)
            issue-resolution-time   Generate a chart of time taken to close issues (histogram/boxplot)
            # More commands coming soon...
        """
        pass


@main.command()
@click.option('--repo', required=True, help='GitHub repository in the form owner/repo')
@click.option('--token', required=True, help='GitHub personal access token')
@click.option('--output', default='pr_activity_timeline.png', help='Output file for the chart')
def pr_activity_timeline(repo, token, output):
    """Generate a PR activity timeline chart (opened/closed/merged per week)."""
    try:
        repos = [r.strip() for r in repo.split(",")]
        repo_name = ", ".join(repos)
        click.echo(f"Fetching pull requests for {repo_name}...")
        prs = utils.fetch_pull_requests_multi(repos, token)
        click.echo(f"Processing PR activity timeline data...")
        week_list, opened_counts, closed_counts, merged_counts = utils.pr_activity_timeline_data(prs)
        click.echo(f"Plotting PR activity timeline chart to {output}...")
        utils.plot_pr_activity_timeline(week_list, opened_counts, closed_counts, merged_counts, output, repo_name=repo_name)
        click.echo("PR activity timeline chart generated.")
    except RuntimeError as e:
        click.echo(f"Error: {e}")


@main.command()
@click.option('--repo', required=True, help='GitHub repository in the form owner/repo')
@click.option('--token', required=True, help='GitHub personal access token')
@click.option('--output', default='issue_resolution_time.png', help='Output file for the chart')
@click.option('--chart-type', type=click.Choice(['hist', 'box']), default='hist', help='Chart type: hist or box')
def issue_resolution_time(repo, token, output, chart_type):
    """Generate an issue resolution time chart (histogram/boxplot of time to close issues)."""
    try:
        repos = [r.strip() for r in repo.split(",")]
        repo_name = ", ".join(repos)
        click.echo(f"Fetching issues for {repo_name}...")
        issues = utils.fetch_all_issues_multi(repos, token)
        click.echo(f"Processing issue resolution time data...")
        times = utils.issue_resolution_time_data(issues)
        click.echo(f"Plotting issue resolution time chart to {output}...")
        utils.plot_issue_resolution_time(times, output, chart_type, repo_name=repo_name)
        click.echo("Issue resolution time chart generated.")
    except RuntimeError as e:
        click.echo(f"Error: {e}")


@main.command()
@click.option('--repo', required=True, help='GitHub repository in the form owner/repo')
@click.option('--token', required=True, help='GitHub personal access token')
@click.option('--output', default='issue_type_breakdown.png', help='Output file for the chart')
@click.option('--chart-type', type=click.Choice(['pie', 'bar']), default='pie', help='Chart type: pie or bar')
def issue_type_breakdown(repo, token, output, chart_type):
    """Generate an issue type breakdown chart (by label)."""
    try:
        repos = [r.strip() for r in repo.split(",")]
        repo_name = ", ".join(repos)
        click.echo(f"Fetching issues for {repo_name}...")
        issues = utils.fetch_all_issues_multi(repos, token)
        click.echo(f"Processing issue type breakdown data...")
        counter = utils.issue_type_breakdown_data(issues)
        click.echo(f"Plotting issue type breakdown chart to {output}...")
        utils.plot_issue_type_breakdown(counter, output, chart_type, repo_name=repo_name)
        click.echo("Issue type breakdown chart generated.")
    except RuntimeError as e:
        click.echo(f"Error: {e}")


@main.command()
@click.option('--repo', required=True, help='GitHub repository in the form owner/repo')
@click.option('--token', required=True, help='GitHub personal access token')
@click.option('--output', default='burndown.png', help='Output file for the burndown chart')
def burndown(repo, token, output):
    """Generate a burndown chart from issues."""
    try:
        repos = [r.strip() for r in repo.split(",")]
        repo_name = ", ".join(repos)
        click.echo(f"Fetching issues for {repo_name}...")
        issues = utils.fetch_all_issues_multi(repos, token)
        click.echo(f"Processing burndown data...")
        date_range, open_counts, closed_counts = utils.burndown_data_from_issues(issues)
        click.echo(f"Plotting burndown chart to {output}...")
        utils.plot_burndown(date_range, open_counts, closed_counts, output, repo_name=repo_name)
        click.echo("Burndown chart generated.")
    except RuntimeError as e:
        click.echo(f"Error: {e}")

@main.command()
@click.option('--repo', required=True, help='GitHub repository in the form owner/repo')
@click.option('--token', required=True, help='GitHub personal access token')
@click.option('--months', default=3, help='Number of months to summarize')
@click.option('--output', default='commits.png', help='Output file for the commit summary chart')
def commit_summary(repo, token, months, output):
    """Generate a commit count summary per user."""
    try:
        repos = [r.strip() for r in repo.split(",")]
        repo_name = ", ".join(repos)
        click.echo(f"Fetching commits for {repo_name} over last {months} months...")
        since = datetime.utcnow() - timedelta(days=months*30)
        commits = utils.fetch_commits_multi(repos, token, since)
        click.echo(f"Processing weekly commit summary data...")
        user_week_counts, week_labels = utils.commit_summary_weekly_data(commits)
        click.echo(f"Plotting weekly commit summary chart to {output}...")
        utils.plot_commit_summary_weekly(user_week_counts, week_labels, output, repo_name=repo_name)
        click.echo("Weekly commit summary chart generated.")
    except RuntimeError as e:
        click.echo(f"Error: {e}")

if __name__ == '__main__':
    main()
