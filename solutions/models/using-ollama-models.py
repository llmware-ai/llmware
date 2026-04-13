
""" This example illustrates how to use Ollama models in llmware.  It assumes that you have separately
    downloaded and installed Ollama and used 'ollama run {model_name}' to cache several models in
    ollama. """

from llmware.models import ModelCatalog

#   Step 1 - register your Ollama models in llmware ModelCatalog
#   -- these two lines will register: llama2 and mistral models
#   -- note: assumes that you have previously cached and installed both of these models with ollama locally

#   register llama2
ModelCatalog().register_ollama_model(model_name="llama2",model_type="chat",host="localhost",port=11434)

#   register mistral - note: if you are using ollama defaults, then OK to register with ollama model name only
ModelCatalog().register_ollama_model(model_name="mistral")

#   optional - confirm that model was registered
my_new_model_card = ModelCatalog().lookup_model_card("llama2")
print("\nupdate: confirming - new ollama model card - ", my_new_model_card)

#   Step 2 - start using the Ollama model like any other model in llmware

print("\nupdate: calling ollama llama 2 model ...")

model = ModelCatalog().load_model("llama2")
response = model.inference("why is the sky blue?")

print("update: example #1 - ollama llama 2 response - ", response)

#   Tip: if you are loading 'llama2' chat model from Ollama, note that it is already included in
#   the llmware model catalog under a different name, "TheBloke/Llama-2-7B-Chat-GGUF"
#   the llmware model name maps to the original HuggingFace repository, and is a nod to "TheBloke" who has
#   led the popularization of GGUF - and is responsible for creating most of the GGUF model versions.
#   --llmware uses the "Q4_K_M" model by default, while Ollama generally prefers "Q4_0"

print("\nupdate: calling Llama-2-7B-Chat-GGUF in llmware catalog ...")

model = ModelCatalog().load_model("TheBloke/Llama-2-7B-Chat-GGUF")
response = model.inference("why is the sky blue?")

print("update: example #1 - [compare] - llmware / Llama-2-7B-Chat-GGUF response - ", response)

#   Now, let's try the Ollama Mistral model with a context passage

model2 = ModelCatalog().load_model("mistral")

context_passage= ("NASA’s rover Perseverance has gathered data confirming the existence of ancient lake "
                  "sediments deposited by water that once filled a giant basin on Mars called Jerezo Crater, "
                  "according to a study published on Friday.  The findings from ground-penetrating radar "
                  "observations conducted by the robotic rover substantiate previous orbital imagery and "
                  "other data leading scientists to theorize that portions of Mars were once covered in water "
                  "and may have harbored microbial life.  The research, led by teams from the University of "
                  "California at Los Angeles (UCLA) and the University of Oslo, was published in the "
                  "journal Science Advances. It was based on subsurface scans taken by the car-sized, six-wheeled "
                  "rover over several months of 2022 as it made its way across the Martian surface from the "
                  "crater floor onto an adjacent expanse of braided, sedimentary-like features resembling, "
                  "from orbit, the river deltas found on Earth.")

response = model2.inference("What are the top 3 points?", add_context=context_passage)

print("\nupdate: calling ollama mistral model ...")

print("update: example #2 - ollama mistral response - ", response)

#   Step 3 - using the ollama discovery API - optional

discovery = model2.discover_models()
print("\nupdate: example #3 - checking ollama model manifest list: ", discovery)

if len(discovery) > 0:
    # note: assumes tht you have at least one model registered in ollama -otherwise, may throw error
    for i, models in enumerate(discovery["models"]):
        print("ollama models: ", i, models)


# for more information and other alternatives for using GGUF models, please see the following examples:
#   -- examples/Models/chat_gguf_fast_start.py
#   -- examples/Models/using_gguf.py
#   -- examples/Models/using-open-chat-models.py
#   -- examples/Models/dragon-gguf_fast_start.py
