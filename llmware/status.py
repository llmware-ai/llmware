import time
from threading import Thread

from llmware.resources import CollectionRetrieval, CollectionWriter
from llmware.configs import LLMWareTableSchema


class Status:

    """ Centralized reading/writing of status that provides a consistent interface for callers (e.g UI).
        Status consists of a summary string and key metrics that can be used to provide graphical widget
        update of progress.   If written to sql collection database, then will use the
        Status schema defined in configs.py"""

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

