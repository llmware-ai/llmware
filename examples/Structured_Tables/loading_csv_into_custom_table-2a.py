
""" This example shows how to quickly build a CustomTable using a 'pseudo-DB' CSV file.  A 'pseudo-DB' is a CSV
    organized in a set of rows with a common column structure.  Below we will show a few tools to analyze and
    validate the CSV upfront to assess if there are areas that need remediation before attempting to safely load
    into a database.

    CustomTable is designed to work with the text collection databases supported by LLMWare:

        SQL DBs     ---     Postgres and SQLIte
        NoSQL DB    ---     Mongo DB

    Even though Mongo does not require a schema for inserting and retrieving information, the CustomTable method
    will expect a defined schema to be provided (good best practice, in any case).  """

from llmware.resources import CustomTable


def building_custom_table_from_csv():

    #   point fp and fn at the file_path of the CSV file
    fp = "/path/to/your/csv_file"

    #   good example in examples folder - customer_table.csv
    fn = "sample_file.csv"

    #   first analyze the csv and confirm that the rows and columns are consistently being extracted
    analysis = CustomTable().validate_csv(fp,fn,delimiter=',',encoding='utf-8-sig')

    print("\nAnalysis of the CSV file")
    for key, value in analysis.items():
        print(f"analysis: {key} - {value}")

    table_name = "sample_table_100"

    #   use "postgres" | "mongo" | "sqlite"
    db_name = "postgres"

    ct = CustomTable(db=db_name,table_name=table_name)

    #   load the csv, which will identify the schema and data types, and package as 'rows' ready for db insertion
    #    -- this method will NOT create the DB table or insert any rows - that happens in the next step
    #    -- if there is a 'header_row', then it will not be inserted in the DB (so row count may differ by 1

    output = ct.load_csv(fp,fn)

    print("\nLoad CSV output")
    for key, value in output.items():
        print(f"output: {key} - {value}")

    #   spot-check the rows that have been created before inserting into database as a final check
    print("\nSpot-Check Rows Before Inserting into DB Table")
    sample_size = min(len(ct.rows), 10)
    for x in range(0,sample_size):
        print("rows: ", x, ct.rows[x])

    #   when ready, uncomment, and insert the rows into the DB
    ct.insert_rows()

    #   basic query
    #   e.g., if using customer_table included in example folder - "customer_name", "Martha Williams"
    customer = ct.lookup("key", "lookup_value")
    print("\nLookup from DB")
    print(f"customer_record: ", customer)

    ct.delete_table(confirm=True)

    return 0


if __name__ == "__main__":

    building_custom_table_from_csv()
