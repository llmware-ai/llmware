
""" To enable rapid testing and prototyping, LLMWare provides a range of sample files that can be accessed
through the Setup class, and specific methods that will pull the files from a non-restricted llmware AWS S3 bucket,
and download the files locally in the /llmware_data/sample_files path.

    Sample files are created from public domain sources, and often developed originally by LLMWare.   They are
provided for convenience in testing.   As we find or develop a good testing set, we will generally try to make it
available so everyone can use - as a result, the sample files collection is evolving and growing all the time!

    If you have an older version, and would like to get the latest, then you can set the over_write=True option.

"""

import os
from llmware.setup import Setup


def get_llmware_sample_files():

    print (f"\n > Loading the llmware Sample Files...")

    #   this call to Setup() will pull the sample files from a public S3 repo
    #   the files will be placed in folders locally at the sample_files_path

    sample_files_path = Setup().load_sample_files(over_write=False)

    print(f"> Sample Files Path - {sample_files_path}")

    print(f"> Sample Folders - {os.listdir(sample_files_path)}")

    #   Current Sample Files:
    #
    #   AgreementsLarge     =   ~80 sample contracts
    #   Agreements          =   ~15 sample employment agreements
    #   UN-Resolutions-500  =   500 United Nations Resolutions (~2 years) - public repo - PDF files
    #   Invoices            =   ~40 invoice sample documents
    #   FinDocs             =   ~15 financial annual reports, earnings and 10Ks
    #   AWS-Transcribe      =   ~5 AWS-transcribe JSON files
    #   SmallLibrary        =   ~10 mixed document types for quick testing
    #   Images              =   ~3 images for OCR processing

    #   Note: these files will be updated from time-to-time - if you want to pull fresh new files
    #   sample_files_path = Setup().load_sample_files(over_write=True)

    #   These files were prepared by LLMWare from public domain materials or invented bespoke as examples
    #   If you have any concerns about PII or the suitability or any material, please let us know
    #   We reserve the right to withdraw documents at any time

    return 0


def get_llmware_voice_sample_files():

    print (f"\n > Loading the llmware Sample Voice Files...")

    #   check out the examples:  Models/using-whisper-cpp-sample-files.py and
    #                            Use_Cases/parsing_great_speeches.py

    #   this call to Setup() will pull the sample files from a public S3 repo
    #   the files will be placed in folders locally at the sample voice files path

    sample_files_path = Setup().load_voice_sample_files(over_write=False,small_only=False)

    print(f"> Sample Voice Files Path - {sample_files_path}")

    print(f"> Sample Voice Folders - {os.listdir(sample_files_path)}")

    # examples - "famous_quotes" | "greatest_speeches" | "youtube_demos" | "earnings_calls"

    #   -- famous_quotes - approximately 20 small .wav files with clips from old movies and speeches
    #   -- greatest_speeches - approximately 60 famous historical speeches in english
    #   -- youtube_videos - wav files of ~3 llmware youtube videos
    #   -- earnings_calls - wav files of ~4 public company earnings calls (gathered from public investor relations)

    # These sample files are hosted in a non-restricted AWS S3 bucket, and downloaded via the Setup method
    # `load_sample_voice_files`.   There are two options:

    #    --  small_only = True:      only pulls the 'famous_quotes' samples
    #    --  small_only = False:     pulls all of the samples    (requires ~1.9 GB in total)

    # Please note that all of these samples have been pulled from open public domain sources, including the
    # Internet Archives, e.g., https://archive.org.  These sample files are being provided solely for the purpose of
    # testing the code scripts below.   Please do not use them for any other purpose.

    return 0


if __name__ == "__main__":

    get_llmware_sample_files()

    get_llmware_voice_sample_files()


