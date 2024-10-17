#!/bin/bash

# Welcome to the LLMWare script - handles basic setup for first-time cloning of the repo
# Windows version

# Function to handle errors
function error_exit {
    echo "Error: $1"
    exit 1
}

# Install core dependencies
echo "Installing core dependencies..."
pip3 install -r ./llmware/requirements.txt || error_exit "Failed to install core dependencies."

# Install optional dependencies (optional step)
echo "Installing optional dependencies..."
pip3 install -r ./llmware/requirements_extras.txt || echo "Optional dependencies installation skipped or failed."

# Move selected examples into root path for easy execution from the command line
echo "Moving selected examples to the root path..."
declare -a examples=(
    "examples/Getting_Started/welcome_example.py"
    "fast_start/rag/*.py"
    "examples/UI/gguf_streaming_chatbot.py"
    "examples/SLIM-Agents/agent-llmfx-getting-started.py"
    "examples/SLIM-Agents/using_slim_extract_model.py"
    "examples/SLIM-Agents/using_slim_summary.py"
    "examples/Models/bling_fast_start.py"
    "examples/Models/dragon_gguf_fast_start.py"
    "examples/Prompts/document_summarizer.py"
    "examples/Use_Cases/web_services_slim_fx.py"
    "examples/Use_Cases/invoice_processing.py"
    "examples/Models/using-whisper-cpp-sample-files.py"
    "examples/Parsing/parsing_microsoft_ir_docs.py"
    "examples/Models/chat_models_gguf_fast_start.py"
    "examples/Models/gguf_streaming.py"
)

for example in "${examples[@]}"; do
    cp "$example" . || error_exit "Failed to copy $example."
done

echo "Welcome Steps Completed"
echo "1. Installed Core Dependencies"
echo "2. Installed Several Optional Dependencies Useful for Running Examples"
echo "3. Moved selected Getting Started examples into /root path"

echo "Selected examples:"
for example in "${examples[@]}"; do
    echo "   -- $(basename "$example")"
done

echo ""
echo "To run an example from the command line: py welcome_example.py"
echo "To run gguf_streaming_chatbot.py: streamlit run gguf_streaming_chatbot.py"
echo "Note: Check the /examples folder for 100+ additional examples."
echo "Note: On first-time use, models will be downloaded and cached locally."
echo "Note: Open up the examples and edit for more configuration options."
echo ""

echo "Running welcome_example.py..."
py welcome_example.py || error_exit "Failed to run welcome_example.py."

# Keeps the bash console open (may be in a separate window)
exec bash
