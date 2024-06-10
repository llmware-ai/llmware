---
layout: default
title: Overview
parent: Getting Started
nav_order: 1
permalink: /getting_started/overview
---

## Welcome to  
<ul class="list-style-none">
    <li class="d-inline-block mr-1">
        <a href="https://llmware.ai/"><span><img src="assets/images/llmware_logo_color_cropped.png" alt="llmware" width="360" height="60"/></span></a>
    </li>
</ul>  

## 🧰🛠️🔩Building Enterprise RAG Pipelines with Small, Specialized Models  

`llmware` provides a unified framework for building LLM-based applications (e.g, RAG, Agents), using small, specialized models that can be deployed privately, integrated with enterprise knowledge sources safely and securely, and cost-effectively tuned and adapted for any business process.  

 `llmware` has two main components:  
 
 1.  **RAG Pipeline** - integrated components for the full lifecycle of connecting knowledge sources to generative AI models; and 

 2.  **50+ small, specialized models** fine-tuned for key tasks in enterprise process automation, including fact-based question-answering, classification, summarization, and extraction.  

By bringing together both of these components, along with integrating leading open source models and underlying technologies, `llmware` offers a comprehensive set of tools to rapidly build knowledge-based enterprise LLM applications.  

Most of our examples can be run without a GPU server - get started right away on your laptop.   

## 🎯  Key features 
Writing code with`llmware` is based on a few main concepts:

<details>
<summary><b>Model Catalog</b>: Access all models the same way with easy lookup, regardless of underlying implementation. 
</summary>  


```python
#   150+ Models in Catalog with 50+ RAG-optimized BLING, DRAGON and Industry BERT models
#   Full support for GGUF, HuggingFace, Sentence Transformers and major API-based models
#   Easy to extend to add custom models - see examples

from llmware.models import ModelCatalog
from llmware.prompts import Prompt

#   all models accessed through the ModelCatalog
models = ModelCatalog().list_all_models()

#   to use any model in the ModelCatalog - "load_model" method and pass the model_name parameter
my_model = ModelCatalog().load_model("llmware/bling-phi-3-gguf")
output = my_model.inference("what is the future of AI?", add_context="Here is the article to read")

#   to integrate model into a Prompt
prompter = Prompt().load_model("llmware/bling-tiny-llama-v0")
response = prompter.prompt_main("what is the future of AI?", context="Insert Sources of information")
```

</details>  

<details>  
<summary><b>Library</b>:  ingest, organize and index a collection of knowledge at scale - Parse, Text Chunk and Embed. </summary>  

```python

from llmware.library import Library

#   to parse and text chunk a set of documents (pdf, pptx, docx, xlsx, txt, csv, md, json/jsonl, wav, png, jpg, html)  

#   step 1 - create a library, which is the 'knowledge-base container' construct
#          - libraries have both text collection (DB) resources, and file resources (e.g., llmware_data/accounts/{library_name})
#          - embeddings and queries are run against a library

lib = Library().create_new_library("my_library")

#    step 2 - add_files is the universal ingestion function - point it at a local file folder with mixed file types
#           - files will be routed by file extension to the correct parser, parsed, text chunked and indexed in text collection DB

lib.add_files("/folder/path/to/my/files")

#   to install an embedding on a library - pick an embedding model and vector_db
lib.install_new_embedding(embedding_model_name="mini-lm-sbert", vector_db="milvus", batch_size=500)

#   to add a second embedding to the same library (mix-and-match models + vector db)  
lib.install_new_embedding(embedding_model_name="industry-bert-sec", vector_db="chromadb", batch_size=100)

#   easy to create multiple libraries for different projects and groups

finance_lib = Library().create_new_library("finance_q4_2023")
finance_lib.add_files("/finance_folder/")

hr_lib = Library().create_new_library("hr_policies")
hr_lib.add_files("/hr_folder/")

#    pull library card with key metadata - documents, text chunks, images, tables, embedding record
lib_card = Library().get_library_card("my_library")

#   see all libraries
all_my_libs = Library().get_all_library_cards()

```
</details>  

<details> 
<summary><b>Query</b>: query libraries with mix of text, semantic, hybrid, metadata, and custom filters. </summary>

