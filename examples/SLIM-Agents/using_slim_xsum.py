
""" This example illustrates how to use the slim-xsum model to provide 'extreme summarizations', generally
    providing a headline or title (typically no more than 10-15 words) to describe a longer text passage. """

from llmware.models import ModelCatalog

slim_xsum_models = ["slim-xsum-tool", "slim-xsum-phi-3-gguf"]

#   load the model
model = ModelCatalog().load_model("slim-xsum-phi-3-gguf",sample=False, temperature=0.0, max_output=200)

#   load the test dataset packaged with the model (will be cached locally the first time you load)
test_set = ModelCatalog().get_test_script("slim-xsum-phi-3-gguf")

#   iterate through the test set samples
for i, sample in enumerate(test_set):

    #   invoke function call on the model, and pass 'xsum' as the parameter
    response = model.function_call(sample["context"], params=["xsum"])

    #   display the output
    print("\nllm_response: ", i, response["llm_response"])


