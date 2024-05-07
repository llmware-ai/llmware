
""" Tests that embedding model is loaded and yielding a structurally correct embedding vector. """


from llmware.models import ModelCatalog


def test_embedding_model_local_load():

    emb_models = ModelCatalog().list_embedding_models()

    test_text = ("This is just a sample text to confirm that the embedding model is loading and correctly "
                 "converting into a structurally accurate embedding vector.")

    for model_card in emb_models:

        if model_card["model_family"] in ["HFEmbeddingModel"]:

            print(f"\nloading model - {model_card['model_name']} - embedding dims - {model_card['embedding_dims']}")

            model = ModelCatalog().load_model(model_card["model_name"])

            embedding_vector = model.embedding(test_text)

            assert embedding_vector is not None

            print(f"created vector successfully with dimensions: ", embedding_vector[0].shape)

            assert embedding_vector[0].shape[0] == model_card['embedding_dims']

    return 0