```python

from llmware.retrieval import Query
from llmware.library import Library

#   step 1 - load the previously created library 
lib = Library().load_library("my_library")

#   step 2 - create a query object and pass the library
q = Query(lib)

#    step 3 - run lots of different queries  (many other options in the examples)

#    basic text query
results1 = q.text_query("text query", result_count=20, exact_mode=False)

#    semantic query
results2 = q.semantic_query("semantic query", result_count=10)

#    combining a text query restricted to only certain documents in the library and "exact" match to the query
results3 = q.text_query_with_document_filter("new query", {"file_name": "selected file name"}, exact_mode=True)

#   to apply a specific embedding (if multiple on library), pass the names when creating the query object
q2 = Query(lib, embedding_model_name="mini_lm_sbert", vector_db="milvus")
results4 = q2.semantic_query("new semantic query")
```

</details>  

<details>
<summary><b>Prompt with Sources</b>: the easiest way to combine knowledge retrieval with a LLM inference. </summary>

```python

from llmware.prompts import Prompt
from llmware.retrieval import Query
from llmware.library import Library

#   build a prompt
prompter = Prompt().load_model("llmware/bling-tiny-llama-v0")

#   add a file -> file is parsed, text chunked, filtered by query, and then packaged as model-ready context,
#   including in batches, if needed, to fit the model context window

source = prompter.add_source_document("/folder/to/one/doc/", "filename", query="fast query")

#   attach query results (from a Query) into a Prompt
my_lib = Library().load_library("my_library")
results = Query(my_lib).query("my query")
source2 = prompter.add_source_query_results(results)

#   run a new query against a library and load directly into a prompt
source3 = prompter.add_source_new_query(my_lib, query="my new query", query_type="semantic", result_count=15)

#   to run inference with 'prompt with sources'
responses = prompter.prompt_with_source("my query")

#   to run fact-checks - post inference
fact_check = prompter.evidence_check_sources(responses)

#   to view source materials (batched 'model-ready' and attached to prompt)
source_materials = prompter.review_sources_summary()

#   to see the full prompt history
prompt_history = prompter.get_current_history()
```

</details>  

<details> 
<summary><b>RAG-Optimized Models</b> -  1-7B parameter models designed for RAG workflow integration and running locally. </summary>  

