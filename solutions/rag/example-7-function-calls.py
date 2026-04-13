
""" Fast Start Example #7 - Model Function Calls

    This example is derived from the example in: examples/SLIM-Agents/using_function_calls.py

    Objective: start moving beyond basic prompting and question-answering, and start using LLMs for
    "function calls" with structured programmatic outputs

    Generally, function-calling is a specialized capability of frontier language models, such as OpenAI GPT4.

    We have adapted this concept to small language models through SLIMs (Structured Language Instruction Models),
    which are 'single function' models fine-tuned to accept three main inputs to construct a prompt and generate a structured output.  

    As of June 2024, there are 18 distinct SLIM function calling models with many more on the way, for most common
    extraction, classification, and summarization tasks.

    All SLIM models have a common prompting structure

    Inputs:
        -- text passage - this is the core passage or piece of text that you would like the model to assess
        -- function - classify, extract, generate - this is handled by default by the model class, so usually does
                not need to be explicitly declared - but is an option for SLIMs that support more than one function
        -- params - depends upon the model, used to configure/guide the behavior of the function call - optional for
                some SLIMs

    Outputs:
        -- structured python output, generally either a dictionary or list

    Main objectives:
        -- enable function calling with small, locally-running models,
        -- simplify prompts by defining specific functions and fine-tuning the model to respond accordingly
            without 'prompt magic'
        -- standardized outputs that can be handled programmatically as part of a multi-step workflow.
    """


from llmware.models import ModelCatalog


def discover_slim_models():

    """ Discover a list of SLIM tools in the Model Catalog.

    -- SLIMs are available in both traditional Pytorch and quantized GGUF packages.
    -- Generally, we train/fine-tune in Pytorch and then package in 4-bit quantized GGUF for inference.
    -- By default, we designate the GGUF versions with 'tool' or 'gguf' in their names.
    -- GGUF versions are generally faster to load, faster for inference and use less memory in most environments."""

    tools = ModelCatalog().list_llm_tools()
    tool_map = ModelCatalog().get_llm_fx_mapping()

    print("\nList of SLIM model tools (GGUF) in the ModelCatalog\n")

    for i, tool in enumerate(tools):
        model_card = ModelCatalog().lookup_model_card(tool_map[tool])
        print(f"{i} - tool: {tool} - "
              f"model_name: {model_card['model_name']} - "
              f"model_family: {model_card['model_family']}")

    return 0


