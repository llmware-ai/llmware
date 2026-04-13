
""" This example illustrates the use of streaming with OpenVINO models, which
    use a callback streaming function, rather than a generator - the example
    shows how to stream text to console using the default streamer, and
    how to modify and create a custom streamer function.

    Prereqs:
        -- pip install openvino_genai

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


model = ModelCatalog().load_model("llama-3.2-3b-instruct-ov",
                                  max_output=500)

prompt = "What are the best sites to see in France?"

# streamer is None by default, pass custom streaming function here
response = model.stream(prompt, streamer=ov_default_streamer)

print("\n\ncompleted streaming response - ", response)



