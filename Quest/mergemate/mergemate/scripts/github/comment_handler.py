import os
import json

from mergemate.llmware.reviewer_agent import ReviewerAgent
from mergemate.providers.github import GithubProvider



class CommandHandler:
    def __init__(self):
        self.gh = GithubProvider()
        self.agent = ReviewerAgent()
        with open(os.getenv('GITHUB_EVENT_PATH')) as event_file:
            self.event_data = json.load(event_file)
        
    def run(self):
        comment_body = self.gh.get_comment_body(self.event_data)
        diff = self.gh.get_diff_for_comment(self.event_data)
        status = self.gh.get_status(self.event_data)
        comment_history = self.gh.get_comments(self.event_data)
        pr_title = self.event_data['issue']['title']
        pr_description = self.event_data['issue']['body']
        response = self.agent.create_comment(comment_body, diff, status, comment_history, pr_title, pr_description)
        self.gh.create_comment(response, self.event_data)


if __name__ == "__main__":
    CommandHandler().run()