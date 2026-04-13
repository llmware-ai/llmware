
""" Sentiment Analysis example - shows how to use the slim-sentiment-tool.  In this example, we will:

        1.  Review several summary earnings transcripts, looking to evaluate the overall sentiment as
        'positive', 'negative', or 'neutral'

        2.  Evaluate a single transcript, and apply if...then based on the result and confidence level.

        3.  Run through a list of earnings transcripts with journaling activated to display the multi-step
        process on the screen.
"""

from llmware.agents import LLMfx

earnings_transcripts = [
    "This is one of the best quarters we can remember for the industrial sector with significant growth across the "
    "board in new order volume, as well as price increases in excess of inflation.  We continue to see very strong "
    "demand, especially in Asia and Europe. Accordingly, we remain bullish on the tier 1 suppliers and would be "
    "accumulating more stock on any dips. ",

    "Not the worst results, but overall we view as negative signals on the direction of the economy, and the likely "
    "short-term trajectory for the telecom sector, and especially larger market leaders, including AT&T, Comcast, and"
    "Deutsche Telekom.",

    "This quarter was a disaster for Tesla, with falling order volume, increased costs and supply, and negative "
    "guidance for future growth forecasts in 2024 and beyond.",

    "On balance, this was an average result, with earnings in line with expectations and no big surprises to either "
    "the positive or the negative."
    ]


def get_one_sentiment_classification(text):

    """This example shows a basic use to get a sentiment classification and use the output programmatically. """

    #   simple basic use to get the sentiment on a single piece of text
    agent = LLMfx(verbose=True)
    agent.load_tool("sentiment")
    sentiment = agent.sentiment(text)

    #   look at the output
    print("sentiment: ", sentiment)
    for keys, values in sentiment.items():
        print(f"{keys}-{values}")

    #   two key attributes of the sentiment output dictionary
    sentiment_value = sentiment["llm_response"]["sentiment"]
    confidence_level = sentiment["confidence_score"]

    #   use the sentiment classification as a 'if...then' decision point in a process
    if "positive" in sentiment_value:
        print("sentiment is positive .... will take 'positive' analysis path ...", sentiment_value)

    if "positive" in sentiment_value and confidence_level > 0.8:
        print("sentiment is positive with high confidence ... ", sentiment_value, confidence_level)

    return sentiment


def review_batch_earning_transcripts():

    """ This example highlights how to review multiple earnings transcripts and iterate through a batch
    using the load_work mechanism. """

    agent = LLMfx()
    agent.load_tool("sentiment")

    #   iterating through a larger list of samples
    #   note: load_work method is a flexible input mechanism - pass a string, list, dictionary or combination, and
    #   it will 'package' as iterable units of processing work for the agent

    agent.load_work(earnings_transcripts)

    while True:
        output = agent.sentiment()
        # print("update: test - output - ", output)
        if not agent.increment_work_iteration():
            break

    response_output = agent.response_list

    agent.clear_work()
    agent.clear_state()

    return response_output


if __name__ == "__main__":

    #   first - quick illustration of getting a sentiment classification
    #   and using in an "if...then"
    sentiment = get_one_sentiment_classification(earnings_transcripts[0])

    #   second - iterate thru a batch of transcripts and apply a sentiment classification
    # response_output = review_batch_earning_transcripts()


