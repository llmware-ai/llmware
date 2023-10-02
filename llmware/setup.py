
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


import shutil
import os
from llmware.resources import CloudBucketManager
from llmware.configs import LLMWareConfig
from llmware.library import Library
from llmware.retrieval import Query

from python_on_whales import DockerClient

import subprocess
import logging


class Setup:

    @staticmethod
    def load_sample_files():

        #   changed name from demo to 'sample_files'
        #   simplified:  no user config - pulls into llmware_path

        if not os.path.exists(LLMWareConfig.get_llmware_path()):
            LLMWareConfig.setup_llmware_workspace()

        # not configurable - will pull into /sample_files under llmware_path
        sample_files_path = os.path.join(LLMWareConfig.get_llmware_path(), "sample_files")

        if not os.path.exists(sample_files_path):
            os.makedirs(sample_files_path,exist_ok=True)
        else:
            logging.info("update: sample_files path already exists - %s ", sample_files_path)

        # pull from sample files bucket
        bucket_name = LLMWareConfig().get_config("llmware_sample_files_bucket")
        remote_zip = bucket_name + ".zip"
        local_zip = os.path.join(sample_files_path, bucket_name + ".zip")
            
        CloudBucketManager().pull_file_from_public_s3(remote_zip, local_zip, bucket_name)
        shutil.unpack_archive(local_zip, sample_files_path, "zip")
        os.remove(local_zip)

        return sample_files_path
