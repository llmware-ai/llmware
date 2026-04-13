
""" This example shows how to add a custom or private OpenVino or ONNX model to the llmware model catalog.

    Over the next few releases, we will be expanding the default ModelCatalog considerably, but for the time
    being, please feel free to follow the steps below to build your own custom catalog.

    We show below templates for the model card dictionaries - most of which is fairly easy to build for a given
    model.

    We highlight both the main step - which is a simple one-liner to register the model, and then provide
    more details on three potential troubleshooting items:

        1 - using a model from a custom/private path - and 'inserting' directly into the model_repo lookup
        2 - identifying the prompt wrapper template
        3 - customizing a new prompt wrapper

"""

from llmware.models import ModelCatalog
from llmware.prompts import Prompt
from llmware.configs import LLMWareConfig

#   Create model card and register in the ModelCatalog

"""             Sample OpenVino Model Card template

 model_card_dict = {"model_name": "phi-3-ov", "model_family": "OVGenerativeModel",
                    "model_category": "generative_local", "display_name": "phi-3-ov",
                    "model_location": "llmware_repo",
                    "context_window": 4096, "instruction_following": False, "prompt_wrapper": "phi_3",
                    "temperature": 0.0, "sample_default": False, "trailing_space": "",
                    "tokenizer_local": "tokenizer_phi3.json",
                    "hf_repo": "llmware/phi-3-ov",
                    "custom_model_files": [], "custom_model_repo": "",
                    "fetch": {"snapshot": True, "module": "llmware.models", "method": "pull_snapshot_from_hf"},
                    "validation_files": ["openvino_model.xml"],
                    "link": "https://huggingface.co/llmware/phi-3-ov"},
"""

"""              Sample ONNX Model Card template 

model_card_dict =  {"model_name": "phi-3-onnx", "model_family": "ONNXGenerativeModel",
                    "model_category": "generative_local", "display_name": "phi-3-onnx",
                    "model_location": "llmware_repo",
                    "context_window": 4096, "instruction_following": False, "prompt_wrapper": "phi_3",
                    "temperature": 0.0, "sample_default": False, "trailing_space": "",
                    "tokenizer_local": "tokenizer_phi3.json",
                    "hf_repo": "llmware/phi-3-onnx",
                    "custom_model_files": [], "custom_model_repo": "",
                    "fetch": {"snapshot": True, "module": "llmware.models", "method": "pull_snapshot_from_hf"},
                    "validation_files": ["model.onnx", "model.onnx.data"],
                    "link": "https://huggingface.co/llmware/phi-3-onnx"},
"""

#   create the model card dictionary manually using the templates above as guides, e.g.,
model_card_dict = {"model_name": "my_model", "insert other params from above...": []}

#   this is the key step - registering the model card - add as a first line in any script/example
ModelCatalog().register_new_model_card(model_card_dict)

#   once the model is registered in the catalog, it can then be accessed anytime by name, e.g.,
model = ModelCatalog().load_model("my_model")
response = model.inference("What is ...")

# or if using in conjunction with building a RAG prompt
prompter = Prompt().load_model("my_model")

""" Issue # 1 - Models in local/custom path

   If you have the model in a local/custom path, then the easiest thing to do is to copy/move manually to 
    /llmware_data/model_repo/{{my_model_name}}/ and place the model components in this path.
"""

# lookup model repo path
model_path = LLMWareConfig().get_model_repo_path()
print("local model path: ", model_path)

# You can manually put the model components in a folder called "model_name" at the model repo path, and
# 'lookups' will all work.

""" Issue # 2 - How do I figure out the prompt template?
        
    Below is a list of the prompt wrapper lookups that covers most of the common models:
        
        # standard used in most llmware models - bling, dragon and slim
        "human_bot": {"main_start": "<human>: ", "main_stop": "\n", "start_llm_response": "<bot>:"},
        
        # commonly used by llama2 and mistral
        "<INST>": {"main_start": "<INST>", "main_stop": "</INST>", "start_llm_response": ""},
        
        "hf_chat": {"system_start": "<|im_start|>system\n", "system_stop": "<|im_end|>\n",
                    "main_start": "<|im_start|>user", "main_stop": "<|im_end|>\n",
                    "start_llm_response": "<|im_start|>assistant"},
        
        "open_chat": {"main_start": "GPT4 User: ", "main_stop": "<|endofturn|>",
                      "start_llm_response": "GPT4 Assistant:"},
        
        "alpaca": {"main_start": "### Instruction: ", "main_stop": "\n",
                   "start_llm_response": "### Response: "},
        
        "chat_ml": {"system_start": "<|im_start|>system", "system_stop": "<|im_end|>\n",
                    "main_start": "<|im_start|>user", "main_stop": "<|im_end|>\n",
                    "start_llm_response": "<|im_start|>assistant"},
        
        "phi_3": {"system_start": "<|system|>\n", "system_stop": "<|end|>\n",
                  "main_start": "<|user|>\n", "main_stop": "<|end|>\n", "start_llm_response": "<|assistant|>"},
        
        "llama_3_chat": {"system_start": "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n",
                         "system_stop": "<|eot_id|>",
                         "main_start": "<|start_header_id|>user>|end_header_id|>\n",
                         "main_stop": "<|eot_id|>",
                         "start_llm_response": "<|start_header_id|>assistant<|end_header_id|>\n"},
        
        "tiny_llama_chat": {"system_start": "<|system|>", "system_stop": "</s>",
                            "main_start": "<|user|>", "main_stop": "</s>",
                            "start_llm_response": "<|assistant|>"},
        
        "stablelm_zephyr_chat": {"system_start": "", "system_stop": "",
                                 "main_start": "<|user|>", "main_stop": "<|endoftext|>\n",
                                 "start_llm_response": "<|assistant|>"},
        
        "google_gemma_chat": {"system_start": "", "system_stop": "",
                              "main_start": "<bos><start_of_turn>user\n",
                              "main_stop": "<end_of_turn>\n",
                              "start_llm_response": "<start_of_turn>model"},
        
        "vicuna_chat": {"system_start": "", "system_stop": "",
                        "main_start": "USER: ", "main_stop": "",
                        "start_llm_response": " ASSISTANT:"}

"""

# if none of these templates work, then you can also register a new prompt template
ModelCatalog().register_new_finetune_wrapper("my_new_template",
                                             main_start="<user starts here>",
                                             main_stop="<user ends here>",
                                             llm_start="<model starts here>",
                                             system_start="<you are useful assistant...",
                                             system_stop="<end system stuff>"
                                             )

# once registered, this new prompt wrapper can also be invoked directly by "my_new_template", and it will be
# picked up in the lookup at the time of instantiating the model

