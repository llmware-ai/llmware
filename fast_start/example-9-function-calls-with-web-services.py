
""" Fast Start #9 - Function Calls with Web Services

    This example illustrates one of the most exciting combinations in LLM-based applications, specifically
    combining function calls with external web services to drive more complex automation patterns.

    This Fast Start example is derived from the original example at: /examples/Use_Cases/web_services_slim_fx.py

    Models
    1.  slim-extract-tool
    2.  slim-summary-tool
    3.  bling-stablelm-3b-tool

    Web Services
    1.  Yfinance - stock ticker
    2.  Wikipedia - company background information

    The example shows how to extract keys from one source that can then be used as a lookup in a web service to
    supplement the original source materials, and provide a secondary source, which can then also be prompted and
    used to extract, analyze and summarize key information.

    NOTE: to run this example, please install yfinance library, e.g., 'pip3 install yfinance'

    """


from llmware.web_services import YFinance
from llmware.models import ModelCatalog
from llmware.parsers import WikiParser

from importlib import util
if not util.find_spec("yfinance"):
    print("\nto run this example, you need to install yfinance first, e.g., pip3 install yfinance")

# our input - financial news article

text=("BEAVERTON, Ore.--(BUSINESS WIRE)--NIKE, Inc. (NYSE:NKE) today reported fiscal 2024 financial results for its "
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


def research_example1():

    """ End-to-end example generating 30 output key:value pairs """

    # load three models in this example

    model = ModelCatalog().load_model("slim-extract-tool", temperature=0.0, sample=False)
    model2 = ModelCatalog().load_model("slim-summary-tool", sample=False,temperature=0.0,max_output=200)
    model3 = ModelCatalog().load_model("bling-stablelm-3b-tool", sample=False, temperature=0.0)

    research_summary = {}

    #   extract information from the source materials

    extract_keys = ["stock ticker", "company name",
                    "total revenues", "restructuring charges",
                    "digital growth", "ceo comment", "quarter end date"]

    print("\nStep 1 - extract information from source text\n")

    for keys in extract_keys:
        response = model.function_call(text,params=[keys])
        dict_keys = keys.replace(" ", "_")
        print(f"update: extracting - {keys} - {response['llm_response']}")
        if dict_keys in response["llm_response"]:
            value = response["llm_response"][dict_keys][0]
            research_summary.update({dict_keys: value})
        else:
            print("could not find look up key successfully - ", response["llm_response"])

    #   secondary lookups using extracted information

    print("\nStep 2 - use extracted stock ticker in web service lookup to YFinance\n")

    if "stock_ticker" in research_summary:
        ticker = research_summary["stock_ticker"]
        # a little kludge related to yfinance api
        ticker_core = ticker.split(":")[-1]

        yf = YFinance().get_stock_summary(ticker=ticker_core)
        print("yahoo finance stock info: ", yf)

        research_summary.update({"current_stock_price": yf["currentPrice"]})
        research_summary.update({"high_ltm": yf["fiftyTwoWeekHigh"]})
        research_summary.update({"low_ltm": yf["fiftyTwoWeekLow"]})
        research_summary.update({"trailing_pe": yf["trailingPE"]})
        research_summary.update({"forward_pe": yf["forwardPE"]})
        research_summary.update({"volume": yf["volume"]})

        yf2 = YFinance().get_financial_summary(ticker=ticker_core)
        print("yahoo finance fin info - ", yf2)
        research_summary.update({"market_cap": yf2["marketCap"]})
        research_summary.update({"price_to_sales": yf2["priceToSalesTrailing12Months"]})
        research_summary.update({"revenue_growth": yf2["revenueGrowth"]})
        research_summary.update({"ebitda": yf2["ebitda"]})
        research_summary.update({"gross_margin": yf2["grossMargins"]})
        research_summary.update({"currency": yf2["currency"]})

        yf3 = YFinance().get_company_summary(ticker=ticker_core)
        print("yahoo finance company info - ", yf3)
        research_summary.update({"sector": yf3["sector"]})
        research_summary.update({"website": yf3["website"]})
        research_summary.update({"industry": yf3["industry"]})
        research_summary.update({"employees": yf3["fullTimeEmployees"]})

        execs = []
        if "companyOfficers" in yf3:
            for entries in yf3["companyOfficers"]:
                if "totalPay" in entries:
                    pay = entries["totalPay"]
                else:
                    pay = "pay-NA"

                if "age" in entries:
                    age = entries["age"]
                else:
                    age = "age-NA"

                execs.append((entries["name"], entries["title"], age, pay))
        research_summary.update({"officers": execs})

    print("\nStep 3 - use extracted company name to lookup in Wikipedia web service - and add background data\n")

    if "company_name" in research_summary:

        company_name = research_summary["company_name"]
        output = WikiParser().add_wiki_topic(company_name, target_results=1)

        #   get company summary
        company_overview = ""
        for i, blocks in enumerate(output["blocks"]):
            if i < 3:
              company_overview += blocks["text"]

        # call summary model to summarize
        print("-- calling summary model to summarize the first part of the Wikipedia article")
        summary = model2.function_call(company_overview, params=["company history (5)"])
        print("-- slim-summary - summary (5 points): ", summary)

        research_summary.update({"summary": summary["llm_response"]})

        #  get founding date
        print("\n-- calling extract model to get key piece of information from the Wikipedia article - company founding date")
        response = model.function_call(company_overview, params=["founding date"])
        print("-- slim-extract - founding date: ", response)

        research_summary.update({"founding_date": response["llm_response"]["founding_date"][0]})

        print("\n-- calling extract model to get a short company business")
        response = model.function_call(company_overview, params=["company description"])
        print("-- slim-extract - response: ", response)
        research_summary.update({"company_description": response["llm_response"]["company_description"][0]})

        #     ask other questions directly
        print("\n-- asking a question directly to the Wikipedia article about the business")
        response = model3.inference("What is an overview of company's business?", add_context=company_overview)
        print("-- bling-answer model - response: ", response)
        research_summary.update({"business_overview": response["llm_response"] })

        print("\n-- asking a question about the origin of the company's name")
        response = model3.inference("What is the origin of the company's name?", add_context=company_overview)
        print("-- bling-answer model - response: ", response)
        research_summary.update({"origin_of_name": response["llm_response"]})

        print("\n-- asking a question about the company's products")
        response = model3.inference("What are the product names", add_context=company_overview)
        print("-- bling-answer model - response: ", response)
        research_summary.update({"products": response["llm_response"]})

    print("\n\nStep 4 - Completed Research - Summary Output\n")
    print("research summary: ", research_summary)

    item_counter = 1

    for keys, values in research_summary.items():
        if isinstance(values, str):

            values = values.replace("\n", "")
            values = values.replace("\r", "")
            values = values.replace("\t", "")

        print(f"\t\t -- {item_counter} - \t - {keys.ljust(25)} - {str(values).ljust(40)}")
        item_counter += 1

    return research_summary


if __name__ == "__main__":

    research_example1()






