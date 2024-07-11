"""
This script demonstrates how to extract topics from a youtube video transcript using the LLMfx agent and the slim topics tool. 
Transcripts are obtained by video ID through the youtube_transcript_api, saved to a text file, and then parsed by the LLMfx agent.
"""

from llmware.parsers import Parser
from llmware.agents import LLMfx
from llmware.setup import Setup
import os
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter



def transcript_parser(file_dest, file_name):
    # Given the filename and filepath, parses pdf into chunks
    
    doc_chunks = Parser().parse_one_text(file_dest, file_name)
    print("number of chunks: ", len(doc_chunks))
    
    # Create a LLMfx object
    agent = LLMfx()
    # Load in the chunked document. To make the demo run faster or to test, slice it with [0:5]
    agent.load_work(doc_chunks)
    # Load in the topic tool
    agent.load_tool_list(["topics"])
    
    funcall_list = []
    while True:
        funcall_list.append(agent.exec_multitool_function_call(["topics"]))

        if not agent.increment_work_iteration():
            break
        
    return funcall_list

# Function to collapse the report to show unique topics
def collapser(report):
    no_duplicates = []
    # Raise this to make your program more selective, lower it to get more topics
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
    #Edit the Video ID to the desired video
    video_id = "a62ghRjnLFU"
    formatter = TextFormatter()
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    text_formatted = formatter.format_transcript(transcript)

# Save the formatted text to a file
    file_name = "transcript.txt"
    file_dest = os.getcwd()
    file_path = os.path.join(file_dest, file_name)
    print("Transcript saved to: ", file_path)
    with open(file_path, "w") as file:
        file.write(text_formatted)


    analysis = transcript_parser(file_dest, file_name)
    print("\n Analysis: Shows Topics located in each chunk of the Document \n")
    print(analysis)
    print("\n Collapsed Analysis: Shows Unique topics located over the entire Document that meet the required confidence score. \n")
    print(collapser(analysis))
