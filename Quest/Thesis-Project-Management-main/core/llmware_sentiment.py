from llmware.agents import LLMfx


def analyze_application_sentiment(text):
	agent = LLMfx(verbose=True)
	agent.load_tool("sentiment")

	agent.load_work(text)

	sentiment = agent.sentiment()

	sentiment_value = sentiment["llm_response"]["sentiment"]
	confidence_level = sentiment["confidence_score"]


	return confidence_level, sentiment_value


def analyze_application_query(text, query):
	agent = LLMfx(verbose=True)
	agent.load_tool("boolean")

	agent.load_work(text)

	ans = agent.boolean(params=[f'{query}(explain)'])

	answer = ans["llm_response"]["answer"]
	explanation = ans["llm_response"]["explanation"]

	return answer, explanation