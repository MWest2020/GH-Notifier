import requests
import yaml
import os
import logging
from datetime import datetime, timedelta
from dateutil import parser

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def get_new_issues(owner, repo):
    # Get the current time in UTC
    current_time = datetime.utcnow()
    # Calculate the cutoff time for new issues (current time - 10 minutes)
    cutoff_time = current_time - timedelta(minutes=10)
    
    logging.debug(f'Cutoff time for new issues: {cutoff_time.isoformat()}Z')  # Log the cutoff time
    
    repo_url = f'https://api.github.com/repos/{owner}/{repo}/issues'
    response = requests.get(repo_url)
    response.raise_for_status()
    all_issues = response.json()
    
    # Filter out the issues created within the last 10 minutes
    new_issues = [issue for issue in all_issues if parser.parse(issue['created_at']) > cutoff_time]
    logging.debug(f'New issues for {owner}/{repo}: {new_issues}')  # Log the new issues
    return new_issues

def notify_slack(issues, repo_info):
    webhook_url = os.environ.get('SLACK_WEBHOOK_URL')
    for issue in issues:
        message = f'New issue in {repo_info["owner"]}/{repo_info["repo"]}: {issue["title"]}\n{issue["html_url"]}'
        payload = {'text': message}
        response = requests.post(webhook_url, json=payload)
        logging.debug(f'Slack response: {response.text}')  # Log the Slack response
        response.raise_for_status()

def main():
    with open('repo_config.yaml', 'r') as file:
        repo_config = yaml.safe_load(file)
    
    for repo_info in repo_config['repositories']:
        issues = get_new_issues(repo_info['owner'], repo_info['repo'])
        notify_slack(issues, repo_info)

if __name__ == '__main__':
    main()
