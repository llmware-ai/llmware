
""" Starting with llmware 0.3.7, we have integrated support for ONNX Runtime Generative models.

    To get started:

    `pip install onnxruntime_genai`

    Please note that onnxruntime_genai is supported on a wide range of Windows, Linux and x86 platforms, but
    does not build for Mac Metal - so it will not work on Macs.

    """

from llmware.models import ModelCatalog

from importlib import util
if not util.find_spec("onnxruntime_genai"):
    print("\nto run this example, you need to install onnxruntime_genai first, e.g., pip3 install onnxruntime_genai")

# we will be adding more ONNX models to the default catalog, but we currently support:
#   -- bling-tiny-llama-onnx
#   -- bling-phi-3-onnx
#   -- phi-3-onnx

# please see the example 'adding_openvino_or_onnx_model.py' to add your own ONNX and OpenVino models


def getting_started():

    """ Simple 'hello world' example. """

    model = ModelCatalog().load_model("bling-tiny-llama-onnx", temperature=0.0, sample=False,
                                      max_output=100)

    query= "What was Microsoft's revenue in the 3rd quarter?"

    context = ("Microsoft Cloud Strength Drives Third Quarter Results \nREDMOND, Wash. — April 25, 2023 — "
               "Microsoft Corp. today announced the following results for the quarter ended March 31, 2023,"
               " as compared to the corresponding period of last fiscal year:\n· Revenue was $52.9 billion"
               " and increased 7% (up 10% in constant currency)\n· Operating income was $22.4 billion "
               "and increased 10% (up 15% in constant currency)\n· Net income was $18.3 billion and "
               "increased 9% (up 14% in constant currency)\n· Diluted earnings per share was $2.45 "
               "and increased 10% (up 14% in constant currency).\n")

    response = model.inference(query,add_context=context)

    print(f"\ngetting_started example - query - {query}")
    print("getting_started example - response: ", response)

    return response


def streaming_example():

    prompt = "What are the benefits of small specialized LLMs?"

    print(f"\nstreaming_example - prompt: {prompt}")

    #   since model.stream provides a generator, then use as follows to consume the generator
    model = ModelCatalog().load_model("phi-3-onnx", max_output=500)
    text_out = ""
    token_count = 0

    for streamed_token in model.stream(prompt):

        text_out += streamed_token
        if text_out.strip():
            print(streamed_token, end="")

        token_count += 1

    print("total text: ", text_out)
    print("total tokens: ", token_count)

    return text_out


if __name__ == "__main__":

    getting_started()

    streaming_example()



