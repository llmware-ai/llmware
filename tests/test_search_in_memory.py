
import os

from llmware.setup import Setup
from llmware.parsers import Parser
from llmware.util import Utilities


def parse_and_search_in_memory():

    # contracts path
    contracts_path = "/path/to/agreements/folder/"

    # mix of queries - empty, single token, multi-token
    #   --if query is empty, then all results returned
    #   --case insensitive

    query_list = ["base salary", "governing law", "effective date", "target annual bonus",
                  "nyx pan", "pan",""]

    for i, contract in enumerate(os.listdir(contracts_path)):

        print(f"\n > Analyzing {contract}")

        if contract == ".DS_Store":
            print("skipping .DS_Store artifact on Mac OS")
        else:

            output = Parser().parse_one(contracts_path, contract)

            for query in query_list:

                print("Query: ", contract, query)
                results = Utilities().fast_search_dicts(query, output, remove_stop_words=True)

                for i, entry in enumerate(results):
                    print("update: in-memory query results - ", i, len(entry["text"]), entry)

    return 0


parse_and_search_in_memory()
