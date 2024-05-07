
""" This tests WhisperCPP deployment and model loading.  """


import os
from llmware.models import ModelCatalog
from llmware.gguf_configs import GGUFConfigs
from llmware.setup import Setup

#   optional / to adjust various log/display parameters of the model
GGUFConfigs().set_config("whisper_cpp_verbose", "OFF")
GGUFConfigs().set_config("whisper_cpp_realtime_display", True)

#   note: english is default output - change to 'es' | 'fr' | 'de' | 'it' ...
GGUFConfigs().set_config("whisper_language", "en")

#   whether to add or remove segment markers in llm response output
GGUFConfigs().set_config("whisper_remove_segment_markers", True)


def test_whisper_cpp():

    """ Execute a basic inference on Voice-to-Text model passing a file_path string """

    voice_samples = Setup().load_voice_sample_files(small_only=True, over_write=True)

    example = "famous_quotes"

    fp = os.path.join(voice_samples,example)

    files = os.listdir(fp)

    #   these are the two key lines
    whisper_base_english = "whisper-cpp-base-english"

    model = ModelCatalog().load_model(whisper_base_english)

    for f in files:

        if f.endswith(".wav"):

            prompt = os.path.join(fp,f)

            print(f"\n\nPROCESSING: prompt = {prompt}")

            response = model.inference(prompt)

            print("\nllm response: ", response["llm_response"])
            print("usage: ", response["usage"])

            assert response is not None

    return 0





