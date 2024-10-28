
""" Starting with llmware 0.3.7, we have integrated support for OpenVino Generative models.

    To get started:

    `pip install openvino`
    `pip install openvino_genai`

    Openvino is supported on a wide range of platforms (including Windows, Linux, Mac OS), and is highly
    optimized for Intel x86 architectures - both CPU and GPU.

    The intent is for OpenVino models to be "drop in" replacements for Pytorch or GGUF models by simply
    replacing the model with the OpenVino equivalent - usually indicated by an 'ov' at the end of the model name

    """

from llmware.models import ModelCatalog

from importlib import util
if not util.find_spec("openvino"):
    print("\nto run this example, you need to install openvino first, e.g., pip3 install openvino")

if not util.find_spec("openvino_genai"):
    print("\nto run this example, you need to install openvino_genai first, e.g., pip3 install openvino_genai")


#  as of llmware 0.3.8, we have integrated the Model Depot collection into the default llmware model catalog
#  please check out home page in Huggingface for a complete view of the collection
#  https://www.huggingface.co/llmware

#   to add your own OpenVino models, please see the example 'adding_openvino_or_onnx_model.py'


def getting_started():

    model = ModelCatalog().load_model("bling-tiny-llama-ov", temperature=0.0, sample=False,
                                      max_output=100)

    query= "What was Microsoft's revenue in the 3rd quarter?"

    context = ("Microsoft Cloud Strength Drives Third Quarter Results \nREDMOND, Wash. — April 25, 2023 — "
               "Microsoft Corp. today announced the following results for the quarter ended March 31, 2023,"
               " as compared to the corresponding period of last fiscal year:\n· Revenue was $52.9 billion"
               " and increased 7% (up 10% in constant currency)\n· Operating income was $22.4 billion "
               "and increased 10% (up 15% in constant currency)\n· Net income was $18.3 billion and "
               "increased 9% (up 14% in constant currency)\n· Diluted earnings per share was $2.45 "
               "and increased 10% (up 14% in constant currency).\n")

    response = model.inference(query ,add_context=context)

    print(f"\ngetting_started example - query - {query}")
    print("getting_started example - response: ", response)

    return response


def sentiment_analysis():

    model = ModelCatalog().load_model("slim-sentiment-ov", temperature=0.0,sample=False)

    text = ("The poor earnings results along with the worrisome guidance on the future has dampened "
            "expectations and put a lot of pressure on the share price.")

    response = model.function_call(text)

    print(f"\nsentiment_analysis - {response}")

    return response


def extract_info():

    model = ModelCatalog().load_model("slim-extract-tiny-ov", temperature=0.0, sample=False)

    text = ("Adobe shares tumbled as much as 11% in extended trading Thursday after the design software maker "
            "issued strong fiscal first-quarter results but came up slightly short on quarterly revenue guidance. "
            "Here’s how the company did, compared with estimates from analysts polled by LSEG, formerly known as Refinitiv: "
            "Earnings per share: $4.48 adjusted vs. $4.38 expected Revenue: $5.18 billion vs. $5.14 billion expected "
            "Adobe’s revenue grew 11% year over year in the quarter, which ended March 1, according to a statement. "
            "Net income decreased to $620 million, or $1.36 per share, from $1.25 billion, or $2.71 per share, "
            "in the same quarter a year ago. During the quarter, Adobe abandoned its $20 billion acquisition of "
            "design software startup Figma after U.K. regulators found competitive concerns. The company paid "
            "Figma a $1 billion termination fee.")

    response = model.function_call(text,function="extract", params=["termination fee"])

    print(f"\nextract_info - {response}")

    return response


if __name__ == "__main__":

    getting_started()
    sentiment_analysis()
    extract_info()

