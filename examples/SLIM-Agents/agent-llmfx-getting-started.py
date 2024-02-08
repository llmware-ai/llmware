
""" Using SLIM tools as part of an agent workflow - introducing LLMfx class - this example shows how to:

    1.  Create an agent using the LLMfx class.
    2.  Load multiple specialized tools for the agent.
    3.  Execute a series of function-calls.
    4.  Generate a consolidated automatic dictionary report.

"""


from llmware.models import ModelCatalog
from llmware.agents import LLMfx


def create_multistep_report(customer_transcript):

    """ Creating a multi-step, multi-model agent workflow """

    #   create an agent using LLMfx class
    agent = LLMfx()

    agent.load_work(customer_transcript)

    #   load tools individually
    agent.load_tool("sentiment")
    agent.load_tool("ner")

    #   load multiple tools
    agent.load_tool_list(["emotions", "topics", "intent", "tags", "ratings", "answer"])

    #   start deploying tools and running various analytics

    #   first conduct three 'soft skills' initial assessment using 3 different models
    agent.sentiment()
    agent.emotions()
    agent.intent()

    #   alternative way to execute a tool, passing the tool name as a string
    agent.exec_function_call("ratings")

    #   call multiple tools concurrently
    agent.exec_multitool_function_call(["ner","topics","tags"])

    #   the 'answer' tool is a quantized question-answering model - ask an 'inline' question
    #   the optional 'key' assigns the output to a dictionary key for easy consolidation
    agent.answer("What is a short summary?",key="summary")

    #   prompting tool to ask a quick question as part of the analytics
    response = agent.answer("What is the customer's account number and user name?", key="customer_info")

    #   you can 'unload_tool' to release it from memory
    agent.unload_tool("ner")
    agent.unload_tool("topics")

    #   at end of processing, show the report that was automatically aggregated by key
    report = agent.show_report()

    #   displays a summary of the activity in the process
    activity_summary = agent.activity_summary()

    #   list of the responses gathered
    for i, entries in enumerate(agent.response_list):
        print("update: response analysis: ", i, entries)

    output = {"report": report, "activity_summary": activity_summary, "journal": agent.journal}

    return output


if __name__ == "__main__":

    # sample customer transcript

    customer_transcript = "My name is Michael Jones, and I am a long-time customer.  " \
                          "The Mixco product is not working currently, and it is having a negative impact " \
                          "on my business, as we can not deliver our products while it is down. " \
                          "This is the fourth time that I have called.  My account number is 93203, and " \
                          "my user name is mjones. Our company is based in Tampa, Florida."

    output = create_multistep_report(customer_transcript)

