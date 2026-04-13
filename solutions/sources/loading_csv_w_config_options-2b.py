
""" This example illustrates how to use the various configuration options to maximize the quality of CSV files
    loading into a custom DB table.  For basic getting started examples, please see "create_custom_table.py" and
    "loading_csv_into_custom_table.py" in this examples repository first.

    CustomTable is designed to work with the text collection databases supported by LLMWare:

        SQL DBs     ---     Postgres and SQLIte
        NoSQL DB    ---     Mongo DB

    Even though Mongo does not require a schema for inserting and retrieving information, the CustomTable method
    will expect a defined schema to be provided (good best practice, in any case).  """

from llmware.resources import CustomTable


def building_custom_table_from_csv(config_option=2):

    #   point fp and fn at the file_path of the CSV file
    fp = "/path/csv/file"

    #   note: this example uses the "customer_table.csv" example file found in the examples repository
    #   -- if substituting for your own csv, please also adjust the sample query below
    fn = "customer_table.csv"

    #   first analyze the csv and confirm that the rows and columns are consistently being extracted
    analysis = CustomTable().validate_csv(fp ,fn ,delimiter=',' ,encoding='utf-8-sig')

    print("\nAnalysis of the CSV file")
    for key, value in analysis.items():
        print(f"analysis: {key} - {value}")

    if not (1 <= config_option <= 5):
        print("\nsetting config to default == 1")
        config_option = 1

    table_name = "customer_table_1000"
    db_name = "sqlite"
    output = None

    #   loading a csv into a database has three main steps
    #   1.  construct CustomTable object
    #   2.  load_csv - *** where most of the configuration will occur ***
    #   3.  insert_rows

    ct = CustomTable(db=db_name,table_name=table_name)

    if config_option == 1:

        #   load_csv - Option #1 - this is the simplest case
        #   -- will view the first row as a "header row" and use to derive the column names for the schema
        #   -- will use the first row after the header_row as a 'test row' and apply a simple mechanical test to
        #      infer the data type for each column as either 'text' | 'integer' | 'float'

        output = ct.load_csv(fp ,fn)

    elif config_option == 2:

        #   load_csv - Option #2 -  pass a set of column names and use as the basis for the schema
        #   -- assumption is that the list of column names will be the same length as the # of columns
        #   -- if there is a header row, it will be skipped.
        #   -- If no header_row and data starts at row 0, then set header_row = False
        #   -- will use the first row after the header row to try to infer the data type automatically

        #   note: if using the query example below, change "customer_name" key to "CUST_NAME"

        cols = ["CUST_NAME", "ACCT_NUM", "LEVEL", "VIP","SPEND","UNAME"]
        output = ct.load_csv(fp, fn, column_names=cols, header_row=True)

    elif config_option == 3:

        #   load_csv - Option #3 - pass a specific mapping of column names and column indices
        #   in this case, the schema will be passed on the col names in the col_mapping - and can be a
        #   subset of the total number of columns
        #   the ordinal indices are 0th-indexed, and correspond to the column numbers that should be pulled

        #   note: if using the query example below, change "customer_name" key to "CUST_NAME"

        col_mapping = {"CUST_NAME": 0, "customer_number" :1, "spend": 4}
        output = ct.load_csv(fp, fn, column_mapping_dict=col_mapping)

    elif config_option == 4:

        #   load_csv - Option #4 - pass an explicit data type mapping, for all or some columns,
        #   which will 'over-ride' the estimation

        dt_mapping = {1: "decimal", 4: "text"}
        output = ct.load_csv(fp, fn, data_type_map=dt_mapping)

    elif config_option == 5:

        #   load_csv - Option #5 - adjust encoding and delimiter

        #   note: this option is not intended for use with the customer_table.csv example, but can be used for
        #   csv that are tab separated, or have different encoding expectations

        output = ct.load_csv(fp, fn, encoding="latin-1", delimiter="\t")

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
    if config_option == 2 or config_option == 3:
        customer_key = "CUST_NAME"
    else:
        customer_key = "customer_name"

    customer = ct.lookup(customer_key, "Martha Williams")
    print("\nLookup from DB")
    print(f"customer_record: ", customer)

    return 0


if __name__ == "__main__":

    # to see how different config options operate, then change the config_option between 1-5

    building_custom_table_from_csv(config_option=2)
