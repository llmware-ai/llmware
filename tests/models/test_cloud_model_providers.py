""" Basic connectivity tests to cloud API providers. """

import os
from llmware.prompts import Prompt

openai_api_key    = os.environ.get("OPENAI_API_KEY","")
anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY","")
ai21_api_key      = os.environ.get("AI21_API_KEY","")
google_api_key    = os.environ.get("GOOGLE_API_KEY","") 
cohere_api_key    = os.environ.get("COHERE_API_KEY", "")


# Simple test to make sure we are reaching OpenAI
def test_openai():
    prompter = Prompt(llm_name="gpt-4", llm_api_key=openai_api_key)
    response = prompter.completion("what is artificial intelligence?")
    llm_response = response["llm_response"]
    assert 'artificial' in llm_response.lower()


# Simple test to make sure we are reaching Google
def test_google():
    prompter = Prompt(llm_name="text-bison@001", llm_api_key=google_api_key)
    response = prompter.completion("what is artificial intelligence?")
    llm_response = response["llm_response"]
    assert 'artificial' in llm_response.lower()


# Simple test to make sure we are reaching Anthropic
def test_anthropic():
    prompter = Prompt(llm_name="claude-instant-v1", llm_api_key=anthropic_api_key)
    response = prompter.completion("what is artificial intelligence?")
    llm_response = response["llm_response"]
    assert 'artificial' in llm_response.lower()


# Simple test to make sure we are reaching AI21
def test_ai21():
    prompter = Prompt(llm_name="j2-grande-instruct", llm_api_key=ai21_api_key)
    response = prompter.completion("what is artificial intelligence?")
    llm_response = response["llm_response"]
    assert 'artificial' in llm_response.lower()
