from llmware.duckdb_integration import DuckDBIntegration

def main():
    # Initialize DuckDB
    db = DuckDBIntegration(db_path='example.duckdb')

    # Create a table for documents
    db.create_table('documents', 'id INTEGER, content TEXT')

    # Insert example data
    documents = [
        (1, 'DuckDB is an in-process SQL OLAP database management system.'),
        (2, 'It is designed for analytical workloads and supports vectorized execution.'),
        (3, 'DuckDB recently added support for similarity search using vectors.')
    ]
    db.insert_data('documents', documents)

    # Query the table
    results = db.query('SELECT * FROM documents;')
    print('Documents in the database:')
    for row in results:
        print(row)

    # Close the connection
    db.close()

if __name__ == '__main__':
    main()
