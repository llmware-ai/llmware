
""" This example demonstrates how to parse various web sources into a Library through HTML scraping.

    When parsing websites, please follow best practices, ethical guidelines and common sense - as a good example,
    see https://monashdatafluency.github.io/python-web-scraping/section-5-legal-and-ethical-considerations/

    To use the WebSite Parser requires several additional python libraries to be installed:

        pip3 install beautifulsoup4
        pip3 install lxml
        pip3 install requests
        pip3 install urllib3

"""

from llmware.parsers import Parser, WebSiteParser


def parsing_web_sources_in_memory():

    """ In this example. we will access the WebSiteParser through the general Parser class, with the main use
    case of integrating a small HTML site into a library with inclusion of other file types.

    We recommend checking the website output first in memory, before automatically adding to a DB - as
    usually the extracted text will require some post-processing to remove redundancies, potential formatting or JS -
    and as a general safety check on the content. """

    print(f"\nExample - Parsing Web Sources")

    #   parse website directly - here are a few ideas for rapid testing
    #   please be respectful in keeping requests at low volume

    #   high volume global website
    website = "https://www.cnbc.com"

    #   come visit NYC
    website = "https://www.ny.com/general/centers.html"
    # website = "https://bronxzoo.com"
    # website = "https://en.wikipedia.org/wiki/Jalen_Brunson"

    website_parsed_output = Parser().parse_website(website, write_to_db=False, save_history=False, get_links=False)

    # look at the first 10 text blocks extracted
    for x in range(0,min(10, len(website_parsed_output))):
        print("text blocks extracted: ", website_parsed_output[x])

    return 0


if __name__ == "__main__":

    parsing_web_sources_in_memory()
