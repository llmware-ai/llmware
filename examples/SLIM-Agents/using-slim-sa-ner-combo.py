
""" This example illustrates how to use the slim-sa-ner-tool, which is a 'combination' model that brings together
    both sentiment and named entity recognition in a single function-calling model. """

from llmware.models import ModelCatalog


model = ModelCatalog().load_model("slim-sa-ner-tool", sample=False, temperature=0.0)

text = ("Tesla stock declined yesterday 8% in premarket trading after a poorly-received event in San Francisco "
        "yesterday, in which the company indicated a likely shortfall in revenue.")

response = model.function_call(text, function="classify", params=["sentiment,person,organization,place"])

print("response: ", response)

ModelCatalog().tool_test_run("slim-sa-ner-tool")
