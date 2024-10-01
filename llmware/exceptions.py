
# Copyright 2023-2024 llmware

# Licensed under the Apache License, Version 2.0 (the "License"); you
# may not use this file except in compliance with the License.  You
# may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.  See the License for the specific language governing
# permissions and limitations under the License.


class LLMWareException(Exception):

    """ Base exception class in LLMWare. """

    __module__ = 'llmware'

    def __init__(self, message="An unspecified error occurred"):
        super().__init__(message)
        self.message = message


class UnsupportedEmbeddingDatabaseException(LLMWareException):

    def __init__(self, embedding_db):
        message = f"'{embedding_db}' is not a supported vector embedding database"
        super().__init__(message)


class LLMInferenceResponseException(LLMWareException):

    def __init__(self, cloud_api_response):
        message = f"'{cloud_api_response}' is not a supported vector embedding database"
        super().__init__(message)


class HomePathDoesNotExistException(LLMWareException):

    def __init__(self, home_path):
        message = f"'{home_path}' file path does not exist"
        super().__init__(message)


class FilePathDoesNotExistException(LLMWareException):

    def __init__(self, file_path):
        message = f"'{file_path}' file path does not exist"
        super().__init__(message)


class UnsupportedCollectionDatabaseException(LLMWareException):

    def __init__(self, collection_db):
        message = f"'{collection_db}' is not currently a supported collection database"
        super().__init__(message)


class UnsupportedTableDatabaseException(LLMWareException):
    def __init__(self, collection_db):
        message = f"'{collection_db}' is not currently a supported SQL / table database"
        super().__init__(message)


class CollectionDatabaseNotFoundException(LLMWareException):

    def __init__(self, uri):
        message = f"'{uri}' path to collection database is not connected currently.   Library functions, such " \
                  f"as add_files, Query, Embedding, and Graph require connection to a collection database to " \
                  f"store, organize and index artifacts."

        super().__init__(message)


class PromptStateNotFoundException(LLMWareException):

    def __init__(self, prompt_id):
        message = f"'{prompt_id}' could not be located"
        super().__init__(message)


class PromptNotInCatalogException(LLMWareException):

    def __init__(self, prompt_name):
        message = f"'{prompt_name}' could not be located in the Prompt Catalog."
        super().__init__(message)


class DependencyNotInstalledException(LLMWareException):

    def __init__(self, required_library_dependency):
        message = f"'{required_library_dependency}' needs to be installed to use this function."
        super().__init__(message)


class LibraryNotFoundException(LLMWareException):

    def __init__(self, library_name,account_name):
        message = f"'{library_name}' in '{account_name}' could not be located"
        super().__init__(message)


class LibraryObjectNotFoundException(LLMWareException):

    """ Used in classes that expect a Library object to be passed - thrown when library object not found."""

    def __init__(self, library):
        message = f"'{library}' object must be passed to use this function."
        super().__init__(message)


class ModelNotFoundException(LLMWareException):

    def __init__(self, model_name):
        message = f"'{model_name}' could not be located"
        super().__init__(message)


class EmbeddingModelNotFoundException(LLMWareException):

    def __init__(self, library_name):
        message = f"Embedding model for '{library_name}' could not be located"
        super().__init__(message)


class ImportingSentenceTransformerRequiresModelNameException(LLMWareException):

    def __init__(self):
        message = f"Importing a sentence transformer model requires that a name is provided so that the model " \
                  f"can be looked up in the future to retrieve the embeddings."
        super().__init__(message)


class APIKeyNotFoundException(LLMWareException):

    def __init__(self, model_name):
        message = f"'{model_name}' could not be located"
        super().__init__(message)


class SetUpLLMWareWorkspaceException(LLMWareException):

    def __init__(self, home_path):
        message = f"Setting up llmware workspace at '{home_path}'.  To set up a custom path, " \
                  f"call Setup() explicitly with Setup().setup_llmware_workspace(home_path='/my/folder/')"

        super().__init__(message)


class DatasetTypeNotFoundException(LLMWareException):

    def __init__(self, ds_name):
        message = f"'{ds_name}' is not a recognized dataset type"
        super().__init__(message)


