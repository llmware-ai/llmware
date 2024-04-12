
""" This example demonstrates the capabilities to use SLIM output values for programmatic evaluation, specifically
    SLIM models that generate 'classification' oriented outputs.

    One of the exciting features of the SLIM models is the ability to generate natural language directly, rather than
    simply 'slotting' an answer into a predefined category - as a result, we believe that the SLIM models can
    generalize better, as the model has the ability to explicitly draw upon the objective in generating a
    response.

    As a result, if you apply SLIM models to out-of-domain content, it is possible (even likely) that you may see a
    different range of values than those outlined below

    The following SLIM models have outputs that tend to be 'classifiers' or labelled 'categories' of specific values:

    1.      sentiment   -   range of 3 values   -   positive, negative, neutral

    2.      ratings     -   range of 5 values   -   1, 2, 3, 4, 5 ('degree' of sentiment)

    3.      nli         -   range of 3 values   -   supports, contradicts, neutral

    4.      emotions    -   ~35 emotion values  -   "afraid", "anger", "angry", "annoyed", "anticipating", "anxious",
                                                    "apprehensive", "ashamed", "caring", "confident", "content",
                                                    "devastated", "disappointed", "disgusted", "embarrassed",
                                                    "excited", "faithful", "fear", "furious", "grateful", "guilty",
                                                    "hopeful", "impressed", "jealous", "joy", "joyful", "lonely",
                                                    "love", "nostalgic", "prepared", "proud", "sad", "sadness",
                                                    "sentimental", "surprise", "surprised", "terrified", "trusting"

    slim-category was trained on a diverse range of business, financial and general news documents with the goal of
    defining the category or larger topic associated with a particular text

    5.      category    -   ~27 category values -   "analyst", "announcements", "bonds", "business", "central bank",
                                                    "commentary", "commodities", "currencies", "dividend", "earnings",
                                                    "energy", "entertainment", "financials", "health",
                                                    "human resources", "legal and regulation", "macroeconomics",
                                                    "markets", "mergers and acquisitions", "opinion", "politics",
                                                    "public markets", "science", "sports", "stocks", "tech", "world"

    slim-intent was trained with wide range of materials from customer service and dialogs with a focus on trying to
    classify the intent of the customer's request

    6.      intent      -   ~14 values          -   "account", "cancel", "complaint", "customer service", "delivery",
                                                    "feedback", "invoice", "new account", "order", "payments",
                                                    "refund", "shipping", "subscription", "terminate"

    7.      topics      -   Generative Topic    -   the topics model was trained primarily on complex financial and
                                                    legal documents, but in our testing, the model generalizes very
                                                    well to almost any text - and will be 'generative' in providing
                                                    essentially a 1-2 word 'summary' of the text.

    The following models are generally 'extractive' in that the output values will have a wide spectrum of potential
    values, based on the subject text:
    
    8.  slim-extract

    9.  slim-ner

    10.  slim-tags

    11.  slim-tags-3b

    12.  slim-summary

    13.  slim-boolean

    14.  slim-xsum

    15.  sli-sql

    16.  slim-sentiment-ner

    """


from llmware.models import ModelCatalog

models = ModelCatalog().list_function_call_models()

for i, model_card in enumerate(models):

    model_name = model_card["model_name"]

    #   to view the "function call primary keys" for a selected model
    keys = ModelCatalog().fc_primary_keys(model_name)

    #   to view the expected range of output values
    values = ModelCatalog().fc_output_values(model_name)

    print("\nmodel_name: ", model_name)
    print("primary keys/parameters: ", keys)
    print("target output values: ", values)

