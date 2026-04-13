
""" This example shows an end-to-end scenario for invoice processing that can be run locally and without a
database.  The example shows how to combine the use of parsing combined with prompts_with_sources to rapidly
iterate through a batch of invoices and ask a set of questions, and then save the full output to both
(1) .jsonl for integration into an upstream application/database and (2) to a CSV for human review in excel.

    note: the sample code pulls from a public repo to load the sample invoice documents the first time -
    please feel free to substitute with your own invoice documents (PDF/DOCX/PPTX/XLSX/CSV/TXT) if you prefer.

    this example does not require a database or embedding

    this example can be run locally on a laptop by setting 'run_on_cpu=True'
    if 'run_on_cpu==False", then please see the example 'launch_llmware_inference_server.py'
    to configure and set up a 'pop-up' GPU inference server in just a few minutes
"""

import os
import re

from llmware.prompts import Prompt, HumanInTheLoop
from llmware.configs import LLMWareConfig
from llmware.setup import Setup
from llmware.models import ModelCatalog


def invoice_processing(run_on_cpu=True):

    #   Step 1 - Pull down the sample files from S3 through the .load_sample_files() command
    #   --note: if you need to refresh the sample files, set 'over_write=True'
    print("update: Downloading Sample Files")

    sample_files_path = Setup().load_sample_files(over_write=False)
    invoices_path = os.path.join(sample_files_path, "Invoices")

    #   Step 2 - simple sample query list - each question will be asked to each invoice
    query_list = ["What is the total amount of the invoice?",
                  "What is the invoice number?",
                  "What are the names of the two parties?"]

    #   Step 3 - Load Model

    if run_on_cpu:

        #   load local bling model that can run on cpu/laptop

        #   note: bling-1b-0.1 is the *fastest* & *smallest*, but will make more errors than larger BLING models
        # model_name = "llmware/bling-1b-0.1"

        #   try the new bling-phi-3 quantized with gguf - most accurate
        model_name = 'bling-phi-3-gguf'
    else:

        #   use GPU-based inference server to process
        #  *** see the launch_llmware_inference_server.py example script to setup ***

        server_uri_string = "http://11.123.456.789:8088"    # insert your server_uri_string
        server_secret_key = "demo-test"
        ModelCatalog().setup_custom_llmware_inference_server(server_uri_string, secret_key=server_secret_key)
        model_name = "llmware-inference-server"

    #   attach inference server to prompt object
    prompter = Prompt().load_model(model_name)

    #   Step 4 - main loop thru folder of invoices

    for i, invoice in enumerate(os.listdir(invoices_path)):

        #   just in case (legacy on mac os file system - not needed on linux or windows)
        if invoice != ".DS_Store":

            print("\nAnalyzing invoice: ", str(i + 1), invoice)

            for question in query_list:

                #   Step 4A - parses the invoices in memory and attaches as a source to the Prompt
                source = prompter.add_source_document(invoices_path,invoice)

                #   Step 4B - executes the prompt on the LLM (with the loaded source)
                output = prompter.prompt_with_source(question,prompt_name="default_with_context")

                for i, response in enumerate(output):
                    print("LLM Response - ", question, " - ", re.sub("[\n]"," ", response["llm_response"]))

                prompter.clear_source_materials()

    # Save jsonl report with full transaction history to /prompt_history folder
    print("\nupdate: prompt state saved at: ", os.path.join(LLMWareConfig.get_prompt_path(),prompter.prompt_id))

    prompter.save_state()

    # Generate CSV report for easy Human review in Excel
    csv_output = HumanInTheLoop(prompter).export_current_interaction_to_csv()

    print("\nupdate: csv output for human review - ", csv_output)

    return 0


if __name__ == "__main__":

    invoice_processing(run_on_cpu=True)


