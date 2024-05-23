
""" This example shows how to use the llmware inference server created in the example:

    -- examples/Use_Cases/llmware_inference_server.py

    The example assumes that the server is running, and requires the following two parameters from the server:

    -- api_key = 'secret_api_key' (e.g., 'demo-test' in example)
    -- api_endpoint = full ip url address of the endpoint, e.g., 'http://54.160.232.56:8080'

    There are three primary client access points into the inference server:

    1. 'load as api' -  pass the api_endpoint and api_key in .load_model(), and the model class will route the
    execution to the api, rather than executing locally  [note: implemented starting in llmware 0.2.15]

    2. 'register endpoint as model' - register the endpoint as a model in the ModelCatalog and then
    call like any other model [note: this method will access the model loaded at the time of starting the server]

    3.  'agent api process' - register the endpoint in an agent process, and the agent will automatically
    call the API instead of executing the model locally

    In this example, we show all three of these access modes.

    Please note that the api inference endpoint is designed for serving locally-deployed GGUF and HuggingFace models,
    and in its current implementation, it is best suited for dev/testing and not production use.

    """


from llmware.models import ModelCatalog


def dynamic_load(api_key='demo-test', api_endpoint='http://127.1.1.1:8080'):

    """ Starting with llmware 0.2.15, you can directly pass the api_key and api_endpoint when loading the
    model, and if those parameters are detected, then the model will automatically route the execution to the
    API rather than executing locally.

    This method is designed to promote high-degree of code re-use, e.g., develop/test locally, and then easily
    shift to production by setting up as a model API server, or shifting the api_endpoint address to go from
    a 'test' to 'production' inference server environment.
    """

    #   local execution
    model = ModelCatalog().load_model("phi-3-gguf")
    response = model.inference("What are the advantages of using small specialized language models?")
    print("\nresponse (local): ", response)

    #   execute over api
    model = ModelCatalog().load_model("phi-3-gguf", api_key=api_key, api_endpoint=api_endpoint)
    response = model.inference("What are the advantages of using small specialized language models?")
    print("\nresponse (api): ", response)

    return True


def register_api_endpoint_as_model(api_key="demo-test", api_endpoint="http://11.123.456.789:8080"):

    """ This example registers the api endpoint inference as a model in the ModelCatalog - which then
    enables it to be called directly like any other model.

    Note: this method will only call the default model loaded at the time of creating the inference server.

        inputs were set up on the server
           -- api_endpoint:  concatenation of URL and PORT, e.g, http://11.123.456.789:8080
           -- api_key = secret_api_key, e.g., "demo-test"
    """

    from llmware.prompts import Prompt
    from llmware.models import LLMWareModel

    #   Step 1 - one-line 'setup' to register the new inference server
    ModelCatalog().setup_custom_llmware_inference_server(api_endpoint, secret_key=api_key)

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

    print("update: llm response (api) - ", output)

    #   USE CASE # 2 - load LLMWareModel directly and invoke
    print("\nupdate: Use Case #2 - loading as LLMWareModel")

    llmware_gpt = LLMWareModel(model_name="llmware-inference-server")
    response = llmware_gpt.inference(query, add_context=context)

    print("update: llm response (api) - ", response)

    return output, response


def agent_api_endpoint(api_key="demo-test", api_endpoint="http://127.0.0.1:8080"):

    """ This example shows how to register the endpoint in an agent process so that the agent will route all
    function calls and model inferences to the endpoint rather than execute locally.

    This example is derived from the script in the example agent-llmfx-getting-started.py. """

    from llmware.agents import LLMfx

    customer_transcript = "My name is Michael Jones, and I am a long-time customer.  " \
                          "The Mixco product is not working currently, and it is having a negative impact " \
                          "on my business, as we can not deliver our products while it is down. " \
                          "This is the fourth time that I have called.  My account number is 93203, and " \
                          "my user name is mjones. Our company is based in Tampa, Florida."

    #   create an agent using LLMfx class
    agent = LLMfx()

    #   inserting this line below into the agent process sets the 'api endpoint' execution to "ON"
    #   all agent function calls will be deployed over the API endpoint on the remote inference server
    #   to "switch back" to local execution, comment out this line

    agent.register_api_endpoint(api_endpoint=api_endpoint, api_key=api_key, endpoint_on=True)

    #   to explicitly turn the api endpoint "on" or "off"
    # agent.switch_endpoint_on()
    # agent.switch_endpoint_off()

    agent.load_work(customer_transcript)

    #   load tools individually
    agent.load_tool("sentiment")
    agent.load_tool("ner")

    #   load multiple tools
    agent.load_tool_list(["emotions", "topics", "intent", "tags", "ratings", "answer"])

    #   start deploying tools and running various analytics

    #   first conduct three 'soft skills' initial assessment using 3 different models
    agent.sentiment()
    agent.emotions()
    agent.intent()

    #   alternative way to execute a tool, passing the tool name as a string
    agent.exec_function_call("ratings")

    #   call multiple tools concurrently
    agent.exec_multitool_function_call(["ner","topics","tags"])

    #   the 'answer' tool is a quantized question-answering model - ask an 'inline' question
    #   the optional 'key' assigns the output to a dictionary key for easy consolidation
    agent.answer("What is a short summary?",key="summary")

    #   prompting tool to ask a quick question as part of the analytics
    response = agent.answer("What is the customer's account number and user name?", key="customer_info")

    #   you can 'unload_tool' to release it from memory
    agent.unload_tool("ner")
    agent.unload_tool("topics")

    #   at end of processing, show the report that was automatically aggregated by key
    report = agent.show_report()

    #   displays a summary of the activity in the process
    activity_summary = agent.activity_summary()

    #   list of the responses gathered
    for i, entries in enumerate(agent.response_list):
        print("update: response analysis: ", i, entries)

    output = {"report": report, "activity_summary": activity_summary, "journal": agent.journal}

    return output

