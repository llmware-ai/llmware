''' This example demonstrates connecting to the following LLMs and doing basic completions
      1. OpenAi - gpt-4
      2. Google - test-bison@001
      3. Anthropic - claude-instant-v1
      3. AI21 - 2-grande-instruct

    Notes: 
      1. API Keys for the given LLMs are assumed to be set as environemnt variables below
      2. Google API Keys are handled differently from others.  The key needs to be the full text of your .json credential file.  
         This can be set as follows:
            export GOOGLE_API_KEY=$(cat credentials.json)
'''

import os
from llmware.prompts import Prompt

# Update these values with your own API Keys, either by setting env vars or editing them directly here:
openai_api_key    = os.environ.get("OPENAI_API_KEY","")
anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY","")
ai21_api_key      = os.environ.get("AI21_API_KEY","")
google_api_key    = os.environ.get("GOOGLE_API_KEY","") 

def prompt_llm_and_print_response(query, vendor_name, llm_name, llm_api_key):
  # Create an instance of the Prompt class using the given LLM
  prompter = Prompt(llm_name=llm_name, llm_api_key=llm_api_key)
  # Perform an LLM completion with the given query
  response = prompter.completion(query)
  # The resononse is a dict that contains "llm_response" which may contain some whitespace, so we'll strip() it
  answer = response["llm_response"].strip()
  # Print
  print (f"\n > {vendor_name}:{llm_name}\nAnswer: {answer}")

query = "what is artificial intelligence?"
print (f"\n > Prompting LLMs with: '{query}'")
prompt_llm_and_print_response(query, "OpenAI", "gpt-4", openai_api_key)
prompt_llm_and_print_response(query, "Google", "text-bison@001", os.environ["GOOGLE_API_KEY"])
prompt_llm_and_print_response(query, "Anthropic", "claude-instant-v1", anthropic_api_key)
prompt_llm_and_print_response(query, "AI21", "j2-grande-instruct", ai21_api_key)


# **********************************************************************************************************
# ************************************** SAMPLE OUTPUT *****************************************************
# **********************************************************************************************************
'''
> python examples/working_with_llms.py

 > Prompting LLMs with: 'what is artificial intelligence?'
 
> OpenAI:gpt-4
Answer: Artificial Intelligence (AI) refers to the simulation of human intelligence processes by machines, especially computer systems. These processes can include activities such as learning (the acquisition of information and rules for using the information), reasoning (using the rules to reach approximate or definite conclusions), and self-correction. Essentially, it involves creating systems that behave intelligently, making complex decisions, solving problems, understanding language, recognizing patterns and learning from experience.

There are two types of AI: narrow AI, which is designed to

> Google:text-bison@001
Answer: Artificial Intelligence (AI) is a branch of computer science that deals with the creation of intelligent agents, which are systems that can reason, learn, and act autonomously. AI research has been highly successful in developing effective techniques for solving a wide range of problems, including natural language processing, computer vision, and robotics. However, AI is still in its early stages of development, and there are many challenges that need to be overcome before AI systems can achieve human-level intelligence.

One of the main challenges in AI is the problem of representation. AI systems need to be able to represent the world in a way that they can understand and reason

> Anthropic:claude-instant-v1
Answer: Here is a brief overview of artificial intelligence:

- Artificial intelligence (AI) refers to intelligence demonstrated by machines, as opposed to the natural intelligence displayed by humans and animals. 

- AI technologies include machine learning, deep learning, natural language processing, expert systems, robotics, and computer vision. These technologies allow machines to sense, comprehend, act, and learn from experiences.

- Machine learning is a core driver of AI. It allows computer systems to automatically learn and improve

> AI21:j2-grande-instruct
Answer: Artificial intelligence (AI) is a field of computer science that aims to create intelligent machines that can perform tasks normally requiring human intelligence. The goal of AI is to develop systems that can understand and reason about the world around them, and that can solve problems and make decisions in the same way that humans do.

There are several different approaches to AI, including rule-based systems, expert systems, machine learning, and natural language processing. Rule-based systems use hard-coded rules to make decisions, while expert systems use a combination of rules and knowledge from a human expert. Machine learning systems use algorithms to learn from data and make predictions, and natural language processing systems use algorithms to process and understand human language.'''






