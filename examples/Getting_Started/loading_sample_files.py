
""" This example reviews the sample files available and how to pull down locally
#   Note: many of the examples will use these sample files.
#   Please feel free to substitute for your own files.
"""

import os
from llmware.setup import Setup


def get_llmware_sample_files():

    print (f"\n > Loading the llmware Sample Files...")

    #   this call to Setup() will pull the sample files from a public S3 repo
    #   the files will be placed in folders locally at the sample_files_path

    sample_files_path = Setup().load_sample_files()

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


if __name__ == "__main__":

    get_llmware_sample_files()

