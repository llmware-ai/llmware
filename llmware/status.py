import time
from threading import Thread

from llmware.resources import DBManager

'''
  Central reading/writing of status that provides a consistent interface for callers (e.g UI). 
  Status consists of a summary string and then also the components that can be used 
  to create a graphical widget/representation:
    {
      "_id": {
        "$oid": "65366141175b27db0cfba505"
      },
      "key": "my_lib_embedding_my_model",
      "summary": "500 of 15000 blocks",
      "start_time": 1698063019.618876,
      "end_time": null,
      "total": 15000,
      "current": 500,
      "units": "blocks"
    }
'''


class Status:

    def __init__ (self, account_name="llmware"):
        self.account_name = account_name
        self.status_collection = DBManager().client[self.account_name]["status"]

    # new status 'get' from c parsers ('set' in parser code directly)
    def get_pdf_parsing_status(self, library_name, job_id="0"):
        status_key = f"{library_name}_pdf_parser_{job_id}"
        status = self.status_collection.find_one({"key": status_key})
        return status

    def get_office_parsing_status(self, library_name,job_id="0"):
        status_key = f"{library_name}_office_parser_{job_id}"
        status = self.status_collection.find_one({"key": status_key})
        return status

    # Return the status dict
    def get_embedding_status(self, library_name, embedding_model):
        status_key = self._get_embedding_status_key(library_name, embedding_model)
        return self.status_collection.find_one({"key": status_key})
    
    # Create or reset the embeddding status for the given embedding_model
    def new_embedding_status(self, library_name, embedding_model, total):
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
        self.status_collection.replace_one({"key": status_key}, status_entry, upsert=True)
   
    # Increment the status progress (this is called by the worker/task as it works through a job)
    def increment_embedding_status(self, library_name, embedding_model, progress):
        status_key = self._get_embedding_status_key(library_name, embedding_model)
        status_entry = self.status_collection.find_one({"key": status_key})
        status_entry["current"] = status_entry["current"] + progress
        if status_entry["current"] >= status_entry["total"]:
            status_entry["end_time"] = time.time()
        status_entry["summary"] = f"{status_entry['current']} of {status_entry['total']} {status_entry['units']}"
        self.status_collection.replace_one({"key": status_key}, status_entry, upsert=True)

    # Kick off a thread that will poll and print the status
    def tail_embedding_status(self, library_name, model_name, poll_seconds=0.2):
        Thread(target = self._tail_embedding_status, args = (library_name, model_name, poll_seconds)).start()

    def _tail_embedding_status(self, library_name, model_name, poll_seconds=0.2):
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
        return f"{library_name}_embedding_{embedding_model}"

