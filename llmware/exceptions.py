
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


# Base exception class for all others
class LLMWareException(Exception):

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
        message = f"'{required_library_dependency}' needs to be installed to use this function.  Please refer to the " \
                  f"documentation with any questions. "
        super().__init__(message)


class LibraryNotFoundException(LLMWareException):

    def __init__(self, library_name,account_name):
        message = f"'{library_name}' in '{account_name}' could not be located"
        super().__init__(message)


# when Library obj passed, and either null or lacking correct attributes
class LibraryObjectNotFoundException(LLMWareException):

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
