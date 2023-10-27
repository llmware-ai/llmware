import os
import sys
from llmware.parsers import Parser
from llmware.setup import Setup
from llmware.util import Utilities

sys.path.append(os.path.join(os.path.dirname(__file__),".."))
from utils import Logger


def test_parse_and_search_in_memory():

    sample_files_path = Setup().load_sample_files()
    contracts_path = os.path.join(sample_files_path, "Agreements")
  
    # mix of queries - empty, single token, multi-token
    #   --if query is empty, then all results returned
    #   --case insensitive
    query_list = ["base salary", "governing law", "effective date", "target annual bonus", "nyx pan", "pan",""]

    for i, contract in enumerate(os.listdir(contracts_path)):
        Logger().log(f"\n  > Analyzing {contract}...")
        if contract != ".DS_Store":
            output = Parser().parse_one(contracts_path, contract)
            for query in query_list:
                Logger().log(f"\nQuery: {contract} {query}")
                results = Utilities().fast_search_dicts(query, output, remove_stop_words=True)

                Logger().log("Results:")
                for j, entry in enumerate(results):
                    Logger().log(f"{j}. {len(entry['text'])} {entry}")

test_parse_and_search_in_memory()
