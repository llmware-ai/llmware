# llmware
![Static Badge](https://img.shields.io/badge/python-3.9_%7C_3.10%7C_3.11%7C_3.12-blue?color=blue)
![PyPI - Version](https://img.shields.io/pypi/v/llmware?color=blue)
[![discord](https://img.shields.io/badge/Chat%20on-Discord-blue?logo=discord&logoColor=white)](https://discord.gg/MhZn5Nc39h)   
[![Documentation](https://github.com/llmware-ai/llmware/actions/workflows/pages.yml/badge.svg)](https://github.com/llmware-ai/llmware/actions/workflows/pages.yml)

## 🧰🛠️🔩Building Enterprise RAG Pipelines with Small, Specialized Models  

`llmware` provides a unified framework for building LLM-based applications (e.g, RAG, Agents), using small, specialized models that can be deployed privately, integrated with enterprise knowledge sources safely and securely, and cost-effectively tuned and adapted for any business process.  

 `llmware` has two main components:  
 
 1.  **RAG Pipeline** - integrated components for the full lifecycle of connecting knowledge sources to generative AI models; and 

 2.  **50+ small, specialized models** fine-tuned for key tasks in enterprise process automation, including fact-based question-answering, classification, summarization, and extraction.  

By bringing together both of these components, along with integrating leading open source models and underlying technologies, `llmware` offers a comprehensive set of tools to rapidly build knowledge-based enterprise LLM applications.  

Most of our examples can be run without a GPU server - get started right away on your laptop.   

[Join us on Discord](https://discord.gg/MhZn5Nc39h)   |  [Watch Youtube Tutorials](https://www.youtube.com/@llmware)  | [Explore our Model Families on Huggingface](https://www.huggingface.co/llmware)   

New to RAG?  [Check out the Fast Start video series](https://www.youtube.com/playlist?list=PL1-dn33KwsmD7SB9iSO6vx4ZLRAWea1DB)  

🔥🔥🔥 [**Multi-Model Agents with SLIM Models**](examples/SLIM-Agents/) - [**Intro-Video**](https://www.youtube.com/watch?v=cQfdaTcmBpY) 🔥🔥🔥   

[Intro to SLIM Function Call Models](https://github.com/llmware-ai/llmware/blob/main/examples/Models/using_function_calls.py)  
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


## 🔥 What's New? 🔥  

-**BizBot - RAG + SQL Local Chatbot** - see [example](https://github.com/llmware-ai/llmware/tree/main/examples/Use_Cases/biz_bot.py) and [video](https://youtu.be/4nBYDEjxxTE?si=o6PDPbu0PVcT-tYd)  

-**Best New Small RAG Model** - BLING finetune of Phi-3 - "bling-phi-3-gguf" - see the [video](https://youtu.be/cViMonCAeSc?si=L6jX0sRdZAmKtRcz)  

-**Web Services with Agent Calls for Financial Research** - end-to-end scenario - [video](https://youtu.be/l0jzsg1_Ik0?si=hmLhpT1iv_rxpkHo) and [example](examples/Use_Cases/web_services_slim_fx.py)  

-**Voice Transcription with WhisperCPP** - [getting_started](examples/Models/using-whisper-cpp-getting-started.py), [using_sample_files](examples/Models/using-whisper-cpp-sample-files.py), and [analysis_use_case](examples/Use_Cases/parsing_great_speeches.py) with [great_speeches_video](https://youtu.be/5y0ez5ZBpPE?si=KVxsXXtX5TzvlEws)    

-**Phi-3 GGUF Streaming Local Chatbot with UI** - setup your own Phi-3-gguf chatbot on your laptop in minutes - [example](examples/UI/gguf_streaming_chatbot.py)  with [video](https://youtu.be/gzzEVK8p3VM?si=8cNn_do0oxSzCEnM)  

-**Small, specialized, function-calling Extract Model** - introducing slim-extract - [video](https://youtu.be/d6HFfyDk4YE?si=VB8JTsN3X7hsB_I) and [example](examples/SLIM-Agents/using_slim_extract_model.py)  

-**LLM to Answer Yes/No questions** - introducing slim-boolean model - [video](https://youtu.be/jZQZMMqAJXs?si=7HpkLqG39ohgNecx) and [example](examples/SLIM-Agents/using_slim_boolean_model.py)  

-**Natural Language Query to CSV End to End example** - using slim-sql model - [video](https://youtu.be/z48z5XOXJJg?si=V-CX1w-7KRioI4Bi) and [example](examples/SLIM-Agents/text2sql-end-to-end-2.py)  and now using Custom Tables on Postgres [example](https://github.com/llmware-ai/llmware/tree/main/examples/Use_Cases/agent_with_custom_tables.py)  

-**Multi-Model Agents with SLIM models** - multi-step Agents with SLIMs on CPU - [video](https://www.youtube.com/watch?v=cQfdaTcmBpY) - [example](examples/SLIM-Agents)  

-**OCR Embedded Document Images Example** - systematically extract text from images embedded in documents [example](examples/Parsing/ocr_embedded_doc_images.py)   

-**Enhanced Parser Functions for PDF, Word, Powerpoint and Excel** - new text-chunking controls and strategies, extract tables, images, header text - [example](examples/Parsing/pdf_parser_new_configs.py)   

-**Agent Inference Server** - set up multi-model Agents over Inference Server [example](https://github.com/llmware-ai/llmware/tree/main/examples/SLIM-Agents/agent_api_endpoint.py)  

-**GGUF - Getting Started** - check out examples - GGUF ([example](examples/Models/using_gguf.py)) and Videos [video](https://www.youtube.com/watch?v=ZJyQIZNJ45E)  

-**Optimizing Accuracy of RAG Prompts** - check out [example](examples/Models/adjusting_sampling_settings.py) and videos - [part I](https://youtu.be/7oMTGhSKuNY?si=14mS2pftk7NoKQbC) and [part II](https://youtu.be/iXp1tj-pPjM?si=T4teUAISnSWgtThu)  

## 🌱 Getting Started

**Step 1 - Install llmware** -  `pip3 install llmware` or `pip3 install 'llmware[full]'`  

- note: starting with v0.3.0, we provide options for a [core install](https://github.com/llmware-ai/llmware/blob/main/llmware/requirements.txt) (minimal set of dependencies) or [full install](https://github.com/llmware-ai/llmware/blob/main/llmware/requirements_extras.txt) (adds to the core with wider set of related python libraries).  

<details>
<summary><b>Step 2- Go to Examples</b> - Get Started Fast with 100+ 'Cut-and-Paste' Recipes </summary>

## 🔥 Top New Examples 🔥  

End-to-End Scenario - [**Function Calls with SLIM Extract and Web Services for Financial Research**](https://github.com/llmware-ai/llmware/tree/main/examples/Use_Cases/web_services_slim_fx.py)  
Analyzing Voice Files - [**Great Speeches with LLM Query and Extract**](https://github.com/llmware-ai/llmware/tree/main/examples/Use_Cases/parsing_great_speeches.py)  
New to LLMWare - [**Fast Start tutorial series**](https://github.com/llmware-ai/llmware/tree/main/fast_start)  
Getting Setup - [**Getting Started**](https://github.com/llmware-ai/llmware/tree/main/examples/Getting_Started)  
SLIM Examples -  [**SLIM Models**](examples/SLIM-Agents/)  

| Example     |  Detail      |
|-------------|--------------|
| 1.   BLING models fast start ([code](examples/Models/bling_fast_start.py) / [video](https://www.youtube.com/watch?v=JjgqOZ2v5oU)) | Get started with fast, accurate, CPU-based models - question-answering, key-value extraction, and basic summarization.  |
| 2.   Parse and Embed 500 PDF Documents ([code](examples/Embedding/docs2vecs_with_milvus-un_resolutions.py))  | End-to-end example for Parsing, Embedding and Querying UN Resolution documents with Milvus  |
| 3.  Hybrid Retrieval - Semantic + Text ([code](examples/Retrieval/dual_pass_with_custom_filter.py)) | Using 'dual pass' retrieval to combine best of semantic and text search |  
| 4.   Multiple Embeddings with PG Vector ([code](examples/Embedding/using_multiple_embeddings.py) / [video](https://www.youtube.com/watch?v=Bncvggy6m5Q)) | Comparing Multiple Embedding Models using Postgres / PG Vector |
| 5.   DRAGON GGUF Models ([code](examples/Models/dragon_gguf_fast_start.py) / [video](https://www.youtube.com/watch?v=BI1RlaIJcsc&t=130s)) | State-of-the-Art 7B RAG GGUF Models.  | 
| 6.   RAG with BLING ([code](examples/Use_Cases/contract_analysis_on_laptop_with_bling_models.py) / [video](https://www.youtube.com/watch?v=8aV5p3tErP0)) | Using contract analysis as an example, experiment with RAG for complex document analysis and text extraction using `llmware`'s BLING ~1B parameter GPT model running on your laptop. |  
| 7.   Master Service Agreement Analysis with DRAGON ([code](examples/Use_Cases/msa_processing.py) / [video](https://www.youtube.com/watch?v=Cf-07GBZT68&t=2s)) | Analyzing MSAs using DRAGON YI 6B Model.   |                                                                                                                         
| 8.   Streamlit Example ([code](examples/UI/simple_rag_ui_with_streamlit.py))  | Ask questions to Invoices with UI run inference.  |  
| 9.   Integrating LM Studio ([code](examples/Models/using-open-chat-models.py) / [video](https://www.youtube.com/watch?v=h2FDjUyvsKE&t=101s)) | Integrating LM Studio Models with LLMWare  |                                                                                                                                       
| 10.  Prompts With Sources ([code](examples/Prompts/prompt_with_sources.py))  | Attach wide range of knowledge sources directly into Prompts.   |   
| 11.  Fact Checking ([code](examples/Prompts/fact_checking.py))  | Explore the full set of evidence methods in this example script that analyzes a set of contracts.   |
| 12.  Using 7B GGUF Chat Models ([code](examples/Models/chat_models_gguf_fast_start.py)) | Using 4 state of the art 7B chat models in minutes running locally |  


Check out:  [llmware examples](https://github.com/llmware-ai/llmware/blob/main/examples/README.md)  

</details>  

<details>
<summary><b>Step 3 - Tutorial Videos</b> - check out our Youtube channel for high-impact 5-10 minute tutorials on the latest examples.   </summary>

🎬 Check out these videos to get started quickly:  
- [Document Summarization](https://youtu.be/Ps3W-P9A1m8?si=Rxvst3RJv8ZaOk0L)  
- [Bling-3-GGUF Local Chatbot](https://youtu.be/gzzEVK8p3VM?si=8cNn_do0oxSzCEnM)  
- [Agent-based Complex Research Analysis](https://youtu.be/y4WvwHqRR60?si=jX3KCrKcYkM95boe)  
- [Getting Started with SLIMs (with code)](https://youtu.be/aWZFrTDmMPc?si=lmo98_quo_2Hrq0C)  
- [Are you prompting wrong for RAG - Stochastic Sampling-Part I](https://youtu.be/7oMTGhSKuNY?si=_KSjuBnqArvWzYbx)  
- [Are you prompting wrong for RAG - Stochastic Sampling-Part II- Code Experiments](https://youtu.be/iXp1tj-pPjM?si=3ZeMgipY0vJDHIMY)  
- [SLIM Models Intro](https://www.youtube.com/watch?v=cQfdaTcmBpY)  
- [Text2SQL Intro](https://youtu.be/BKZ6kO2XxNo?si=tXGt63pvrp_rOlIP)  
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

## ✍️ Working with the llmware Github repository  

The llmware repo can be pulled locally to get access to all the examples, or to work directly with the latest version of the llmware code.  

```bash
git clone git@github.com:llmware-ai/llmware.git
```  

We have provided a **welcome_to_llmware** automation script in the root of the repository folder.  After cloning:  
- On Windows command line:  `.\welcome_to_llmware_windows.sh`  
- On Mac / Linux command line:  `sh ./welcome_to_llmware.sh`  

Alternatively, if you prefer to complete setup without the welcome automation script, then the next steps include:  

1.  **install requirements.txt** - inside the /llmware path - e.g., ```pip3 install -r llmware/requirements.txt```  

2.  **install requirements_extras.txt** - inside the /llmware path - e.g., ```pip3 install -r llmware/requirements_extras.txt```  (Depending upon your use case, you may not need all or any of these installs, but some of these will be used in the examples.)  

3.  **run examples** - copy one or more of the example .py files into the root project path.   (We have seen several IDEs that will attempt to run interactively from the nested /example path, and then not have access to the /llmware module - the easy fix is to just copy the example you want to run into the root path).  

4.  **install vector db** - no-install vector db options include milvus lite, chromadb, faiss and lancedb - which do not require a server install, but do require that you install the python sdk library for that vector db, e.g., `pip3 install pymilvus`, or `pip3 install chromadb`.  If you look in [examples/Embedding](https://github.com/llmware-ai/llmware/tree/main/examples/Embedding), you will see examples for getting started with various vector DB, and in the root of the repo, you will see easy-to-get-started docker compose scripts for installing milvus, postgres/pgvector, mongo, qdrant, neo4j, and redis.  

5.  Pytorch 2.3 note:  we have seen recently issues with Pytorch==2.3 on some platforms - if you run into any issues, we have seen that uninstalling Pytorch and downleveling to Pytorch==2.1 usually solves the problem.  

6.  Numpy 2.0 note: we have seen issues with numpy 2.0 with many libraries not yet supporting.  Our pip install setup will accept numpy 2.0 (to avoid pip conflicts), but if you pull from repo, we restrict to <2.   If you run into issues with numpy, we have found that they can be fixed by downgrading numpy to <2, e.g., 1.26.4.  To use WhisperCPP, you should downlevel to numpy <2.  


## Data Store Options

<details>
<summary><b>Fast Start</b>:  use SQLite3 and ChromaDB (File-based) out-of-the-box - no install required </summary>  

```python
from llmware.configs import LLMWareConfig 
LLMWareConfig().set_active_db("sqlite")   
LLMWareConfig().set_vector_db("chromadb")  
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

<details>  
    
<summary> ✨  <b>Roadmap - Where are we going ... </b>  </summary>

- 💡 Making it easy to deploy fine-tuned open source models to build state-of-the-art RAG workflows  
- 💡 Private cloud - keeping documents, data pipelines, data stores, and models safe and secure  
- 💡 Model quantization, especially GGUF, and democratizing the game-changing use of 1-7B CPU-based LLMs  
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

See also [additional deployment/install release notes in wheel_archives](https://github.com/llmware-ai/llmware/tree/main/wheel_archives)   

**Monday, July 8 - v03.3**  
- Improvements in model configuration options, logging, and various small fixes  
- Improved Azure OpenAI configs - see [example](https://github.com/llmware-ai/llmware/blob/main/examples/Models/using-azure-openai.py)  
  
**Saturday, June 29 - v0.3.2**  
- Update to PDF and Office parsers - improvements to configurations in logging and text chunking options  
  
**Saturday, June 22 - v0.3.1**  
- Added module 3 to Fast Start example series [examples 7-9 on Agents & Function Calls](https://github.com/llmware-ai/llmware/tree/main/fast_start)  
- Added reranker Jina model for in-memory semantic similarity RAG - see [example](https://github.com/llmware-ai/llmware/tree/main/examples/Embedding/using_semantic_reranker_with_rag.py)  
- Enhanced model fetching parameterization in model loading process  
- Added new 'tiny' versions of slim-extract and slim-summary in both Pytorch and GGUF versions - check out 'slim-extract-tiny-tool' and 'slim-summary-tiny-tool'  
- [Biz Bot] use case - see [example](https://github.com/llmware-ai/llmware/tree/main/examples/Use_Cases/biz_bot.py) and [video](https://youtu.be/4nBYDEjxxTE?si=o6PDPbu0PVcT-tYd)  
- Updated numpy reqs <2 and updated yfinance version minimum (>=0.2.38)     

**Tuesday, June 4 - v0.3.0**  
- Added support for new Milvus Lite embedded 'no-install' database - see [example](https://github.com/llmware-ai/llmware/tree/main/examples/Embedding/using_milvus_lite.py).   
- Added two new SLIM models to catalog and agent processes - ['q-gen'](https://github.com/llmware-ai/llmware/tree/main/examples/SLIM-Agents/using-slim-q-gen.py) and ['qa-gen'](https://github.com/llmware-ai/llmware/tree/main/examples/SLIM-Agents/using-slim-qa-gen.py)    
- Updated model class instantiation to provide more extensibility to add new classes in different modules  
- New welcome_to_llmware.sh and welcome_to_llmware_windows.sh fast install scripts  
- Enhanced Model class base with new configurable post_init and register methods  
- Created InferenceHistory to track global state of all inferences completed  
- Multiple improvements and updates to logging at module level  
- Note: starting with v0.3.0, pip install provides two options - a base minimal install `pip3 install llmware` which will support most use cases, and a larger install `pip3 install 'llmware[full]'` with other commonly-used libraries.  
  
**Wednesday, May 22 - v0.2.15**  
- Improvements in Model class handling of Pytorch and Transformers dependencies (just-in-time loading, if needed)  
- Expanding API endpoint options and inference server functionality - see new [client access options](https://github.com/llmware-ai/llmware/tree/main/examples/Use_Cases/llmware_inference_api_client.py)  and [server_launch](https://github.com/llmware-ai/llmware/tree/main/examples/Use_Cases/llmware_inference_server.py)  

**Saturday, May 18 - v0.2.14**  
- New OCR image parsing methods with [example](https://github.com/llmware-ai/llmware/tree/main/examples/Use_Cases/slicing_and_dicing_office_docs.py)  
- Adding first part of logging improvements (WIP) in Configs and Models.    
- New embedding model added to catalog - industry-bert-loans.  
- Updates to model import methods and configurations.  

**Sunday, May 12 - v0.2.13**  
- New GGUF streaming method with [basic example](https://github.com/llmware-ai/llmware/tree/main/examples/Models/gguf_streaming.py) and [phi3 local chatbot](https://github.com/llmware-ai/llmware/tree/main/examples/UI/gguf_streaming_chatbot.py)  
- Significant cleanups in ancillary imports and dependencies to reduce install complexity - note: the updated requirements.txt and setup.py files.  
- Defensive code to provide informative warning of any missing dependencies in specialized parts of the code, e.g., OCR, Web Parser.  
- Updates of tests, notice and documentation.   
- OpenAIConfigs created to support Azure OpenAI.   
  
**Sunday, May 5 - v0.2.12 Update**  
- Launched ["bling-phi-3"](https://huggingface.co/llmware/bling-phi-3) and ["bling-phi-3-gguf"](https://huggingface.co/llmware/bling-phi-3-gguf) in ModelCatalog - newest and most accurate BLING/DRAGON model  
- New long document summarization method using slim-summary-tool [example](https://github.com/llmware-ai/llmware/tree/main/examples/Prompts/document_summarizer.py)  
- New Office (Powerpoint, Word, Excel) sample files [example](https://github.com/llmware-ai/llmware/tree/main/examples/Parsing/parsing_microsoft_ir_docs.py)  
- Added support for Python 3.12  
- Deprecated faiss and replaced with 'no-install' chromadb in Fast Start examples  
- Refactored Datasets, Graph and Web Services classes  
- Updated Voice parsing with WhisperCPP into Library  
  
**Monday, April 29 - v0.2.11 Update**  
- Updates to gguf libs for Phi-3 and Llama-3  
- Added Phi-3 [example](https://github.com/llmware-ai/llmware/tree/main/examples/Models/using-microsoft-phi-3.py)  and Llama-3 [example](https://github.com/llmware-ai/llmware/tree/main/examples/Models/using-llama-3.py) and Quantized Versions to Model Catalog  
- Integrated WhisperCPP Model class and prebuilt shared libraries - [getting-started-example](https://github.com/llmware-ai/llmware/tree/main/examples/Models/using-whisper-cpp-getting-started.py)  
- New voice sample files for testing - [example](https://github.com/llmware-ai/llmware/tree/main/examples/Models/using-whisper-cpp-sample-files.py)  
- Improved CUDA detection on Windows and safety checks for older Mac OS versions  

**Monday, April 22 - v0.2.10 Update**  
- Updates to Agent class to support Natural Language queries of Custom Tables on Postgres [example](https://github.com/llmware-ai/llmware/tree/main/examples/Use_Cases/agent_with_custom_tables.py)  
- New Agent API endpoint implemented with LLMWare Inference Server and new Agent capabilities [example](https://github.com/llmware-ai/llmware/tree/main/examples/SLIM-Agents/agent_api_endpoint.py)  
  
**Tuesday, April 16 - v0.2.9 Update**  
- New CustomTable class to rapidly create custom DB tables in conjunction with LLM-based workflows.  
- Enhanced methods for converting CSV and JSON/JSONL files into DB tables.  
- See new examples [Creating Custom Table example](https://github.com/llmware-ai/llmware/tree/main/examples/Structured_Tables/create_custom_table-1.py)
    
**Tuesday, April 9 - v0.2.8 Update**  
- Office Parser (Word Docx, Powerpoint PPTX, and Excel XLSX) - multiple improvements - new libs + Python method.  
- Includes: several fixes, improved text chunking controls, header text extraction and configuration options.  
- Generally, new office parser options conform with the new PDF parser options.  
- Please see [Office Parsing Configs example](https://github.com/llmware-ai/llmware/tree/main/examples/Parsing/office_parser_new_configs.py)  

**Wednesday, April 3 - v0.2.7 Update**  
- PDF Parser - multiple improvements - new libs + Python methods.  
- Includes: UTF-8 encoding for European languages.  
- Includes: Better text chunking controls, header text extraction and configuration options.  
- Please see [PDF Parsing Configs example](https://github.com/llmware-ai/llmware/tree/main/examples/Parsing/pdf_parser_new_configs.py) for more details.  
- Note:  deprecating support for aarch64-linux (will use 0.2.6 parsers).  Full support going forward for Linux Ubuntu20+ on x86_64 + with CUDA.  
  
**Friday, March 22 - v0.2.6 Update**  
- New SLIM models:  summary, extract, xsum, boolean, tags-3b, and combo sentiment-ner.  
- New logit and sampling analytics.  
- New SLIM examples showing how to use the new models.  
  
**Thursday, March 14 - v0.2.5 Update**  
- Improved support for GGUF on CUDA (Windows and Linux), with new prebuilt binaries and exception handling.  
- Enhanced model configuration options (sampling, temperature, top logit capture).  
- Added full back-level support for Ubuntu 20+ with parsers and GGUF engine.  
- Support for new Anthropic Claude 3 models.  
- New retrieval methods: document_lookup and aggregate_text.  
- New model:  bling-stablelm-3b-tool - fast, accurate 3b quantized question-answering model - one of our new favorites.  

**Wednesday, February 28 - v0.2.4 Update**  
- Major upgrade of GGUF Generative Model class - support for Stable-LM-3B, CUDA build options, and better control over sampling strategies.
- Note: new GGUF llama.cpp built libs packaged with build starting in v0.2.4.  
- Improved GPU support for HF Embedding Models.   
  
**Friday, February 16 - v0.2.3 Update**  
- Added 10+ embedding models to ModelCatalog - nomic, jina, bge, gte, ember and uae-large.   
- Updated OpenAI support >=1.0 and new text-3 embedding models.    
- SLIM model keys and output_values now accessible in ModelCatalog.  
- Updating encodings to 'utf-8-sig' to better handle txt/csv files with bom.  

**Supported Operating Systems**: MacOS (Metal and x86), Linux (x86 and aarch64), Windows  
- note on Linux: we test most extensively on Ubuntu 22 and now Ubuntu 20 and recommend where possible  
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

