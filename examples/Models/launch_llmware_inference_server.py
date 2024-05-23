
""" This example provides a detailed set of instructions and comments for setting up a fast inference
server on a GPU using llmware model classes.   Please see also two other examples that mirror this code:

    -- examples/SLIM-Agents/agent_api_endpoint.py
    -- examples/Use_Cases/llmware_inference_server.py

    Example sets up a 'pop up' development/testing inference server on a remote GPU

    The inference server has been designed for DRAGON and BLING models (www.huggingface.co/llmware)
    If you are interested in serving any other generative decoder model on Huggingface, the architecture
    should generally support, but may require some modification depending upon the prompt wrapping
    If you have a specific model in mind, please raise an issue, and we will work with you to ensure full support.

    Getting Started:   run this file on cloud GPU server instance, e.g., AWS, Paperspace, Lambda Labs

    Example GPU machines that we use and test regularly-

       -- AWS g5.2xlarge & g5.4xlarge - both use A10s with 24GB RAM - and <$2 per hour
       -- Paperspace A5000 & A6000 machines - both <$2 per hour
       -- Lambda Labs A10 & A100 machines - ~$1 per hour (when available on demand)

    7B parameter models typically requires minimum of 20-24 GB of GPU memory
    we test primarily on Nvidia A10, A5000, A6000, and A100 GPUs

    Quantized GGUF models can generally run with lower memory requirements than Pytorch models.

    note: depending upon the GPU server configs, may need to install a few dependencies first:

   --  pip3 install flask
   --  pip3 install flash-attn (improves speed of inference for supported models)

   -- *** intended for rapid development and testing only - not production use ***

    """

import sys

from llmware.models import ModelCatalog, LLMWareInferenceServer


if __name__ == "__main__":

    #   note: designed to be used with any generative GGUF or Pytorch model in the llmware ModelCatalog

    #   by default, we will use a dragon-llama-7b
    model_selection = "llmware/dragon-llama-7b-v0"

    # different models can be selected by adding as parameter on the launch command line
    if len(sys.argv) > 1:
        model_selection = sys.argv[1]

    print("update: model selection - ", model_selection)

    #   pulls down and instantiates the selected model and then launches a very simple Flask-based API server

    LLMWareInferenceServer(model_selection,
                           model_catalog=ModelCatalog(),
                           secret_api_key="demo-test",
                           home_path="/home/ubuntu/").start()

    #   note: run on client will need 2 parameters from the server:
    #       1 - server URL and PORT - e.g., URL = 123.456.78.90 & PORT = 8080
    #       2 - secret_api_key

    #   NOTE: see accompanying example - 'launch_llmware-inference-server.py' for the client code to use this server



