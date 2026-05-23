
"""This example demonstrates how to parse a PDF document 'in-line' and integrate in memory directly into a
Prompt as a source of evidence for an LLM inference. """

import os
from llmware.prompts import Prompt
from llmware.gguf_configs import GGUFConfigs

# Configure the GGUF models
GGUFConfigs().set_config("max_output_tokens", 500)


def prompt_with_sources(model_name):

    prompter = Prompt().load_model(model_name, max_output=450,
                                   temperature=0.0, sample=False, register_trx=True)

    prompter.add_source_document(
        "./", "Mini Project Abstract@SemVI.pdf")

    response = prompter.prompt_with_source(
        "What is the Roll ?", prompt_name="default_with_context")
    print(response[0]["llm_response"])


if __name__ == "__main__":

    chat_models = [
        "phi-3-gguf",
        "llama-2-7b-chat-gguf",
        "llama-3-instruct-bartowski-gguf",
        "openhermes-mistral-7b-gguf",
        "zephyr-7b-gguf",
        "tiny-llama-chat-gguf"
    ]

    model_name = chat_models[1]

    print(f"\nExample - intro to prompt_with_sources - adding a document source to a prompt\n")

    prompt_with_sources(model_name)
