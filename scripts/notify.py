import requests
import yaml
import os
import json

def get_new_issues(owner, repo, last_issue_id, open_issues):
    repo_url = f'https://api.github.com/repos/{owner}/{repo}/issues'
    response = requests.get(repo_url)
    response.raise_for_status()
    issues = response.json()
    
    new_issues = [issue for issue in issues if issue['number'] > last_issue_id]
    closed_issues = [issue for issue in open_issues if issue not in issues]
    
    # Update last_issue_id and open_issues
    if new_issues:
        last_issue_id = max(issue['number'] for issue in new_issues)
    open_issues = [issue['number'] for issue in issues if issue['state'] == 'open']
    
    return new_issues, closed_issues, last_issue_id, open_issues

def notify_slack(issues, repo_info, issue_type):
    webhook_url = os.environ.get('SLACK_WEBHOOK_URL')
    for issue in issues:
        message = f'{issue_type} in {repo_info["owner"]}/{repo_info["repo"]}: {issue["title"]}\n{issue["html_url"]}'
        payload = {'text': message}
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()

def main():
    # Specify the relative path to repo_config.yaml from notify.py
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../repo_config.yaml')

    with open(config_path, 'r') as file:
        repo_config = yaml.safe_load(file)
    
    # Read the last issue ID and open issues list from files, with defaults for the first run
    if os.path.exists('last_issue_id.txt'):
        with open('last_issue_id.txt', 'r') as file:
            last_issue_id = int(file.read().strip())
    else:
        last_issue_id = 0
    
    if os.path.exists('open_issues.txt'):
        with open('open_issues.txt', 'r') as file:
            open_issues = json.load(file)
    else:
        open_issues = []
    
    for repo_info in repo_config['repositories']:
        new_issues, closed_issues, last_issue_id, open_issues = get_new_issues(
            repo_info['owner'], repo_info['repo'], last_issue_id, open_issues)
        notify_slack(new_issues, repo_info, 'New issue')
        notify_slack(closed_issues, repo_info, 'Closed issue')
    
    # Write the updated last issue ID and open issues list to files
    with open('last_issue_id.txt', 'w') as file:
        file.write(str(last_issue_id))
    with open('open_issues.txt', 'w') as file:
        json.dump(open_issues, file)

if __name__ == '__main__':
    main()
