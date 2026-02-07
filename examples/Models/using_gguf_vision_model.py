
""" GGUF Vision Model example - get started with vision-to-text using mtmd tool in conjunction with llama cpp """

from llmware.models import ModelCatalog

model_name = "qwen2.5-vl-3b-instruct-gguf"

# add path to local image
image_file_path = "/local/path/to/jpg_or_png_image"

# add text prompt/instruction
prompt = "Describe this image."

model = ModelCatalog().load_model(model_name, max_output=500)

# to run streaming generation
for token in model.stream(prompt,image_file_path):
    print(token, end="")

# to run inference (response once completed at the end)
response = model.inference(prompt,image_file_path)
print("--test: inference response: ", response)
