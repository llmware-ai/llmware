
##   OS Insight X

This application allows users to interact with Galvin's Operating System textbook by asking questions and receiving accurate, context-aware answers. The system leverages LangChain for document processing and LLMWare for intelligent responses.

## Features

- Load and process PDF documents from Galvin's OS textbook.
- Split documents into manageable chunks for efficient retrieval.
- Use pre-trained LLMWare models to generate embeddings and provide answers.
- Simple Streamlit interface for easy interaction.



## APP PREVIEW

https://github.com/sneha-4-22/RAG-OS-qa/assets/112711068/04735392-d9e1-46ea-951b-17ab7a662f58


## Model Used

The model used in this project is [Industry-BERT for Insurance](https://huggingface.co/llmware/industry-bert-insurance-v0.1) provided by Hugging Face. It was employed for the operating system question-answering task using the RAG (Retrieval-Augmented Generation) framework.


## Prerequisites

- Python
- Streamlit
- Hugging Face Hub API token
- Required Python libraries listed in `requirements.txt`
- If you encounter any issues during installation, then create anaconda env open its terminal then proceed . 
## Installation 
1. **Clone the Repository**
    ```bash
    git clone https://github.com/yourusername/os-insight-x.git
    ```
2. **Create and Activate Anaconda Environment**
3. **Install Dependencies in Anaconda powershell**
   ```bash
    pip install -r requirements.txt
    ```
4. **Set Up Environment Variables**
    - Create a `.env` file in the project root directory.
    - Add your Hugging Face Hub API token:
        ```
        HUGGINGFACEHUB_API_TOKEN=your_huggingfacehub_api_token
        ```
5. **Run vector.py**
   ```bash
    python run vector.py
    ```
6. **Run app.py**
   ```bash
    streamlit run app.py
    ```


