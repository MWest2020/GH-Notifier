import requests
import yaml
import os
import logging
import pytz
from datetime import datetime, timedelta
from dateutil import parser

# Configure logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

def get_new_issues(owner, repo, cutoff_time):
    repo_url = f'https://api.github.com/repos/{owner}/{repo}/issues'
    response = requests.get(repo_url, params={'since': cutoff_time.isoformat()})
    response.raise_for_status()
    all_issues = response.json()
    
    # Filter out issues created within the last 10 minutes and that are not pull requests
    new_issues = [
        issue for issue in all_issues
        if parser.parse(issue['created_at']) > cutoff_time and 'pull_request' not in issue
    ]
    logging.debug(f'New issues for {owner}/{repo}: {new_issues}')
    return new_issues

def filter_issues(issues, exclude_words):
    # Exclude issues whose title contains any of the exclude words (case insensitive)
    return [
        issue for issue in issues
        if not any(word.lower() in issue["title"].lower() for word in exclude_words)
    ]

def notify_slack(issues, repo_info):
    webhook_url = os.environ.get('SLACK_WEBHOOK_URL')
    if webhook_url is None:
        logging.error('SLACK_WEBHOOK_URL environment variable is not set')
        return

    headers = {'Content-Type': 'application/json'}

    for issue in issues:
        message = f'New issue in {repo_info["owner"]}/{repo_info["repo"]}: {issue["title"]}\n{issue["html_url"]}'
        payload = {'text': message}
        response = None
        try:
            response = requests.post(webhook_url, json=payload, headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logging.error(f'Failed to send notification to Slack: {e}')
            if response is not None:
                logging.error(f'Slack response: {response.status_code} - {response.text}')

def main():
    with open('repo_config.yaml', 'r') as file:
        config = yaml.safe_load(file)
    
    exclude_words = config.get('exclude_words', [])
    current_time = datetime.utcnow().replace(tzinfo=pytz.UTC)
    cutoff_time = current_time - timedelta(minutes=10)
    logging.debug(f'Cutoff time for new issues: {cutoff_time.isoformat()}')
    
    for repo_info in config['repositories']:
        issues = get_new_issues(repo_info['owner'], repo_info['repo'], cutoff_time)
        issues = filter_issues(issues, exclude_words)
        notify_slack(issues, repo_info)

if __name__ == '__main__':
    main()
