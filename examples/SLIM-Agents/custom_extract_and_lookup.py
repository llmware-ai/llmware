
""" This example illustrates one of the core function-calling recipes, specifically how to extract a set of values
    from a text, using a custom key, and then programmatically use those values as the next step in a lookup
    process.  There are two different versions included in this script:

        1.  Company name extract and lookup - simple core recipe that can be copied-pasted and adapted.

        2.  Generic extract and lookup - builds on the first recipe and includes some error handling and
            parameterizing of key values.  Also intended to be a 'copy-paste-adapt' recipe, with highlight on some
            of the areas of attention in managing function call outputs programmatically. """


from llmware.models import ModelCatalog
from llmware.parsers import WikiParser

# our input - financial news article

text =("BEAVERTON, Ore.--(BUSINESS WIRE)--NIKE, Inc. (NYSE:NKE) today reported fiscal 2024 financial results for its "
      "third quarter ended February 29, 2024.) “We are making the necessary adjustments to drive NIKE’s next chapter "
      "of growth Post this Third quarter revenues were slightly up on both a reported and currency-neutral basis* "
      "at $12.4 billion NIKE Direct revenues were $5.4 billion, slightly up on a reported and currency-neutral basis "
      "NIKE Brand Digital sales decreased 3 percent on a reported basis and 4 percent on a currency-neutral basis "
      "Wholesale revenues were $6.6 billion, up 3 percent on a reported and currency-neutral basis Gross margin "
      "increased 150 basis points to 44.8 percent, including a detriment of 50 basis points due to restructuring charges "
      "Selling and administrative expense increased 7 percent to $4.2 billion, including $340 million of restructuring "
      "charges Diluted earnings per share was $0.77, including $0.21 of restructuring charges. Excluding these "
      "charges, Diluted earnings per share would have been $0.98* “We are making the necessary adjustments to "
      "drive NIKE’s next chapter of growth,” said John Donahoe, President & CEO, NIKE, Inc. “We’re encouraged by "
      "the progress we’ve seen, as we build a multiyear cycle of new innovation, sharpen our brand storytelling and "
      "work with our wholesale partners to elevate and grow the marketplace.")


def company_name_extract_and_lookup():

    """ This example shows how to perform the following core extract-and-lookup steps:

        1.  Use slim-extract-tool to extract a company name from a piece of text
        2.  Use the extracted value programmatically as the basis for a lookup using a web service
    """

    print("\nFirst Example - extract company name and then use as a lookup.\n")

    company_name = ""
    output = ""

    # step 1 - run an extract function call on the text
    model = ModelCatalog().load_model("slim-extract-tool", temperature=0.0, sample=False)
    response = model.function_call(text, function="extract", params=["company name"])
    llm_response = response["llm_response"]

    print("update: llm response: ", llm_response)

    # unpack the output
    if "company_name" in llm_response:
        company_name = llm_response["company_name"]
        if len(company_name) > 0:
            company_name = company_name[0]
        else:
            print(f"no company name found in text - {company_name}")

    print("update: extracted company name: ", company_name)

    # step 2 - use extracted value for lookup
    if company_name:
        output = WikiParser().add_wiki_topic(company_name, target_results=1)

        if output:
            if "articles" in output:
                for i, articles in enumerate(output["articles"]):
                    summary_pp = articles["summary"][0:min(150,len(articles["summary"]))]

                    print(f"update: wikipedia articles on {company_name} found: ", i, articles["title"], summary_pp)

    return company_name, output


def extract_then_lookup_generalized_example(lookup_key, secondary_key=None):

    """ This example shows the building blocks of using slim-extract function call to perform an extract on
    a text, and then programmatically use the extract lookup to perform a research step - with basic unpacking
    of the function call model response and error handling. There is an optional secondary_key, which will be used
    as an extraction key when and if the secondary material in the lookup step is found. """

    #   objective: find one or more values in a text corresponding to a specific custom key
    print(f"\nSecond Example - extract {lookup_key} and then use as a lookup.\n")

    #   this is the value that we are looking for
    target_value = ""

    #   this is the name of the llm response dictionary key derived from the lookup_key
    dict_key = lookup_key.replace(" ", "_")

    #   step 1 - load the slim-extract-tool model
    model = ModelCatalog().load_model("slim-extract-tool", temperature=0.0, sample=False)

    #   step 2 - execute a function call with the model, passing our text source and the lookup key
    response = model.function_call(text, function="extract", params=[lookup_key])
    llm_response = response["llm_response"]

    if not isinstance(llm_response, dict):
        print(f"something has gone wrong, and the model could not produce a function call output.\n"
              f"model output: {llm_response})")
        return target_value

    if dict_key in llm_response:

        #   expect that llm_response will generate a dictionary with key mapping to the params
        #   e.g., dict_key = "company_name"

        target_value = llm_response[dict_key]

        if isinstance(target_value, list):

            #   general form is that the value will be contained in a list, often times in a list with
            #   a single element consisting of the target value string

            if len(target_value) > 0:
                # take the first value in the list
                #   -- depending upon the query, you may want to keep all of these values for separate lookups
                target_value = target_value[0]
            else:
                # key exception case - the model did not find the lookup key and is returning an empty list
                print(f"Lookup key value not found in the text: {lookup_key} - {target_value}")

    else:
        # target key structure not found, we can triage in a variety of ways
        print(f"update: did not find the target key expected, but was able to extract the following: {llm_response}")

        # for simplicity, we will take the first output value, regardless of the key name

        for keys, values in llm_response.items():
            print(f"llm response: {keys} - {values}")
            target_value = values

        if target_value:
            if len(target_value) > 0:
                target_value = target_value[0]

    if not target_value:
        print("update: unfortunately, could not succeed in finding a target value for lookup")
        return target_value

    # second step - use the target value for lookup
    #   -- feel free to replace with a library query or another form of information retrieval

    print(f"update: looked up key - {lookup_key} - and found target value - {target_value} - now using as lookup")

    research_output = WikiParser().add_wiki_topic(target_value, target_results=1)
    supplemental_text = research_output["articles"][0]["summary"]
    if len(supplemental_text) > 250:
        supplemental_text_pp = supplemental_text[0:250] + " ... "
    else:
        supplemental_text_pp = supplemental_text

    print(f"update: completed research using {lookup_key} - {target_value} - {supplemental_text_pp}")

    output_dict = {"lookup": lookup_key, "target_value": target_value, "research_output": research_output}

    if secondary_key and supplemental_text:
        # add a secondary extraction
        follow_up_response = model.function_call(supplemental_text, params=[secondary_key])
        print(f"update: follow-up - {target_value} - {secondary_key} - ", follow_up_response["llm_response"])

    return output_dict


if __name__ == "__main__":

    # first example
    company_name_extract_and_lookup()

    # second example - a couple of fun prompts to try:
    # e.g., #1 - "city" and "population"
    # e.g., #2 - "ceo" & "birth date"
    output_dict= extract_then_lookup_generalized_example("ceo", secondary_key="birth date")

