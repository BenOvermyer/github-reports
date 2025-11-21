import click
import utils
from datetime import datetime, timedelta

@click.group()
def main():
    """GitHub Reports CLI: Generate project management charts from GitHub data."""
    pass

@main.command()
@click.option('--repo', required=True, help='GitHub repository in the form owner/repo')
@click.option('--token', required=True, help='GitHub personal access token')
@click.option('--output', default='burndown.png', help='Output file for the burndown chart')
def burndown(repo, token, output):
    """Generate a burndown chart from issues."""
    try:
        click.echo(f"Fetching issues for {repo}...")
        issues = utils.fetch_all_issues(repo, token)
        click.echo(f"Processing burndown data...")
        date_range, open_counts, closed_counts = utils.burndown_data_from_issues(issues)
        click.echo(f"Plotting burndown chart to {output}...")
        utils.plot_burndown(date_range, open_counts, closed_counts, output)
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
        click.echo(f"Fetching commits for {repo} over last {months} months...")
        since = datetime.utcnow() - timedelta(days=months*30)
        commits = utils.fetch_commits(repo, token, since)
        click.echo(f"Processing weekly commit summary data...")
        user_week_counts, week_labels = utils.commit_summary_weekly_data(commits)
        click.echo(f"Plotting weekly commit summary chart to {output}...")
        utils.plot_commit_summary_weekly(user_week_counts, week_labels, output)
        click.echo("Weekly commit summary chart generated.")
    except RuntimeError as e:
        click.echo(f"Error: {e}")

if __name__ == '__main__':
    main()
