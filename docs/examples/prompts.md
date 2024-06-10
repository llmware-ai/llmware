---
layout: default
title: Prompts
parent: Examples
nav_order: 6
description: overview of the major modules and classes of LLMWare  
permalink: /examples/prompts
---
# Prompts - Introduction by Examples
We introduce ``llmware`` through self-contained examples.

# Basic RAG Scenario - Invoice Processing 

```python

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
```

# Document Summarizer 

```python

""" This Example shows a packaged 'document_summarizer' prompt using the slim-summary-tool. It shows a variety of
techniques to summarize documents generally larger than a LLM context window, and how to assemble multiple source
batches from the document, as well as using a 'query' and 'topic' to focus on specific segments of the document. """

import os

from llmware.prompts import Prompt
from llmware.setup import Setup


def test_summarize_document(example="jd salinger"):

    # pull a sample document (or substitute a file_path and file_name of your own)
    sample_files_path = Setup().load_sample_files(over_write=False)

    topic = None
    query = None
    fp = None
    fn = None

    if example not in ["jd salinger", "employment terms", "just the comp", "un resolutions"]:
        print ("not found example")
        return []

    if example == "jd salinger":
        fp = os.path.join(sample_files_path, "SmallLibrary")
        fn = "Jd-Salinger-Biography.docx"
        topic = "jd salinger"
        query = None

    if example == "employment terms":
        fp = os.path.join(sample_files_path, "Agreements")
        fn = "Athena EXECUTIVE EMPLOYMENT AGREEMENT.pdf"
        topic = "executive compensation terms"
        query = None

    if example == "just the comp":
        fp = os.path.join(sample_files_path, "Agreements")
        fn = "Athena EXECUTIVE EMPLOYMENT AGREEMENT.pdf"
        topic = "executive compensation terms"
        query = "base salary"

    if example == "un resolutions":
        fp = os.path.join(sample_files_path, "SmallLibrary")
        fn = "N2126108.pdf"
        # fn = "N2137825.pdf"
        topic = "key points"
        query = None

    # optional parameters:  'query' - will select among blocks with the query term
    #                       'topic' - will pass a topic/issue as the parameter to the model to 'focus' the summary
    #                       'max_batch_cap' - caps the number of batches sent to the model
    #                       'text_only' - returns just the summary text aggregated

    kp = Prompt().summarize_document_fc(fp, fn, topic=topic, query=query, text_only=True, max_batch_cap=15)

    print(f"\nDocument summary completed - {len(kp)} Points")
    for i, points in enumerate(kp):
        print(i, points)

    return 0


if __name__ == "__main__":

    print(f"\nExample: Summarize Documents\n")

    #   4 examples - ["jd salinger", "employment terms", "just the comp", "un resolutions"]
    #   -- "jd salinger" - summarizes key points about jd salinger from short biography document
    #   -- "employment terms" - summarizes the executive compensation terms across 15 page document
    #   -- "just the comp" - queries to find subset of document and then summarizes the key terms
    #   -- "un resolutions" - summarizes the un resolutions document

    summary_direct = test_summarize_document(example="employment terms")
```

For more examples, see the [prompt examples]((https://www.github.com/llmware-ai/llmware/tree/main/examples/Prompts/) in the main repo.   

Check back often - we are updating these examples regularly - and many of these examples have companion videos as well.  



# More information about the project - [see main repository](https://www.github.com/llmware-ai/llmware.git)


# About the project

`llmware` is &copy; 2023-{{ "now" | date: "%Y" }} by [AI Bloks](https://www.aibloks.com/home).

## Contributing
Please first discuss any change you want to make publicly, for example on GitHub via raising an [issue](https://github.com/llmware-ai/llmware/issues) or starting a [new discussion](https://github.com/llmware-ai/llmware/discussions).
You can also write an email or start a discussion on our Discrod channel.
Read more about becoming a contributor in the [GitHub repo](https://github.com/llmware-ai/llmware/blob/main/CONTRIBUTING.md).

## Code of conduct
We welcome everyone into the ``llmware`` community.
[View our Code of Conduct](https://github.com/llmware-ai/llmware/blob/main/CODE_OF_CONDUCT.md) in our GitHub repository.

## ``llmware`` and [AI Bloks](https://www.aibloks.com/home)
``llmware`` is an open source project from [AI Bloks](https://www.aibloks.com/home) - the company behind ``llmware``.
The company offers a Software as a Service (SaaS) Retrieval Augmented Generation (RAG) service.
[AI Bloks](https://www.aibloks.com/home) was founded by [Namee Oberst](https://www.linkedin.com/in/nameeoberst/) and [Darren Oberst](https://www.linkedin.com/in/darren-oberst-34a4b54/) in October 2022.

## License

`llmware` is distributed by an [Apache-2.0 license](https://www.github.com/llmware-ai/llmware/blob/main/LICENSE).

## Thank you to the contributors of ``llmware``!
<ul class="list-style-none">
{% for contributor in site.github.contributors %}
  <li class="d-inline-block mr-1">
     <a href="{{ contributor.html_url }}">
        <img src="{{ contributor.avatar_url }}" width="32" height="32" alt="{{ contributor.login }}">
    </a>
  </li>
{% endfor %}
</ul>


---
<ul class="list-style-none">
    <li class="d-inline-block mr-1">
        <a href="https://discord.gg/MhZn5Nc39h"><span><i class="fa-brands fa-discord"></i></span></a>
    </li>
    <li class="d-inline-block mr-1">
        <a href="https://www.youtube.com/@llmware"><span><i class="fa-brands fa-youtube"></i></span></a>
    </li>
    <li class="d-inline-block mr-1">
        <a href="https://huggingface.co/llmware"><span><img src="assets/images/hf-logo.svg" alt="Hugging Face" class="hugging-face-logo"/></span></a>
    </li>
    <li class="d-inline-block mr-1">
        <a href="https://www.linkedin.com/company/aibloks/"><span><i class="fa-brands fa-linkedin"></i></span></a>
    </li>
    <li class="d-inline-block mr-1">
        <a href="https://twitter.com/AiBloks"><span><i class="fa-brands fa-square-x-twitter"></i></span></a>
    </li>
    <li class="d-inline-block mr-1">
        <a href="https://www.instagram.com/aibloks/"><span><i class="fa-brands fa-instagram"></i></span></a>
    </li>
</ul>
---

