#! /bin/bash

# Welcome to LLMWare script - handles some basic setup for first-time cloning of the repo
# Windows version

# Install core dependencies
pip3 install -r ./llmware/requirements.txt

# Note: this step is optional but adds many commonly-used optional dependencies (including in several examples)
pip3 install -r ./llmware/requirements_extras.txt

# Move selected examples into root path for easy execution from command line
scp ./solutions/rag/*.py .
scp ./solutions/slim_agents/*.py .
scp ./solutions/models/bling_fast_start.py .
scp ./solutions/onnxruntime/using_onnx_models.py .
scp ./solutions/openvino/using_openvino_models.py .
scp ./solutions/use_cases/web_services_slim_fx.py .
scp ./solutions/use_cases/invoice_processing.py .
scp ./solutions/gguf/using-whisper-cpp-sample-files.py .
scp ./solutions/sources/parsing_microsoft_ir_docs.py .
scp ./solutions/gguf/gguf_streaming.py .
scp ./tutorials/getting_started/welcome_example.py .
scp ./tutorials/getting_started/loading_sample_files.py .

echo "Welcome Steps Completed"
echo "1.  Installed Core Dependencies"
echo "2.  Installed Several Optional Dependencies Useful for Running Examples"
echo "3.  Moved selected Getting Started examples into /root path"
echo ""
echo "To run an example from command-line:  python {example-name}.py"
echo "Note: check the /solutions folder for 100+ additional examples"
echo "Note: on first time use, models will be downloaded and cached locally"
echo "Note: open up the examples and edit for more configuration options"
echo ""

echo "Running welcome_example.py"
py welcome_example.py

# keeps bash console open (may be in separate window)
bash
