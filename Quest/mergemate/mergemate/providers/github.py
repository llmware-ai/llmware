from github import Github
import os
import requests


class GithubProvider:
    def __init__(self):
        self.g = Github(os.getenv('GITHUB_TOKEN'))

    def get_repo(self, full_name):
        return self.g.get_repo(full_name)

    def get_issue(self, repo, number):
        return repo.get_issue(number=number)

    def get_pull(self, repo, number):
        return repo.get_pull(number=number)

    def create_comment(self, body, event_data):
        repo = self.get_repo(event_data['repository']['full_name'])
        if 'pull_request' in event_data:
            issue_number = event_data['pull_request']['number']
        else:
            issue_number = event_data['issue']['number']
        issue = self.get_issue(repo, number=issue_number)
        issue.create_comment(body)

    def get_diff(self, event_data):
        diff_url = event_data['pull_request']['diff_url']
        diff = requests.get(diff_url).text
        return diff
    
    def get_diff_for_comment(self, event_data):
        diff_url = event_data['issue']['pull_request']['diff_url']
        diff = requests.get(diff_url).text
        return diff
    
    def get_status(self, event_data):
        return event_data['issue']['state']
    
    def get_comment_body(self, event_data):
        return event_data['comment']['body'].strip().lower()
    
    def get_comments(self, event_data):
        repo = self.get_repo(event_data['repository']['full_name'])
        issue = self.get_issue(repo, number=event_data['issue']['number'])
        res_comments = issue.get_comments()
        comments = []
        for comment in res_comments:
            comments.append({
                'body': comment.body,
                'user': comment.user.login
            })
        return comments
        

    

    