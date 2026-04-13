
# Developer Guide for Building AI Applications with LLMWare and OpenVINO™

## Table of Contents

* [Introduction](#introduction)
* [Prerequisites and Installation](#prerequisites-and-installation)
  * [Setup and Install LLMWare and OpenVINO](#setup-and-install-llmware-and-openvino)
* [Model Catalog Integration](#model-catalog-integration)
  * [Loading OpenVINO Models](#loading-openvino-models)
  * [Performance Benefits](#performance-benefits)
  * [Available Model Families](#available-model-families)
* [Quick Start Examples](#quick-start-examples)
* [OpenVINO Model Configuration and Optimizations](#openvino-model-configuration-and-optimizations)
  * [Temperature and Sampling](#temperature-and-sampling)
  * [Device Placement and Performance Tuning](#device-placement-and-performance-tuning)
  * [OpenVINO Model Loading Phases](#openvino-model-loading-phases)

## Introduction

This guide provides a concise walkthrough for developers on using [LLMWare](https://llmware-ai.github.io/llmware/getting_started) with [OpenVINO](https://docs.openvino.ai/2025/index.html) to build high-performance AI applications. LLMWare's integration with OpenVINO is designed to be seamless and straightforward. The core principle is that OpenVINO models are treated as **"drop-in" replacements** for any other model type in `llmware`. This is achieved by loading all models through the standard `ModelCatalog` interface. To use an OpenVINO-optimized model, you simply need to select a model with the `-ov` suffix from the [Model Catalog](https://huggingface.co/llmware/models?search=-ov).

```python
from llmware.models import ModelCatalog

# Load any OpenVINO(OV) model by name ending with "-ov"
ov_model = ModelCatalog().load_model("bling-tiny-llama-ov")
```

## Prerequisites and Installation

For detailed system requirements, please see the [Platform Support Guide.](https://llmware-ai.github.io/llmware/getting_started/platforms)

> [!NOTE]  
> For optimal performance, the respective Intel GPU or NPU drivers must be updated.
> Driver installation: [GPU](https://docs.openvino.ai/2025/get-started/install-openvino/configurations/configurations-intel-gpu.html) | [NPU](https://docs.openvino.ai/2025/get-started/install-openvino/configurations/configurations-intel-npu.html)

#### Setup and Install LLMWare and OpenVINO:
```bash
# (Windows) Set Up Python Virtual Environment and Activate 
python -m venv llmware-ov-env
llmware-ov-env\Scripts\activate

# (Linux) Set Up Python Virtual Environment and Activate 
python3 -m venv llmware-ov-env
source llmware-ov-env/bin/activate

# Install llmware and openvino_genai
pip install llmware openvino_genai
```

## Model Catalog Integration

LLMWare integrated over **100+ OpenVINO and ONNX models** from the [Model Depot](https://medium.com/@darrenoberst/model-depot-9e6625c5fc55) collection into the default model catalog. This extensive collection provides ready-to-use, pre-optimized models for various AI applications. Explore the complete OpenVINO model collection in the [llmware repository on Hugging Face (`-ov` suffix).](https://huggingface.co/llmware/models?search=-ov)

Because OpenVINO models are loaded through the standard catalog, they are **fully compatible with all other `llmware` features**, including advanced RAG pipelines, agentic workflows, and function-calling with SLIM models.

### Loading OpenVINO Models
LLMWare introduced the `OVGenerativeModel` class to support models packaged in OpenVINO format. This class provides optimized inference performance particularly beneficial for Intel CPU, GPU and NPU architectures. OpenVINO models are loaded through the standard `ModelCatalog` interface, with model names ending in `-ov` to indicate the OpenVINO format.
- [OpenVINO model collection (`-ov` suffix).](https://huggingface.co/llmware/models?search=-ov)
- [OpenVINO NPU friendly model collection (`npu-ov` suffix).](https://huggingface.co/llmware/models?search=npu-ov)

```python
from llmware.models import ModelCatalog

# Get all models whose names end with "-ov"
ov_models = [m["model_name"]
             for m in ModelCatalog().list_all_models()
             if "-ov" in m["model_name"]]

print(f"Available OpenVINO models: {ov_models}") # For the latest list see Hugging Face LLMWare OpenVINO model collection (`-ov` suffix)
```
> [!IMPORTANT]  
> The models listed via `ModelCatalog().list_all_models()` use  [llmware/model_configs.py](https://github.com/llmware-ai/llmware/blob/main/llmware/model_configs.py) and might not contain all the models. For the latest models availability, see [Hugging Face LLMWare OpenVINO model collection (`-ov` suffix)](https://huggingface.co/llmware/models?search=-ov).

### Performance Benefits
OpenVINO provides several performance optimizations for LLMWare models:

- **Model Compilation:** Optimized execution graphs for target hardware automatically.
- **Quantization:** Reduced precision for faster inference.
- **Hardware Acceleration:** OpenVINO is highly optimized for Intel x86 architectures, providing significant performance improvements on CPU, GPU and NPU configurations.

### Available Model Families

All models are prepackaged in inference-ready x86-optimized formats, such as OpenVINO and ONNX, quantized with int4, and include smart quantization ratios to mitigate quality impacts (e.g., retaining some parameters at 8-bit).

* **Leading Generative Models**: leading generative decoder models from 1B — 14B+ parameters in the following leading open source series: Llama 3.2/3.1/3.0/2, Qwen 2.5/2, Mistral 0.3/0.2/0.1, Phi-3, Gemma-2, Yi 1.5/1.0, StableLM, Tiny Llama and popular and leading fine-tunes including Zephyr, Dolphin, Bling, OpenHermes, Wizard, OpenOrca, Nemo, and Dragon;

* **Specialized Models**: specialized fine-tuned models in math and programming including: Mathstral, Qwen Code-7B, and CodeGemma;

* **Multimodal Models**: Qwen2-VL-7B, Qwen2-VL-2B, Llama 3.2 11B vision designed for edge deployment of vision+text -> text models;

* **BLING Models**: Small CPU-optimized models (1B-3B parameters);

* **DRAGON Models**: Larger RAG-optimized models;

* **Function-Calling Models**: specialized function-calling SLIM models for multi-model, multi-step agent-based workflows; and

* **Encoders**: embedding models, rerankers, and classifiers.

* **Custom Model Integration**: To add your own OpenVINO models to LLMWare, see [examples/Models/adding_openvino_or_onnx_model.py](https://github.com/llmware-ai/llmware/blob/main/examples/Models/adding_openvino_or_onnx_model.py)

> [!NOTE]  
> The models are all in open source, licensed on permissive terms consistent with the terms of the underlying models, and made available as a resource to the wider community to use in their own deployments.

## Quick Start Examples

Explore a wide range of [examples in the llmware repository](https://llmware-ai.github.io/llmware/examples). Because OpenVINO models are loaded through the standard catalog, they are **fully compatible with all other `llmware` features**, including advanced RAG pipelines, agentic workflows, and function-calling with SLIM models.

-   **Core OpenVINO Examples**: See [examples/Models/using_openvino_models.py](https://github.com/llmware-ai/llmware/blob/main/examples/Models/using_openvino_models.py)
    ```python
    from llmware.models import ModelCatalog

    # ---------------------------
    # Basic Inference Example
    # ---------------------------
    # Load an OpenVINO-optimized model
    model = ModelCatalog().load_model("bling-tiny-llama-ov")

    # Perform inference
    response = model.inference("What are the key benefits of using OpenVINO?")
    print(f"Response: {response}")

    # ---------------------------
    # Sentiment Analysis Example
    # ---------------------------
    # Load the OpenVINO optimized sentiment analysis model
    sentiment_model = ModelCatalog().load_model("slim-sentiment-ov")

    # Analyze sentiment
    result = sentiment_model.function_call("I love using LLMWare with OpenVINO! The performance is amazing.")
    print(f"Sentiment Analysis Result: {result}")

    # ---------------------------
    # Information Extraction Example
    # ---------------------------
    # Load the OpenVINO optimized information extraction model
    extraction_model = ModelCatalog().load_model("slim-extract-ov")

    # Extract key information
    text = "The invoice total is $1,234.56 and the due date is 2024-12-31."
    extracted_info = extraction_model.function_call(text, function="extract", params=["invoice total", "due date"])
    print(f"Extracted Information: {extracted_info}")
    ```
-   **Advanced Multimedia Bot**: A multi-threaded application using multiple OpenVINO models on different hardware (CPU, GPU, NPU) simultaneously. See [examples/UI/multimedia_bot.py](https://github.com/llmware-ai/llmware/blob/main/examples/UI/multimedia_bot.py)
-   **Fast Start Examples**: [Learn llmware through examples.](https://github.com/llmware-ai/llmware/tree/main/fast_start)
    - RAG Pipelines: See [fast_start/rag/](https://github.com/llmware-ai/llmware/tree/main/fast_start/rag)
    - Agentic workflows: See [fast_start/agents/](https://github.com/llmware-ai/llmware/tree/main/fast_start/agents)

## OpenVINO Model Configuration and Optimizations

### Temperature and Sampling

You can control the behavior of OpenVINO models using standard `llmware` parameters passed during the `load_model` call.

-   **`temperature`**: Controls randomness in the output. A value of `0.0` is deterministic.
-   **`sample`**: A boolean that enables or disables sampling.
-   **`max_output`**: An integer to limit the length of the generated response.

```python
# Example of loading a model with specific sampling parameters
model = ModelCatalog().load_model(
    "bling-tiny-llama-ov",
    temperature=0.0,
    sample=False,
    max_output=256,
)
```

### Device Placement and Performance Tuning
OpenVINO models automatically detect and utilize available hardware:
- **CPU:** Default fallback, optimized for Intel architectures.
- **GPU:** Automatically used when an Intel GPU (integrated or discrete) is available.
- **NPU:** Supported on the Intel Core Ultra processors (codename "Meteor Lake" and newer) for sustained, low-power AI workloads. Must be targeted explicitly by setting `device="NPU"`.

You can fine-tune OpenVINO performance using the `OVConfig` class. This is particularly useful for specifying device placement or adjusting performance hints.

```python
from llmware.models import ModelCatalog
from llmware.configs import OVConfig

# Option 1: Use OVConfig to set a global default device
OVConfig().set_config("device", "CPU")

# Option 2: Specify the device directly when loading a model
npu_model = ModelCatalog().load_model("slim-topics-npu-ov", device="NPU")
```

The available configuration options in `OVConfig` are:

| Parameter                 | Type    | Default Value        | Description                                                     |
| ------------------------- | ------- | -------------------- | ----------------------------------------------------------------|
| `device`                  | `str`   | `"GPU"`              | The device to run the model on (`"CPU"` or `"GPU"` or `"NPU"`). |
| `use_ov_tokenizer`        | `bool`  | `False`              | Whether to use the OpenVINO™ tokenizer.                         |
| `generation_version`      | `str`   | `"ov_genai_pip"`     | The generation version to use.                                  |
| `use_gpu_if_available`    | `bool`  | `True`               | If `True`, automatically uses the GPU if available.             |
| `cache`                   | `bool`  | `True`               | Enables caching of models to optimize subsequent loads.         |
| `cache_with_model`        | `bool`  | `True`               | If `True`, caches with the model.                               |
| `cache_custom_path`       | `str`   | `""`                 | A custom path for caching models.                               |
| `apply_performance_hints` | `bool`  | `True`               | Applies performance hints for GPU.                              |
| `verbose_mode`            | `bool`  | `False`              | Enables verbose logging for debugging.                          |
| `get_token_counts`        | `bool`  | `True`               | Whether to retrieve token counts during inference.              |


You can also set GPU-specific performance hints:
```python
# Example: Set the model priority to high
OVConfig().set_gpu_hint("MODEL_PRIORITY", "HIGH")
```
- Supported GPU hints include: `MODEL_PRIORITY`, `GPU_HOST_TASK_PRIORITY`, `GPU_QUEUE_THROTTLE`, `GPU_QUEUE_PRIORITY`.
- For more details, you can view the source code for the `OVConfig` class in [`llmware/configs.py`](https://github.com/llmware-ai/llmware/blob/main/llmware/configs.py#L537).

### OpenVINO Model Loading Phases
The OpenVINO model loading follows these phases when `ModelCatalog().load_model("..."),` is executed:
1. **Download**: Checks local copy of the model; if missing, downloads from Hugging Face.
2. **First Inference**: Compiles model, saves compiled artifacts as cache in model directory. 
3. **Subsequent Inferences**: Reuses cached artifacts. No recompilation is needed as the cache contains the optimized model representation, making subsequent model loads much faster.

The caching behavior can be customized through `OVConfig` methods if needed, such as disabling caching with `OVConfig().set_config("cache", False)` or setting a custom cache path.

Below is a sample to inspect model storage locations and verify downloaded OpenVINO models and caches locally.
```python
from llmware.configs import LLMWareConfig  
from llmware.models import ModelCatalog

# Print the general model repository path  
model_repo_path = LLMWareConfig.get_model_repo_path()  
print(f"Model repository path: {model_repo_path}")  

# Load model (downloads if missing, compiles and caches on first use, uses caches for subsequent)
ov_model = ModelCatalog().load_model("bling-tiny-llama-ov")
print("Loaded model path:", ov_model.model_repo_path)
```
