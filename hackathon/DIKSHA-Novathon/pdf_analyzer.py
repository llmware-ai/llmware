import sys
import os
import traceback
from llmware.prompts import Prompt
from llmware.gguf_configs import GGUFConfigs

def analyze_pdf(pdf_path, question):
    try:
        # Extensive input validation
        if not pdf_path:
            raise ValueError("PDF path is empty")
        
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found at: {pdf_path}")
        
        if not question:
            raise ValueError("Question cannot be empty")

        # Detailed model and configuration logging
        print(f"Debug: Attempting to analyze PDF at {pdf_path}")
        print(f"Debug: Question - {question}")

        # Configure GGUF models with more verbose settings
        GGUFConfigs().set_config("max_output_tokens", 500)
        
        # Attempt to list and select model
        try:
            available_models = Prompt().list_available_models()
            print(f"Debug: Available Models - {available_models}")
        except Exception as model_list_error:
            print(f"Error listing models: {model_list_error}")
            available_models = []

        # Select appropriate model
        model_name = "llama-2-7b-chat-gguf"
        
        print(f"Debug: Attempting to load model {model_name}")
        
        # Create prompter with extensive error handling
        try:
            prompter = Prompt().load_model(
                model_name,
                max_output=450,
                temperature=0.0,
                sample=False,
                register_trx=True
            )
        except Exception as model_load_error:
            print(f"Critical Error Loading Model: {model_load_error}")
            print(traceback.format_exc())
            raise

        # Add PDF source with error handling
        try:
            prompter.add_source_document(".", os.path.basename(pdf_path))
        except Exception as source_add_error:
            print(f"Error adding source document: {source_add_error}")
            print(traceback.format_exc())
            raise

        # Generate response with comprehensive error tracking
        try:
            response = prompter.prompt_with_source(
                question,
                prompt_name="default_with_context"
            )
            
            # Detailed response logging
            print(f"Debug: Full Response - {response}")
            
            # Print LLM response
            print(response[0]["llm_response"])
        
        except Exception as response_error:
            print(f"Error generating response: {response_error}")
            print(traceback.format_exc())
            raise

    except Exception as e:
        print(f"Comprehensive Error Processing PDF: {str(e)}")
        print(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python pdf_analyzer.py <pdf_path> <question>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    question = sys.argv[2]

    analyze_pdf(pdf_path, question)