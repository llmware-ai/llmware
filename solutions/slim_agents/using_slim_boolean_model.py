
""" This example illustrates how to use the slim-boolean model.  In this case, we will use test documents provided
    in the model package, which will be cached locally the first time that you load the model. """

from llmware.models import ModelCatalog

#   load the model - best results with sample=False, but feel free to experiment
model = ModelCatalog().load_model("slim-boolean-tool",sample=False, temperature=0.0, max_output=200)

#   get the test set packaged with the model
test_set = ModelCatalog().get_test_script("slim-boolean-tool")

#   iterate through the test set
for i, sample in enumerate(test_set):

    #   add optional "explain" parameter to each question
    question = sample["question"] + " (explain)"

    #   key line:  invoke function call on the model, with boolean function, and pass the question as the parameter
    response = model.function_call(sample["context"], function="boolean", params=[question])

    print("response: ", response)

    #   analyze the logits
    analysis = ModelCatalog().get_fx_scores(response,"slim-boolean-tool")

    #   display to the screen
    print("\nllm_response: ", i, question, response["llm_response"])
    print("analysis: ", analysis)