def hello_world_slim():

    """ SLIM models can be identified in the ModelCatalog like any llmware model.  Instead of using
    inference method, SLIM models are used with the function_call method that prepares a special prompt
    instruction, and takes optional parameters.

    This example shows a series of function calls with different SLIM models.

    Please note that the first time the models will be pulled from the llmware Huggingface repository, and will
    take a couple of minutes.  Future calls will be much faster once cached in memory locally. """

    print("\nExecuting Function Call Inferences with SLIMs\n")

    #   Sentiment Analysis

    passage1 = ("This is one of the best quarters we can remember for the industrial sector "
               "with significant growth across the board in new order volume, as well as price "
               "increases in excess of inflation.  We continue to see very strong demand, especially "
               "in Asia and Europe. Accordingly, we remain bullish on the tier 1 suppliers and would "
               "be accumulating more stock on any dips.")

    #   here are the two key lines of code
    model = ModelCatalog().load_model("slim-sentiment-tool")
    response = model.function_call(passage1)

    print("sentiment response: ", response['llm_response'])

    #  Named Entity Recognition

    passage2 = "Michael Johnson was a famous Olympic sprinter from the U.S. in the early 2000s."

    model = ModelCatalog().load_model("slim-ner-tool")
    response = model.function_call(passage2)

    print("ner response: ", response['llm_response'])

    #   Extract anything with Slim-extract

    passage3 = ("Adobe shares tumbled as much as 11% in extended trading Thursday after the design software maker "
    "issued strong fiscal first-quarter results but came up slightly short on quarterly revenue guidance. "
    "Here’s how the company did, compared with estimates from analysts polled by LSEG, formerly known as Refinitiv: "
    "Earnings per share: $4.48 adjusted vs. $4.38 expected Revenue: $5.18 billion vs. $5.14 billion expected "
    "Adobe’s revenue grew 11% year over year in the quarter, which ended March 1, according to a statement. "
    "Net income decreased to $620 million, or $1.36 per share, from $1.25 billion, or $2.71 per share, "
    "in the same quarter a year ago. During the quarter, Adobe abandoned its $20 billion acquisition of "
    "design software startup Figma after U.K. regulators found competitive concerns. The company paid "
    "Figma a $1 billion termination fee.")

    model = ModelCatalog().load_model("slim-extract-tool")
    response = model.function_call(passage3, function="extract", params=["revenue growth"])

    print("extract response: ", response['llm_response'])

    #   Generate questions with Slim-Q-Gen

    model = ModelCatalog().load_model("slim-q-gen-tiny-tool", temperature=0.2, sample=True)
    #   supported params - "question", "multiple choice", "boolean"
    response = model.function_call(passage3, params=['multiple choice'])

    print("question generation response: ", response['llm_response'])

    #   Generate topic

    model = ModelCatalog().load_model("slim-topics-tool")
    response = model.function_call(passage3)

    print("topics response: ", response['llm_response'])

    #   Generate headline summary with slim-xsum
    model = ModelCatalog().load_model("slim-xsum-tool", temperature=0.0, sample=False)
    response = model.function_call(passage3)

    print("xsum response: ", response['llm_response'])

    #   Generate boolean with optional '(explain)` in parameter
    model = ModelCatalog().load_model("slim-boolean-tool")
    response = model.function_call(passage3, params=["Did Adobe revenue increase? (explain)"])

    print("boolean response: ", response['llm_response'])

    #   Generate tags
    model = ModelCatalog().load_model("slim-tags-tool", temperature=0.0, sample=False)
    response = model.function_call(passage3)

    print("tags response: ", response['llm_response'])

    return 0


def using_logits_and_integrating_into_process():

    """ This example shows two key elements of function calling SLIM models -

    1.  Using Logit Information to indicate confidence levels, especially for classifications.
    2.  Using the structured dictionary generated for programmatic handling in a larger process.

    """

    print("\nExample: using logits and integrating into process\n")

    text_passage = ("On balance, this was an average result, with earnings in line with expectations and "
                    "no big surprises to either the positive or the negative.")

    #   two key lines (load_model + execute function_call) + additional logit_analysis step
    sentiment_model = ModelCatalog().load_model("slim-sentiment-tool", get_logits=True)
    response = sentiment_model.function_call(text_passage)
    analysis = ModelCatalog().logit_analysis(response,sentiment_model.model_card, sentiment_model.hf_tokenizer_name)

    print("sentiment response: ", response['llm_response'])

    print("\nAnalyzing response")
    for keys, values in analysis.items():
        print(f"{keys} - {values}")

    #   two key attributes of the sentiment output dictionary
    sentiment_value = response["llm_response"]["sentiment"]
    confidence_level = analysis["confidence_score"]

    #   use the sentiment classification as a 'if...then' decision point in a process
    if "positive" in sentiment_value:
        print("sentiment is positive .... will take 'positive' analysis path ...", sentiment_value)
    else:
        print("sentiment is negative .... will take 'negative' analysis path ...", sentiment_value)

    if "positive" in sentiment_value and confidence_level > 0.8:
        print("sentiment is positive with high confidence ... ", sentiment_value, confidence_level)

    return 0


if __name__ == "__main__":

    #   discovering slim models in the llmware catalog
    discover_slim_models()

    #   running function call inferences
    hello_world_slim()

    #   doing interesting stuff with the output
    using_logits_and_integrating_into_process()


