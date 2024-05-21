import streamlit as st
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

@st.cache_resource
def load_model_and_tokenizer(model_name):
    model = AutoModelForCausalLM.from_pretrained(model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    return model, tokenizer

def generate_code_completion(model, tokenizer, prompt, max_length=100):
    inputs = tokenizer(prompt, return_tensors="pt")
    input_ids = inputs['input_ids']

    with torch.no_grad():
        outputs = model.generate(input_ids, max_length=max_length, num_return_sequences=1)

    completion = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return completion

def main():
    st.title("Code Completion and Checker app")

    model_name = "llmware/bling-tiny-llama-v0"  # Change to the path of your trained model if needed
    st.write(f"Loading model and tokenizer for {model_name}...")
    model, tokenizer = load_model_and_tokenizer(model_name)
    st.write("Model and tokenizer loaded.")

    prompt = st.text_area("Enter incomplete code snippet:", height=200)

    if st.button("Complete Code"):
        if prompt:
            st.write("Generating completion...")
            completion = generate_code_completion(model, tokenizer, prompt)
            st.write("### Completed Code:")
            st.code(completion, language='python')
        else:
            st.write("Please enter an incomplete code snippet.")

if __name__ == "__main__":
    main()
