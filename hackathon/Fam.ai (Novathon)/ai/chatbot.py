from typing import Union
from llmware.models import ModelCatalog

context = '''User: Hi, can you help me keep track of the projects I'm working on?
Assistant: Of course! Let me know about your projects, and I’ll create a record for them.

User: Great! I’m currently working on a decentralized voting system using blockchain and smart contracts.
Assistant: Got it. Could you provide more details, like the tech stack or any challenges you’re facing?

User: Sure! The project is called VoteChain. I’m using Ethereum for smart contracts with Solidity, Python for the backend using FastAPI, and a React.js frontend. The challenge is ensuring voter privacy while maintaining transparency.
Assistant: Noted! I’ll add VoteChain to your project list, including the tech stack and the voter privacy challenge.

User: Also, I’m collaborating with a friend named Divya on this. She’s handling the UI/UX design and is really creative.
Assistant: Nice! I’ll note that Divya is collaborating with you on VoteChain and is responsible for UI/UX design. Anything else?

User: No, that’s all for now. Thanks!
Assistant: You’re welcome! Let me summarize for you:

Project Name: VoteChain
Description: A decentralized voting system using blockchain and smart contracts.
Tech Stack: Ethereum (Solidity), Python (FastAPI), React.js.
Key Challenge: Ensuring voter privacy while maintaining transparency.
Collaboration: Divya (UI/UX design).
Does this look good to you?

User: Perfect!'''

chat_bot = ModelCatalog().load_model("bartowski/Meta-Llama-3-8B-Instruct-GGUF")
def get_response(prompt:str, context:Union[None, str]=""):
    response = chat_bot.inference(prompt, add_context=context)
    return response

print(get_response(prompt="What do you know about the user ?", context=context))





