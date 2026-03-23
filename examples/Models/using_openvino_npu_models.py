
""" This example illustrates how to run models on an Intel NPU using OpenVINO, using
    a simple callback streaming function.

    Prereqs:
        -- pip install openvino_genai

    """

from llmware.models import ModelCatalog
import openvino_genai as ovg


# this is the default streamer included in the OVGenerativeModel class -
# if no streamer explicitly passed, then this will be used

def ov_default_streamer(x):
    print(x, end="", flush=True)
    return ovg.StreamingStatus.RUNNING

#   lists all intel npu optimized models in the catalog
npu_models = ModelCatalog().list_intel_npu_optimized_models()


for i, model in enumerate(npu_models):
    print("--intel npu models - ", i, model.get("model_name", ""))

#   use any of these models, and the NPU will automatically be set as the device
#   the device can also be manually by adding: device="NPU" to the load_model call

model = ModelCatalog().load_model("llama-3.2-1b-instruct-npu-ov",
                                  max_output=500)

prompt = "What are the best sites to see in France?"

# streamer is None by default, pass custom streaming function here
response = model.stream(prompt, streamer=ov_default_streamer)

print("\n\ncompleted streaming response - ", response)

