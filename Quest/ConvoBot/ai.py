from llmware.prompts import Prompt


def generate_response(query: str) -> str:
    prompter = Prompt().load_model("phi-3-gguf")

    output = prompter.prompt_main(
        query, prompt_name="default_with_context", temperature=0.30
    )
    response = output["llm_response"].strip("\n").partition("<|end|>")[0]
    return response if response else "I'm sorry, I don't understand that."
