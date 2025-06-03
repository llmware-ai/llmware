""" Test for Cohere Command R model integration. """

from llmware.models import ModelCatalog

def test_cohere_command_r():
    """ Test loading and basic inference for Cohere Command R model. """

    model_name = "command-r"

    # Load the model using ModelCatalog
    model = ModelCatalog().load_model(model_name)

    # Define a simple prompt for testing
    prompt = "What is the capital of France?"

    # Perform inference
    response = model.inference(prompt)

    # Print the response for debugging
    print("LLM Response:", response["llm_response"])
    print("Usage:", response["usage"])

    # Assert that the response is not None
    assert response is not None

    return 0

if __name__ == "__main__":
    test_cohere_command_r()
