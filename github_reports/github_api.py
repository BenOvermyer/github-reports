from cache_utils import load_cache, save_cache
import requests


def fetch_all_issues(repo, token):
    """Fetch all issues (open and closed) from a GitHub repo."""
    # Use repo and token as cache key (token is sensitive, but needed for private repos)
    cache_key = f"fetch_all_issues::{repo}::{token}"
    cached = load_cache(cache_key)
    if cached is not None:
        return cached
    issues = []
    page = 1
    while True:
        url = f'https://api.github.com/repos/{repo}/issues'
        params = {'state': 'all', 'per_page': 100, 'page': page}
        batch = github_api_get(url, token, params)
        if not batch:
            break
        # Exclude pull requests (they have a 'pull_request' key)
        filtered_batch = [issue for issue in batch if 'pull_request' not in issue]
        issues.extend(filtered_batch)
        page += 1
    save_cache(cache_key, issues)
    return issues


def fetch_all_issues_multi(repos, token):
    """Fetch and aggregate issues from multiple repositories."""
    all_issues = []
    for repo in repos:
        all_issues.extend(fetch_all_issues(repo.strip(), token))
    return all_issues


def fetch_commits(repo, token, since):
    """Fetch commits since a given date from a GitHub repo."""
    cache_key = f"fetch_commits::{repo}::{token}::{since.isoformat()}"
    cached = load_cache(cache_key)
    if cached is not None:
        return cached
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
    save_cache(cache_key, commits)
    return commits


def fetch_commits_multi(repos, token, since):
    """Fetch and aggregate commits from multiple repositories since a given date."""
    all_commits = []
    for repo in repos:
        all_commits.extend(fetch_commits(repo.strip(), token, since))
    return all_commits


def fetch_pull_requests(repo, token, state='all'):
    """Fetch all pull requests from a GitHub repo."""
    cache_key = f"fetch_pull_requests::{repo}::{token}::{state}"
    cached = load_cache(cache_key)
    if cached is not None:
        return cached
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
    save_cache(cache_key, prs)
    return prs


def fetch_pull_requests_multi(repos, token, state='all'):
    """Fetch and aggregate pull requests from multiple repositories."""
    all_prs = []
    for repo in repos:
        all_prs.extend(fetch_pull_requests(repo.strip(), token, state))
    return all_prs


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
