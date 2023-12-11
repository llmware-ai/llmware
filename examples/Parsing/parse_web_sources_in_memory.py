
""" This example demonstrates how to parse various web sources into a Library
      1. Website
      2. Wikipedia
"""

import os
from llmware.library import Library
from llmware.parsers import Parser, WebSiteParser, WikiParser


def parsing_web_sources_in_memory():

    print(f"\nExample - Parsing Web Sources")

    # parse website directly
    website = "https://politico.com"
    print(f"\n > Parsing {website}")
    website_parsed_output = Parser().parse_website(website, write_to_db=False, save_history=False, get_links=False)
    block_text = website_parsed_output[0]["text"]
    print(f"\nFirst block found in website:\n{block_text}")

    # Parse wiki
    wiki_topic = "Canada"
    print(f"\n > Parsing wiki article '{wiki_topic}'")
    wiki_parsed_output = Parser().parse_wiki([wiki_topic], write_to_db=False, save_history=False, target_results=10)
    block_text = wiki_parsed_output[0]["text"]
    print(f"\nFirst block found in wiki:\n{block_text}")

    return 0


if __name__ == "__main__":

    parsing_web_sources_in_memory()
