
""" This example demonstrates how to parse various web sources into a Library
      1. Website
      2. Wikipedia
"""

import os
from llmware.library import Library
from llmware.parsers import Parser, WebSiteParser, WikiParser


# Demonstrate adding files to a library, which implicitly parses them and creates blocks
def parsing_web_sources_into_library(library_name):

    print(f"\nExample - Parsing Web Sources")

    #   *** OPTION # 1 - Add website scrape and wikipedia articles to LIBRARY ****

    # create new library
    print(f"\nstep 1 - creating library {library_name}")
    library = Library().create_new_library(library_name)

    # add website to library
    print(f"\nstep 2 - adding Website to library")
    library.add_website("https://www.politico.com")

    lib_card = library.get_library_card()
    print("update: website parsing results - ", lib_card)

    # add wikipedia set of articles to library
    print(f"\nstep 3 - adding wikipedia to library")
    wikipedia_results = library.add_wiki("Joe Biden")

    lib_card = library.get_library_card()
    print("update: wikipedia parsing results - ", lib_card)

    return 0


if __name__ == "__main__":

    lib_name = "my_web_library_1"
    parsing_web_sources_into_library(lib_name)
