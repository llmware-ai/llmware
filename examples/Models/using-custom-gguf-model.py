
""" This example shows how to use any gguf model available on HuggingFace, and start using in inferences and
workflows with llmware.  In this scenario, we will take the following steps:

    1.  Register new GGUF model
    2.  Register new finetune wrapper, if needed
    3.  Start running inferences
"""

import time
import re

from llmware.models import ModelCatalog
from llmware.prompts import Prompt

#   Step 1 - register new gguf model - we will pick the popular LLama-2-13B-chat-GGUF

ModelCatalog().register_gguf_model(model_name="TheBloke/Llama-2-13B-chat-GGUF-Q2",
                                   gguf_model_repo="TheBloke/Llama-2-13B-chat-GGUF",
                                   gguf_model_file_name="llama-2-13b-chat.Q2_K.gguf",
                                   prompt_wrapper="my_version_inst")

#   Step 2- if the prompt_wrapper is a standard, e.g., Meta's <INST>, then no need to do anything else
#   -- however, if the model uses a custom prompt wrapper, then we need to define that too
#   -- in this case, we are going to create our "own version" of the Meta <INST> wrapper

ModelCatalog().register_new_finetune_wrapper("my_version_inst", main_start="<INST>", llm_start="</INST>")

#   Once we have completed these two steps, we are done - and can begin to use the model like any other

prompter = Prompt().load_model("TheBloke/Llama-2-13B-chat-GGUF-Q2")

question_list = ["I am interested in gaining an understanding of the banking industry. What topics should I research?",
                 "What are some tips for creating a successful business plan?",
                 "What are the best books to read for a class on American literature?"]


for i, entry in enumerate(question_list):

    start_time = time.time()
    print("\n")
    print(f"query - {i + 1} - {entry}")

    response = prompter.prompt_main(entry)

    # Print results
    time_taken = round(time.time() - start_time, 2)
    llm_response = re.sub("[\n\n]", "\n", response['llm_response'])
    print(f"llm_response - {i + 1} - {llm_response}")
    print(f"time_taken - {i + 1} - {time_taken}")

