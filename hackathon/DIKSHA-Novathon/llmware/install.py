from huggingface_hub import hf_hub_download

# Download model file
model_path = hf_hub_download(
    repo_id="TheBloke/Llama-2-7B-Chat-GGUF",
    filename="llama-2-7b-chat.Q4_K_M.gguf"
)

# Then load model using this path
model = ModelCatalog().load_model(
    model_name,
    temperature=0.3,
    sample=True,
    max_output=450,
    model_path=model_path
)