```
""" This 'Hello World' example demonstrates how to get started using local BLING models with provided context, using both
Pytorch and GGUF versions. """

import time
from llmware.prompts import Prompt


def hello_world_questions():

    test_list = [

    {"query": "What is the total amount of the invoice?",
     "answer": "$22,500.00",
     "context": "Services Vendor Inc. \n100 Elm Street Pleasantville, NY \nTO Alpha Inc. 5900 1st Street "
                "Los Angeles, CA \nDescription Front End Engineering Service $5000.00 \n Back End Engineering"
                " Service $7500.00 \n Quality Assurance Manager $10,000.00 \n Total Amount $22,500.00 \n"
                "Make all checks payable to Services Vendor Inc. Payment is due within 30 days."
                "If you have any questions concerning this invoice, contact Bia Hermes. "
                "THANK YOU FOR YOUR BUSINESS!  INVOICE INVOICE # 0001 DATE 01/01/2022 FOR Alpha Project P.O. # 1000"},

    {"query": "What was the amount of the trade surplus?",
     "answer": "62.4 billion yen ($416.6 million)",
     "context": "Japan’s September trade balance swings into surplus, surprising expectations"
                "Japan recorded a trade surplus of 62.4 billion yen ($416.6 million) for September, "
                "beating expectations from economists polled by Reuters for a trade deficit of 42.5 "
                "billion yen. Data from Japan’s customs agency revealed that exports in September "
                "increased 4.3% year on year, while imports slid 16.3% compared to the same period "
                "last year. According to FactSet, exports to Asia fell for the ninth straight month, "
                "which reflected ongoing China weakness. Exports were supported by shipments to "
                "Western markets, FactSet added. — Lim Hui Jie"},

    {"query": "When did the LISP machine market collapse?",
     "answer": "1987.",
     "context": "The attendees became the leaders of AI research in the 1960s."
                "  They and their students produced programs that the press described as 'astonishing': "
                "computers were learning checkers strategies, solving word problems in algebra, "
                "proving logical theorems and speaking English.  By the middle of the 1960s, research in "
                "the U.S. was heavily funded by the Department of Defense and laboratories had been "
                "established around the world. Herbert Simon predicted, 'machines will be capable, "
                "within twenty years, of doing any work a man can do'.  Marvin Minsky agreed, writing, "
                "'within a generation ... the problem of creating 'artificial intelligence' will "
                "substantially be solved'. They had, however, underestimated the difficulty of the problem.  "
                "Both the U.S. and British governments cut off exploratory research in response "
                "to the criticism of Sir James Lighthill and ongoing pressure from the US Congress "
                "to fund more productive projects. Minsky's and Papert's book Perceptrons was understood "
                "as proving that artificial neural networks approach would never be useful for solving "
                "real-world tasks, thus discrediting the approach altogether.  The 'AI winter', a period "
                "when obtaining funding for AI projects was difficult, followed.  In the early 1980s, "
                "AI research was revived by the commercial success of expert systems, a form of AI "
                "program that simulated the knowledge and analytical skills of human experts. By 1985, "
                "the market for AI had reached over a billion dollars. At the same time, Japan's fifth "
                "generation computer project inspired the U.S. and British governments to restore funding "
                "for academic research. However, beginning with the collapse of the Lisp Machine market "
                "in 1987, AI once again fell into disrepute, and a second, longer-lasting winter began."},

    {"query": "What is the current rate on 10-year treasuries?",
     "answer": "4.58%",
     "context": "Stocks rallied Friday even after the release of stronger-than-expected U.S. jobs data "
                "and a major increase in Treasury yields.  The Dow Jones Industrial Average gained 195.12 points, "
                "or 0.76%, to close at 31,419.58. The S&P 500 added 1.59% at 4,008.50. The tech-heavy "
                "Nasdaq Composite rose 1.35%, closing at 12,299.68. The U.S. economy added 438,000 jobs in "
                "August, the Labor Department said. Economists polled by Dow Jones expected 273,000 "
                "jobs. However, wages rose less than expected last month.  Stocks posted a stunning "
                "turnaround on Friday, after initially falling on the stronger-than-expected jobs report. "
                "At its session low, the Dow had fallen as much as 198 points; it surged by more than "
                "500 points at the height of the rally. The Nasdaq and the S&P 500 slid by 0.8% during "
                "their lowest points in the day.  Traders were unclear of the reason for the intraday "
                "reversal. Some noted it could be the softer wage number in the jobs report that made "
                "investors rethink their earlier bearish stance. Others noted the pullback in yields from "
                "the day’s highs. Part of the rally may just be to do a market that had gotten extremely "
                "oversold with the S&P 500 at one point this week down more than 9% from its high earlier "
                "this year.  Yields initially surged after the report, with the 10-year Treasury rate trading "
                "near its highest level in 14 years. The benchmark rate later eased from those levels, but "
                "was still up around 6 basis points at 4.58%.  'We’re seeing a little bit of a give back "
                "in yields from where we were around 4.8%. [With] them pulling back a bit, I think that’s "
                "helping the stock market,' said Margaret Jones, chief investment officer at Vibrant Industries "
                "Capital Advisors. 'We’ve had a lot of weakness in the market in recent weeks, and potentially "
                "some oversold conditions.'"},

    {"query": "Is the expected gross margin greater than 70%?",
     "answer": "Yes, between 71.5% and 72.%",
     "context": "Outlook NVIDIA’s outlook for the third quarter of fiscal 2024 is as follows:"
                "Revenue is expected to be $16.00 billion, plus or minus 2%. GAAP and non-GAAP "
                "gross margins are expected to be 71.5% and 72.5%, respectively, plus or minus "
                "50 basis points.  GAAP and non-GAAP operating expenses are expected to be "
                "approximately $2.95 billion and $2.00 billion, respectively.  GAAP and non-GAAP "
                "other income and expense are expected to be an income of approximately $100 "
                "million, excluding gains and losses from non-affiliated investments. GAAP and "
                "non-GAAP tax rates are expected to be 14.5%, plus or minus 1%, excluding any discrete items."
                "Highlights NVIDIA achieved progress since its previous earnings announcement "
                "in these areas:  Data Center Second-quarter revenue was a record $10.32 billion, "
                "up 141% from the previous quarter and up 171% from a year ago. Announced that the "
                "NVIDIA® GH200 Grace™ Hopper™ Superchip for complex AI and HPC workloads is shipping "
                "this quarter, with a second-generation version with HBM3e memory expected to ship "
                "in Q2 of calendar 2024. "},

    {"query": "What is Bank of America's rating on Target?",
     "answer": "Buy",
     "context": "Here are some of the tickers on my radar for Thursday, Oct. 12, taken directly from "
                "my reporter’s notebook: It’s the one-year anniversary of the S&P 500′s bear market bottom "
                "of 3,577. Since then, as of Wednesday’s close of 4,376, the broad market index "
                "soared more than 22%.  Hotter than expected September consumer price index, consumer "
                "inflation. The Social Security Administration issues announced a 3.2% cost-of-living "
                "adjustment for 2024.  Chipotle Mexican Grill (CMG) plans price increases. Pricing power. "
                "Cites consumer price index showing sticky retail inflation for the fourth time "
                "in two years. Bank of America upgrades Target (TGT) to buy from neutral. Cites "
                "risk/reward from depressed levels. Traffic could improve. Gross margin upside. "
                "Merchandising better. Freight and transportation better. Target to report quarter "
                "next month. In retail, the CNBC Investing Club portfolio owns TJX Companies (TJX), "
                "the off-price juggernaut behind T.J. Maxx, Marshalls and HomeGoods. Goldman Sachs "
                "tactical buy trades on Club names Wells Fargo (WFC), which reports quarter Friday, "
                "Humana (HUM) and Nvidia (NVDA). BofA initiates Snowflake (SNOW) with a buy rating."
                "If you like this story, sign up for Jim Cramer’s Top 10 Morning Thoughts on the "
                "Market email newsletter for free. Barclays cuts price targets on consumer products: "
                "UTZ Brands (UTZ) to $16 per share from $17. Kraft Heinz (KHC) to $36 per share from "
                "$38. Cyclical drag. J.M. Smucker (SJM) to $129 from $160. Secular headwinds. "
                "Coca-Cola (KO) to $59 from $70. Barclays cut PTs on housing-related stocks: Toll Brothers"
                "(TOL) to $74 per share from $82. Keeps underweight. Lowers Trex (TREX) and Azek"
                "(AZEK), too. Goldman Sachs (GS) announces sale of fintech platform and warns on "
                "third quarter of 19-cent per share drag on earnings. The buyer: investors led by "
                "private equity firm Sixth Street. Exiting a mistake. Rise in consumer engagement for "
                "Spotify (SPOT), says Morgan Stanley. The analysts hike price target to $190 per share "
                "from $185. Keeps overweight (buy) rating. JPMorgan loves elf Beauty (ELF). Keeps "
                "overweight (buy) rating but lowers price target to $139 per share from $150. "
                "Sees “still challenging” environment into third-quarter print. The Club owns shares "
                "in high-end beauty company Estee Lauder (EL). Barclays upgrades First Solar (FSLR) "
                "to overweight from equal weight (buy from hold) but lowers price target to $224 per "
                "share from $230. Risk reward upgrade. Best visibility of utility scale names."},

    {"query": "What was the rate of decline in 3rd quarter sales?",
     "answer": "20% year-on-year.",
     "context": "Nokia said it would cut up to 14,000 jobs as part of a cost cutting plan following "
                "third quarter earnings that plunged. The Finnish telecommunications giant said that "
                "it will reduce its cost base and increase operation efficiency to “address the "
                "challenging market environment. The substantial layoffs come after Nokia reported "
                "third-quarter net sales declined 20% year-on-year to 4.98 billion euros. Profit over "
                "the period plunged by 69% year-on-year to 133 million euros."},

    {"query": "What is a list of the key points?",
     "answer": "•Stocks rallied on Friday with stronger-than-expected U.S jobs data and increase in "
               "Treasury yields;\n•Dow Jones gained 195.12 points;\n•S&P 500 added 1.59%;\n•Nasdaq Composite rose "
               "1.35%;\n•U.S. economy added 438,000 jobs in August, better than the 273,000 expected;\n"
               "•10-year Treasury rate trading near the highest level in 14 years at 4.58%.",
     "context": "Stocks rallied Friday even after the release of stronger-than-expected U.S. jobs data "
               "and a major increase in Treasury yields.  The Dow Jones Industrial Average gained 195.12 points, "
               "or 0.76%, to close at 31,419.58. The S&P 500 added 1.59% at 4,008.50. The tech-heavy "
               "Nasdaq Composite rose 1.35%, closing at 12,299.68. The U.S. economy added 438,000 jobs in "
               "August, the Labor Department said. Economists polled by Dow Jones expected 273,000 "
               "jobs. However, wages rose less than expected last month.  Stocks posted a stunning "
               "turnaround on Friday, after initially falling on the stronger-than-expected jobs report. "
               "At its session low, the Dow had fallen as much as 198 points; it surged by more than "
               "500 points at the height of the rally. The Nasdaq and the S&P 500 slid by 0.8% during "
               "their lowest points in the day.  Traders were unclear of the reason for the intraday "
               "reversal. Some noted it could be the softer wage number in the jobs report that made "
               "investors rethink their earlier bearish stance. Others noted the pullback in yields from "
               "the day’s highs. Part of the rally may just be to do a market that had gotten extremely "
               "oversold with the S&P 500 at one point this week down more than 9% from its high earlier "
               "this year.  Yields initially surged after the report, with the 10-year Treasury rate trading "
               "near its highest level in 14 years. The benchmark rate later eased from those levels, but "
               "was still up around 6 basis points at 4.58%.  'We’re seeing a little bit of a give back "
               "in yields from where we were around 4.8%. [With] them pulling back a bit, I think that’s "
               "helping the stock market,' said Margaret Jones, chief investment officer at Vibrant Industries "
               "Capital Advisors. 'We’ve had a lot of weakness in the market in recent weeks, and potentially "
               "some oversold conditions.'"}

    ]

    return test_list


# this is the main script to be run

def bling_meets_llmware_hello_world (model_name):

    t0 = time.time()

    # load the questions
    test_list = hello_world_questions()

    print(f"\n > Loading Model: {model_name}...")

    # load the model 
    prompter = Prompt().load_model(model_name)

    t1 = time.time()
    print(f"\n > Model {model_name} load time: {t1-t0} seconds")
 
    for i, entries in enumerate(test_list):

        print(f"\n{i+1}. Query: {entries['query']}")
     
        # run the prompt
        output = prompter.prompt_main(entries["query"],context=entries["context"]
                                      , prompt_name="default_with_context",temperature=0.30)

        # print out the results
        llm_response = output["llm_response"].strip("\n")
        print(f"LLM Response: {llm_response}")
        print(f"Gold Answer: {entries['answer']}")
        print(f"LLM Usage: {output['usage']}")

    t2 = time.time()

    print(f"\nTotal processing time: {t2-t1} seconds")

    return 0


if __name__ == "__main__":

    # list of 'rag-instruct' laptop-ready small bling models on HuggingFace

    pytorch_models = ["llmware/bling-1b-0.1",                    #  most popular
                      "llmware/bling-tiny-llama-v0",             #  fastest 
                      "llmware/bling-1.4b-0.1",
                      "llmware/bling-falcon-1b-0.1",
                      "llmware/bling-cerebras-1.3b-0.1",
                      "llmware/bling-sheared-llama-1.3b-0.1",    
                      "llmware/bling-sheared-llama-2.7b-0.1",
                      "llmware/bling-red-pajamas-3b-0.1",
                      "llmware/bling-stable-lm-3b-4e1t-v0",
                      "llmware/bling-phi-3"                      # most accurate (and newest)  
                      ]

    #  Quantized GGUF versions generally load faster and run nicely on a laptop with at least 16 GB of RAM
    gguf_models = ["bling-phi-3-gguf", "bling-stablelm-3b-tool", "dragon-llama-answer-tool", "dragon-yi-answer-tool", "dragon-mistral-answer-tool"]

    #   try model from either pytorch or gguf model list
    #   the newest (and most accurate) is 'bling-phi-3-gguf'  

    bling_meets_llmware_hello_world(gguf_models[0]  

    #   check out the model card on Huggingface for RAG benchmark test performance results and other useful information
```

