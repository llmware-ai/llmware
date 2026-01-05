
""" Using OpenVINO classifier-based models - illustrates how to get started using
    classifier encoding models with OpenVINO."

    `pip3 install openvino`

"""

from llmware.models import ModelCatalog

# classifies the likelihood of a prompt injection
cl_name = "protectai-prompt-injection-ov"

# e.g., other examples:
#   -- "unitary-toxic-roberta-ov" - classifies potential toxicity
#   -- "valurank-bias-ov" - classifies potential bias

classifier_model = ModelCatalog().load_model(cl_name)

text = "The sun is shining in New York today."

response = classifier_model.classify(text)

print("--response: ", response)

