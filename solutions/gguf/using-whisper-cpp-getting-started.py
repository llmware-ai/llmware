
""" This example shows how to get started using WhisperCPP as a fast, local voice-to-text processing engine.

    Whisper is a leading open voice voice-to-text model from OpenAI - https://github.com/openai/whisper

    WhisperCPP is the implementation of Whisper packaged as a GGML deliverable - https://github.com/ggerganov/whisper.cpp

    Starting with llmware 0.2.11, we have integrated WhisperCPPModel as a new model class,
    providing options for direct inference, and coming soon, integration into the Parser for easy text chunking and
    parsing into a Library with other document types.

    llmware provides prebuilt shared libraries for WhisperCPP on the following platforms:
        --Mac M series
        --Linux x86 (no CUDA)
        --Linux x86 (with CUDA) - really fast
        --Windows x86 (only on CPU) currently.

    We have added three Whisper models to the default model catalog:
        1.  ggml-base.en.bin - english-only base model
        2.  ggml-base.bin - multi-lingual base model
        2.  ggml-small.en-tdrz.bin - this is a 'tiny-diarize' implementation that has been finetuned to identify the
            speakers and inserts special [_SOLM_] tags to indicate a conversation turn / change of speaker.
            Main repo:  https://github.com/akashmjn/tinydiarize/
            Citation:   @software{mahajan2023tinydiarize,
                        author = {Mahajan, Akash}, month = {08},
                        title = {tinydiarize: Minimal extension of Whisper for speaker segmentation with special tokens},
                        url = {https://github.com/akashmjn/tinydiarize},
                        year = {2023}

    To use WAV files, there is one additional Python dependency required:
        --pip install librosa
        --Note: this has been added to the default requirements.txt and pypy build starting with 0.2.11

    To use other popular audio/video file formats, such as MP3, MP4, M4A, etc., then the following dependencies are
    required:
        --pip install pydub
        --ffmpeg library - which can be installed as follows:
            --  Linux:  `sudo apt install ffmpeg'
            --  Mac:    `brew install ffmpeg`
            -- Windows:  direct download and install from ffmpeg

    """

import os
from llmware.models import ModelCatalog
from llmware.gguf_configs import GGUFConfigs

#   optional / to adjust various log/display parameters of the model
GGUFConfigs().set_config("whisper_cpp_verbose", "OFF")
GGUFConfigs().set_config("whisper_cpp_realtime_display", True)

#   note: english is default output - change to 'es' | 'fr' | 'de' | 'it' ...
GGUFConfigs().set_config("whisper_language", "en")

#   whether to add or remove segment markers in llm response output
GGUFConfigs().set_config("whisper_remove_segment_markers", True)


def basic_whisper_cpp_use_example():

    """ Hello world example to get started using WhisperCPP in LLMWare. """

    fp = "/local/path/to/.wav"
    fn = "my_wav.wav"

    #   prompt = string representing the path to a .wav file
    prompt = os.path.join(fp,fn)

    #   choose between english-only and multilingual
    whisper_base_english = "whisper-cpp-base-english"
    whisper_base_multi = "whisper-cpp-base"

    #   load and run inference like any other model in llmware
    model = ModelCatalog().load_model(whisper_base_english)
    response = model.inference(prompt)

    print("\nllm response: ", response["llm_response"])
    print("usage: ", response["usage"])

    return response


if __name__ == "__main__":

    response = basic_whisper_cpp_use_example()

