
""" This example illustrates the use of Vision models with OpenVINO, to convert
    an image with text instruction -> text generation output.

    Prereqs:
        -- pip install openvino_genai
        -- pip install PIL (Pillow library for image preparation)

        If you want to use the web streamer:
        -- pip install pywebio

    """

from llmware.models import ModelCatalog
import openvino_genai as ovg

try:
    from pywebio.output import put_text
except:
    pass


# this is the default streamer included in the OVGenerativeModel class -
# if no streamer explicitly passed, then this will be used

def ov_default_streamer(x):
    print(x, end="", flush=True)
    return ovg.StreamingStatus.RUNNING

# here is a simple example that will stream the text to local host
# to run this example: `pip install pywebio`

def web_streamer(x):
    put_text(x,inline=True)
    return ovg.StreamingStatus.RUNNING

# supported OpenVINO vision models in llmware:
#   -- qwen2.5-vl-3b-ov
#   -- gemma-3-4b-ov
#   -- phi-3.5-vision-ov
#   -- phi-4-mm-ov

model = ModelCatalog().load_model("phi-4-mm-ov",
                                  max_output=500, device="GPU")

image_path = "C:\\Users\\path\\to\\image_file"

prompt = "Describe this image."

import time
t0=time.time()

response = model.stream(prompt, image_path, streamer=ov_default_streamer)

t1= time.time()


print("\n\ncompleted streaming response - ", response)
print("\ntime taken: ", t1-t0)


