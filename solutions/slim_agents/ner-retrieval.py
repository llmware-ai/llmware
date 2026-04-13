
""" This example illustrates a common two-step retrieval pattern using a SLIM NER model:

        Step 1:  Extract named entity information from a text.  In this case, the name of a musician.
        Step 2:  Use the extracted name information as the basis for a retrieval.  In this case, we will use the
                 extracted named entities to do a lookup in Wikipedia. """

from llmware.agents import LLMfx
from llmware.parsers import WikiParser


def ner_lookup_retrieval():

    text = ("The new Miko Marks album is one of the best I have ever heard in a number of years.  "
            "She is definitely an artist worth exploring further.")

    #   create agent
    agent = LLMfx()
    agent.load_work(text)
    agent.load_tool("ner")
    named_entities = agent.ner()
    ner_dict= named_entities["llm_response"]

    #   take named entities found and package into a lookup list

    lookup = []
    for keys, value in ner_dict.items():
        if value:
            lookup.append(value)

    for entries in lookup:

        # run a wiki topic query with each of the named entities found

        wiki_info = WikiParser().add_wiki_topic(entries, target_results=1)

        print("update: wiki_info - ", wiki_info)
        summary = wiki_info["articles"][0]["summary"]

        print("update: summary - ", summary)

    return 0


if __name__ == "__main__":

    ner_lookup_retrieval()
