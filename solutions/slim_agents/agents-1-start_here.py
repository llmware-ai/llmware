
""" The objective of this script is to provide several entrypoints into LLMWare models and to start integrating
these models into larger workflows.

    Prereqs:

        `pip3 install llmware`

    This is the 'entrypoint' example that provides a general introduction of llmware models.

    If you have any dependency install issues, please review the README, docs link, or raise an Issue.

    Usually, if there is a missing dependency, the code will give the warning - and a clear
    direction like `pip install transformers' required for this example, etc.

    As an alternative to pip install ... if you prefer, you can also clone the repo from github -
    which provides a benefit of having access to 100+ examples.

    To clone the repo:

        git clone "https://www.github.com/llmware-ai/llmware.git"
        sh "welcome_to_llmware.sh"

    The second script "welcome_to_llmware.sh" will install all of the dependencies.

    If using Windows, then use the "welcome_to_llmware_windows.sh" script.

"""


from llmware.models import ModelCatalog

#   GETTING STARTED - all LLMWare models are accessible through the ModelCatalog generally consisting of two steps
#   to access any model

#   Step 1 - load the model - pulls from global repo the first time, and then automatically caches locally
#   Step 2 - use the model with inference or function call

#   'Standard' Models use 'inference' and take a general text input and provide a general text output

model = ModelCatalog().load_model("bling-answer-tool")
response = model.inference("My son is 21 years old.\nHow old is my son?")

print("\nresponse: ", response)

#   Optional parameters can improve results
model = ModelCatalog().load_model("bling-phi-3-gguf", temperature=0.0,sample=False, max_output=200)

#   all LLMWare models have been fine-tuned to assume that the input will include a text passage, and that the
#   model's main job is to 'read' the passage, and then 'answer' a question based on that information

text_passage = "The company's stock price increased by $3 after reporting positive earnings."
prompt = "What was the increase in the stock price?"

response = model.inference(prompt,add_context=text_passage)

print("\nresponse: ", response)

#   inference models can also be integrated into Prompts - which provide advanced handling for integrating
#   with knowledge retrieval, managing source information, and providing fact-checking

#   Discovering other models is easy -> to invoke a model, simply use the 'model_name' and pass in .load_model()
#   note: model_names starting with 'bling', 'dragon' and 'slim' are llmware models
#   -- we do include other popular models such as phi-3, qwen-2, yi, llama-3, mistral
#   -- it is easy to extend the model catalog to include other 3rd party models, including ollama and lm studio
#   -- we do support open ai, anthropic, cohere and google api models as well

all_generative_models = ModelCatalog().list_generative_local_models()
print("\n\nModel Catalog - load model with ModelCatalog().load_model(model_name)")
for i, model in enumerate(all_generative_models):

    model_name = model["model_name"]
    model_family = model["model_family"]

    print("model: ", i, model)

#   slim models are 'Function Calling' Models that perform a specialized task and output python dictionaries
#   -- by design, slim models are specialists that perform single function
#   -- by design, slim models generally do not require any specific 'prompt instructions', but will often accept a
#      a "parameter" which is passed to the function.

model = ModelCatalog().load_model("slim-sentiment-tool")
response = model.function_call("That was the worst earnings call ever - what a disaster.")

#   the 'overall' model response is just a python dictionary
print("\nresponse: ", response)
print("llm_response: ", response['llm_response'])
print("sentiment: ", response['llm_response']['sentiment'])

#   here are several slim models applied against a common earnings extract

text_passage = ("Here’s what Costco reported for its fiscal second quarter of 2024 compared with what Wall Street "
                "was expecting, based on a survey of analysts by LSEG, formerly known as Refinitiv: Earnings "
                "per share: $3.92 vs. $3.62 expected.  Revenue: $58.44 billion vs. $59.16 billion expected "
                "In the three-month period that ended Feb. 18, Costco’s net income rose to $1.74 billion, or "
                "$3.92 per share, compared with $1.47 billion, or $3.30 per share, a year earlier. ")

#   extract model takes a 'key' for a parameter, and looks for the 'value' in the text

model = ModelCatalog().load_model("slim-extract-tool")

#   the general structure of a function call includes a text passage input, a function and parameters
response = model.function_call(text_passage,function="extract",params=["revenue"])

print("\nextract response: ", response)

#   topics model will generate a 1-2 word summary that captures the key topic of the passage

model = ModelCatalog().load_model("slim-topics-tool")
response = model.function_call(text_passage,function="classify", params=["topic"])

print("topics response: ", response)

#   tags model will generate a list of key words that can be used as 'tags' to summarize and lookup the information
model = ModelCatalog().load_model("slim-tags-tool")
response = model.function_call(text_passage,function="classify", params=["tags"])

print("tags response: ", response)

#   xsum model generates a 'headline' summary (e.g., 'extreme summarization')
model = ModelCatalog().load_model("slim-xsum-tool")

#   where the parameters can be inferred, they are optional
response = model.function_call(text_passage)

print("xsum (extreme summarization) response - ", response)

#   boolean model answers a question with Yes/No, and is provided an optional '(explain)' will provide an explanation
model = ModelCatalog().load_model("slim-boolean-tool")
response = model.function_call(text_passage,params=["did earnings beat expectations? (explain)"])
print("boolean yes-no response - ", response)

#   Function calling models generally come with a test set that is a great way to learn how they work
#   --please note that each test can take a few minutes with 20-40 test questions

ModelCatalog().tool_test_run("slim-topics-tool")
ModelCatalog().tool_test_run("slim-tags-tool")
ModelCatalog().tool_test_run("slim-emotions-tool")
ModelCatalog().tool_test_run("slim-summary-tool")
ModelCatalog().tool_test_run("slim-xsum-tool")

#   Function calling models can be integrated into Agent processes which can orchestrate processes comprising multiple
#   models and steps - most of our use cases will use the function calling models in that context

#   Last note: most of the models are packaged as "gguf" - usually identified as GGUFGenerativeModel, or
#   with '-gguf' or '-tool' at the end of their name.   These models are optimized to run most efficiently on
#   a CPU-based laptop (especially Mac OS).   You can also try the standard Pytorch versions of these models,
#   which should yield virtually identical results, but will be slower.

#   Check out some of the other examples in the other files for more details and building off these recipes

#    NEW - if you are running on Windows machines, then we would encourage you to also check out the following two examples
#    -- using_openvino - /examples/Models/using_openvino_models.py
#    -- using_onnx - /examples/Models/using_onnx_models.py

#   Welcome to LLMWare!


