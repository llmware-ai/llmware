---
layout: default
title: Whisper CPP
parent: Components
nav_order: 14
description: overview of the major modules and classes of LLMWare  
permalink: /components/whisper_cpp
---
# Whisper CPP
---

llmware has an integrated WhisperCPP backend which enables fast, easy local voice-to-text processing. 

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
3.  ggml-small.en-tdrz.bin - this is a 'tiny-diarize' implementation that has been finetuned to identify the 
speakers and inserts special [_SOLM_] tags to indicate a conversation turn / change of speaker.
               
    Main repo:  https://github.com/akashmjn/tinydiarize/
    Citation:   @software{mahajan2023tinydiarize,
                author = {Mahajan, Akash}, month = {08},
                title = {tinydiarize: Minimal extension of Whisper for speaker segmentation with special tokens}
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


```python

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
```


Need help or have questions?
============================

Check out the [llmware videos](https://www.youtube.com/@llmware) and [GitHub repository](https://github.com/llmware-ai/llmware).

Reach out to us on [GitHub Discussions](https://github.com/llmware-ai/llmware/discussions).


# About the project

`llmware` is &copy; 2023-{{ "now" | date: "%Y" }} by [AI Bloks](https://www.aibloks.com/home).

## Contributing
Please first discuss any change you want to make publicly, for example on GitHub via raising an [issue](https://github.com/llmware-ai/llmware/issues) or starting a [new discussion](https://github.com/llmware-ai/llmware/discussions).
You can also write an email or start a discussion on our Discrod channel.
Read more about becoming a contributor in the [GitHub repo](https://github.com/llmware-ai/llmware/blob/main/CONTRIBUTING.md).

## Code of conduct
We welcome everyone into the ``llmware`` community.
[View our Code of Conduct](https://github.com/llmware-ai/llmware/blob/main/CODE_OF_CONDUCT.md) in our GitHub repository.

## ``llmware`` and [AI Bloks](https://www.aibloks.com/home)
``llmware`` is an open source project from [AI Bloks](https://www.aibloks.com/home) - the company behind ``llmware``.
The company offers a Software as a Service (SaaS) Retrieval Augmented Generation (RAG) service.
[AI Bloks](https://www.aibloks.com/home) was founded by [Namee Oberst](https://www.linkedin.com/in/nameeoberst/) and [Darren Oberst](https://www.linkedin.com/in/darren-oberst-34a4b54/) in Oktober 2022.

## License

`llmware` is distributed by an [Apache-2.0 license](https://github.com/llmware-ai/llmware/blob/main/LICENSE).

## Thank you to the contributors of ``llmware``!
<ul class="list-style-none">
{% for contributor in site.github.contributors %}
  <li class="d-inline-block mr-1">
     <a href="{{ contributor.html_url }}">
        <img src="{{ contributor.avatar_url }}" width="32" height="32" alt="{{ contributor.login }}">
    </a>
  </li>
{% endfor %}
</ul>


---
<ul class="list-style-none">
    <li class="d-inline-block mr-1">
        <a href="https://discord.gg/MhZn5Nc39h"><span><i class="fa-brands fa-discord"></i></span></a>
    </li>
    <li class="d-inline-block mr-1">
        <a href="https://www.youtube.com/@llmware"><span><i class="fa-brands fa-youtube"></i></span></a>
    </li>
  <li class="d-inline-block mr-1">
    <a href="https://huggingface.co/llmware"><span> <img src="https://huggingface.co/front/assets/huggingface_logo-noborder.svg" alt="Hugging Face" class="hugging-face-logo"/> </span></a>
     </li>
    <li class="d-inline-block mr-1">
        <a href="https://www.linkedin.com/company/aibloks/"><span><i class="fa-brands fa-linkedin"></i></span></a>
    </li>
    <li class="d-inline-block mr-1">
        <a href="https://twitter.com/AiBloks"><span><i class="fa-brands fa-square-x-twitter"></i></span></a>
    </li>
    <li class="d-inline-block mr-1">
        <a href="https://www.instagram.com/aibloks/"><span><i class="fa-brands fa-instagram"></i></span></a>
    </li>
</ul>
---

