---
layout: default
title: Use Cases
parent: Examples
nav_order: 1
description: overview of the major modules and classes of LLMWare  
permalink: /examples/use_cases
---
🚀 Use Cases Examples  🚀  
---

**End-to-End Scenarios**    

We provide several 'end-to-end' examples that show how to use LLMWare in a complex recipe combining different elements to accomplish a specific objective.   While each example is still high-level, it is shared in the spirit of providing a high-level framework 'starting point' that can be developed in more detail for a variety of common use cases.  All of these examples use small, specialized models, running locally - 'Small, but Mighty' !  


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
    

For more examples, see the [use cases example]((https://www.github.com/llmware-ai/llmware/tree/main/examples/Use_Cases/) in the main repo.   

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
        <a href="https://huggingface.co/llmware"><span>  <i class="fa-solid fa-face-smiling-hands"></i>
        </span></a>
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
