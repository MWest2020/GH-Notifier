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
    # Specify the relative path to repo_config.yaml from notify.py
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../repo_config.yaml')

    with open(config_path, 'r') as file:
        repo_config = yaml.safe_load(file)
    for repo_info in repo_config['repositories']:
        issues = get_new_issues(repo_info['owner'], repo_info['repo'])
        notify_slack(issues, repo_info)

if __name__ == '__main__':
    main()
