
""" Getting Started with SLIM classifier function calling models - this script demonstrates seven
    mini examples to get started using SLIMs:

    1.  Discover list of SLIM models.
    2.  'Hello World' first inference with SLIM model.
    3.  Models vs. Tools
    4.  Download and cache the SLIM tools.
    5.  Run automated tests to confirm installation and demonstrate output.
    6.  Using with LLMWare Prompts.
    7.  Using the new LLMfx class.

"""

from llmware.models import ModelCatalog
from llmware.agents import LLMfx
from llmware.prompts import Prompt


def step1_discover_and_load_slim_models():

    """ Discover a list of SLIM tools in the Model Catalog """

    tools = ModelCatalog().list_llm_tools()
    tool_map = ModelCatalog().get_llm_fx_mapping()

    print("\nList of SLIM model tools in the ModelCatalog\n")

    for i, tool in enumerate(tools):
        model_card = ModelCatalog().lookup_model_card(tool_map[tool])
        print("update: step1 - slim tools: ", i, tool, model_card)

    return 0


def step2_hello_world_slim():

    """ SLIM models can be identified in the ModelCatalog like any llmware model.  Instead of using
    inference method, SLIM models are used with the function_call method that prepares a special prompt
    instruction, and takes optional parameters. """

    print("\n'Hello World' Inference Using SLIM Function call\n")

    # load like any other model anytime
    model = ModelCatalog().load_model("slim-ner-tool")
    response = model.function_call("Michael Johnson was a famous Olympic sprinter from the U.S. in the early 2000s.")

    print("update: step2 - response: ", response)
    print("update: step2 - usage: ", response["usage"])

    return 0


def step3_models_versus_tools():

    """ All SLIM models are delivered in two different packages - as a traditional 'model' and as a
    quantized 'tool.' In most scenarios, the tool is intended to be used for fast inference. """

    print("\nSLIMs come packaged as 'models' (pytorch) and 'tools' (gguf)\n")

    model = ModelCatalog().load_model("llmware/slim-ner")
    response = model.function_call("Michael Johnson was a famous Olympic sprinter from the U.S. in the early 2000s.")

    print("update: step3 - response: ", response)
    print("update: step3 - usage: ", response["usage"])

    return 0


def step4_load_and_cache_slim_tools():

    """ To cache the SLIM toolkit locally, use .get_llm_toolkit.   If you prefer to select specific tools,
    then you can pass a tool_list in the method call as shown below. """

    #   get all tools
    ModelCatalog().get_llm_toolkit()

    #   select specific tools
    ModelCatalog().get_llm_toolkit(tool_list=["sentiment", "ner"])

    return 0


def step5_run_automated_tests():

    """ Each of these one line commands will locally cache the model and then run a series of tests using
    the model to demonstrate its use and confirm that installation locally was successfully. """

    #   running automated tests - see the tools in action

    tools= ["slim-sentiment-tool" , "slim-topics-tool", "slim-ner-tool", "slim-ratings-tool",
            "slim-emotions-tool",  "slim-intent-tool", "slim-tags-tool", "slim-sql-tool",
            "slim-category-tool", "slim-nli-tool"]

    # run tests for one tool
    ModelCatalog().tool_test_run("slim-sentiment-tool")

    # run tests for a bunch of tools
    for tool in tools:
        # excluding sentiment, since ran above as separate test
        if tool != "slim-sentiment-tool":
            ModelCatalog().tool_test_run(tool)

    return 0


def step6_simple_use_case():

    """ This illustrates how to run a basic function call inference on a SLIM model used in conjunction with
    a LLMWare prompt. """

    text = ("This is Melinda Wyngardt from Silvertech Ventures.  We are extremely unhappy with the delays in closing "
            "the loan and are considering whether to cancel and back out of the deal.")

    tags_model = ModelCatalog().load_model("slim-tags-tool")
    response = tags_model.function_call(text,get_logits=True)
    print("update: step6 - 'tags' response: ", response)

    intent_model = ModelCatalog().load_model("slim-intent-tool")
    response2 = intent_model.function_call(text)
    print("update: step6 - 'intent' response: ", response2)

    prompter = Prompt().load_model("llmware/bling-tiny-llama-v0")
    output = prompter.prompt_main("What is the name of the company?", context=text)
    print("update: step6 - 'question/answer' response: ", output)

    return 0


def step7_introducing_llm_fx_class():

    """ In addition to using SLIM models to 'supplement' primary LLM calls, SLIMs can be orchestrated in a
    multi-step, multi-model workflow using the high-level LLMfx() - more examples on LLMfx() are in the next
    main example 'agent-llmfx-getting-started.py' """

    #  shift verbose to True to see step-by-step processing on the screen
    agent = LLMfx(verbose=False)
    agent.load_tool("sentiment")

    text = "That is the worst thing that I have ever heard."
    response = agent.exec_function_call("sentiment", text)

    print("update: step 7 - response - ", response)

    return 0


if __name__ == "__main__":

    step1_discover_and_load_slim_models()
    step2_hello_world_slim()
    step3_models_versus_tools()
    step4_load_and_cache_slim_tools()
    step5_run_automated_tests()
    step6_simple_use_case()
    step7_introducing_llm_fx_class()


