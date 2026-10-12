 🚀 Use Cases Examples  🚀  
===============

**End-to-End Scenarios**    

In this repository, we feature several 'end-to-end' examples that show how to use LLMWare in a complex recipe combining different elements to accomplish a specific objective.   While each example is still high-level, it is shared in the spirit of providing a high-level framework 'starting point' that can be developed in more detail for a variety of common use cases.  All of these examples use small, specialized models, running locally - 'Small, but Mighty' !  


1.  [**Research Automation with Agents and Web Services**](https://www.github.com/llmware-ai/llmware/tree/main/examples/Use_Cases/web_services_slim_fx.py)  

    - Prepare a 30-key research analysis on a company  
    - Extract key lookup and other information from an earnings press release  
    - Automatically use the lookup data for real-time stock information from YFinance 
    - Automatically use the lookup date for background company history information in Wikipedia  
    - Run LLM prompts to ask key questions of the Wikipedia sources 
    - Aggregate into a consolidated research analysis
    - All with local open source models  


2.  [**Invoice Processing**](https://www.github.com/llmware-ai/llmware/tree/main/examples/Use_Cases/invoice_processing.py)  

    - Parse a batch of invoices (provided as sample files)  
    - Extract key information from the invoices 
    - Save the prompt state for follow-up review and analysis 


3.  [**Analyzing and Extracting Voice Transcripts**](https://www.github.com/llmware-ai/llmware/tree/main/examples/Use_Cases/parsing_great_speeches.py)  

    - Voice transcription of 50+ wav files of great speeches of the 20th century  
    - Run text queries against the transcribed wav files 
    - Execute LLM agent inferences to extract and identify key elements of interest 
    - Prepare 'bibliography' with the key extracted points, including time-stamp 


4.  [**MSA Processing**](https://www.github.com/llmware-ai/llmware/tree/main/examples/Use_Cases/msa_processing.py)

    - Identify the termination provisions in Master Service Agreements among a larger batch of contracts  
    - Parse and query a large batch of contracts and identify the agreements with "Master Service Agreement" on the first page  
    - Find the termination provisions in each MSA  
    - Prompt LLM to read the termination provisions and answer a key question  
    - Run a fact-check and source-check on the LLM response
    - Save all of the responses in CSV and JSON for follow-up review.  


5.  [**Querying a CSV**](https://www.github.com/llmware-ai/llmware/tree/main/examples/Use_Cases/agent_with_custom_tables.py) 

    - Start running natural language queries on CSVs with Postgres and slim-sql-tool.  
    - Load a sample 'customer_table.csv' into Postgres
    - Start running natural language queries that get converted into SQL and query the DB  
    

6.  [**Contract Analysis**](https://www.github.com/llmware-ai/llmware/tree/main/examples/Use_Cases/contract_analysis_on_laptop_with_bling_models.py)  

    - Extract key information from set of employment agreement  
    - Use a simple retrieval strategy with keyword search to identify key provisions and topic areas  
    - Prompt LLM to read the key provisions and answer questions based on those source materials  

7.  [**Slicing and Dicing Office Docs**](https://www.github.com/llmware-ai/llmware/tree/main/examples/Use_Cases/slicing_and_dicing_office_docs.py)  

    - Shows a variety of advanced parsing techniques with Office document formats packaged in ZIP archives  
    - Extracts tables and images, runs OCR against the embedded images, exports the whole library, and creates dataset  
    
8. **LLMWare Private Inference Server**

    - Set up server in minutes on CPU, GPU or local - [server](https://www.github.com/llmware-ai/llmware/tree/main/examples/Use_Cases/llmware_inference_server.py)  
    
    - Run 3 different modes of client access to the API - [client](https://www.github.com/llmware-ai/llmware/tree/main/examples/Use_Cases/llmware_inference_api_client.py)  
   
    - Supports rapid development, testing and prototyping and flexibility of deployment models for wide range of RAG and Agent use cases  


### Optional market sentiment research

[Adanos market sentiment](adanos_market_sentiment.py) fetches a dated snapshot
and passes it as `add_context` to the existing `bling-phi-3-gguf` local model.
It does not replace llmware's sentiment models or change core dependencies.
Design discussion: [#1320](https://github.com/llmware-ai/llmware/discussions/1320).

[Adanos](https://adanos.org/) is a commercial service with a free plan; the
integration author represents Adanos. Source access, historical retention, and
quotas differ by account plan. See the [API documentation](https://api.adanos.org/docs).
Set `ADANOS_API_KEY` through your process environment or secret manager, never
in this source file. Without a key the example skips API calls and model loading.
With a key, first use may download the local model weights.

```shell
python solutions/use_cases/adanos_market_sentiment.py --source news_stocks --asset BRK --from 2026-10-01 --to 2026-10-02
```

Sources: `reddit_stocks`, `reddit_crypto`, `x_stocks`, `news_stocks`,
`polymarket_stocks`. Only Reddit supports crypto; use `--asset BTC` there.
News uses company keys such as `BRK`, not `BRK.B`. Dates are inclusive UTC
`from`/`to`, not deprecated `days`. Choose a recent window covered by your plan.
401/403/429, unavailable providers, invalid JSON and oversized responses remain
errors, not neutral sentiment. Transport is capped at 32 KB and model context
at 3,000 ASCII characters; narrow the dates rather than silently truncate data.

The returned evidence retains source, dates and retrieval time. Historical
aggregates fetched today are not evidence of past availability. Provider data
and generated summaries need independent verification and are not investment
advice. No trading, historical backtest, or storage workflow is added.

Check back often - we are updating these examples regularly - and many of these examples have companion videos as well.


### **Let's get started!  🚀**