</details>

<details>
<summary><b>Simple-to-Scale Database Options </b> - integrated data stores from laptop to parallelized cluster. </summary>

```python

from llmware.configs import LLMWareConfig

#   to set the collection database - mongo, sqlite, postgres  
LLMWareConfig().set_active_db("mongo")  

#   to set the vector database (or declare when installing)  
#   --options: milvus, pg_vector (postgres), redis, qdrant, faiss, pinecone, mongo atlas  
LLMWareConfig().set_vector_db("milvus")  

#   for fast start - no installations required  
LLMWareConfig().set_active_db("sqlite")  
LLMWareConfig().set_vector_db("chromadb")   # try also faiss and lancedb  

#   for single postgres deployment  
LLMWareConfig().set_active_db("postgres")  
LLMWareConfig().set_vector_db("postgres")  

#   to install mongo, milvus, postgres - see the docker-compose scripts as well as examples

```

</details>

<details>

<summary> 🔥 <b> Agents with Function Calls and SLIM Models </b> 🔥 </summary>  

```python

from llmware.agents import LLMfx

text = ("Tesla stock fell 8% in premarket trading after reporting fourth-quarter revenue and profit that "
        "missed analysts’ estimates. The electric vehicle company also warned that vehicle volume growth in "
        "2024 'may be notably lower' than last year’s growth rate. Automotive revenue, meanwhile, increased "
        "just 1% from a year earlier, partly because the EVs were selling for less than they had in the past. "
        "Tesla implemented steep price cuts in the second half of the year around the world. In a Wednesday "
        "presentation, the company warned investors that it’s 'currently between two major growth waves.'")

#   create an agent using LLMfx class
agent = LLMfx()

#   load text to process
agent.load_work(text)

#   load 'models' as 'tools' to be used in analysis process
agent.load_tool("sentiment")
agent.load_tool("extract")
agent.load_tool("topics")
agent.load_tool("boolean")

#   run function calls using different tools
agent.sentiment()
agent.topics()
agent.extract(params=["company"])
agent.extract(params=["automotive revenue growth"])
agent.xsum()
agent.boolean(params=["is 2024 growth expected to be strong? (explain)"])

#   at end of processing, show the report that was automatically aggregated by key
report = agent.show_report()

#   displays a summary of the activity in the process
activity_summary = agent.activity_summary()

#   list of the responses gathered
for i, entries in enumerate(agent.response_list):
    print("update: response analysis: ", i, entries)

output = {"report": report, "activity_summary": activity_summary, "journal": agent.journal}  

```

