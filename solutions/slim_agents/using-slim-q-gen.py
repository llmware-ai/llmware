
""" This example shows how to use the slim-q-gen models to automatically generate a question based on a
context passage.

    There are two 'q-gen' models - (a) tiny-llama base (1.1b), and (b) phi-3 base (3.8b)

    Both models work the same way with tiny-llama a little faster, and phi-3 a little higher quality.

    The models come packaged both as pytorch and gguf - for most inference use cases, we would recommend
    the gguf versions which are considerably faster.

    We would recommend experimenting with the temperature settings to optimize varied and
    creative question generations.

    Automated question generation has several use cases, including:

        -- quiz test question generation for education, enablement, self-training or testing
        -- search retrieval tagging to add top questions to the search index (both text and semantic)
        -- agent-oriented scenarios in which one model 'asks' the question, and another model 'answers' it

    models in catalog:

        -- "slim-q-gen-phi-3"
        -- "slim-q-gen-phi-3-tool"
        -- "slim-q-gen-tiny"
        -- "slim-q-gen-tiny-tool"

    """

from llmware.models import ModelCatalog


def hello_world_test(source_passage, q_model="slim-q-gen-tiny-tool", number_of_tries=10, question_type="question",
                     temperature=0.5):

    """ Shows a basic example of generating questions from a text passage, running a number of inferences,
    and then keeping only the unique questions generated.

        -- source_passage = text passage
        -- number_of_tries = integer number of times to call the model to generate a question
        -- question_type = "question" | "boolean" | "multiple choice"

    """

    #   recommend using temperature of 0.2 - 0.8 - for multiple choice, use lower end of the range
    q_model = ModelCatalog().load_model(q_model, sample=True, temperature=temperature)

    questions = []

    for x in range(0, number_of_tries):

        response = q_model.function_call(source_passage, params=[question_type], get_logits=False)

        # expect response in the form of:  "llm_response": {"question": ["generated question?"] }

        if response:
            if "llm_response" in response:
                if "question" in response["llm_response"]:
                    new_q = response["llm_response"]["question"]

                    #   keep only new questions
                    if new_q not in questions:
                        questions.append(new_q)

                print(f"inference {x} - response: {response['llm_response']}")

    print(f"\nDe-duped list of questions created\n")
    for i, question in enumerate(questions):

        print(f"new generated questions: {i} - {question}")

    return questions


def ask_and_answer_game(source_passage, q_model="slim-q-gen-tiny-tool", number_of_tries=10, question_type="question",
                        temperature=0.5):

    """ Shows a simple two model game of using q-gen model to generate a question, and then a second model
    to answer the question generated. """

    #   this is the model that will generate the 'question'
    q_model = ModelCatalog().load_model(q_model, sample=True, temperature=temperature)

    #   this will be the model used to 'answer' the question
    answer_model = ModelCatalog().load_model("bling-phi-3-gguf")

    questions = []

    print(f"\nGenerating a set of questions automatically from the source passage.\n")

    for x in range(0,number_of_tries):

        response = q_model.function_call(source_passage, params=[question_type], get_logits=False)

        if response:
            if "llm_response" in response:
                if "question" in response["llm_response"]:
                    new_q = response["llm_response"]["question"]

                    #   only keep new questions
                    if new_q and new_q not in questions:
                        questions.append(new_q)

        print(f"inference - {x} - response: {response}")

    print("\nAnswering the generated questions\n")
    for i, question in enumerate(questions):

        print(f"\nquestion: {i} - {question}")
        if isinstance(question, list) and len(question) > 0:
            response = answer_model.inference(question[0], add_context=test_passage)
            print(f"response: ", response["llm_response"])

    return True


if __name__ == "__main__":

    #   test passage pulled from CNBC news story on Tuesday, May 28, 2024
    test_passage = ("OpenAI said Tuesday it has established a new committee to make recommendations to the "
                    "company’s board about safety and security, weeks after dissolving a team focused on AI safety.  "
                    "In a blog post, OpenAI said the new committee would be led by CEO Sam Altman as well as "
                    "Bret Taylor, the company’s board chair, and board member Nicole Seligman.  The announcement "
                    "follows the high-profile exit this month of an OpenAI executive focused on safety, "
                    "Jan Leike. Leike resigned from OpenAI leveling criticisms that the company had "
                    "under-invested in AI safety work and that tensions with OpenAI’s leadership had "
                    "reached a breaking point.")

    #   first example
    hello_world_test(test_passage,q_model="slim-q-gen-tiny-tool",number_of_tries=10,
                     question_type="question",
                     temperature=0.5)

    #   second example
    ask_and_answer_game(test_passage,q_model="slim-q-gen-phi-3-tool", number_of_tries=10,
                        question_type="question",
                        temperature=0.5)
