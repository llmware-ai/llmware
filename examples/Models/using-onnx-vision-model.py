""" This example shows how to use multimedia vision-to-text model with onnxruntime -

    to run, pip install onnxruntime_genai
"""

from llmware.models import ModelCatalog

model = ModelCatalog().load_model("phi-3-vision-onnx")

# supported image types: jpg, png
img_path = "/path/to/local/image"

# to run a streaming response
for token in model.stream("Describe this image",img_path):
    print(token, end="")

# to get a complete response upon completion only
response = model.inference("Describe this image", img_path)
print("--vision response - ", response)
