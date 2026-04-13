
"""
This example illustrates parsing a document and extracting unique topics using the SLIM topics tool 
"""

from llmware.parsers import Parser
from llmware.agents import LLMfx
from llmware.setup import Setup



def document_parser():
    # Add the path to the directory in fp, add the filename in fn
    fp = "#Add/Path/To/Document"
    fn = "Filename for analysis.pdf"


    #Given the filename and filepath, parses pdf into chunks
    doc_chunks = Parser().parse_one_pdf(fp,fn)
    print ("number of chunks: ", len(doc_chunks))
    #   create a LLMfx object
    agent = LLMfx()
    #load in the chunked document. to make the demo run faster or to test, slice it with [0:5]
    agent.load_work(doc_chunks)
    #load in the topic tool 
    agent.load_tool_list(["topics"])
    
    funcall_list = []
    while True:
        funcall_list.append(agent.exec_multitool_function_call(["topics"]))

        if not agent.increment_work_iteration():
            break
        
    return funcall_list
#Function to collapse the report to show unique topics


def collapser(report):
    no_duplicates = []
    #raise this to make your program more selective, lower it to get more topics
    required_confidence_score = 0.1
    for entry in report:
        if entry[0]['confidence_score'] > required_confidence_score:
            if 'topics' not in entry[0]['llm_response']:
                continue
            for topics in entry[0]['llm_response']['topics']:
                if topics not in no_duplicates:
                    no_duplicates.append(topics)
    return no_duplicates
        

if __name__ == "__main__":
    analysis = document_parser()
    print("\n Analysis: Shows Topics located in each chunk of the Document \n")
    print(analysis)
    print("\n Collapsed Analysis: Shows Unique topics located over the entire Document that meet the required confidence score. \n")
    print(collapser(analysis))



