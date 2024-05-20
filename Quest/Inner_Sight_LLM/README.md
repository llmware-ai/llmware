# Inner Sight 
InnerSight is a sentiment analysis LLM Integrated - Web App for Therapeutic Conversations. <br /> <br />
It Integrates ```LLMware library``` to perform Retrieval Augmented Generation (RAG) based document analysis on collection of medical, mental illness & therapeutical books
providing sentiment analysis and a QA Chatbot for Conversations with the LLM used


<br /> <br />


## Models Information
* ```llmrails/ember-v1```:  Embeddings Model for generating text embeddings.  [Link](https://huggingface.co/llmrails/ember-v1)
* ```TheBloke/zephyr-7B-beta-GGUF```:  Used as the Generative LLM Model 

## Tech Stack

* ```LLMWARE```: AI Toolkit -  Document, Text Chunking, Embeddings & Generative Model
* ```FastAPI```: Backend Web Server for Serving LLM
* ```React.js + Axios```:  Client Side Web App


 <br />


## Getting Started

1. First Clone the repo
```
  git clone https://github.com/ShubhamTiwary914/innersightLLM.git
  cd innersightLLM
```

 <br />

2. Install Dependencies

> Server Side - Create Virtual env(conda) and install fastapi dependencies
```
  cd api
  conda create --name innersight
  conda activate
  pip install -r requirements.txt
  uvicorn server:app --port 8000
```

> Client Side - React App
```
   cd app
   npm install
   npm run dev
```

<br />

3. After successfull, your app should be running at: http://localhost:3100/


<br /> <br />


## Screenshots

![Screenshot from 2024-05-20 04-14-46](https://github.com/ShubhamTiwary914/innersightLLM/assets/67773966/faca2669-3c1f-4f13-a76a-1d39d32042d7)

<br />

![Screenshot from 2024-05-20 04-14-54](https://github.com/ShubhamTiwary914/innersightLLM/assets/67773966/d4f5ec77-d586-48c7-9118-2494fa1b5984)

<br />

![Screenshot from 2024-05-20 04-16-48](https://github.com/ShubhamTiwary914/innersightLLM/assets/67773966/e2afaa6c-134a-4379-aa20-6a613522b5ce)


<br />


## Video Link - Youtube

[![Video](https://img.youtube.com/vi/ztF8juU62ew/maxresdefault.jpg)](https://www.youtube.com/watch?v=ztF8juU62ew)


