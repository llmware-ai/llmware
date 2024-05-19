# ManualMate

## Overview

ManualMate is a tool for easily accessing and understanding user manuals for a broad array of home appliances, such as washing machines and dryers.

ManualMate is a Flask-based web application designed to facilitate the automatic processing of appliance manuals through semantic queries and prompts. The application parses manuals, executes semantic queries based on user prompts, and provides detailed responses, making it an ideal tool for quick reference and safety guideline extraction from user manuals of home appliances.


**Demo video:** [https://youtu.be/7XZjfo3bL-4](https://youtu.be/7XZjfo3bL-4)


## Technology 

This application showcases the Retrieve and Generate (RAG) model, which comprises the following steps:

1. It initiates with a natural language query to retrieve relevant text segments from an extensive library.
2. These segments then serve as context in constructing prompts for posing questions to a sophisticated large language model (LLM).

In this demonstration, we will explore:

1. Building a comprehensive library and establishing embeddings.
2. Performing an extensive semantic search throughout the library.
3. Identifying and selecting the documents most relevant to the query.
4. Processing each selected document to extract contextual information, which is then used to query our LLM for insights.
5. Delivering precise answers through a JSON HTTP API.

A notable aspect of this project is the integration of [LLMWare](https://llmware-ai.github.io/llmware/), a tool designed to enhance applications with advanced language model capabilities. According to the LLMWare documentation, LLMWare provides APIs that facilitate the incorporation of large language models into various software applications, enabling functionalities such as text analysis, natural language understanding, and automated content generation. In this context, LLMWare could be used to refine the querying process, enhance the analysis of text data, or even interpret and summarize the contents of the logged results more intelligently.

## Application Structure

The application is organized into several directories, each serving a specific function:

- **`app/`** - The main package containing all application-related code.
  - **`__init__.py`** - Contains the application factory setup to initialize the Flask app with configured settings.
  - **`api/`** - Houses the API route definitions using Blueprints to handle HTTP requests.
    - **`routes.py`** - API route definitions for processing manuals.
  - **`services/`** - Contains business logic for the core functionality of the application.
    - **`manuals_processor.py`** - Handles the processing of manuals using semantic queries and responses.
  - **`utils/`** - Utility functions and classes supporting the main application functions.
    - **`manual_downloader.py`** - Manages the downloading of manuals from a specified source.
  - **`config.py`** - Manages configuration settings and environment-specific configurations for the Flask application.

- **`run.py`** - The entry point script that runs the Flask application using the application factory.


## Setup and Installation


To get ManualMate running on your local machine, follow these steps:

1. **Clone the Repository:**
   ```bash
   git clone https://yourrepositorylink.com/manualmate.git
   cd manualmate
   ```

2. **Create and Activate a Virtual Environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application:**
   ```bash
   python run.py
   ```

## Environment Setup

To configure the application to run properly in your environment, you will need to set up the necessary environment variables. These variables are crucial for connecting to databases, specifying library settings, and integrating with external APIs.

### `.env` File

The `.env` file should be placed in the root of the repository and must not be checked into version control for security reasons. This file contains sensitive and environment-specific settings.

### `.env.sample`

For ease of setup, a sample environment file named `.env.sample` is provided in the root of the repository. This file includes all the necessary environment variables with example or default values (where applicable) that you can use as a template to create your own `.env` file.

Here is what the `.env.sample` contains:

```
ACTIVE_DB = "sqlite"
LIBRARY_NAME = "manuals_library"
EMBEDDING_MODEL_NAME = "mini-lm-sbert"
VECTOR_DB = "chromadb"
LLM_MODEL_NAME = "llmware/bling-tiny-llama-v0"
LOCAL_DIRECTORY = 'data/manuals'
BUCKET_NAME = 'manual-mate'
OPENAI_API_KEY=
```

### Setting Up Your `.env` File

1. Copy the `.env.sample` file to a new file named `.env` in the same directory.
2. Fill in the `OPENAI_API_KEY` and any other environment-specific values in the `.env` file.
3. Ensure that the `.env` file is included in your `.gitignore` to prevent it from being exposed in version control.

The application will load these settings at runtime, ensuring it operates with configurations appropriate for your environment.


## API Usage

### Processing Manuals

**Endpoint:** `/process_manuals`

**Method:** POST

**Description:** Processes uploaded manuals based on the provided semantic query and returns responses related to the query.

**Sample Request:**
```bash
curl --location 'http://127.0.0.1:5000/process_manuals' \
--header 'Content-Type: application/json' \
--data '{
    "prompt": "What are the warnings?"
}'
```

**Sample Response:**
```json
{
    "response": {
        "DR_EUS_MFL70442693_07_240307_00_OM_WEB_EN.pdf": [
            "•You may be killed or seriously injured if you do not follow instructions. ... •All safety messages will tell you what the potential hazard is, tell you how to reduce the chance of injury, and tell you what may happen if the instructions are not followed."
        ],
        "WM_EUS_MFL71728908_03_230322_00_OM_WEB_EN.pdf": [
            "•WARNING: Do not use this product for other than normal and proper household use (e.g., commercial or industrial use) or contrary to the Product owner's manual. ... •WARNING: Damage or failure"
        ]
    }
}
```

## Contributing

We welcome contributions from the community, whether it's in the form of feature requests, bug reports, or code contributions.

## License

ManualMate is licensed under [MIT LICENSE](LICENSE). For more information on the terms of use and distribution, please review the license agreement.
