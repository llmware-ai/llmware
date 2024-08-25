

Fast Start: Building Agent workflows with small language models with llmware  
===============

**Welcome to llmware!**    

Set up  

`pip3 install llmware` or `pip3 install 'llmware[full]'` or, if you prefer clone the github repo locally, e.g., `git clone git@github.com:llmware-ai/llmware.git`.  If you clone the repo, then we would recommend that you run the `welcome_to_llmware.sh` or `welcome_to_llmware_windows.sh` scripts to install all of the dependencies.    

Note: starting in llmware>=0.3.0, we offer two pip install options.  If you use the standard `pip3 install llmware`, then you will need to add a few additional pip3 installs to run examples 2 and 5 below, specifically:  

  `pip3 install torch`  
  `pip3 install transformers`  

Platforms:  
- Mac M1/M2/M3, Windows, Linux (Ubuntu 20 or Ubuntu 22 preferred)  
- RAM: 16 GB minimum  
- Python 3.9, 3.10, 3.11, 3.12 
- Pull the latest version of llmware
- Please note that we have updated the examples from the original versions, to use new features in llmware, so there may be minor differences with the videos, which are annotated in the comments in each example.    
  
There are 15 examples, designed to be used step-by-step, but each is self-contained,  
so you can feel free to jump into any of the examples, in any order, that you prefer.  

Each example has been designed to be "copy-paste" and RUN with lots of helpful comments and explanations embedded in the code samples.  

Examples:  

1.  **Start here** - start downloading and running question-answering and function-calling models in minutes.   

2.  **llmware_sampler_bling_dragon** - get started with BLING and DRAGON models for high-quality, fact-based inferencing.  

3.  **using-slim-extract** - start using a function-calling small specialized model for extracting information from documents.  

4.  **using-slim-summary** - start using a function-calling small specialized model for summarizing information.  

5.  **agent-llmfx** - build your first agent process and run it all locally.   

6.  **agent-multistep-process** - a second example of a multi-step agent process to analyze, classify and extract information from a complex document.  

7.  **using-whisper** - voice transcription to text in minutes, running locally with whisper-cpp.  

8.  **using-phi-3-function-calls** - using phi3-mini for various function call processes.  

9.  **summarize_document** - summarizing a larger document.  

10.  **semantic similarity ranking** - using a semantic reranker to filter and build relevant text chunks from larger documents.  

11.  **gguf_streaming** - use the stream interface to stream text for larger generations.  

12.  **web_services** - integrate web services to build a complex research report, combined with three distinct function calling models.  

13.  **text-2-sql** - convert natural language queries into SQL and extract information from structured databases.  

14.  **rag-instruct-benchark-tester** - script for building rag benchmark performance tests.  

15.  **using-rag-benchmark-scores** - how to access and filter models by ranking accuracy on the benchmark test.    


After completing these 15 examples, you should have a good foundation and set of recipes to start 
exploring the other 100+ examples in the /examples folder, and build more sophisticated 
LLM-based applications.  

**Models**  
  - All of these examples are optimized for using local CPU-based models, primarily BLING, DRAGON and SLIM models.   
  - If you want to substitute for any other model in the catalog, it is generally as easy as 
    switching the model_name.  If the model requires API keys, we show in the examples how to pass those keys as an
    environment variable.  

**Local Private**
    - All of the processing will take place locally on your laptop.

*This is an ongoing initiative to provide easy-to-get-started tutorials - we welcome and encourage feedback, as well
as contributions with examples and other tips for helping others on their LLM application journeys!*  

**Let's get started!**


