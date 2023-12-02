
import sys

from llmware.models import ModelCatalog, LLMWareInferenceServer

#   Example sets up a 'pop up' development/testing inference server on a remote GPU
#
#   The inference server has been designed for DRAGON and BLING models (www.huggingface.co/llmware)
#   If you are interested in serving any other generative decoder model on Huggingface, the architecture
#   should generally support, but may require some modification depending upon the prompt wrapping
#   If you have a specific model in mind, please raise an issue, and we will work with you to ensure full support.
#
#   Getting Started:   run this file on cloud GPU server instance, e.g., AWS, Paperspace, Lambda Labs
#   Example GPU machines -
#       -- AWS g5.2xlarge & g5.4xlarge - both use A10s with 24GB RAM - and <$2 per hour
#       -- Paperspace A5000 & A6000 machines - both <$2 per hour
#       -- Lambda Labs A10 & A100 machines - ~$1 per hour (when available on demand)
#   7B parameter models typically requires minimum of 20-24 GB of GPU memory
#   we test primarily on Nvidia A10, A5000, A6000, and A100 GPUs

#   note: depending upon the GPU server configs, may need to install a few dependencies first:
#   --  pip install flask
#   --  pip install transformers==4.35
#   --  pip install einops  (required for some models)
#   --  pip install flash-attn (improves speed of inference for supported models)

#   -- *** intended for rapid development and testing only - not production use ***


if __name__ == "__main__":

    #   note: designed for DRAGON and BLING RAG-instruct fine-tuned models available on HuggingFace
    #
    #   -- 7B models:
    #       -- llmware/dragon-mistral-7b-v0
    #       -- llmware/dragon-llama-7b-v0
    #       -- llmware/dragon-red-pajama-7b-v0
    #       -- llmware/dragon-falcon-7b-v0
    #       -- llmware/dragon-stablelm-7b-v0
    #
    #   --6B models:
    #       -- llmware/dragon-yi-6b-v0
    #       -- llmware/dragon-deci-6b-v0
    #
    #   --3B models:
    #       -- llmware/bling-red-pajamas-3b-0.1
    #       -- llmware/bling-sheared-llama-2.7b-0.1
    #       -- llmware/bling-stablelm-3b-4e1t-v0
    #
    #   --1B models:
    #       -- llmware/bling-falcon-1b-0.1
    #       -- llmware/bling-sheared-llama-1.3b-0.1
    #       -- llmware/bling-1b-0.1
    #       -- llmware/bling-1.4b-0.1
    #       -- llmware/bling-cerebras-1.3b-0.1

    #
    #   *** updated model list available at:  www.huggingface.co/llmware ***

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
                           home_path="/home/ubuntu/",
                           port=8080).start()

    #   note: run on client will need 2 parameters from the server:
    #       1 - server URL and PORT - e.g., URL = 123.456.78.90 & PORT = 8080
    #       2 - secret_api_key

    #   NOTE: see accompanying example - 'launch_llmware-inference-server.py' for the client code to use this server



