"""This example demonstrates several leading open source chat models running in 4-bit GGUF on local laptop."""

import time
import re
from llmware.prompts import Prompt
import logging


# Run the benchmark test
def run_test(model_name: str, prompt_list: list[dict]) -> int:
    """Run the benchmark test on the specified model with the given prompts.

    Args:
        model_name (str): The name of the model to load.
        prompt_list (list[dict]): A list of prompts to test the model with.

    Returns:
        int: Status code (0 for success).
    """
    logging.basicConfig(level=logging.INFO)

    logging.info(f"Loading model '{model_name}'")
    
    try:
        prompter = Prompt().load_model(model_name)
    except Exception as e:
        logging.error(f"Failed to load model: {e}")
        return 1

    for i, entry in enumerate(prompt_list):
        start_time = time.time()
        logging.info(f"query - {i+1} - {entry['query']}")

        try:
            response = prompter.prompt_main(entry["query"])
        except Exception as e:
            logging.error(f"Error during prompting: {e}")
            continue

        # Print results
        time_taken = round(time.time() - start_time, 2)
        llm_response = re.sub("[\n\n]", "\n", response['llm_response'])
        logging.info(f"llm_response - {i+1} - {llm_response}")
        logging.info(f"time_taken - {i+1} - {time_taken}")

    return 0


if __name__ == "__main__":

    #   Example open-ended queries with no context - looking for chat model to draw on general know-how and ability
    #   to look at a problem conceptually, with focus on language understanding without specific focus on facts

    ds = [
        {"query": "I am interested in gaining an understanding of the banking industry. What topics should I research?",
         "context": "", "answer": "NO_GOLD_ANSWER"},
        {"query": "What are some tips for creating a successful business plan?", "context": "", "answer": ""},
        {"query": "What do you think about the recent news about Microsoft\u2019s GitHub acquisition?", "context": "",
         "answer": ""},
        {"query": "What are the best books to read for a class on American literature?", "context": "", "answer": ""},
        {"query" : "What is the most important thing I should know about my local school district?", "context": "", "answer": ""},
        {"query": "Can you recommend some good books for me to read?", "context": "", "answer": ""},
        {"query": "What are the differences between the four principal cloud computing service models: IaaS, PaaS, SaaS, and CaaS?",
         "context": "", "answer": ""},
        {"query": "I've heard a lot of good things about the iPhone. Should I buy one?", "context": "", "answer": ""},
        {"query": "What is the difference between a sociological and psychological approach to social problems?",
         "context": "", "answer": ""},
        {"query": "What job opportunities are available for someone with degree in chemistry?", "context": "", "answer": ""},
        {"query": "I'd like to know how to get the most out of my money in the stock market?", "context": "", "answer": ""},
        {"query": "How do I know if my computer is secure?", "context": "", "answer": ""},
        {"query": "I'm writing an essay on the importance of reading. What are some good questions to ask "
                  "in this type of essay?", "context": "", "answer": ""},
        {"query": "What is the best way for small businesses to raise capital for their operations?", "context": "", "answer": ""},
        {"query": "I want to start a blog but don't know what to write about. What should I do?", "context": "", "answer": ""},
        {"query": "What are the best ways to learn a new language?", "context": "", "answer": ""},
        {"query": "I'm having some problems with my computer. What are some of the most common computer problems"
                  " and how can I fix them?", "context": "", "answer": ""},
        {"query": "How can I improve my credit score?", "context": "", "answer": ""},
        {"query": "How can I build confidence in my ability to write articles and be a good writer?",
         "context": "", "answer": ""},
        {"query": "How do I negotiate a salary raise?", "context": "", "answer": ""},
        {"query": "What's the best way to learn how to write a good essay?", "context": "", "answer": ""},
        {"query": "I'm a little nervous about taking my first trip abroad. What do I need to know?", "context": "",
         "answer": ""},
        {"query": "What is the difference between a dividend and a capital gain?", "context": "", "answer": ""},
        {"query": "What are the best ways to make a house a home?", "context": "", "answer": ""},
        {"query": "I have a question about ecology. What is the difference between a population and a community?",
         "context": "", "answer": ""}
        ]

    #   please note that these models will produce multiple bulletpoints and paragraph length answers, so
    #   it can take ~30 seconds for each response on a typical Mac M1 laptop

    #   for full citations and links, please go to www.huggingface.co/llmware/bonchon model repository
    #       -- TheBloke/OpenHermes-2.5-Mistral-7B-GGUF
    #       -- TheBloke/zephyr-7B-beta-GGUF
    #       -- TheBloke/Starling-LM-7B-alpha-GGUF
    #       -- TheBloke/Llama-2-7B-Chat-GGUF
    #
    #       -- Llama-3:  bartowski/Meta-Llama-3-8B-Instruct-GGUF
    #       -- Phi-3:    microsoft/Phi-3-mini-4k-instruct-gguf

    output = run_test("bartowski/Meta-Llama-3-8B-Instruct-GGUF",ds)
