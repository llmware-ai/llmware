#! /bin/bash

# Welcome to LLMWare script - handles some basic setup for first-time cloning of the repo
# Mac / Linux version

# Install core dependencies
pip3 install -r ./llmware/requirements.txt

# # Note: this step is optional but adds many commonly-used optional dependencies (including in several examples)
pip3 install -r ./llmware/requirements_extras.txt

# Move selected examples into root path for easy execution from command line
scp ./examples/Getting_Started/welcome_example.py .
scp ./fast_start/rag/*.py .
scp ./examples/UI/gguf_streaming_chatbot.py .
scp ./examples/SLIM-Agents/agent-llmfx-getting-started.py .
scp ./examples/SLIM-Agents/using_slim_extract_model.py .
scp ./examples/SLIM-Agents/using_slim_summary.py .
scp ./examples/Models/bling_fast_start.py .
scp ./examples/Models/dragon_gguf_fast_start.py .
scp ./examples/Prompts/document_summarizer.py .
scp ./examples/Use_Cases/web_services_slim_fx.py .
scp ./examples/Use_Cases/invoice_processing.py .
scp ./examples/Models/using-whisper-cpp-sample-files.py .
scp ./examples/Parsing/parsing_microsoft_ir_docs.py .
scp ./examples/Models/chat_models_gguf_fast_start.py .
scp ./examples/Models/gguf_streaming.py .

echo "\nWelcome Steps Completed"
echo "1.  Installed Core Dependencies"
echo "2.  Installed Several Optional Dependencies Useful for Running Examples"
echo "3.  Moved selected Getting Started examples into /root path"
echo "    -- welcome_example.py"
echo "    -- example-1-create_first_library.py"
echo "    -- example-2-build_embeddings.py"
echo "    -- example-3-prompts_and_models.py"
echo "    -- example-4-rag-text-query.py"
echo "    -- example-5-rag-semantic-query.py"
echo "    -- example-6-rag-multi-step-query.py"
echo "    -- gguf_streaming.py"
echo "    -- bling_fast_start.py"
echo "    -- using_slim_extract_model.py"
echo "    -- using_slim_summary.py"
echo "    -- dragon_gguf_fast_start.py"
echo "    -- invoice_processing.py"
echo "    -- gguf_streaming_chatbot.py"
echo "    -- agent-llmfx-getting-started.py"
echo "    -- whisper-cpp-sample-files.py"
echo "    -- web_services_slim_fx.py"
echo "    -- parsing_microsoft_ir_docs.py"
echo "    -- document_summarizer.py"
echo "    -- chat_models_gguf_fast_start.py"

echo ""
echo "To run an example from command-line:  python3 welcome_example.py"
echo "To run gguf_streaming_chatbot.py: streamlit run gguf_streaming_chatbot.py"
echo "Note: check the /examples folder for 100+ additional examples"
echo "Note: on first time use, models will be downloaded and cached locally"
echo "Note: open up the examples and edit for more configuration options"
echo ""

# run welcome_example.py which serves as a test that the installation is successful
echo "Running welcome_example.py"
python3 welcome_example.py
