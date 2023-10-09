import requests
import yaml
import os

def get_new_issues(owner, repo):
    repo_url = f'https://api.github.com/repos/{owner}/{repo}/issues'
    response = requests.get(repo_url)
    response.raise_for_status()
    return response.json()

def notify_slack(issues, repo_info):
    webhook_url = os.environ.get('SLACK_WEBHOOK_URL')
    for issue in issues:
        message = f'New issue in {repo_info["owner"]}/{repo_info["repo"]}: {issue["title"]}\n{issue["html_url"]}'
        payload = {'text': message}
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()

def main():
    # Get the path to the repository root
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Build the path to repo_config.yaml
    config_path = os.path.join(repo_root, 'repo_config.yml')

    with open(config_path, 'r') as file:
        repo_config = yaml.safe_load(file)
    for repo_info in repo_config['repositories']:
        issues = get_new_issues(repo_info['owner'], repo_info['repo'])
        notify_slack(issues, repo_info)

if __name__ == '__main__':
    main()
