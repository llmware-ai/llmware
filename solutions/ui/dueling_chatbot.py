
""" This example shows how to build a unique 'Dueling Q&A ChatBot' in which a question-generating model 'chats'
with a question-answering model using a selected context passage from the user.

    The user provides input of selecting the context passage, and then typing "Go" on the prompt bar, and the
'dueling' bots take it from there ...

    Please note that two models will be downloaded and cached locally on first use - so please expect 1-2 minutes
for the first run, and then much faster loads on subsequent tries.

    This example uses Streamlit for the UI.  If you are new to using Steamlit, to run this example:

    1.  `pip3 install streamlit`

    2.  to run, go to the command line:  streamlit run "path/to/dueling_chatbot.py"

"""

import streamlit as st
from llmware.models import ModelCatalog
from llmware.gguf_configs import GGUFConfigs

GGUFConfigs().set_config("max_output_tokens", 500)

if "question_history" not in st.session_state:
    st.session_state["question_history"] = []


#   test passage pulled from CNBC news story on Tuesday, May 28, 2024
test_passage = ("OpenAI said Tuesday it has established a new committee to make recommendations to the "
                "company’s board about safety and security, weeks after dissolving a team focused on AI safety.  "
                "In a blog post, OpenAI said the new committee would be led by CEO Sam Altman as well as "
                "Bret Taylor, the company’s board chair, and board member Nicole Seligman.  The announcement "
                "follows the high-profile exit this month of an OpenAI executive focused on safety, "
                "Jan Leike. Leike resigned from OpenAI leveling criticisms that the company had "
                "under-invested in AI safety work and that tensions with OpenAI’s leadership had "
                "reached a breaking point.")


@st.cache_resource
def load_question_model(temperature=0.5):
    """ Loads the Question Generating Model. """
    question_model = ModelCatalog().load_model("slim-q-gen-tiny-tool",
                                               temperature=temperature,
                                               sample=True)
    return question_model


@st.cache_resource
def load_answer_model():
    """ Loads the Answering Model. """
    answer_model = ModelCatalog().load_model("bling-phi-3-gguf",temperature=0.0, sample=False)
    return answer_model


def get_new_question(q_model, question_type, test_passage):

    new_q = ""
    max_tries = 10
    tries = 0

    while not new_q or new_q in st.session_state["question_history"]:

        response = q_model.function_call(test_passage, params=[question_type], get_logits=False)
        if response:
            if "llm_response" in response:
                if "question" in response["llm_response"]:
                    new_q = response["llm_response"]["question"]
                    if isinstance(new_q, list) and len(new_q) > 0:
                        new_q = new_q[0]
                        if new_q not in st.session_state["question_history"]:
                            st.session_state["question_history"].append(new_q)
                            break

        tries += 1
        if tries >= max_tries:
            break

    return new_q


def get_new_answer(question, ans_model, test_passage):

    response = ans_model.inference(question, add_context=test_passage)
    answer = response["llm_response"]

    return answer


