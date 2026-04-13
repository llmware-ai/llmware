
""" This example shows how to use llmware provided sample files for testing with WhisperCPP, integrated as of
    llmware 0.2.11.

    # examples - "famous_quotes" | "greatest_speeches" | "youtube_demos" | "earnings_calls"

        -- famous_quotes - approximately 20 small .wav files with clips from old movies and speeches
        -- greatest_speeches - approximately 60 famous historical speeches in english
        -- youtube_videos - wav files of ~3 llmware youtube videos
        -- earnings_calls - wav files of ~4 public company earnings calls (gathered from public investor relations)

    These sample files are hosted in a non-restricted AWS S3 bucket, and downloaded via the Setup method
    `load_sample_voice_files`.   There are two options:

        --  small_only = True:      only pulls the 'famous_quotes' samples
        --  small_only = False:     pulls all of the samples    (requires ~1.9 GB in total)

    Please note that all of these samples have been pulled from open public domain sources, including the
    Internet Archives, e.g., https://archive.org.  These sample files are being provided solely for the purpose of
    testing the code scripts below.   Please do not use them for any other purpose.

    To run these examples, please make sure to `pip install librosa`
    """

import os
from llmware.models import ModelCatalog
from llmware.gguf_configs import GGUFConfigs
from llmware.setup import Setup

#   optional / to adjust various parameters of the model
GGUFConfigs().set_config("whisper_cpp_verbose", "OFF")
GGUFConfigs().set_config("whisper_cpp_realtime_display", True)

#   note: english is default output - change to 'es' | 'fr' | 'de' | 'it' ...
GGUFConfigs().set_config("whisper_language", "en")
GGUFConfigs().set_config("whisper_remove_segment_markers", True)


def sample_files(example="famous_quotes", small_only=False):

    """ Execute a basic inference on Voice-to-Text model passing a file_path string """

    voice_samples = Setup().load_voice_sample_files(small_only=small_only)

    examples = ["famous_quotes", "greatest_speeches", "youtube_demos", "earnings_calls"]

    if example not in examples:
        print("choose one of the following - ", examples)
        return 0

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

    return 0


if __name__ == "__main__":

    # pick among the four examples: famous_quotes | greatest_speeches | youtube_demos | earnings_calls

    sample_files(example="famous_quotes", small_only=False)

