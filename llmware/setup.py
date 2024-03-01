# Copyright 2023 llmware

# Licensed under the Apache License, Version 2.0 (the "License"); you
# may not use this file except in compliance with the License.  You
# may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.  See the License for the specific language governing
# permissions and limitations under the License.
"""The setup module implements the init process.

The module implements the Setup class, which has one static method - load_sample_files. This method
creates the necessary directory if they do not exist and downloads the sample files from an AWS S3 instance.
"""


import shutil
import os
from llmware.resources import CloudBucketManager
from llmware.configs import LLMWareConfig
from llmware.library import Library
from llmware.retrieval import Query

import subprocess
import logging


class Setup:
    """Implements the download of sample files from an AWS S3 bucket.

    ``Setup`` implements the download of sample files from an AWS S3 bucket. Currently, there are samples
    from eight domains. Which are

    - AgreementsLarge (~80 sample contracts)
    - Agreements (~15 sample employment agreements)
    - UN-Resolutions-500 (500 United Nations Resolutions over ~2 years)
    - Invoices (~40 invoice sample documents)
    - FinDocs (~15 financial annual reports, earnings and 10Ks)
    - AWS-Transcribe (~5 AWS-transcribe JSON files)
    - SmallLibrary (~10 mixed document types for quick testing)
    - Images (~3 images for OCR processing)

    The sample files are updated continously. By calling ``Setup().load_sample_files(over_write=True)``
    you will get the newest version of the sample files.

    The sample files were prepared by LLMWare from public domain materials, or invented bespoke.
    If you have any concerns about Personally Identifiable Information (PII), or the suitability of any material
    we included, please contact us, e.g. either by raising an issue on GitHub or sending an E-Mail.
    We reserve the right to withdraw documents at any time.

    Examples
    ----------
    >>> import os
    >>> from llmware.setup import Setup
    >>> sample_files_path = Setup().load_sample_files()
    >>> sample_files_path
    '/home/user/llmware_data/sample_files'
    >>> os.listdir(sample_files_path)
    ['AWS-Transcribe', '.DS_Store', 'SmallLibrary', 'UN-Resolutions-500', 'Invoices', 'Images', 'AgreementsLarge', 'Agreements', 'FinDocs']

    If you have called the function before but want to get the newest updates to the sample files, or you simply
    want to get the newest sample files, you simply set ``over_write=True``.
    >>> sample_files_path = Setup().load_sample_files(over_write=True)
    """
    @staticmethod
    def load_sample_files(over_write=False):

        #   changed name from demo to 'sample_files'
        #   simplified:  no user config - pulls into llmware_path

        if not os.path.exists(LLMWareConfig.get_llmware_path()):
            LLMWareConfig.setup_llmware_workspace()

        # not configurable - will pull into /sample_files under llmware_path
        sample_files_path = os.path.join(LLMWareConfig.get_llmware_path(), "sample_files")

        if not os.path.exists(sample_files_path):
            os.makedirs(sample_files_path,exist_ok=True)
        else:
            if not over_write:
                logging.info("update: sample_files path already exists - %s ", sample_files_path)
                return sample_files_path

        # pull from sample files bucket
        bucket_name = LLMWareConfig().get_config("llmware_sample_files_bucket")
        remote_zip = bucket_name + ".zip"
        local_zip = os.path.join(sample_files_path, bucket_name + ".zip")
            
        CloudBucketManager().pull_file_from_public_s3(remote_zip, local_zip, bucket_name)
        shutil.unpack_archive(local_zip, sample_files_path, "zip")
        os.remove(local_zip)

        return sample_files_path