def get_input_passage(sample_passage_name, custom_passage_text):

    if sample_passage_name != "None":

        if sample_passage_name == "OpenAI":

            return ("OpenAI said Tuesday it has established a new committee to make recommendations to the "
                "company’s board about safety and security, weeks after dissolving a team focused on AI safety.  "
                "In a blog post, OpenAI said the new committee would be led by CEO Sam Altman as well as "
                "Bret Taylor, the company’s board chair, and board member Nicole Seligman.  The announcement "
                "follows the high-profile exit this month of an OpenAI executive focused on safety, "
                "Jan Leike. Leike resigned from OpenAI leveling criticisms that the company had "
                "under-invested in AI safety work and that tensions with OpenAI’s leadership had "
                "reached a breaking point.  The name of the new committee is the AI Safety Committee.")

        elif sample_passage_name == "Apple":

            return ("Apple shares popped 5% to a new record high of around $203 per share on Tuesday, a day "
                    "after the company announced its long-awaited push into artificial intelligence at its annual "
                    "developer conference on Monday.  Apple introduced a range of new AI features during the event, "
                    "including an overhaul of its voice assistant Siri, integration with OpenAI’s ChatGPT, "
                    "a range of writing assistance tools and new customizable emojis. The company pitched the "
                    "features as AI for the average person, though users will likely need to upgrade their "
                    "iPhones to access the tools.  With Tuesday’s share move, Apple bested its previous record "
                    "from Dec. 14. The company’s developer conference came as a welcome sign for investors who "
                    "have been watching to see how Apple will capitalize on the ongoing AI boom. Analysts from "
                    "Morgan Stanley said Apple’s AI features strongly position the company with “the most "
                    "differentiated consumer digital agent.” Additionally, the analysts believe that the "
                    "features will drive consumers to upgrade their iPhones, which should “accelerate "
                    "device replacement cycles.” They said Apple will still have to deliver when the AI "
                    "features are first available in the fall, but they think the “building blocks are in "
                    "place for a return to growth and more sustained outperformance.")

        elif sample_passage_name == "Los Angeles Lakers":

            return ("The Lakers have finished better than seventh in the Western Conference standings just once "
                    "in the past 12 seasons (when they won the title in 2019-20). Their franchise player, "
                    "LeBron James, turns 40 in December. They have no salary-cap space unless James were "
                    "to leave in free agency (he has until June 29 to make a decision on his $51.4 million "
                    "player option). They have limited trade assets.  They play in a super-competitive conference "
                    "where the teams behind them are upwardly mobile and aggressive and most of the teams in "
                    "front of them are going to continue to be good -- or get even better -- in the "
                    "immediate future. And they have a massive and highly demanding fanbase and are "
                    "under a constant microscope by the national media because they drive massive "
                    "audience engagement across the world.  Vogel won a title in 2020. Darvin Ham reached the "
                    "Western Conference finals in 2023. Neither lasted longer than three seasons. No "
                    "Lakers coach has since Phil Jackson has lasted more than three seasons. These are some of "
                    "the factors Hurley undoubtedly was weighing before making his choice over the weekend. "
                    "It's hard to even quantify what would be considered a successful season for the Lakers "
                    "in 2024-25 without knowing what changes are made to the roster. Avoiding the play-in tournament, "
                    "frankly, would be a reasonable if challenging goal.")

        elif sample_passage_name == "Buy Home":

            return ("The price for owning a home is rising rapidly and not just the mortgage payments. "
        "US homeowners are now paying an average of $18,118 a year on property taxes, homeowners’ "
        "insurance, maintenance, energy and various other expenses linked to owning a home, "
        "according to a new Bankrate study.  That’s nearly the cost to buy a used car and represents "
        "a 26% increase from four years ago when it cost $14,428 annually to own and maintain a home. "
        "All of these variable expenses are on top of the fixed cost of a mortgage, including "
        "property taxes, homeowners insurance, energy costs, internet, cable bills and "
        "home maintenance. The findings are another reminder of how much more expensive life "
        "has become since Covid-19. Many Americans would like to buy a home but have been unable to "
        "because home prices have spiked to record highs and mortgage rates remain elevated. "
        "The housing market is historically unaffordable. But even the ones fortunate enough to "
        "have bought a home over the past few years are grappling with sticker shock over the cost "
        "of maintaining it. The per-month cost of owning and maintaining a home has gone from "
        "$1,202 a month in 2020 to $1,510 now, Bankrate found.")

        elif sample_passage_name == "Vacation":

            return ("Temperatures are rising. Hotel prices are exploding. And travelers are already behaving badly. "
                    "Welcome to another summer in Europe.  From the headlines, things already look chaotic. "
                    "Famous sites are raising their entry fees. Hotel rooms are like gold dust. And the "
                    "dollar has slipped against both the pound and the euro.  Oh, and there’s the small matter "
                    "of crowds. “There’s been a substantial increase on last year’s demand,” says Tom "
                    "Jenkins, CEO of the European Tourism Organisation, speaking about US travelers to "
                    "Europe. “2023 saw higher numbers than 2019, and this year we’re comfortably seeing more – "
                    "record volumes of Americans coming to Europe.” Kayla Zeigler agrees. As the owner of "
                    "Destination Europe, she is sending “record numbers” of clients to the continent this year.  "
                    "Graham Carter, director of Unforgettable Travel, a tour operator with a 90% US "
                    "client base, says that many guests are finding the idea of Europe prohibitively "
                    "expensive this year. People are wondering, is Europe worth it?” he says. “It’s "
                    "booking up in advance and prices are quite high. There’s been such a huge demand "
                    "for travel in the past three years, and lots of places are pushing up prices.”  "
                    "Is summer in Europe already a washout? According to the experts, that all depends "
                    "on what kind of sacrifices you’re prepared to make. A weak dollar First things first: "
                    "travelers from the US are already at a disadvantage due to a weak dollar. Against "
                    "the euro, $1 was worth around 91 or 92 euro cents as of June 5, at mid-market rates. "
                    "Sure, that’s better than the December 2020-January 2021 five-year low when the "
                    "dollar was hovering around 82 cents. But it’s also down from a year earlier, "
                    "when a dollar was worth about 95 euro cents – and it’s way down from last "
                    "September’s five-year high when it peaked at 1.04 euros, according to currency "
                    "conversion specialists Wise.  For those traveling to the UK it’s a similar state of "
                    "affairs. This time last year, $1 netted travelers 80 pence. As of Wednesday, it was "
                    "78p – a fall from the September peak of nearly 83p. The dollar is also down, year on year, "
                    "against 11 more European currencies. From Bosnia to Bulgaria, Denmark to Iceland, "
                    "Poland to Romania and Sweden to Switzerland, travelers changing dollars will be worse off. "
                    "While a few cents to the dollar doesn’t sound much on a single transaction, the small "
                    "drops can make a difference on credit card bills on the return home. A 500 euro hotel "
                    "room equates to $543 at Friday’s mid-market exchange rate, where it would have been "
                    "$480 in September.")

        elif sample_passage_name == "Taylor Swift":

            return ("Taylor Swift stopped her concert in Edinburgh, Scotland, on Friday to help a fan. Swift was "
                    "in the middle of singing her “Midnights” song “Would’ve Could’ve Should’ve” when she noticed "
                    "a fan who was in distress. In a video that went viral on social media, the singer-songwriter "
                    "is seen requesting assistance for the fan. “We need help right in front of me, please, "
                    "right in front of me,” Swift sang while playing her guitar and keeping her eyes locked on "
                    "the fan. “Just gonna keep playing until we notice where it is. Swift continued strumming "
                    "her guitar while motioning over to the person in need of help.")

        else:
            return custom_passage_text
    else:
        return custom_passage_text


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


