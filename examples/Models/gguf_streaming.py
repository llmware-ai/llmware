
""" This example illustrates how to use the stream method for GGUF models for fast streaming of inference,
especially for real-time chat interactions.

    Please note that the stream method has been implemented for GGUF models starting in llmware-0.2.13.  This will be
any model with GGUFGenerativeModel class, and generally includes models with names that end in "gguf".

    See also the chat UI example in the UI examples folder.

    We would recommend using a chat optimized model, and have included a representative list below.


"""


from llmware.models import ModelCatalog
from llmware.gguf_configs import GGUFConfigs

#   sets an absolute output maximum for the GGUF engine - normally set by default at 256
GGUFConfigs().set_config("max_output_tokens", 1000)

chat_models = ["phi-3-gguf",
               "llama-2-7b-chat-gguf",
               "llama-3-instruct-bartowski-gguf",
               "openhermes-mistral-7b-gguf",
               "zephyr-7b-gguf",
               "tiny-llama-chat-gguf"]

model_name = chat_models[0]

#   maximum output can be set optionally at any number up to the "max_output_tokens" set
model = ModelCatalog().load_model(model_name, max_output=500)

text_out = ""

token_count = 0

# prompt = "I am interested in gaining an understanding of the banking industry.  What topics should I research?"
prompt = "What are the benefits of small specialized LLMs?"

#   since model.stream provides a generator, then use as follows to consume the generator

for streamed_token in model.stream(prompt):

    text_out += streamed_token
    if text_out.strip():
        print(streamed_token, end="")

    token_count += 1

#   final output text and token count

print("\n\n***total text out***: ", text_out)
print("\n***total tokens***: ", token_count)
