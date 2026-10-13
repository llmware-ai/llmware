from llmware.prompts import Prompt
from llmware.gguf_configs import GGUFConfigs

# Configure the GGUF models
GGUFConfigs().set_config("max_output_tokens", 500)


def simple_chat_terminal(model_name):
    print(f"Simple Chat with {model_name}\n")
    print("Type 'exit' to end the chat.\n")

    model = Prompt(save_state=True).load_model(
        model_name,
        temperature=0.0,
        sample=False,
        max_output=450,
        register_trx=True  # Specify local model path
    )

    while True:

        try:
            prompt = input("You: ")
            if prompt.lower() == "exit":
                print("Chat ended. Goodbye!")
                break

            print("Assistant: ", end="", flush=True)

            response_generator = model.prompt_main(prompt)

            print(response_generator['llm_response'])

        except Exception as e:
            print(f"\nAn error occurred: {e}")
            break


if __name__ == "__main__":
    chat_models = [
        "phi-3-gguf",
        "llama-2-7b-chat-gguf",
        "llama-2-13b-chat-ov",
        "llama-3-instruct-bartowski-gguf",
        "openhermes-mistral-7b-gguf",
        "zephyr-7b-gguf",
        "tiny-llama-chat-gguf"
    ]

    model_name = chat_models[2]
    simple_chat_terminal(model_name)
