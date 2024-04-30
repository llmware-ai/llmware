
"""This example demonstrates basic use of Prompts, and how to capture and track the Prompt State and
interaction history."""


from llmware.prompts import Prompt
from llmware.resources import PromptState

def prompt_state(llm_model):

    # Create a new prompter with state persistence
    prompter = Prompt(save_state=True)

    # Capture the prompt_id (which can be used later to reload state)
    prompt_id = prompter.prompt_id

    # Load the model
    prompter.load_model(llm_model, temperature=0.0, sample=False)

    # Define a list of prompts
    prompts = [
        {"query": "How old is Bob?", "context": "John is 43 years old.  Bob is 27 years old."},
        {"query": "When did COVID start?", "context": "COVID started in March of 2020 in most of the world."},
        {"query": "What is the current stock price?", "context": "The stock is trading at $26 today."},
        {"query": "When is the big game?", "context": "The big game will be played on November 14, 2023."},
        {"query": "What is the CFO's salary?", "context": "The CFO has a salary of $285,000."},
        {"query": "What grade is Michael in school?", "context": "Michael is starting 11th grade."}
    ]

    # Iterate through the prompt which will save each response dict in in the prompt_state
    print (f"> Sending a series of prompts to {llm_model}...")

    for i, prompt in enumerate(prompts):
        print ("  - " + prompt["query"])
        response = prompter.prompt_main(prompt["query"] ,context=prompt["context"] ,register_trx=True)

        print(f"  -  LLM Responses: {response}")

    # Print how many interactions are now in the prompt history
    interaction_history = prompter.interaction_history
    print (f"> Prompt Interaction History now contains {len(interaction_history)} interactions")

    # Use the dialog_tracker to regenerate the conversation with the LLM
    print (f"> Reconstructed Dialog")
    dialog_history = prompter.dialog_tracker
    for i, conversation_turn in enumerate(dialog_history):
        print("  - ", i, "[user]: ", conversation_turn["user"])
        print("  - ", i, "[ bot]: ", conversation_turn["bot"])

    # Saving and clean the prompt state
    prompter.save_state()
    prompter.clear_history()

    # Print the number of interactions
    interaction_history = prompter.interaction_history
    print (f"> Prompt history has been cleared")
    print (f"> Prompt Interaction History now contains {len(interaction_history)} interactions")

    # Reload the prompt state using the prompt_id and print again the number of interactions
    prompter.load_state(prompt_id)
    interaction_history = prompter.interaction_history
    print (f"> The previous prompt state has been re-loaded")
    print (f"> Prompt Interaction History now contains {len(interaction_history)} interactions")

    # Generate a Prompt transaction report
    prompt_transaction_report = PromptState().generate_interaction_report([prompt_id])
    print (f"> A prompt transaction report has been generated: {prompt_transaction_report}")

    return 0


if __name__ == "__main__":

    model_name = "llmware/bling-1b-0.1"

    print(f"\nExample - basic prompt state and interaction history management.\n")

    prompt_state(model_name)
