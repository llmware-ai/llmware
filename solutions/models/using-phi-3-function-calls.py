
""" This example shows how to use 7 different SLIM function calling models fine-tuned on top of Phi-3:

    -- Extraction       -       slim-extract-phi-3-gguf    -   generates python dictionary with 'key' and 'value'
    -- Summarization    -       slim-summary-phi-3-gguf    -   generates python list with key bullet-point summary
    -- XSUM (titles)    -       slim-xsum-phi-3-gguf       -   generates python dictionary with 'xsum' key
    -- Boolean          -       slim-boolean-phi-3-gguf    -   generate python dictionary with "answer" & "explanation" keys
    -- Sentiment-NER    -       slim-sa-ner-phi-3-gguf     -   generates python dictionary with "sentiment" and selected ner keys
    -- Question-Gen     -       slim-q-gen-phi-3-tool      -   generates python dictionary with "question" key
    -- Question-Answer  -       slim-qa-gen-phi-3-tool     -   generates python dictionary with "question" and "answer" key

    The design of these models is to simplify both the input prompt and output to enable easy integration into
    programmatic workflows.

    """

from llmware.models import ModelCatalog

#   sample text passage that will be used as the basis for the function call analysis

context_passage = ("Best Buy surpassed Wall Street’s revenue and earnings expectations for the holiday quarter on "
                 "Thursday, even as the company navigated through a period of tepid consumer electronics demand.  "
                 "But the retailer warned of another year of softer sales and said it would lay off workers and "
                 "cut other costs across the business. CEO Corie Barry offered few specifics, but said the "
                 "company has to make sure its workforce and stores match customers’ changing shopping habits. "
                 "Cuts will free up capital to invest back into the business and in newer areas, such as artificial "
                 "intelligence, she added. “This is giving us some of that space to be able to reinvest into "
                 "our future and make sure we feel like we are really well positioned for the industry to "
                 "start to rebound,” she said on a call with reporters. For this fiscal year, Best Buy anticipates "
                 "revenue will range from $41.3 billion to $42.6 billion. That would mark a drop from the most "
                 "recently ended fiscal year, when full-year revenue totaled $43.45 billion. It said comparable "
                 "sales will range from flat to a 3% decline. The retailer plans to close 10 to 15 stores "
                 "this year after shuttering 24 in the past fiscal year. One challenge that will affect sales "
                 "in the year ahead: it is a week shorter. Best Buy said the extra week in the past fiscal "
                 "year lifted revenue by about $735 million and boosted diluted earnings per share by about "
                 "30 cents. Shares of Best Buy closed more than 1% higher Thursday after briefly touching "
                 "a 52-week high of $86.11 earlier in the session. Here’s what the consumer electronics "
                 "retailer reported for its fiscal fourth quarter of 2024 compared with what Wall Street was "
                 "expecting, based on a survey of analysts by LSEG, formerly known as Refinitiv: "
                 "Earnings per share: $2.72, adjusted vs. $2.52 expected Revenue: $14.65 billion vs. $14.56 "
                 "billion expected A dip in demand, but a better-than-feared holiday Best Buy has dealt "
                 "with slower demand in part due to the strength of its sales during the pandemic. Like "
                 "home improvement companies, Best Buy saw outsized spending as shoppers were stuck at "
                 "home. Plus, many items that the retailer sells like laptops, refrigerators and home "
                 "theater systems tend to be pricier and less frequent purchases. The retailer has cited other "
                 "challenges, too: Shoppers have been choosier about making big purchases while dealing "
                 "with inflation-driven higher prices of food and more. Plus, they’ve returned to "
                 "splitting their dollars between services and goods after pandemic years of little "
                 "activity. Even so, Best Buy put up a holiday quarter that was better than feared. "
                 "In the three-month period that ended Feb. 3, the company’s net income fell by 7% to "
                 "$460 million, or $2.12 per share, from $495 million, or $2.23 per share in the year-ago "
                 "period. Revenue dropped from $14.74 billion a year earlier. Comparable sales, a metric that "
                 "includes sales online and at stores open at least 14 months, declined 4.8% during the "
                 "quarter as shoppers bought fewer appliances, mobile phones, tablets and home theater "
                 "setups than the year-ago period. Gaming, on the other hand, was a strong sales "
                 "category in the holiday quarter.")


#   for convenience to execute a 'loop', we will set up a dictionary with each function call, and the associated
#   model and parameters that are being passed to the model

phi3_function_call_models = {

    #   extract model will look for the 'key' in the params, and return the 'value' found in the text
    "extract": {"model": "slim-extract-phi-3-gguf", "params": ["net income"]},

    #   summary model will return a python list with key summary points related to the parameter
    "summary": {"model": "slim-summary-phi-3-gguf", "params": ["financial highlights"]},

    #   xsum model produces an 'extreme summarization', e.g. a headline or title
    "xsum": {"model": "slim-xsum-phi-3-gguf", "params": ["xsum"]},

    #   boolean model is designed to answer yes/no questions
    "boolean": {"model": "slim-boolean-phi-3-gguf", "params": ["Is Best Buy closing stores? (explain)"]},

    #   sentiment-ner model returns several keys for sentiment and ner attributes (e.g., people, place, organization)
    "sentiment-ner": {"model": "slim-sa-ner-phi-3-gguf", "params": ["sentiment", "people"]},

    #   q-gen model generates a question from the context passage
    "q-gen": {"model": "slim-q-gen-phi-3-tool", "params": ["question"]},

    #   qa-gen model generates question and answer from the context passage
    "qa-gen": {"model": "slim-qa-gen-phi-3-tool", "params": ["question, answer"]}
    }

for function, model in phi3_function_call_models.items():

    print(f"\nfunction: {function} - model - {model['model']} - params - {model['params']}")
    slim_model = ModelCatalog().load_model(model["model"], temperature=0.0, sample=False)

    #   note: this is the line doing all of the work - each model has been fine-tuned as a 'specialist' for
    #   its function, so the only required inputs are the source context passage, and the specific parameters to be used

    response = slim_model.function_call(context_passage, params=model["params"])

    print("response: ", response)



