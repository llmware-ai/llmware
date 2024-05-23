
""" This example shows how to set up an inference server for accessing llmware models over API.

    Note: this code mirrors the script in "examples/SLIM-Agents/agent_api_endpoint.py" which shows
    specifically how to use an inference server as part of an agent process, integrating into the
    example:   "examples/SLIM-Agents/agent-llmfx-getting-started.py"

    Pre-reqs:  to execute this code, please install Flask - `pip3 install Flask`
        -- Flask is a popular lightweight Python web server framework that is used under the covers to serve the API

"""


from llmware.models import ModelCatalog, LLMWareInferenceServer

#   select one model that will be loaded at the time of starting the server
#   -- note:  other models can be used at any time, but will be loaded into memory at the time of being invoked

load_on_start_model = "llmware/bling-tiny-llama-v0"

LLMWareInferenceServer(load_on_start_model,
                       model_catalog=ModelCatalog(),
                       secret_api_key="demo-test",
                       home_path="/home/ubuntu/",
                       verbose=True).start()

#   this will start Flask-based server, which will display the launched IP address and port, e.g.,
#   "Running on " ip_address = "http://127.0.0.1:8080"



