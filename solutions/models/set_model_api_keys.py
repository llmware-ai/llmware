
"""This example script shows how to set the os.environ variables with API keys for supported models"""

import os


def user_managed_secrets_setup(key, value):

    user_managed_access_key_list = ["USER_MANAGED_OPENAI_API_KEY",
                                    "USER_MANAGED_COHERE_API_KEY",
                                    "USER_MANAGED_ANTHROPIC_API_KEY",
                                    "USER_MANAGED_AI21_API_KEY",
                                    "USER_MANAGED_GOOGLE_API_KEY",
                                    "USER_MANAGED_PINECONE_API_KEY",
                                    "USER_MANAGED_PINECONE_ENVIRONMENT",
                                    "USER_MANAGED_AWS_ACCESS_KEY",
                                    "USER_MANAGED_AWS_SECRET_KEY"]

    if key in user_managed_access_key_list:
        os.environ[key] = value

    # set environ variables- and will be automatically passed to corresponding model when invoked

    # os.environ["USER_MANAGED_OPENAI_API_KEY"] = "{INSERT-YOUR-OPENAI-KEY}"
    # os.environ["USER_MANAGED_COHERE_API_KEY"] = "{INSERT_YOUR-COHERE-API-KEY}"
    # os.environ["USER_MANAGED_ANTHROPIC_API_KEY"] = "{INSERT_YOUR_ANTHROPIC_API_KEY}"
    # os.environ["USER_MANAGED_AI21_API_KEY"] = "{INSERT_YOUR_AI21_API_KEY}"
    # os.environ["USER_MANAGED_GOOGLE_API_KEY"] = "{INSERT_YOUR_GOOGLE_API_KEY}"
    # os.environ["USER_MANAGED_PINECONE_API_KEY"] = "{INSERT_YOUR_PINECONE_API_KEY}"
    # os.environ["USER_MANAGED_PINECONE_ENVIRONMENT"] = "{INSERT_YOUR_PINECONE_ENVIRONMENT_KEY}"
    # os.environ["USER_MANAGED_AWS_ACCESS_KEY"] = "{INSERT_YOUR_AWS_ACCESS_KEY}"
    # os.environ["USER_MANAGED_AWS_SECRET_KEY"] = "{INSERT_YOUR_AWS_SECRET_KEY}"

    return 0

#   Example Usage
#       os.environ["USER_MANAGED_OPENAI_API_KEY"] = "..."
#       prompter = Prompt().load_model("gpt-4")
#       --> prompter will look to the environ variable and pass the API key

