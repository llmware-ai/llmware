
""" Example of using QNN Onnxruntime Models on Windows Arm64 

    -- NPU optimized models for Windows ARM64 with Qualcomm Snapdragon NPU

    To use, pip install the following (pinned to specific versions)
    
    --pip3 install onnxruntime-qnn==1.22.2
    --pip3 install onnxruntime-genai==0.9.0
    
    These versions are built with QNN SDK 2.36.1, and aligns to the supported QNN models in the
    Model Catalog.

    """


from llmware.models import ModelCatalog

# qnn models in llmware model catalog

qnn_model_list = ["llama-3.2-3b-onnx-qnn",
                  "phi-3.5-mini-instruct-onnx-qnn",
                  "phi-3-mini-4k-instruct-onnx-qnn",
                  "qwen2.5-1.5b-instruct-onnx-qnn",
                  "qwen2.5-7b-instruct-onnx-qnn",
                  "deepseek-r1-distill-qwen-7b-onnx-qnn",
                  "deepseek-r1-distill-qwen-14b-onnx-qnn"
                  ]

# select a model
qnn_model_name = qnn_model_list[1]

# load model
qnn_model = ModelCatalog().load_model(qnn_model_name, max_output=200)

prompt = "Write a 100 word essay on the major themes of Moby Dick."

# run stream with prompt
for token in qnn_model.stream(prompt):
    print(token, end="")



