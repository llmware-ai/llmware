from llmware.prompts import Prompt
import os
from mergemate.prompts import answer_comment, create_review, explain_code

class ReviewerAgent:
    def __init__(self):
        self.prompt = Prompt().load_model('gpt-3.5-turbo', api_key=os.environ['OPENAI_API_KEY'])
        self.help_commands = {
            '/help': 'List all available commands.',
            '/explain': 'Explain the current code context',
            '/status': 'Get the current status of the PR.',
            '/ask': 'Ask a question about the the PR.'
        }

        self.review_prompt = create_review.PROMPT
        self.explain_code_prompt = explain_code.PROMPT
        self.answer_comment_prompt = answer_comment.PROMPT
        
    def return_response(self, response):
        header = ":sparkles: **MergeMate Bot** :sparkles:\n\n"
        footer = "\n\n:bulb: *Use `/help` to list all available commands.* :bulb:"
        return header + response + footer

    def run(self, prompt, context=None):
        response = self.prompt.prompt_main(
            prompt=prompt,
            context=context
        )
        return self.return_response(response['llm_response'])
    
    def create_comment(self, comment, diff, status, comment_history, pr_title, pr_description):
        if comment.startswith('/'):
            command = comment.split(' ')[0]
            if command == '/help':
                return self.return_response('\n'.join([f"`{k}`: {v}" for k, v in self.help_commands.items()]))
            elif command == '/explain':
                return self.explain_code(diff)
            elif command == '/status':
                return self.give_status(status)
            elif command == '/ask':
                return self.ask(comment, diff, status, comment_history, pr_title, pr_description)    
            else:
                return self.return_response("Command not recognized. Use `/help` to see available commands.")
        else:
            return "not a command"

    def create_review(self, title, description, diff):
        print("Creating review...")
        prompt = self.review_prompt.format(
            title=title,
            description=description,
            file_diff=diff
        )
        return self.run(prompt, context=diff)

    def explain_code(self, diff):
        print("Explaining code...")
        prompt = self.explain_code_prompt.format(
            file_diff=diff
        )
        return self.run(prompt, context=diff)
    
    def give_status(self, status):
        return self.return_response(f"The current status of the PR is: {status}")
    
    def ask(self, comment, diff, status, comment_history, pr_title, pr_description):
        print("Asking question...")
        prompt = self.answer_comment_prompt.format(
            comment=comment,
            file_diff=diff,
            status=status,
            comment_history=comment_history,
            title=pr_title,
            description=pr_description
        )
        
        context = diff
        return self.run(prompt, context)