class OCRDependenciesNotFoundException(LLMWareException):
    def __init__(self, dependency_name):
        message = f"'{dependency_name}' does not appear to be installed locally. " \
                  f"OCR requires both tesseract and poppler. " \
                  f"For MacOS: 'brew install tesseract poppler'. " \
                  f"For Linux: 'apt install -y tesseract-ocr poppler-utils'."
        super().__init__(message)


class ConfigKeyException(LLMWareException):

    def __init__(self, config_key):
        message = f"'{config_key}' is not a valid configuration key."
        super().__init__(message)


class InvalidNameException(LLMWareException):

    def __init__(self, config_key):
        message = (f"'{config_key}' is not a valid name for this resource - please check special "
                   f"characters and/or may be reserved name.")
        super().__init__(message)


class ModuleNotFoundException(LLMWareException):

    def __init__(self, module_name):
        message = (f"Module '{module_name}' could not be located.  Please confirm the file path and extension. "
                   f"\n--There may be a missing binary, or an unsupported "
                   f"operating system platform.\n--Binaries are shipped in LLMWare for Mac (Metal), Windows (x86), "
                   f"and Linux (x86).\n--Please try re-installing and check documentation or raise issue "
                   f"at main Github repository at:  https://www.github.com/llmware-ai/llmware.git.")

        super().__init__(message)


class ModelCardNotRegisteredException(LLMWareException):

    def __init__(self, config_key):
        message = (f"'{config_key}' is missing key attributes and fails validation to be registered as a model.")
        super().__init__(message)


class GGUFLibNotLoadedException(LLMWareException):

    """ Exception raised when GGUF Lib back-end can not be loaded successfully.   Exception tries to be
    more helpful in sharing suggestions for potential causes and remedies. """

    def __init__(self, module_name, os_platform, use_gpu, _lib_path, custom_path):

        # over time, may add more details by os_platform

        if custom_path:

            message = (f"GGUF lib from custom path - '{_lib_path}' could not be successfully loaded.  Please "
                       f"check that the lib is a llama_cpp back-end binary.  Assuming that it is a valid build,"
                       f"then the most likely cause of the error is that the back-end binary was compiled "
                       f"with instructions not compatible with the current system.")

        else:

            if not use_gpu:

                message = (f"GGUF lib '{module_name}' could not be successfully loaded from shared library.  This is "
                           f"most likely because the prepackaged binary does not match your OS configuration.   "
                           f"LLMWare ships with 6 pre-built GGUF back-ends for Mac (Metal, Metal-no-acc), Windows (x86, CUDA), and "
                           f"Linux (x86, CUDA).  These binaries depend upon low-level instruction capabilities provided"
                           f"by the processor and OS, and for Windows and Linux assume that AVX and AVX2 will be "
                           f"enabled.  Useful debugging tips:\n--Ensure llmware 0.2.4+ installed, and if cloned from "
                           f"repository that all of the libs were fully updated"
                           f"\n--Linux - Ubuntu 20+ and GLIBC 2.31+ (will likely not run if GLIBC < 2.31); "
                           f"\n--Check CPU capabilities using `py-cpuinfo' library, which will generate a nice "
                           f"dictionary view of supported OS capabilities.\n"
                           f"--Raise an Issue on llmware github and please share the py-cpuinfo report for your system.")
            else:

                message = (f"GGUF lib '{module_name}' for CUDA could not be loaded successfully, and an attempt to "
                           f"fall-back to the CPU based library also failed.   To debug the CUDA availability, "
                           f"check the following:\n--`nvcc --version` to get the CUDA Driver version on your system."
                           f"\n--Win CUDA and Linux CUDA builds today require at least CUDA >= 12.1.\n"
                           f"--Pytorch is used to identify CUDA information - please check with the commands - "
                           f"`torch.cuda.is_available()` and `torch.version.cuda` that Pytorch is finding the "
                           f"right driver on your system.\n--Raise on Issue on llwmare github and share relevant "
                           f"system details on OS and CUDA drivers installed.")

        super().__init__(message)


