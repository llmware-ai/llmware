
""" OpenVINO embedding models - this example shows how to use OpenVINO embedding
 models which can be prepared in batch, and used in conjunction with vector databases
 or other vector semantic search retrieval applications.

    Prerequisites:
        -- pip3 install openvino

"""

from llmware.models import ModelCatalog

# industry-bert-contracts-ov
# industry-bert-insurance-ov
# all-mini-lm-l6-v2-ov
# all-mpnet-base-v2-ov

model = ModelCatalog().load_model("industry-bert-contracts-ov")

text = "We are at the airport waiting for our flight."
text2 = "The airport is boring, but OK to work from."
text3 = "I am looking forward to our trip."

embedding = model.embedding([text, text2,text3])

print("--test: embedding - ", embedding.shape, embedding)
