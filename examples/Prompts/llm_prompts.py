
""" This example demonstrates:
      1. Prompting LLMs with different kinds of sources/context
      2. The Prompt Catalog and the use different prompt styles

      Note: This example uses OpenAI's gpt-4 LLM.
"""

import os
from llmware.prompts import Prompt
from llmware.setup import Setup
from llmware.models import PromptCatalog

# Update this value with your own API Key, either by setting the env var or editing it directly here:
openai_api_key = os.environ.get("OPENAI_API_KEY","")

# llmware provides many out of the box prompt instructions such as yes_no, number_or_none, summarize_with_bullets,etc
def print_all_prompt_instructions():
    print (f"\n > ALL AVAILABLE PROMPT INSTRUCTIONS")
    for prompt in PromptCatalog().get_all_prompts():
        print (" - " + prompt["prompt_name"])

# With the provided context submit the given prompt to the LLM
def simple_prompt_with_context_string(prompt, context, llm_name, api_key):
    print (f"\n > SIMPLE PROMPT WITH CONTEXT STRING")
    prompter = Prompt(llm_name=llm_name, llm_api_key=api_key)
    response = prompter.prompt_main(prompt=prompt, context=context)["llm_response"]
    print (f"- Context: {context}\n- Prompt: {prompt}\n- LLM Response:\n{response}")

# Use an llmware prompt_instruction to submit the given prompt and prompt_instruction to the LLM
def prompt_with_prompt_instruction(prompt, context, prompt_instruction, llm_name, api_key):
    print (f"\n > PROMPT WITH CONTEXT USING '{prompt_instruction}' PROMPT INSTRUCTION")
    prompter = Prompt(llm_name=llm_name, llm_api_key=api_key)
    response = prompter.prompt_from_catalog(prompt=prompt, context=context, prompt_name=prompt_instruction)["llm_response"]
    print (f"- Context: {context}\n- Prompt: {prompt}\n- LLM Response:\n{response}")


# In some cases you may want to add additional configuraton.
def prompt_with_inference_config(prompt, context, prompt_instruction, inference_config, llm_name, api_key):
    print (f"\n > PROMPT WITH CONTEXT USING '{prompt_instruction}' PROMPT INSTRUCTION")
    prompter = Prompt(llm_name=llm_name, llm_api_key=api_key)
    response = prompter.prompt_main(prompt=prompt, context=context, prompt_name=prompt_instruction, 
                                    inference_dict=inference_config)["llm_response"]
    print (f"- Context: {context}\n- Prompt: {prompt}\n- LLM Response:\n{response}")

# If the context you need to pass to an LLM is contained in Wikipedia you can easily add it as a source
def prompt_with_wiki_source(prompt, wiki_topic, prompt_instruction, llm_name, api_key):
    print (f"\n > PROMPT WITH CONTEXT FROM WIKIPEDIA USING '{prompt_instruction}' PROMPT INSTRUCTION")
    prompter = Prompt(llm_name=llm_name, llm_api_key=api_key)
    prompter.add_source_wikipedia(wiki_topic, article_count=1)
    response = prompter.prompt_with_source(prompt=prompt, prompt_name=prompt_instruction)[0]["llm_response"]
    print (f"- Context: Wikepedia article(s) for '{wiki_topic}'\n- Prompt: {prompt}\n- LLM Response:\n{response}")

# If the context you need to pass is in local files, you can easily add then as sources
def prompt_with_local_file_sources(prompt, local_folder, local_files, prompt_instruction, llm_name, api_key):
    print (f"\n > PROMPT WITH CONTEXT FROM LOCAL FILE USING '{prompt_instruction}' PROMPT INSTRUCTION")
    prompter = Prompt(llm_name=llm_name, llm_api_key=api_key)
    for local_file in local_files:
        prompter.add_source_document(local_folder, local_file)
    response = prompter.prompt_with_source(prompt=prompt, prompt_name=prompt_instruction)[0]["llm_response"]
    print (f"- Context: {local_files}\n- Prompt: {prompt}\n- LLM Response:\n{response}")

print_all_prompt_instructions()

simple_prompt_with_context_string( prompt = "What is my 3rd favorite type of food?",
                                   context = "My favorite foods are Sushi, Italian and Greek",
                                   llm_name = "gpt-4",
                                   api_key = openai_api_key
                                 )

prompt_with_prompt_instruction( prompt = "How old is my oldest sibling?",
                                context = "My brother is 20 years old and my sister is 1.5 times older",
                                prompt_instruction = "number_or_none",
                                llm_name = "gpt-4",
                                api_key = openai_api_key
                              )

prompt_with_inference_config( prompt = "Why is it difficult?",
                              context = "I am interested in building rockets",
                              prompt_instruction = "explain_child",
                              inference_config = {"temperature": 0.8, "llm_max_output_len": 1000, "max_tokens": 1000},
                              llm_name = "gpt-4",
                              api_key = openai_api_key)

prompt_with_wiki_source( prompt = "Was Barack Obama the Prime Minister of Canada?",
                         wiki_topic = "Barack Obama",
                         prompt_instruction = "yes_no",
                         llm_name = "gpt-4",
                         api_key = openai_api_key)

prompt_with_local_file_sources( prompt = "What was the effective date of this agreement?",
                                local_folder = os.path.join(Setup().load_sample_files(), "SmallLibrary"),
                                local_files = ['Gaia EXECUTIVE EMPLOYMENT AGREEMENT.pdf'],
                                prompt_instruction = "just_the_facts",
                                llm_name = "gpt-4",
                                api_key = openai_api_key)
