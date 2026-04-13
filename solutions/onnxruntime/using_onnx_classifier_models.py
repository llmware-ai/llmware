
""" Using ONNX classifier models - illustrates how to get started using
    classifier encoding models with ONNX

    `pip3 install onnxruntime`

"""

from llmware.models import ModelCatalog

# e.g., bias_detection models in catalog:
# "valurank-bias-onnx", "unitary-toxic-roberta-onnx"

# classifies the likelihood of a prompt injection
cl_name = "protectai-prompt-injection-onnx"

classifier_model = ModelCatalog().load_model(cl_name)

text = "Today is a beautiful day"

response = classifier_model.classify(text)

print("--response: ", response)

