"""
    This example shows how to use a remote OpenAI-compatible Chat Completions endpoint with
    llmware's OpenChatModel path (register_open_chat_model + api_base).

    DaoXE is a multi-model, multi-protocol API gateway. Besides OpenAI-compatible Chat
    Completions / Responses, it also exposes Anthropic Messages (Claude protocol) and other
    catalog endpoints. This example focuses on the OpenAI-compatible surface that llmware
    already supports via OpenChatModel.

    Setup:
        1. Create an API key at https://daoxe.com (availability can vary by account / region;
           DaoXE does not serve users in mainland China).
        2. Export:

            export DAOXE_API_KEY="your_api_key"
            export DAOXE_MODEL="model_id_from_your_catalog"   # use an ID from your live catalog

        Optional override for the base URL (default is https://daoxe.com/v1):

            export DAOXE_BASE_URL="https://daoxe.com/v1"

    Notes:
        - register_open_chat_model uses model_name both as the llmware catalog key and as the
          `model` field sent to the remote API, so set DAOXE_MODEL to a real catalog model ID.
        - OpenChatModel reads the API key from load_model(..., api_key=...) or
          USER_MANAGED_OPEN_CHAT_API_KEY; we pass DAOXE_API_KEY explicitly below.
        - Do not hard-code model IDs: DaoXE model availability depends on the live catalog
          and the caller's account.
"""

import os
import sys

from llmware.models import ModelCatalog
from llmware.prompts import Prompt


def main():
    api_key = os.environ.get("DAOXE_API_KEY")
    model_id = os.environ.get("DAOXE_MODEL")
    api_base = os.environ.get("DAOXE_BASE_URL", "https://daoxe.com/v1")

    if not api_key or not model_id:
        print(
            "Set DAOXE_API_KEY and DAOXE_MODEL before running this example.\n"
            "  export DAOXE_API_KEY='your_api_key'\n"
            "  export DAOXE_MODEL='model_id_from_your_catalog'\n"
            "Optional:\n"
            "  export DAOXE_BASE_URL='https://daoxe.com/v1'"
        )
        sys.exit(1)

    # Register the remote OpenAI-compatible endpoint in the Model Catalog.
    # prompt_wrapper="" keeps the chat messages path without extra local instruct wrappers
    # (remote chat models typically expect normal role/content messages).
    ModelCatalog().register_open_chat_model(
        model_name=model_id,
        api_base=api_base,
        prompt_wrapper="",
        model_type="chat",
        display_name=f"daoxe:{model_id}",
    )

    # Confirm registration
    card = ModelCatalog().lookup_model_card(model_id)
    print("update: registered open-chat model card -", card)

    # Load with the remote API key (OpenChatModel also accepts USER_MANAGED_OPEN_CHAT_API_KEY)
    prompter = Prompt().load_model(model_id, api_key=api_key)
    response = prompter.prompt_main("In one short sentence, what is retrieval-augmented generation?")

    print("update: daoxe remote response -", response)

    # Direct ModelCatalog path (same registration)
    model = ModelCatalog().load_model(model_id, api_key=api_key)
    direct = model.inference("Reply with a single word: ready")
    print("update: daoxe direct inference -", direct)

    return 0


if __name__ == "__main__":
    main()
