
""" Test that GGUF models are loading correctly in local environment.  By default, will run through a series of
    different GGUF models in the ModelCatalog to spot-check that the model is correctly loading and
    successfully completing an inference:

        #   tests several different underlying models:

    #   bling-answer-tool           ->  tiny-llama (1b)
    #   bling-phi-3-gguf            ->  phi-3 (3.8b)
    #   dragon-yi-answer-tool       ->  yi (6b)
    #   dragon-llama-answer-tool    ->  llama-2 (7b)
    #   llama-2-7b-chat-gguf        ->  llama-2-chat (7b)
    #   dragon-mistral-answer-tool  ->  mistral-1 (7b)

    """


from llmware.models import ModelCatalog


def test_gguf_model_load():

    # feel free to adapt this model list

    model_list = ["bling-answer-tool",
                  "bling-phi-3-gguf",
                  "dragon-yi-answer-tool",
                  "dragon-llama-answer-tool",
                  "llama-2-7b-chat-gguf",
                  "dragon-mistral-answer-tool"]

    #   please note that the unusually short and simple prompt at times actually yields more variability in the model
    #   response - we are only testing for successful loading and inference

    sample_prompt = ("The company stock declined by $12 after poor earnings results."
                     "\nHow much did the stock price decline?")

    for model_name in model_list:

        print("\nmodel name: ", model_name)

        model = ModelCatalog().load_model(model_name, temperature=0.0, sample=False)

        response = model.inference(sample_prompt)

        print(f"{model_name} - response: ", response)

        assert response is not None