</details>
<details>

<summary> 🚀 <b>Start coding - Quick Start for RAG </b> 🚀 </summary>

```python
# This example illustrates a simple contract analysis
# using a RAG-optimized LLM running locally

import os
import re
from llmware.prompts import Prompt, HumanInTheLoop
from llmware.setup import Setup
from llmware.configs import LLMWareConfig

def contract_analysis_on_laptop (model_name):

    #  In this scenario, we will:
    #  -- download a set of sample contract files
    #  -- create a Prompt and load a BLING LLM model
    #  -- parse each contract, extract the relevant passages, and pass questions to a local LLM

    #  Main loop - Iterate thru each contract:
    #
    #      1.  parse the document in memory (convert from PDF file into text chunks with metadata)
    #      2.  filter the parsed text chunks with a "topic" (e.g., "governing law") to extract relevant passages
    #      3.  package and assemble the text chunks into a model-ready context
    #      4.  ask three key questions for each contract to the LLM
    #      5.  print to the screen
    #      6.  save the results in both json and csv for furthe processing and review.

    #  Load the llmware sample files

    print (f"\n > Loading the llmware sample files...")

    sample_files_path = Setup().load_sample_files()
    contracts_path = os.path.join(sample_files_path,"Agreements")
 
    #  Query list - these are the 3 main topics and questions that we would like the LLM to analyze for each contract

    query_list = {"executive employment agreement": "What are the name of the two parties?",
                  "base salary": "What is the executive's base salary?",
                  "vacation": "How many vacation days will the executive receive?"}

    #  Load the selected model by name that was passed into the function

    print (f"\n > Loading model {model_name}...")

    prompter = Prompt().load_model(model_name, temperature=0.0, sample=False)

    #  Main loop

    for i, contract in enumerate(os.listdir(contracts_path)):

        #   excluding Mac file artifact (annoying, but fact of life in demos)
        if contract != ".DS_Store":

            print("\nAnalyzing contract: ", str(i+1), contract)

            print("LLM Responses:")

            for key, value in query_list.items():

                # step 1 + 2 + 3 above - contract is parsed, text-chunked, filtered by topic key,
                # ... and then packaged into the prompt

                source = prompter.add_source_document(contracts_path, contract, query=key)

                # step 4 above - calling the LLM with 'source' information already packaged into the prompt

                responses = prompter.prompt_with_source(value, prompt_name="default_with_context")  

                # step 5 above - print out to screen

                for r, response in enumerate(responses):
                    print(key, ":", re.sub("[\n]"," ", response["llm_response"]).strip())

                # We're done with this contract, clear the source from the prompt
                prompter.clear_source_materials()

    # step 6 above - saving the analysis to jsonl and csv

    # Save jsonl report to jsonl to /prompt_history folder
    print("\nPrompt state saved at: ", os.path.join(LLMWareConfig.get_prompt_path(),prompter.prompt_id))
    prompter.save_state()

    # Save csv report that includes the model, response, prompt, and evidence for human-in-the-loop review
    csv_output = HumanInTheLoop(prompter).export_current_interaction_to_csv()
    print("csv output saved at:  ", csv_output)


if __name__ == "__main__":

    # use local cpu model - try the newest - RAG finetune of Phi-3 quantized and packaged in GGUF  
    model = "bling-phi-3-gguf"

    contract_analysis_on_laptop(model)

```
</details>


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
