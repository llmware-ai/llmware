import os
from llmware.library import Library
from llmware.prompts import Prompt
from llmware.setup import Setup

openai_api_key    = os.environ.get("OPENAI_API_KEY","")

def test_fact_checking():
    # Setup library
    library = Library().create_new_library("test_fact_checking")
    library.add_wiki(["joe biden"],target_results=5)

    # create the Prompt
    #prompter = Prompt().load_model("aib-read-gpt")
    prompter = Prompt().load_model("gpt-4", api_key=openai_api_key)
    # add a new query as a source
    source = prompter.add_source_new_query(library,query="Joe Biden's years in Congress",
                                           query_type="semantic", result_count=12)

    response = prompter.prompt_with_source("when was Joe Biden first elected to the Senate?")

    assert len(response) > 0
    assert 'llm_response' in response [0]

    # run evidence fact-checks against the response
    sources_check = prompter.evidence_check_sources(response)
    numbers_check = prompter.evidence_check_numbers(response)
    token_comparison = prompter.evidence_comparison_stats(response)
    classify_not_verified = prompter.classify_not_found_response(response, parse_response=True,
                                                                 evidence_match=True, ask_the_model=True)
    library.delete_library()



