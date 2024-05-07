

from llmware.models import ModelCatalog
from llmware.prompts import Prompt


def test_load_hf_model_in_prompt():

    model_list = ["llmware/bling-1b-0.1",
                  "llmware/bling-1.4b-0.1",
                  "llmware/bling-tiny-llama-v0",
                  "llmware/bling-falcon-1b-0.1"]

    test_prompt = ("The best time to visit New York City is in the Fall when the weather is nicest."
                   "\nWhen is the best time to visit New York?")

    for model_name in model_list:

        print("model_name: ", model_name)

        prompter = Prompt().load_model(model_name, temperature=0.0, sample=False)
        assert prompter is not None

        response = prompter.prompt_main(test_prompt)

        print(f"{model_name} response - ", response)

        assert response is not None



test_load_hf_model_in_prompt()
