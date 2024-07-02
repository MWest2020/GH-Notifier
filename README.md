# GitHub to Slack Notifier

This repository contains a setup to notify a Slack channel about new issues created in specified GitHub repositories. The notification system is built using a Python script which is executed through a GitHub Actions workflow. Keep in  mind that it will fail after 90 days of inactivity (that's a GitHub policy)

## Repository Structure

- `scripts/notify.py`: The main script that queries the GitHub API to find new issues and sends notifications to Slack.
- `repo_config.yaml`: A configuration file listing the repositories to be monitored.
- `.github/workflows/notify.yaml`: The GitHub Actions workflow file to execute the script.

## Setup

1. **Slack Webhook:**
   Create a new Slack app and activate incoming webhooks.
   Create a new webhook and copy the URL.
   Add the webhook URL as a secret in your GitHub repository under the name `SLACK_WEBHOOK_URL`.

2. **Repository Configuration:**
   Update the `repo_config.yaml` file with the owner and repository name details of the repositories you want to monitor.
   
   ```yaml
   repositories:
     - owner: Username
       repo: RepoName
     # ... add more repositories as needed
3. **Script and Workflow:**
Make sure the scripts/notify.py, repo_config.yaml, and .github/workflows/notify.yaml files are present in your repository.
The workflow is set to run every 10 minutes, you can adjust the schedule in the notify.yaml file if needed.

## Workflow File
The notify.yaml workflow is configured to run every 10 minutes and will execute the notify.py script to check for new issues in the specified repositories.

```yaml
name: Notify Slack of New Issues

on:
  schedule:
    - cron: '*/10 * * * *'  # Run every 10 minutes

jobs:
  notify:
    runs-on: ubuntu-latest
    steps:
      - name: Check out code
        uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.8
      
      - name: Install dependencies
        run: pip install requests python-dateutil pytz
      
      - name: Run script
        run: python scripts/notify.py
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```
The secret is the webhook from the Slack app, and stored in GitHub environmentals / secrets.


## Python Script

The `scripts/notify.py` script serves as the core of this notification system. It reads the repository configuration from `repo_config.yaml`, checks the specified GitHub repositories for newly created issues within the last 10 minutes, and sends a notification to a configured Slack channel for each new issue found.

Here's a high-level overview of the script's operation:

1. **Importing Necessary Libraries:**
    - `requests` for making HTTP requests to the GitHub API.
    - `yaml` for reading the repository configuration file.
    - `os` for accessing environment variables.
    - `datetime` and `dateutil.parser` for handling and parsing date-time information.

### Defining Functions:

`get_new_issues(owner, repo)`: Queries the GitHub API to retrieve issues from a specified repository that were created within the last 10 minutes.
`notify_slack(issues, repo_info)`: Sends a notification to Slack for each new issue found.
`main()`: Reads the repository configuration, checks each repository for new issues, and sends notifications to Slack.


### Executing the Script:

The script is executed by the `main()` function if it's run as the main module.
The `main()` function reads the repository configuration from `repo_config.yaml`, iterates through each repository specified, retrieves new issues, and sends notifications to Slack.
This script is executed in the GitHub Actions environment as specified in the workflow file `.github/workflows/notify.yaml`. The workflow file takes care of setting up the environment, installing the necessary dependencies via pip, and running the script.

```yaml
      - name: Install dependencies
        run: pip install requests python-dateutil pytz
```
The workflow is triggered every 10 minutes, ensuring that your Slack channel is updated with new issues from the specified GitHub repositories in a timely manner.


## Notifications

Notifications include the title of the new issue and a link to the issue on GitHub, and are sent to the Slack channel configured via the Slack webhook.

