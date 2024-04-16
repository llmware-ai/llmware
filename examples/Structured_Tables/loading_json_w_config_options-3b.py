
""" This example illustrates how to use the various configuration options to maximize the quality of JSON/JSONL files
    loading into a custom DB table.  For basic getting started examples, please see "create_custom_table.py" and
    "loading_json_into_custom_table.py" in this examples repository first.

    CustomTable is designed to work with the text collection databases supported by LLMWare:

        SQL DBs     ---     Postgres and SQLIte
        NoSQL DB    ---     Mongo DB

    Even though Mongo does not require a schema for inserting and retrieving information, the CustomTable method
    will expect a defined schema to be provided (good best practice, in any case).  """

from llmware.resources import CustomTable


def building_custom_table_from_json(config_option=2):

    #   point fp and fn at the file_path of the JSON file
    fp = "/local/path/to/json_file"

    #   note: this example uses the "model_list.json" example file found in the examples repository
    #   -- if substituting for your own json/jsonl, please also adjust the sample query below
    fn = "model_list.json"

    #   first analyze the csv and confirm that the rows and columns are consistently being extracted
    #   key_list is optional and can be removed - will validate all columns
    #   if key_list provided, then will look only at the keys provided
    analysis = CustomTable().validate_json(fp,fn, key_list=["model_name", "context_window"])

    print("\nAnalysis of the JSON file")
    for key, value in analysis.items():
        print(f"analysis: {key} - {value}")

    if not (1 <= config_option <= 4):
        print("\nsetting config to default == 1")
        config_option = 1

    table_name = "model_table_100"
    db_name = "mongo"
    output = None

    #   loading a json into a database has three main steps
    #   1.  construct CustomTable object
    #   2.  load_json - *** where most of the configuration will occur ***
    #   3.  insert_rows

    ct = CustomTable(db=db_name,table_name=table_name)

    if config_option == 1:

        #   load_json - Option #1 - this is the simplest case
        #   -- will use the first row as the 'test row' to extract keys for the schema
        #   -- will infer the data type for each column as either 'text' | 'integer' | 'float'

        output = ct.load_json(fp ,fn)

    elif config_option == 2:

        #   load_json - Option #2 -  pass a subset of the keys to use for the schema
        #   -- will look for key in each row, and ignore keys not in the selected_keys

        target_keys = ["model_name", "context_window"]
        output = ct.load_json(fp, fn, selected_keys=target_keys)

    elif config_option == 3:

        #   load_csv - Option #3 - pass an explicit data type mapping, for all or some columns,
        #   which will 'over-ride' the estimation
        #   -- for json, the mapping needs to be done by the name of the key, e.g., "context_window"

        dt_mapping = {"context_window": "decimal"}
        output = ct.load_json(fp, fn, data_type_map=dt_mapping)

    elif config_option == 4:

        #   load_csv - Option #4 - pass a complete schema to be used

        #   note: this option is not intended for use with the customer_table.csv example
        my_schema = {"model_name": "text", "model_family": "text", "context_window": "text"}
        output = ct.load_json(fp, fn, schema=my_schema)

    print("\nLoad CSV output")
    for key, value in output.items():
        print(f"output: {key} - {value}")

    #   spot-check the rows that have been created before inserting into database as a final check
    print("\nSpot-Check Rows Before Inserting into DB Table")
    sample_size = min(len(ct.rows), 10)
    for x in range(0 ,sample_size):
        print("rows: ", x, ct.rows[x])

    #   when ready, uncomment, and insert the rows into the DB
    ct.insert_rows()

    #   basic query
    customer = ct.lookup("model_name", "slim-extract-tool")
    print("\nLookup from DB")
    print(f"customer_record: ", customer)

    return 0


if __name__ == "__main__":

    building_custom_table_from_json(config_option=2)