def ask_and_answer_dueling_bots_ui_app (input_passage):

    question_model = "slim-q-gen-phi-3-tool"
    answer_model = "bling-stablelm-3b-tool"

    st.title(f"Ask and Answer Dueling Bots")
    st.write(f"Asking the questions: {question_model}")
    st.write(f"Answering the questions: {answer_model}")

    question_model = load_question_model()
    answer_model = load_answer_model()

    with st.sidebar:

        st.write("Today's Subject")
        sample_passage = st.selectbox("sample_passage", ["OpenAI", "Apple", "Los Angeles Lakers", "Buy Home",
                                                         "Taylor Swift", "Vacation", "None"], index=0)
        # custom_passage = st.text_area(label="Subject",value=input_passage,height=100)
        custom_passage = test_passage

        input_passage = get_input_passage(sample_passage,custom_passage)

        mode = st.selectbox("mode", ["question", "boolean", "multiple choice"],index=0)

        number_of_tries = st.selectbox("tries", [5,10,20],index=0)

        st.write(input_passage)

    # initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # accept user input
    prompt = st.chat_input("Say 'Go' and the Bots will Start")
    if prompt:

        for x in range(0, number_of_tries):

            with st.chat_message("user"):

                new_question = get_new_question(question_model,mode, input_passage)
                st.markdown(new_question)

            with st.chat_message("assistant"):

                new_answer = get_new_answer(new_question,answer_model, input_passage)
                st.markdown(new_answer)

            st.session_state.messages.append({"role": "user", "content": new_question})
            st.session_state.messages.append({"role": "assistant", "content": new_answer})

    return 0


if __name__ == "__main__":

    ask_and_answer_dueling_bots_ui_app(test_passage)




