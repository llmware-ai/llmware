from llmware.models import ModelCatalog
from llmware.prompts import Prompt

def simple_chatbot(model_name):
    model = Prompt().load_model(model_name)

    print(f"Chatbot initialized with model: {model_name}")
    
    while True:
        user_input = input("You: ")
        
        output = model.prompt_main(user_input,
                                  prompt_name="default_with_context",
                                  temperature=0.30)
        bot_response = output["llm_response"].strip("\n")

        print("Bot:", bot_response)
        
        if user_input.lower() == 'quit':
            print("Exiting chatbot...")
            break

if __name__ == "__main__":
    model_name = "phi-3-gguf"
    simple_chatbot(model_name)