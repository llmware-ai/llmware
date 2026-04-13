
""" This example illustrates how to parse voice-to-text files in memory, run searches against those files, and then
use to run extract inference calls to identify specific content - and in the end, produce a list of the key source
citations with source file, time_stamp, and target text. """


import os

from llmware.parsers import Parser
from llmware.setup import Setup
from llmware.util import Utilities
from llmware.models import ModelCatalog


def greatest_speeches_example():

    # four sample file sets - "famous_quotes" | "greatest_speeches" | "youtube_demos" | "earnings_calls"
    voice_sample_files = Setup().load_voice_sample_files(small_only=False)

    input_folder = os.path.join(voice_sample_files, "greatest_speeches")

    print("\nStep 1 - converting, parsing and text chunking ~56 WAV files")

    parser_output = Parser(chunk_size=400, max_chunk_size=600).parse_voice(input_folder,
                                                                           write_to_db=False,
                                                                           copy_to_library=False,
                                                                           remove_segment_markers=True,
                                                                           chunk_by_segment=True,
                                                                           real_time_progress=False)

    print("\nStep 2- look at the text chunks with all of the metadata")

    for i, entries in enumerate(parser_output):
        print("all parsed blocks: ", i, entries)

    print("\nStep 3- run an inline text search for 'president'")

    results = Utilities().fast_search_dicts("president", parser_output)

    for i, res in enumerate(results):
        print("search results: ", i, res)

    print("\nStep 4- use LLM to review each search result - and if specific U.S. presidents found, then display the source")

    extract_model = ModelCatalog().load_model("slim-extract-tool", sample=False, temperature=0.0, max_output=200)

    final_list = []

    for i, res in enumerate(results):

        response = extract_model.function_call(res["text"], params=["president name"])

        various_american_presidents = ["kennedy", "carter", "nixon", "reagan", "clinton", "obama"]

        extracted_name = ""
        if "president_name" in response["llm_response"]:
            if len(response["llm_response"]["president_name"]) > 0:
                extracted_name = response["llm_response"]["president_name"][0].lower()
            else:
                print("\nupdate: skipping result - no president name found - ", response["llm_response"], res["text"])

        for president in various_american_presidents:
            if president in extracted_name:
                print("\nextracted american president text: ", i, extracted_name)
                print("file source: ", res["file_source"])
                print("time stamp: ", res["coords_x"], res["coords_y"], res["coords_cx"], res["coords_cy"])
                print("text: ", i, res["text"])
                final_list.append({"key": president, "source": res["file_source"], "time_start": res["coords_x"],
                                   "text": res["text"]})

    print("\nStep 5 - final results")
    for i, f in enumerate(final_list):
        print("final results: ", i, f)

    return final_list


if __name__ == "__main__":

    greatest_speeches_example()




