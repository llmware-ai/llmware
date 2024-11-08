"""Tests the execution of a multi-step Agent process using multiple SLIM models."""

from llmware.agents import LLMfx

def test_multistep_agent_process():
    # Sample customer transcript
    customer_transcript = "My name is Michael Jones, and I am a long-time customer. The Mixco product is not working currently, and it is having a negative impact on my business, as we can not deliver our products while it is down. This is the fourth time that I have called. My account number is 93203, and my user name is mjones. Our company is based in Tampa, Florida."

    # Create an agent using LLMfx class
    agent = LLMfx()

    # Load the work
    agent.load_work(customer_transcript)

    # Load tools individually
    agent.load_tool("sentiment")
    agent.load_tool("ner")

    # Load multiple tools
    agent.load_tool_list(["emotions", "topics", "intent", "tags", "ratings", "answer"])

    # Start deploying tools and running various analytics
    # First, conduct three 'soft skills' initial assessment using 3 different models
    agent.sentiment()
    agent.emotions()
    agent.intent()

    # Alternative way to execute a tool, passing the tool name as a string
    agent.exec_function_call("ratings")

    # Call multiple tools concurrently
    agent.exec_multitool_function_call(["ner", "topics", "tags"])

    # The 'answer' tool is a quantized question-answering model - ask an 'inline' question
    # The optional 'key' assigns the output to a dictionary key for easy consolidation
    agent.answer("What is a short summary?", key="summary")

    # Prompting tool to ask a quick question as part of the analytics
    response = agent.answer("What is the customer's account number and user name?", key="customer_info")

    # You can 'unload_tool' to release it from memory
    agent.unload_tool("ner")
    agent.unload_tool("topics")

    # At the end of processing, show the report that was automatically aggregated by key
    report = agent.show_report()

    # Display a summary of the activity in the process
    activity_summary = agent.activity_summary()

    # List of the responses gathered
    for i, entries in enumerate(agent.response_list):
        print(f"Update: response analysis {i}: {entries}")
        assert entries is not None

    assert activity_summary is not None
    assert agent.journal is not None
    assert report is not None

    output = {
        "report": report,
        "activity_summary": activity_summary,
        "journal": agent.journal
    }

    return output
