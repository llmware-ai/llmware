
""" Test that 'SLIM' tool GGUF models are loading correctly in local environment.  By default, will run
    through a series of automated tests packaged with each model.  Feel free to select among shorter list
    of models - generally, if one model is working than likely the rest will work as well.  """


from llmware.models import ModelCatalog


def slim_tests():

    """ Each of these one line commands will locally cache the model and then run a series of tests using
    the model to demonstrate its use and confirm that installation locally was successfully. """

    #   running automated tests - see the tools in action

    tools= ["slim-extract-tool", "slim-xsum-tool", "slim-summary-tool", "slim-boolean-tool",
            "slim-sentiment-tool" , "slim-topics-tool", "slim-ner-tool", "slim-ratings-tool",
            "slim-emotions-tool",  "slim-intent-tool", "slim-tags-tool", "slim-sql-tool",
            "slim-category-tool", "slim-nli-tool", "slim-sa-ner-tool", "slim-tags-3b-tool"]

    small_tool_list = ["slim-extract-tool", "slim-topics-tool"]

    # run tests for one tool
    ModelCatalog().tool_test_run("slim-sentiment-tool")

    # run tests for a bunch of tools - try the 'small_tool_list' as alternative
    for tool in tools:
        # excluding sentiment, since ran above as separate test
        if tool != "slim-sentiment-tool":
            ModelCatalog().tool_test_run(tool)

    return 0


