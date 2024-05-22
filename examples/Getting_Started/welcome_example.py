
""" This 'welcome_example' can serve as a quick 'hello world' test to verify that LLMWare has been installed
and that local model inference serving over GGUF is available and working as expected.   This example will
pull down two models and run a quick 'Welcome' for a new user.  """


from llmware.models import ModelCatalog
from llmware.configs import LLMWareConfig

#   optional - adds a dash of color to the console output
try:
    from colorama import Fore
    BLUE = Fore.BLUE
    RESET = Fore.RESET
except:
    BLUE = ""
    RESET = ""

print(f"\n{BLUE}Welcome to LLMWare - Test Script{RESET}")

#   run first inference
print(f"\nLoading {BLUE}bling-phi-3-gguf model{RESET} for First Inference: may take a minute to download the first time")
print(f"Model will be cached at the local path: {BLUE}{LLMWareConfig().get_model_repo_path()}{RESET}")

try:

    #   loads the model from the model catalog
    model = ModelCatalog().load_model("bling-phi-3-gguf", temperature=0.0, sample=False)

    prompt = ("When this script is loaded, we should greet the person by saying, 'Welcome to LLMWare.'"
            "\nThis script has been loaded - what should we say?")

    print(f"\nprompt: {prompt}")

    #   executes inference
    response = model.inference(prompt)

    print("\nmodel response: ", response)

except:
    print("\nWe are sorry but something has gone wrong with the installation and/or download of the file, and it "
          "did not start correctly.   Please check the documentation.\nMost common sources of this error: "
          "\n1.  Supported platforms - Mac M1/M2/M3, Linux x86, Windows"
          "\n2.  Model did not download correctly.  Try again and confirm that model instantiated in local folder path."
          "\n3.  Update/pull from the latest repo and/or the latest pip install version.")


#   run second inference
print(f"\nLoading {BLUE}slim-sentiment-tool{RESET}")

try:

    #   load the model from the model catalog
    model = ModelCatalog().load_model("slim-sentiment-tool", temperature=0.0, sample=False)

    user = "We are very happy and excited to get started with LLMWare."
    print(f"\nuser: {user}")

    #   execute a 'sentiment' function call on the model
    response = model.function_call(user, function="classify", params=["sentiment"],get_logits=False)

    print("\nclassifying the sentiment: ", response)

except:
    print("We are sorry but something has gone wrong with the installation and/or download of the file, and it "
          "did not start correctly.   Please check the documentation.\nMost common sources of this error: "
          "\n1.  Supported platforms - Mac M1/M2/M3, Linux x86, Windows"
          "\n2.  Model did not download correctly.  Try again and confirm that model instantiated in local folder path."
          "\n3.  Update/pull from the latest repo and/or the latest pip install version.")


print(f"\n\nPlease review /examples for other examples.\n\n{BLUE}Welcome to the LLMWare community.{RESET}")
