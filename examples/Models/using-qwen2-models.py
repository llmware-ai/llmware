
""" This example shows how to use Qwen2 models in LLMWare, consisting of three main categories -

    1 - standard QWEN2 chat/instruct models, packaged in GGUF in 7B / 1.5B / 0.5B sizes.

    2 - RAG fine-tuned QWEN2 in DRAGON and BLING series.

    3 - Extract function-calling finetune in SLIM series.

"""

from llmware.models import ModelCatalog

#  1 - MAIN CATALOG - 3 QWEN2 GGUF models for chat (7B / 1.5B / 0.5B)

qwen2_base_gguf = ["qwen2-7b-instruct-gguf", "qwen2-1.5b-instruct-gguf", "qwen2-0.5b-instruct-gguf"]

print("\nExample #1 - loading Qwen2-instruct model - may take a minute the first time.")

qwen2 = ModelCatalog().load_model("qwen2-1.5b-instruct-gguf", max_output=200)
response = qwen2.inference("I am going to visit Istanbul.  What should I see?")
print("\nresponse: ", response)

#   2 - RAG FINETUNE - DRAGON + BLING

print("\nExample #2 - RAG finetuned Qwen2 for fact-based question answering with context passage.")

qwen2_rag_finetunes = ["dragon-qwen-7b-gguf", "bling-qwen-1.5b-gguf", "bling-qwen-0.5b-gguf"]

qwen2_rag = ModelCatalog().load_model("bling-qwen-1.5b-gguf", temperature=0.0, sample=False)
context = "The stock is now soaring to $120 per share after great earnings."
response = qwen2_rag.inference("What is the current stock price?", add_context=context)

print("\nqwen2-rag response: ", response)


#   3 - FUNCTION-CALLING EXTRACTION SLIM MODELS

print("\nExample #3 - Qwen2 Extract function calling model.")

qwen2_extract_function_calls = ["slim-extract-qwen-1.5b-gguf", "slim-extract-qwen-0.5b-gguf"]

context_passage = ("Adobe shares tumbled as much as 11% in extended trading Thursday after the design software maker "
    "issued strong fiscal first-quarter results but came up slightly short on quarterly revenue guidance. "
    "Here’s how the company did, compared with estimates from analysts polled by LSEG, formerly known as Refinitiv: "
    "Earnings per share: $4.48 adjusted vs. $4.38 expected Revenue: $5.18 billion vs. $5.14 billion expected "
    "Adobe’s revenue grew 11% year over year in the quarter, which ended March 1, according to a statement. "
    "Net income decreased to $620 million, or $1.36 per share, from $1.25 billion, or $2.71 per share, "
    "in the same quarter a year ago. During the quarter, Adobe abandoned its $20 billion acquisition of "
    "design software startup Figma after U.K. regulators found competitive concerns. The company paid "
    "Figma a $1 billion termination fee.")

qwen2_extract = ModelCatalog().load_model("slim-extract-qwen-1.5b-gguf",temperature=0.0,sample=False)
response = qwen2_extract.function_call(context_passage, params=["earnings per share"])

print("\nqwen2-extract response: ", response)

