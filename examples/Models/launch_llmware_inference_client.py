
""" This example is intended to work in conjunction with the "launch_llmware_inference_server.py" example.

    This shows how to set up the client, e.g., developer laptop, to quickly integrate the 'pop up' inference server

    Before using this script, please implement the steps in "launch_llmware_inference_server.py" example

    Note:  this is not intended to be a production-grade inference server
    It is intended for fast, simple, easy-to-use and platform-agnostic to rapidly test and develop LLM-based apps
    in a private-cloud, self-hosted environment.

    Please also see examples/Use_Cases/llmware_inference_api_client.py for other ways to leverage the API endpoint.

"""

from llmware.models import ModelCatalog, LLMWareModel
from llmware.prompts import Prompt


def client_code_setup_inference_server(server_uri_string, server_secret_key):

    #   inputs were set up on the server
    #       -- example server_uri_string:  concatenation of URL and PORT, e.g, http://11.123.456.789:8080
    #       -- example secret key:  "demo-test"

    #   Step 1 - one-line 'setup' to register the new inference server
    ModelCatalog().setup_custom_llmware_inference_server(server_uri_string, secret_key=server_secret_key)

    #   test query and context
    query = "What is the total amount of the invoice?"
    context = "Services Vendor Inc. \n100 Elm Street Pleasantville, NY \nTO Alpha Inc. 5900 1st Street " \
              "Los Angeles, CA \nDescription Front End Engineering Service $5000.00 \n Back End Engineering" \
              "Service $7500.00 \n Quality Assurance Manager $10,000.00 \n Total Amount $22,500.00 \n" \
              "Make all checks payable to Services Vendor Inc. Payment is due within 30 days." \
              "If you have any questions concerning this invoice, contact Bia Hermes."

    #   USE CASE # 1 = use LLMWareModel directly in prompt, like any other model
    #   -- "llmware-inference_server" is special reserved keyword that points to the registered inference server
    print("\nupdate: Use Case #1 - loading into Prompt")

    prompter = Prompt().load_model("llmware-inference-server")
    output = prompter.prompt_main(query, context=context)

    print("update: llm response - ", output)

    #   USE CASE # 2 - load LLMWareModel directly and invoke
    print("\nupdate: Use Case #2 - loading as LLMWareModel")

    llmware_gpt = LLMWareModel(model_name="llmware-inference-server")
    response = llmware_gpt.inference(query, add_context=context)

    print("update: llm response - ", response)

    return output, response


if __name__ == "__main__":

    # insert your uri & port
    my_uri_string = "http://11.123.456.788:8080"

    # insert your secret key  [note: this can be any string, which must be exact-match on the server]
    my_secret_key = "demo-test"

    output, response = client_code_setup_inference_server(my_uri_string,my_secret_key)
