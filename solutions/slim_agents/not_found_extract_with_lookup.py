
""" This example illustrates one of the most challenging RAG situations, specifically when a core text does
    not provide the answer to a question - will the combination of model and workflow code identify the
    'not found' correctly, and then provide a way to triage.

    In this example, we will use the slim-extract-tool with the following steps:

    1.  Try to obtain the "company founding date" from the first text passage.
    2.  Correctly identify that the answer is not in the text.
    3.  Programmatically identify and handle the empty [] response.
    4.  Based on the empty response condition, trigger a triage process:

        A.  Extract a lookup key from the original text, e.g., "company name"
        B.  Use the lookup key to retrieve a supplemental material from Wikipedia (in this case)
        C.  Try to extract the "company founding date" from the new materials.

    5.  Provide the correct answer to "company founding date" based on these steps.

    """

from llmware.models import ModelCatalog
from llmware.parsers import WikiParser


#   our input - financial news article - note: the 'company founding date' is not mentioned in the text
#   -- our worry is that the model will either 'make up' an answer from background knowledge (which may or may not
#      be accurate), or try to incorrectly use a date in the text, e.g, February 29, 2024.


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


def not_found_then_triage_lookup():

    print("\nNot Found Example - if info not found, then lookup in another source.\n")

    extract_key = "company founding date"
    dict_key = extract_key.replace(" ", "_")

    company_founding_date = ""

    # step 1 - run an extract function call on the text
    model = ModelCatalog().load_model("slim-extract-tool", temperature=0.0, sample=False)
    response = model.function_call(text, function="extract", params=[extract_key])
    llm_response = response["llm_response"]

    print(f"update: first text reviewed for {extract_key} - llm response: ", llm_response)

    # unpack the output
    if dict_key in llm_response:

        company_founding_date = llm_response[dict_key]

        if len(company_founding_date) > 0:

            # in this case, the value is a list with at least one element, so an 'answer' was found
            company_founding_date = company_founding_date[0]
            print(f"update: found the {extract_key} value - ", company_founding_date)
            return company_founding_date

        else:

            # step 2 - could not find the answer in the original source materials
            #   e.g., the len of the list associated with the key is zero, or []

            print(f"update: did not find the target value in the text - {company_founding_date}")
            print("update: initiating a secondary process to try to find the information")

            #   look up the company name from the original text
            response = model.function_call(text, function="extract", params=["company name"])

            if "company_name" in response["llm_response"]:
                company_name = response["llm_response"]["company_name"][0]

                if company_name:
                    print(f"\nupdate: found the company name - {company_name} - now using to lookup in secondary source")

                    # use the company name to lookup materials in Wikipedia secondary source
                    output = WikiParser().add_wiki_topic(company_name,target_results=1)

                    if output:

                        supplemental_text = output["articles"][0]["summary"]

                        if len(supplemental_text) > 150:
                            supplemental_text_pp = supplemental_text[0:150] + " ... "
                        else:
                            supplemental_text_pp = supplemental_text

                        print(f"update: using lookup - {company_name} - found secondary source article "
                              f"(extract displayed) - ", supplemental_text_pp)

                        #   finally, try to get the company founding date from the supplemental text
                        new_response = model.function_call(supplemental_text,params=["company founding date"])

                        print("\nupdate: reviewed second source article - ", new_response["llm_response"])

                        if "company_founding_date" in new_response["llm_response"]:
                            company_founding_date = new_response["llm_response"]["company_founding_date"]
                            if company_founding_date:
                                print("update: success - found the answer - ", company_founding_date)

    return company_founding_date


if __name__ == "__main__":

    founding_date = not_found_then_triage_lookup()


