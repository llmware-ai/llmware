
""" This example illustrates how to adjust sampling parameters when loading a model to analyze the impact of
    sampling on token selection from the model.
    -- note: these parameters are implemented and designed for locally deployed models, e.g., HFGenerativeModel class
             and GGUFGenerativeModel class.
    -- note: we have seen for function-calling, in particular, that turning sample=False generally yields better
            and more consistent results.
"""

from llmware.models import ModelCatalog

sample = "Services Vendor Inc. \n100 Elm Street Pleasantville, NY \nTO Alpha Inc. 5900 1st Street "\
         "Los Angeles, CA \nDescription Front End Engineering Service $5000.00 \n Back End Engineering"\
         " Service $7500.00 \n Quality Assurance Manager $10,000.00 \n Total Amount $22,500.00 \n"\
         "Make all checks payable to Services Vendor Inc. Payment is due within 30 days."\
         "If you have any questions concerning this invoice, contact Bia Hermes. "\
         "THANK YOU FOR YOUR BUSINESS!  INVOICE INVOICE # 0001 DATE 01/01/2022 FOR Alpha Project P.O. # 1000"


#   the objective of the example is to run several times, and adjust the following parameters to experiment:
#   -- sample:      True or False
#   -- temperature: range between 0.0 - 1.0  (for GGUF models, you can also try setting to negative)
#   -- using get_logits and max_output configuration variables


# load model and configure sampling parameters
model = ModelCatalog().load_model("bling-stablelm-3b-tool",
                                  sample=False,
                                  temperature=0.0,
                                  get_logits=True,
                                  max_output=123)

# run a basic summary inference
response = model.inference("What is a list of the key points?", sample)

# analyze the sampling
sampling_analysis = ModelCatalog().analyze_sampling(response)

# display the response
print("response: ", response)

# display the logits
print("logits: ", response["logits"])

# show the sampling analysis
print("sampling analysis: ", sampling_analysis)

# optional (for more detail) - look 'token-by-token' at 'not_top_tokens' selected due to sampling impact
for i, entries in enumerate(sampling_analysis["not_top_tokens"]):
    print("sampled choices: ", i, entries)


