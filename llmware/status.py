"""The status module implements the Status class, which provides an interface for callers to read and write
a status.

The callers can for example be a UI or a SQL datacase.
"""

import time
from threading import Thread

from llmware.resources import CollectionRetrieval, CollectionWriter
from llmware.configs import LLMWareTableSchema


class Status:
    """Provides callers with an interface on the status of the parsing and embedding process.

    ``Status`` is the central class for accessing (reading and writting) the status of processes.
    The intended use case is to be an interface for non-llmware components (the callers) that need
    information on llmware progress, e.g user interface components may need to change depending on the
    progress of parsing. A status consists of a summary string and metrics that can be used to provide
    graphical widgets an update. If a status is written to SQL collection database, then it will use the
    Status schema defined in configs.py.

    Parameters
    ----------
    account_name : str, optional, default='llmware'
        Sets the name of the account, which is used for writting and retrieving a status.

    Returns
    -------
    status : Status
        A new ``Status`` object.

    Examples
    ----------
    >>> import llmware.status
    >>> llmware_status = llmare.status.Status()
    >>> llmware_status.account_name 
    "llmware"
    >>> llmware_status = llmware.status.Status(account_name="my_account")
    >>> llmware_status.account_name 
    "my_account"
    """
    def __init__ (self, account_name="llmware"):

        self.account_name = account_name
        self.schema = LLMWareTableSchema.get_status_schema()

        #  if table does not exist (and required by the underlying collection db), then create
        if CollectionWriter("status", account_name=self.account_name).check_if_table_build_required():

            # create "status" table
            CollectionWriter("status", account_name=self.account_name).create_table("status", self.schema)

    def get_pdf_parsing_status(self, library_name, job_id="0"):

        """ Gets the status written by the PDF parser """

        status_key = f"{library_name}_pdf_parser_{job_id}"
        status = CollectionRetrieval("status", account_name=self.account_name).lookup("key", status_key)

        return status

    def get_office_parsing_status(self, library_name,job_id="0"):

        """ Gets the status written by the Office parser """

        status_key = f"{library_name}_office_parser_{job_id}"
        status = CollectionRetrieval("status", account_name=self.account_name).lookup("key", status_key)

        return status

    # Return the status dict
    def get_embedding_status(self, library_name, embedding_model):

        """ Gets the embedding status written by the EmbeddingHandler class and each supported vector DB """

        status_key = self._get_embedding_status_key(library_name, embedding_model)
        status = CollectionRetrieval("status", account_name=self.account_name).lookup("key", status_key)

        return status
    
    def new_embedding_status(self, library_name, embedding_model, total):

        """ Creates a new embedding status - invoked at start of embedding job """

        status_key = self._get_embedding_status_key(library_name, embedding_model)
        status_entry = {
            "key": status_key,
            "summary": f"0 of {total} blocks",
            "start_time": time.time(),
            "end_time": None,
            "total": total,
            "current": 0,
            "units": "blocks" 
        }
        CollectionWriter("status", account_name=self.account_name).replace_record({"key":status_key},status_entry)

        return 0

    def increment_embedding_status(self, library_name, embedding_model, progress):

        """ Increments the embedding status throughout the embedding job - enables parallelized writing and updates """

        status_key = self._get_embedding_status_key(library_name, embedding_model)

        status_entry = CollectionRetrieval("status", account_name=self.account_name).lookup("key", status_key)

        if len(status_entry) == 1:
            status_entry = status_entry[0]

        status_entry["current"] = status_entry["current"] + progress
        if status_entry["current"] >= status_entry["total"]:
            status_entry["end_time"] = time.time()

        status_entry["summary"] = f"{status_entry['current']} of {status_entry['total']} {status_entry['units']}"

        CollectionWriter("status", account_name=self.account_name).replace_record({"key":status_key}, status_entry)

        return 0

    def tail_embedding_status(self, library_name, model_name, poll_seconds=0.2):

        """ Can be invoked in tests to poll and check and print out embedding status """

        thread = Thread(target = self._tail_embedding_status, args = (library_name, model_name, poll_seconds))
        thread.daemon=True
        thread.start()

    def _tail_embedding_status(self, library_name, model_name, poll_seconds=0.2):

        """ Display of embedding status """

        current_summary = ""
        while True:
            status_dict = self.get_embedding_status(library_name, model_name)
            if status_dict:
                if current_summary != status_dict["summary"]:  # If the status has changed, print it
                    current_summary = status_dict["summary"]
                    print(current_summary)
                    if status_dict["current"] >= status_dict["total"]:  # If the job is done exit
                        return     
            time.sleep(poll_seconds)

    # Generate and return a unique key for status, combining the library_name and embedding_model
    def _get_embedding_status_key(self, library_name, embedding_model):

        """ Gets the embedding status key """

        return f"{library_name}_embedding_{embedding_model}"

