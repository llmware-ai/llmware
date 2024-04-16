
""" This example shows how to quickly build a CustomTable using a 'pseudo-DB' JSON/JSONL file.  A 'pseudo-DB' is a
    well-formed JSON/JSONL file that has a common set of keys in each dictionary entry, and multiple repeating
    'row-like' entries that can be iterated through and converted into a row/column database structure.  Below we
    will show a few tools to analyze and validate the JSON/JSONL upfront to assess if there are areas that
    need remediation before attempting to safely loading into a database.

    CustomTable is designed to work with the text collection databases supported by LLMWare:

        SQL DBs     ---     Postgres and SQLIte
        NoSQL DB    ---     Mongo DB

    Even though Mongo does not require a schema for inserting and retrieving information, the CustomTable method
    will expect a defined schema to be provided (good best practice, in any case).  """

from llmware.resources import CustomTable


def building_custom_table_from_json():

    #   point fp and fn at the file_path of the JSON/JSONL file
    fp = "/local_path/to/json_files"

    #   good example file in examples folder path - "model_list.json"
    fn = "my_test_file.json"

    #   first analyze the json and confirm that the rows and columns are consistently being extracted
    analysis = CustomTable().validate_json(fp,fn,key_list=None)

    print(f"\nAnalysis of JSON/JSONL file")
    for key, value in analysis.items():
        print(f"analysis: {key} - {value}")

    table_name = "example_json_table_100"

    #   use any of "mongo" | "sqlite" | "postgres"
    db_name = "mongo"

    ct = CustomTable(db=db_name,table_name=table_name)

    output = ct.load_json(fp,fn)

    print(f"\nOutput from load_json")
    for key, value in output.items():
        print(f"load_json: {key} - {value}")

    #   spot-check the rows that have been created before inserting into database as a final check
    print("\nSpot-Check Rows Before Inserting into DB Table")
    sample_size = min(len(ct.rows), 10)
    for x in range(0,sample_size):
        print("rows: ", x, ct.rows[x])

    #   when ready, uncomment, and insert the rows into the DB
    ct.insert_rows()

    #   lookup - if using the model_list.json sample file, use "model_name", "slim-extract-tool"
    res = ct.lookup("key", "selected_value")

    print("\nLookup Test")
    print("result: ", res)

    return 0


if __name__ == "__main__":

    building_custom_table_from_json()
