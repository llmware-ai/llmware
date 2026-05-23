""" Test for DuckDB integration in llmware"""
from llmware.duckdb_integration import DuckDBIntegration

def test_duckdb_integration():
    # Initialize DuckDB in memory
    db = DuckDBIntegration()

    # Create a table
    db.create_table('test_table', 'id INTEGER, name TEXT')

    # Insert data
    data = [
        (1, 'Alice'),
        (2, 'Bob'),
        (3, 'Charlie')
    ]
    db.insert_data('test_table', data)

    # Query the data
    results = db.query('SELECT * FROM test_table;')

    # Validate the results
    assert len(results) == 3
    assert results[0] == (1, 'Alice')
    assert results[1] == (2, 'Bob')
    assert results[2] == (3, 'Charlie')

    # Close the connection
    db.close()
