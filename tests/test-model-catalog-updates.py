
import os
import time

from llmware.models import ModelCatalog, LLMWareModel
from llmware.prompts import Prompt, HumanInTheLoop
from llmware.configs import LLMWareConfig


def new_expanded_list_in_model_catalog():

    #   new models from OpenAI (turbo-3.5 and turbo-4 added
    #   new embedding models (v3) from Cohere added
    #   'bling' models on HuggingFace added directly, so that they can be invoked and discovered like any other model

    mc = ModelCatalog()

    for i, models in enumerate(mc.global_model_list):

        print("update: models in catalog - ", i, models)

    return 0


# new_expanded_list_in_model_catalog()


def add_new_model_name_to_catalog_directly():

    # new model name
    new_model_card = {"model_name": "llmware2", "display_name": "LLMWare-GPT2", "model_family": "LLMWareModel",
                      "model_category": "generative_api", "model_location": "api", "is_trainable": "no",
                      "context_window": 2048}

    mc = ModelCatalog()
    mc.register_new_model_card(new_model_card)

    # print list of models and will now include in the new_model_card in the registry list
    for i, models in enumerate(mc.global_model_list):
        print("update: models in catalog - ", i, models)

    return 0


# add_new_model_name_to_catalog_directly()


def add_new_model_name_to_catalog_in_prompt():

    # new model name in ***existing model classes***
    #   --enables user to add a newly created model (or some model_name not in our global catalog)

    new_model_card = {"model_name": "llmware2", "display_name": "LLMWare-GPT2", "model_family": "LLMWareModel",
                      "model_category": "generative_api", "model_location": "api", "is_trainable": "no", "context_window": 2048}

    # create new Prompt object, which now has its own copy of the ModelCatalog() object
    prompter = Prompt()

    # register new model_card in the catalog associated with the prompt
    prompter.model_catalog.register_new_model_card(new_model_card)

    # now, the new 'custom' model can be loaded into the prompt
    prompter.load_model("llmware2", api_key="llmware-custom-api-key")

    return 0


def register_custom_llmware_inference_server():

    #   adds a LLMWare Model class to be used for remote API-based models
    #   --intended for use case with 7B open source model running on a remote GPU server
    #   --will be used to support AIB specific use cases, but in principle, enables any custom API-based model

    #   --note:  the setup method on the client-side is very thin
    #            -> just puts the uri_string and secret_key in os.environ variables

    uri_string = "http://184.105.6.239:8080"
    secret_key = "demo-test"
    ModelCatalog().setup_custom_llmware_inference_server(uri_string, secret_key=secret_key)

    return 0


def new_llmware_model_class():

    #   adds a LLMWare Model class to be used for remote API-based models
    #   --will be used to support AIB specific use cases, but in principle, enables any custom API-based model

    register_custom_llmware_inference_server()

    # use LLMWareModel directly in prompt, like any other model
    prompter = Prompt()
    prompter.load_model("llmware-inference-server")
    output = prompter.prompt_main("sample question", context="This is a sample context")

    # directly instantiate LLMWareModel
    llmware_gpt = LLMWareModel(model_name="llmware-inference-server")
    response = llmware_gpt.inference("sample prompt", add_context="This is a sample context")

    return 0


def integrate_llmware_remote_inference_server_into_prompt():

    # setup custom inference on GPU server
    register_custom_llmware_inference_server()

    # load "llmware" model into prompt-> which will connect to the remote GPU server
    prompter = Prompt().load_model("llmware-inference-server")

    prompt_list = [

        {"context": "Services Vendor Inc. \n100 Elm Street Pleasantville, NY \nTO Alpha Inc. 5900 1st Street "
                    "Los Angeles, CA \nDescription Front End Engineering Service $5000.00 \n Back End Engineering"
                    " Service $7500.00 \n Quality Assurance Manager $10,000.00 \n Total Amount $22,500.00 \n"
                    "Make all checks payable to Services Vendor Inc. Payment is due within 30 days."
                    "If you have any questions concerning this invoice, contact Bia Hermes. "
                    "THANK YOU FOR YOUR BUSINESS!  INVOICE INVOICE # 0001 DATE 01/01/2022 FOR Alpha Project P.O. # 1000",
         "query": "What is the PO number?", "answer": "# 1000"}
        ]

    for i, prompt in enumerate(prompt_list):

        print("update: query - ", prompt["query"])
        print("update: context - ", prompt["context"])

        response = prompter.prompt_main(prompt["query"],context=prompt["context"])

        print("update: response - SUCCESS - ", response)

        # note: previously the response dictionary for the prompt_main method was missing the evidence_metadata key
        #   --without the evidence_metadata key, fact checking could not be run on a "prompt_main" inference
        #   --to fix this, a simple/placeholder "evidence_metadata" is added to every prompt_main call
        #   --this "placeholder" is over-written if prompt_with_sources is used
        #   --this is the placeholder that is added in the prompt_main method:
        #
        #   response.update({"evidence_metadata": [{"evidence_start_char":0, "evidence_stop_char":
        #                                           len(prompt["context"]),
        #                                           "page_num": "NA", "source_name": "NA"}]})

        # fact check now works, but of course, there is no source_name or page_num since not provided in the prompt

        fc = prompter.evidence_check_numbers(response)

        for entries in fc:
            print("update: fact check - ", entries["fact_check"])

        sc = prompter.evidence_comparison_stats(response)
        for entries in sc:
            print("update: comparison stats - ", entries["comparison_stats"])

        sr = prompter.evidence_check_sources(response)
        for entries in sr:
            print("update: sources - ", entries["source_review"])

    return 0


integrate_llmware_remote_inference_server_into_prompt()


def invoice_processing():

    # setup custom inference on GPU server
    register_custom_llmware_inference_server()

    # in setting up prompt object load "llmware" model
    prompter = Prompt().load_model("llmware-inference-server")

    t0 = time.time()

    # my invoices folder path -> this is a set of ~40 of our template invoice documents
    invoices_path = "/Users/darrenoberst/llmware_data/test_files/invoices/"

    query_list = ["What is the total amount of the invoice?",
                  "What is the invoice number?",
                  "What are the names of the two parties?",
                  "What is a list of the items purchased?"
                  # "What is a list of the key summary points?"
                  ]

    for i, invoice in enumerate(os.listdir(invoices_path)):

        print("\nAnalyzing invoice: ", str(i+1), invoice)

        for question in query_list:

            source = prompter.add_source_document(invoices_path, invoice)

            response = prompter.prompt_with_source(question,prompt_name="default_with_context")

            print("\nupdate: question - ", question)
            print("update: llm response - ", response[0]["llm_response"])

            fc = prompter.evidence_check_numbers(response)

            for entries in fc:
                if entries:
                    print("update: fact check - ", entries["fact_check"])

            sc = prompter.evidence_comparison_stats(response)
            for entries in sc:
                print("update: comparison stats - ", entries["comparison_stats"])

            sr = prompter.evidence_check_sources(response)
            for entries in sr:
                print("update: sources - ", entries["source_review"])

            prompter.clear_source_materials()

    # capture time of the processing
    print("\nupdate: time cycle: ", time.time() - t0)

    # Save jsonl report to jsonl to /prompt_history folder
    print("\nupdate: prompt state saved at: ", os.path.join(LLMWareConfig.get_prompt_path(),prompter.prompt_id))

    prompter.save_state()

    csv_output = HumanInTheLoop(prompter).export_current_interaction_to_csv()

    print("csv output - ", csv_output)

    return 0


# note: this is a nice workflow - will convert into a demo video in the next 2-3 days
invoice_processing()
