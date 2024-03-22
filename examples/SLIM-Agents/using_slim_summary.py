
""" This example illustrates how to use slim-summary model to summarize a longer text. """

from llmware.models import ModelCatalog

#   load the model and set the sampling and output parameters
model = ModelCatalog().load_model("slim-summary-tool",
                                  sample=False,
                                  temperature=0.0,
                                  max_output=200)

#   get the test data set packaged with the model
test_script = ModelCatalog().get_test_script("slim-summary-tool")

#   iterate through the samples
for i, sample in enumerate(test_script):

    #   invoke function call on the model, passing the context passage and the 'summarize' function
    #   the parameter can be a generic phrase, e.g., 'key points' or 'brief description' or 'summary'
    #   if the material has a lot of numeric data points, try the parameter 'data points' or 'financial data points'
    #   if you are looking for a single line of output, try 'brief description'
    #   the number in ( ) is optional - but is intended to guide the model to provide with a list with the requested
    #   number of elements

    response = model.function_call(sample["context"], function="summarize", params=["data points (5)"])

    #   display the response
    print("\nresponse: ", response)

    #   check how effectively the model mapped the output to the requested number of points
    r = response["llm_response"]
    for j, entries in enumerate(r):
        print("summary points: ", j, entries)


