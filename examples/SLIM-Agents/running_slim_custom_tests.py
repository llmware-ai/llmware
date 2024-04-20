
""" This example shows how to use a custom test script in conjunction with a slim model tool test run. """

from llmware.models import ModelCatalog

#   custom test should be a json / python list of dictionaries with minimally a 'context' key for most models.
#   some models require a "query" key
#   optional "answer" key will be used in display if provided
#   to check the existing tests, look @:  /llmware_data/model_repo/{model_name}/config.json file

custom_test = [

    {"context": "Stocks rallied Friday even after the release of stronger-than-expected U.S. jobs data and a "
                "major increase in Treasury yields.  The Dow Jones Industrial Average gained 195.12 points, or "
                "0.76%, to close at 31,419.58. The S&P 500 added 1.59% at 4,008.50. The tech-heavy Nasdaq "
                "Composite rose 1.35%, closing at 12,299.68. The U.S. economy added 438,000 jobs in August, "
                "the Labor Department said. Economists polled by Dow Jones expected 273,000 jobs. However, "
                "wages rose less than expected last month.  Stocks posted a stunning turnaround on Friday, "
                "after initially falling on the stronger-than-expected jobs report. "},

    {"context": "The Nasdaq and the S&P 500 slid by 0.8% during their lowest points in the day.  Some noted it "
                "could be the softer wage number in the jobs report that made investors confirm their bearish "
                "stance. Others noted the pullback in yields from the day’s highs.  'We’re seeing a little "
                "bit of a give back in yields from where we were around 4.8%. 'We’ve had a lot of weakness "
                "in the market in recent weeks, and potentially some oversold conditions.'"},

    {"context": "Nokia said it would cut up to 14,000 jobs as part of a cost cutting plan following third "
                "quarter earnings that plunged. The Finnish telecommunications giant said that it will reduce "
                "its cost base and increase operation efficiency to “address the challenging market environment. "
                "The substantial layoffs come after Nokia reported third-quarter net sales declined 20% year-on-year "
                "to 4.98 billion euros. Profit over the period plunged by 69% year-on-year to 133 million euros."},

    {"context": "Moody’s Investors Service lowered its ratings outlook on the United States’ government to "
                "negative from stable, pointing to rising risks to the nation’s fiscal strength."},

    {"context": "'The world's most advanced AI models are coming together with the world's most universal "
                "user interface - natural language - to create a new era of computing,' said Satya Nadella, "
                "chairman and chief executive officer of Microsoft. 'Across the Microsoft Cloud, we are the "
                "platform of choice to help customers get the most value out of their digital spend and "
                "innovate for this next generation of AI.' 'Focused execution by our sales teams and "
                "partners in this dynamic environment resulted in Microsoft Cloud revenue of $28.5 billion, "
                "up 22% (up 25% in constant currency) year-over-year,' said Amy Hood, executive vice "
                "president and chief financial officer of Microsoft."}
    ]

#   pass optional custom_test_script parameter
#   if no custom_test_script passed, then the default test set will be used automatically

ModelCatalog().tool_test_run("slim-sentiment-tool", custom_test_script=custom_test)

