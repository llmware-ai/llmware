# llmware
![Static Badge](https://img.shields.io/badge/python-3.9_%7C_3.10%7C_3.11-blue?color=blue)
![PyPI - Version](https://img.shields.io/pypi/v/llmware?color=blue)
[![discord](https://img.shields.io/badge/Chat%20on-Discord-blue?logo=discord&logoColor=white)](https://discord.gg/MhZn5Nc39h)   

`llmware` is a unified framework for developing LLM-based application patterns including Retrieval Augmented Generation (RAG).  

This project provides an integrated set of tools that anyone can use - from a beginner to the most sophisticated AI developer - to rapidly build industrial-grade, knowledge-based enterprise LLM applications. 

Our specific focus is on making it easy to integrate open source small specialized models and connecting enterprise knowledge safely and securely. 

[Join us on Discord](https://discord.gg/MhZn5Nc39h)   |  [Watch Youtube Tutorials](https://www.youtube.com/@llmware)  | [Explore our Model Families on Huggingface](https://www.huggingface.co/llmware)   


🔥🔥🔥 [**Multi-Model Agents with SLIM Models**](examples/SLIM-Agents/) - [**Intro-Video**](https://www.youtube.com/watch?v=cQfdaTcmBpY) 🔥🔥🔥   
Can't wait?  Get SLIMs right away:  

```python 
from llmware.models import ModelCatalog

ModelCatalog().get_llm_toolkit()  # get all SLIM models, delivered as small, fast quantized tools 
ModelCatalog().tool_test_run("slim-sentiment-tool") # see the model in action with test script included  
```

## 🎯  Key features 
Writing code with`llmware` is based on a few main concepts:

<details>
<summary><b>Model Catalog</b>: Access all models the same way with easy lookup, regardless of underlying implementation. 
</summary>  


```python
#   50+ Models in Catalog with 20+ RAG-optimized BLING, DRAGON and Industry BERT models
#   Full support for GGUF, HuggingFace, Sentence Transformers and major API-based models
#   Easy to extend to add custom models - see examples

from llmware.models import ModelCatalog
from llmware.prompts import Prompt

#   all models accessed through the ModelCatalog
models = ModelCatalog().list_all_models()

#   to use any model in the ModelCatalog - "load_model" method and pass the model_name parameter
my_model = ModelCatalog().load_model("llmware/bling-tiny-llama-v0")
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

#   to parse and text chunk a set of documents (pdf, pptx, docx, xlsx, txt, csv, md, json)

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
lib.install_new_embedding(embedding_model_name="industry-bert-sec", vector_db="faiss", batch_size=100)

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
""" This 'Hello World' example demonstrates how to get started using local BLING models with provided context """

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

    model_list = ["llmware/bling-1b-0.1",                    #  fastest + most popular
                  "llmware/bling-tiny-llama-v0",             #  *** newest ***
                  "llmware/bling-1.4b-0.1",
                  "llmware/bling-falcon-1b-0.1",
                  "llmware/bling-cerebras-1.3b-0.1",
                  "llmware/bling-sheared-llama-1.3b-0.1",    
                  "llmware/bling-sheared-llama-2.7b-0.1",
                  "llmware/bling-red-pajamas-3b-0.1",
                  "llmware/bling-stable-lm-3b-4e1t-v0"        # most accurate
                  ]

    #  dragon models are 6-7B and designed for GPU use - but the GGUF versions run nicely on a laptop with at least 16 GB of RAM
    gguf_models = ["llmware/dragon-yi-6b-gguf", "llmware/dragon-llama-7b-gguf", "llmware/dragon-mistral-7b-gguf"]

    #   try the newest bling model - 'tiny-llama' or load a gguf model
    bling_meets_llmware_hello_world(model_list[1])

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
LLMWareConfig().set_vector_db("faiss")

#   for single postgres deployment
LLMWareConfig().set_active_db("postgres")
LLMWareConfig().set_vector_db("postgres")

#   to install mongo, milvus, postgres - see the docker-compose scripts as well as examples

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
                  "governing law": "What is the governing law?"}

    #  Load the selected model by name that was passed into the function

    print (f"\n > Loading model {model_name}...")

    prompter = Prompt().load_model(model_name)

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

                responses = prompter.prompt_with_source(value, prompt_name="just_the_facts", temperature=0.3)

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

    # use local cpu model - smallest, fastest (use larger BLING models for higher accuracy)
    model = "llmware/bling-tiny-llama-v0"

    contract_analysis_on_laptop(model)

```
</details>


## 🔥 What's New? 🔥

-**Multi-Model Agents with SLIM models** - multi-step Agents with SLIMs on CPU - [video](https://www.youtube.com/watch?v=cQfdaTcmBpY) - [example](examples/SLIM-Agents)  

-**Fast start with no db installation** - SQLite (text collection) and FAISS (vector file database) - [example](examples/Getting_Started/configure_db.py) 

-**Postgres integration** as option for text collection with PGVector support ([example](examples/Embedding/using_pg_vector.py))  

-**GGUF support** - check out examples - GGUF ([example](examples/Models/using_gguf.py)) and Videos [video](https://www.youtube.com/watch?v=ZJyQIZNJ45E)  

-**OpenChat API integration** - OpenChat ([example](examples/Models/using-open-chat-models.py))  

-**Neo4j Vector Database integration** - ([example](examples/Embedding/using_neo4j.py))  



## 🌱 Getting Started

**Step 1 - Install llmware** -  `pip3 install llmware `

<details>
<summary><b>Step 2- Go to Examples</b> - Get Started Fast with 50+ 'Cut-and-Paste' Recipes </summary>

## 🔥 Top New Examples 🔥  

New to LLMWare - [**Fast Start tutorial series**](https://github.com/llmware-ai/llmware/tree/main/fast_start)  
SLIM Examples -  [**SLIM Models**](examples/SLIM-Agents/)

| Example     |  Detail      |
|-------------|--------------|
| 1.   BLING models fast start ([code](examples/Models/bling_fast_start.py) / [video](https://www.youtube.com/watch?v=JjgqOZ2v5oU)) | Get started with fast, accurate, CPU-based models - question-answering, key-value extraction, and basic summarization.  |
| 2.   Parse and Embed 500 PDF Documents ([code](examples/Embedding/docs2vecs_with_milvus-un_resolutions.py))  | End-to-end example for Parsing, Embedding and Querying UN Resolution documents with Milvus  |
| 3.  Hybrid Retrieval - Semantic + Text ([code](examples/Retrieval/dual_pass_with_custom_filter.py)) | Using 'dual pass' retrieval to combine best of semantic and text search |  
| 4.   Multiple Embeddings with PG Vector ([code](examples/Embedding/using_multiple_embeddings.py) / [video](https://www.youtube.com/watch?v=Bncvggy6m5Q)) | Comparing Multiple Embedding Models using Postgres / PG Vector |
| 5.   DRAGON GGUF Models ([code](examples/Models/dragon_gguf_fast_start.py) / [video](https://www.youtube.com/watch?v=BI1RlaIJcsc&t=130s)) | State-of-the-Art 7B RAG GGUF Models.  | 
| 6.   RAG with BLING ([code](examples/RAG/contract_analysis_on_laptop_with_bling_models.py) / [video](https://www.youtube.com/watch?v=8aV5p3tErP0)) | Using contract analysis as an example, experiment with RAG for complex document analysis and text extraction using `llmware`'s BLING ~1B parameter GPT model running on your laptop. |  
| 7.   Master Service Agreement Analysis with DRAGON ([code](examples/RAG/msa_processing.py) / [video](https://www.youtube.com/watch?v=Cf-07GBZT68&t=2s)) | Analyzing MSAs using DRAGON YI 6B Model.   |                                                                                                                         
| 8.   Streamlit Example ([code](examples/Getting_Started/ui_without_a_database.py))  | Upload pdfs, and run inference on llmware BLING models.  |  
| 9.   Integrating LM Studio ([code](examples/Models/using-open-chat-models.py) / [video](https://www.youtube.com/watch?v=h2FDjUyvsKE&t=101s)) | Integrating LM Studio Models with LLMWare  |                                                                                                                                       
| 10.  Prompts With Sources ([code](examples/Prompts/prompt_with_sources.py))  | Attach wide range of knowledge sources directly into Prompts.   |   
| 11.  Fact Checking ([code](examples/Prompts/fact_checking.py))  | Explore the full set of evidence methods in this example script that analyzes a set of contracts.   |
| 12.  Using 7B GGUF Chat Models ([code](examples/Models/chat_models_gguf_fast_start.py)) | Using 4 state of the art 7B chat models in minutes running locally |  


Check out:  [llmware examples](https://github.com/llmware-ai/llmware/blob/main/examples/README.md)  

</details>  

<details>
<summary><b>Step 3 - Tutorial Videos</b> - check out our Youtube channel for high-impact 5-10 minute tutorials on the latest examples.   </summary>

🎬 Check out these videos to get started quickly:  
- [SLIM Models Intro] (https://www.youtube.com/watch?v=cQfdaTcmBpY)  
- [RAG with BLING on your laptop](https://www.youtube.com/watch?v=JjgqOZ2v5oU)    
- [DRAGON-7B-Models](https://www.youtube.com/watch?v=d_u7VaKu6Qk&t=37s)  
- [Install and Compare Multiple Embeddings with Postgres and PGVector](https://www.youtube.com/watch?v=Bncvggy6m5Q)  
- [Background on GGUF Quantization & DRAGON Model Example](https://www.youtube.com/watch?v=ZJyQIZNJ45E)  
- [Using LM Studio Models](https://www.youtube.com/watch?v=h2FDjUyvsKE)  
- [Using Ollama Models](https://www.youtube.com/watch?v=qITahpVDuV0)  
- [Use any GGUF Model](https://www.youtube.com/watch?v=9wXJgld7Yow)  
- [Use small LLMs for RAG for Contract Analysis (feat. LLMWare)](https://www.youtube.com/watch?v=8aV5p3tErP0)
- [Invoice Processing with LLMware](https://www.youtube.com/watch?v=VHZSaBBG-Bo&t=10s)
- [Ingest PDFs at Scale](https://www.youtube.com/watch?v=O0adUfrrxi8&t=10s)
- [Evaluate LLMs for RAG with LLMWare](https://www.youtube.com/watch?v=s0KWqYg5Buk&t=105s)
- [Fast Start to RAG with LLMWare Open Source Library](https://www.youtube.com/watch?v=0naqpH93eEU)
- [Use Retrieval Augmented Generation (RAG) without a Database](https://www.youtube.com/watch?v=tAGz6yR14lw)
- [Pop up LLMWare Inference Server](https://www.youtube.com/watch?v=qiEmLnSRDUA&t=20s)


</details>  

## Data Store Options

<details>
<summary><b>Fast Start</b>:  use SQLite3 and FAISS out-of-the-box - no install required </summary>  

```python
from llmware.configs import LLMWareConfig 
LLMWareConfig().set_active_db("sqlite")   
LLMWareConfig().set_vector_db("faiss")
```
</details>  

<details>
<summary><b>Speed + Scale</b>:  use MongoDB (text collection) and Milvus (vector db) - install with Docker Compose </summary> 

```bash
curl -o docker-compose.yaml https://raw.githubusercontent.com/llmware-ai/llmware/main/docker-compose.yaml
docker compose up -d
```

```python
from llmware.configs import LLMWareConfig
LLMWareConfig().set_active_db("mongo")
LLMWareConfig().set_vector_db("milvus")
```

</details>  

<details>
<summary><b>Postgres</b>:  use Postgres for both text collection and vector DB - install with Docker Compose </summary> 

```bash
curl -o docker-compose.yaml https://raw.githubusercontent.com/llmware-ai/llmware/main/docker-compose-pgvector.yaml
docker compose up -d
```

```python
from llmware.configs import LLMWareConfig
LLMWareConfig().set_active_db("postgres")
LLMWareConfig().set_vector_db("postgres")
```

</details>  

<details>
<summary><b>Mix-and-Match</b>: LLMWare supports 3 text collection databases (Mongo, Postgres, SQLite) and 
10 vector databases (Milvus, PGVector-Postgres, Neo4j, Redis, Mongo-Atlas, Qdrant, Faiss, LanceDB, ChromaDB and Pinecone)  </summary>

```bash
# scripts to deploy other options
curl -o docker-compose.yaml https://raw.githubusercontent.com/llmware-ai/llmware/main/docker-compose-redis-stack.yaml
```

</details>  

## Meet our Models   

- **SLIM model series:** small, specialized models fine-tuned for function calling and multi-step, multi-model Agent workflows.  
- **DRAGON model series:**  Production-grade RAG-optimized 6-7B parameter models - "Delivering RAG on ..." the leading foundation base models.
- **BLING model series:**  Small CPU-based RAG-optimized, instruct-following 1B-3B parameter models.
- **Industry BERT models:**  out-of-the-box custom trained sentence transformer embedding models fine-tuned for the following industries:  Insurance, Contracts, Asset Management, SEC.  
- **GGUF Quantization:** we provide 'gguf' and 'tool' versions of many SLIM, DRAGON and BLING models, optimized for CPU deployment.  

## Using LLMs and setting-up API keys & secrets

LLMWare is an open platform and supports a wide range of open source and proprietary models.  To use LLMWare, you do not need to use any proprietary LLM - we would encourage you to experiment with [SLIM](https://www.huggingface.co/llmware/), [BLING](https://huggingface.co/llmware), [DRAGON](https://huggingface.co/llmware), [Industry-BERT](https://huggingface.co/llmware), the GGUF examples, along with bringing in your favorite models from HuggingFace and Sentence Transformers. 

If you would like to use a proprietary model, you will need to provide your own API Keys.   API keys and secrets for models, aws, and pinecone can be set-up for use in environment variables or passed directly to method calls. 


## ✍️ Working with the llmware Github repository

The llmware repo can be pulled locally to get access to all the examples, or to work directly with the latest version of the llmware code.

```bash
git clone git@github.com:llmware-ai/llmware.git
```

<details>  
    
<summary> ✨  <b>Roadmap - Where are are going ... </b>  </summary>

- 💡 Making it easy to deploy fine-tuned open source models to build state-of-the-art RAG workflows
- 💡 Private cloud - keeping documents, data pipelines, data stores, and models safe and secure  
- 💡 Model quantization, especially GGUF, and democratizing the game-changing use of 7B CPU-based LLMs
- 💡 Developing small specialized RAG optimized LLMs between 1B-7B parameters
- 💡 Industry-specific LLMs, embedding models and processes to support core knowledge-based use cases
- 💡 Enterprise scalability - containerization, worker deployments and Kubernetes
- 💡 Integration of SQL and other scale enterprise data sources  
- 💡 Multi-step, multi-model Agent-based workflows with small, specialized function-calling models  


Like our models, we aspire for llmware to be "small, but mighty" - easy to use and get started, but packing a powerful punch!

</details>

Interested in contributing to llmware? Information on ways to participate can be found in our [Contributors Guide](https://github.com/llmware-ai/llmware/blob/main/CONTRIBUTING.md#contributing-to-llmware).  As with all aspects of this project, contributing is governed by our [Code of Conduct](https://github.com/llmware-ai/llmware/blob/main/CODE_OF_CONDUCT.md).

Questions and discussions are welcome in our [github discussions](https://github.com/llmware-ai/llmware/discussions).  

## 📣  Release notes and Change Log

**Friday, February 16 - v0.2.3 WIP Update**  
- Added 10+ embedding models to ModelCatalog - nomic, jina, bge, gte, ember and uae-large.   
- Updated OpenAI support >=1.0 and new text-3 embedding models.    
- SLIM model keys and output_values now accessible in ModelCatalog.  
- Updating encodings to 'utf-8-sig' to better handle txt/csv files with bom.  

**Reported notable issues on priority resolution path**  
- stablelm-based models using gguf  
- older linux versions with GLIBC < 2.34  
- 3.12 python support - waiting on one last dependency (coming soon)
  
**Supported Operating Systems**: MacOS (Metal and x86), Linux (x86 and aarch64), Windows  
- note on Linux: we test most extensively on Ubuntu 22 and recommend where possible  
- if you need another Linux version, please raise an issue - we will prioritize testing and ensure support.  

**Supported Vector Databases**: Milvus, Postgres (PGVector), Neo4j, Redis, LanceDB, ChromaDB, Qdrant, FAISS, Pinecone, Mongo Atlas Vector Search

**Supported Text Index Databases**: MongoDB, Postgres, SQLite  



<details>
<summary><b>Optional</b></summary>

- [Docker](https://docs.docker.com/get-docker/)
  
- To enable the OCR parsing capabilities, install [Tesseract v5.3.3](https://tesseract-ocr.github.io/tessdoc/Installation.html) and [Poppler v23.10.0](https://poppler.freedesktop.org/) native packages.

</details>

<details>
  <summary><b>🚧 Change Log</b></summary>

**Latest Updates - 19 Jan 2024 - llmware v0.2.0**
  - Added new database integration options - Postgres and SQlite
  - Improved status update and parser event logging options for parallelized parsing
  - Significant enhancements to interactions between Embedding + Text collection databases
  - Improved error exception handling in loading dynamic modules

**Latest Updates - 15 Jan 2024: llmware v0.1.15**
  - Enhancements to dual pass retrieval queries
  - Expanded configuration objects and options for endpoint resources
    
**Latest Updates - 30 Dec 2023: llmware v0.1.14**
  - Added support for Open Chat inference servers (compatible with OpenAI API)
  - Improved capabilities for multiple embedding models and vector DB configurations
  - Added docker-compose install scripts for PGVector and Redis vector databases
  - Added 'bling-tiny-llama' to model catalog
         
**Latest Updates - 22 Dec 2023: llmware v0.1.13**
  - Added 3 new vector databases - Postgres (PG Vector), Redis, and Qdrant
  - Improved support for integrating sentence transformers directly in the model catalog
  - Improvements in the model catalog attributes
  - Multiple new Examples in Models & Embeddings, including GGUF, Vector database, and model catalog

- **17 Dec 2023: llmware v0.1.12**
  - dragon-deci-7b added to catalog - RAG-finetuned model on high-performance new 7B model base from Deci
  - New GGUFGenerativeModel class for easy integration of GGUF Models
  - Adding prebuilt llama_cpp / ctransformer shared libraries for Mac M1, Mac x86, Linux x86 and Windows
  - 3 DRAGON models packaged as Q4_K_M GGUF models for CPU laptop use (dragon-mistral-7b, dragon-llama-7b, dragon-yi-6b)
  - 4 leading open source chat models added to default catalog with Q4_K_M
  
- **8 Dec 2023: llmware v0.1.11**
  - New fast start examples for high volume Document Ingestion and Embeddings with Milvus.
  - New LLMWare 'Pop up' Inference Server model class and example script.
  - New Invoice Processing example for RAG.
  - Improved Windows stack management to support parsing larger documents.
  - Enhancing debugging log output mode options for PDF and Office parsers.

- **30 Nov 2023: llmware v0.1.10**
  - Windows added as a supported operating system.
  - Further enhancements to native code for stack management. 
  - Minor defect fixes.

- **24 Nov 2023: llmware v0.1.9**
  - Markdown (.md) files are now parsed and treated as text files.
  - PDF and Office parser stack optimizations which should avoid the need to set ulimit -s.
  - New llmware_models_fast_start.py example that allows discovery and selection of all llmware HuggingFace models.
  - Native dependencies (shared libraries and dependencies) now included in repo to faciliate local development.
  - Updates to the Status class to support PDF and Office document parsing status updates.
  - Minor defect fixes including image block handling in library exports.

- **17 Nov 2023: llmware v0.1.8**
  - Enhanced generation performance by allowing each model to specific the trailing space parameter.
  - Improved handling for eos_token_id for llama2 and mistral.
  - Improved support for Hugging Face dynamic loading
  - New examples with the new llmware DRAGON models.
    
- **14 Nov 2023: llmware v0.1.7**
  - Moved to Python Wheel package format for PyPi distribution to provide seamless installation of native dependencies on all supported platforms.  
  - ModelCatalog enhancements:
    - OpenAI update to include newly announced ‘turbo’ 4 and 3.5 models.
    - Cohere embedding v3 update to include new Cohere embedding models.
    - BLING models as out-of-the-box registered options in the catalog. They can be instantiated like any other model, even without the “hf=True” flag.
    - Ability to register new model names, within existing model classes, with the register method in ModelCatalog.
  - Prompt enhancements:
    - “evidence_metadata” added to prompt_main output dictionaries allowing prompt_main responses to be plug into the evidence and fact-checking steps without modification.
    - API key can now be passed directly in a prompt.load_model(model_name, api_key = “[my-api-key]”)
  - LLMWareInference Server - Initial delivery:
    - New Class for LLMWareModel which is a wrapper on a custom HF-style API-based model.    
    - LLMWareInferenceServer is a new class that can be instantiated on a remote (GPU) server to create a testing API-server that can be integrated into any Prompt workflow.    
 
- **03 Nov 2023: llmware v0.1.6**
  - Updated packaging to require mongo-c-driver 1.24.4 to temporarily workaround segmentation fault with mongo-c-driver 1.25.
  - Updates in python code needed in anticipation of future Windows support.  

- **27 Oct 2023: llmware v0.1.5**
  - Four new example scripts focused on RAG workflows with small, fine-tuned instruct models that run on a laptop (`llmware` [BLING](https://huggingface.co/llmware) models).
  - Expanded options for setting temperature inside a prompt class.
  - Improvement in post processing of Hugging Face model generation.
  - Streamlined loading of Hugging Face generative models into prompts.
  - Initial delivery of a central status class: read/write of embedding status with a consistent interface for callers.
  - Enhanced in-memory dictionary search support for multi-key queries.
  - Removed trailing space in human-bot wrapping to improve generation quality in some fine-tuned models.
  - Minor defect fixes, updated test scripts, and version update for Werkzeug to address [dependency security alert](https://github.com/llmware-ai/llmware/security/dependabot/2).
- **20 Oct 2023: llmware v0.1.4**
  - GPU support for Hugging Face models.
  - Defect fixes and additional test scripts.
- **13 Oct 2023: llmware v0.1.3**
  - MongoDB Atlas Vector Search support.
  - Support for authentication using a MongoDB connection string.
  - Document summarization methods.
  - Improvements in capturing the model context window automatically and passing changes in the expected output length.  
  - Dataset card and description with lookup by name.
  - Processing time added to model inference usage dictionary.
  - Additional test scripts, examples, and defect fixes.
- **06 Oct 2023: llmware v0.1.1**
  - Added test scripts to the github repository for regression testing.
  - Minor defect fixes and version update of Pillow to address [dependency security alert](https://github.com/llmware-ai/llmware/security/dependabot/1).
- **02 Oct 2023: llmware v0.1.0**  🔥 Initial release of llmware to open source!! 🔥


</details>

