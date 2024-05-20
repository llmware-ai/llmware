import os


class ManualsProcessor:
    """
    A class to process manuals by running semantic queries and generating prompts based on the results.

    Attributes:
        manuals_path (str): The file system path to the directory containing manual files.
        results (list): A list of semantic query results.
        prompter (object): An instance of a Prompter class capable of managing prompts.
        response_data (dict): A dictionary to store responses for each processed manual.

    Methods:
        process(query): Processes all manuals and collects responses based on the given query.
        process_manual(manual, index, query): Processes a single manual and collects responses.
        retrieve_queries(manual): Retrieves and filters query results relevant to a specific manual.
        run_prompt(query, qr, manual): Runs a prompt for a manual based on specific query results.
        collect_responses(responses, manual): Collects and stores responses from the LLM.
    """

    def __init__(self, manuals_path, results, prompter):
        """
        Initializes the ManualsProcessor with the given path, results, and prompter.

        Args:
            manuals_path (str): Path to the directory containing manual files.
            results (list): Semantic query results to be used for generating prompts.
            prompter (Prompter): The prompter instance capable of managing and executing prompts.
        """
              
        self.manuals_path = manuals_path
        self.results = results
        self.prompter = prompter
        self.response_data = {}

    def process(self, query):
        """
        Processes all manuals in the specified directory and collects responses for each.

        Args:
            query (str): The query string to use for generating prompts and collecting responses.

        Returns:
            dict: A dictionary containing responses for each processed manual.
        """

        manuals = [file for file in os.listdir(
            self.manuals_path) if not file.startswith('.')]
        for i, manual in enumerate(manuals):
            self.process_manual(manual, i, query)
        return self.response_data

    def process_manual(self, manual, index, query):
        """
        Processes a single manual, retrieves relevant queries, and runs prompts.

        Args:
            manual (str): The filename of the manual to process.
            index (int): The index of the manual in the list of all manuals.
            query (str): The query string to use for prompt generation.

        """        
        qr = self.retrieve_queries(manual)
        if qr:
            print(f"\nManual Name: {index} {manual}")
            self.run_prompt(query, qr, manual)

    def retrieve_queries(self, manual):
        """
        Retrieves and filters query results that are relevant to the specified manual.

        Args:
            manual (str): The filename of the manual for which to retrieve queries.

        Returns:
            list: A list of query results relevant to the manual.
        """        
        qr = []
        for j, entry in enumerate(self.results):
            library_fn = os.path.basename(entry["file_source"])
            if library_fn == manual:
                print(f"Top Retrieval: {j} {
                      entry['distance']} {entry['text']}")
                qr.append(entry)
        return qr

    def run_prompt(self, query, qr, manual):
        """
        Runs a prompt for the specified manual using the given query results.

        Args:
            query (str): The query string to use for generating the prompt.
            qr (list): A list of query results to use as source material for the prompt.
            manual (str): The filename of the manual for which the prompt is being run.
        """
         
        self.prompter.add_source_query_results(query_results=qr)
        response = self.prompter.prompt_with_source(
            query, prompt_name="default_with_context", temperature=0.3)
        self.collect_responses(response, manual)
        self.prompter.clear_source_materials()

    def collect_responses(self, responses, manual):
        """
        Collects and stores responses from the LLM for the specified manual.

        Args:
            responses (list): A list of responses from the LLM.
            manual (str): The filename of the manual for which responses are collected.

        """        
        llm_responses = []
        for response in responses:
            if "llm_response" in response:
                print(f"\nUpdate: LLM answer - {response['llm_response']}")
                llm_responses.append(response["llm_response"])
        self.response_data[manual] = llm_responses
