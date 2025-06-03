""" Example script for using the Cohere Command R model. """

from llmware.models import ModelCatalog

def main():
    """ Demonstrates loading and using the Cohere Command R model. """

    model_name = "command-r"

    # Load the model using ModelCatalog
    model = ModelCatalog().load_model(model_name)

    # Define a prompt for inference
    prompt = "Explain the theory of relativity in simple terms."

    # Perform inference
    response = model.inference(prompt)

    # Print the response
    print("LLM Response:", response["llm_response"])
    print("Usage:", response["usage"])

if __name__ == "__main__":
    main()
