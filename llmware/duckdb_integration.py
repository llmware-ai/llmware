import duckdb

class DuckDBIntegration:
    def __init__(self, db_path: str = ':memory:'):
        """Initialize the DuckDB connection.

        Args:
            db_path (str): Path to the DuckDB database file. Defaults to in-memory.
        """
        self.connection = duckdb.connect(database=db_path, read_only=False)

    def create_table(self, table_name: str, schema: str):
        """Create a table in the DuckDB database.

        Args:
            table_name (str): Name of the table to create.
            schema (str): Schema definition for the table.
        """
        self.connection.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({schema});")

    def insert_data(self, table_name: str, data: list):
        """Insert data into a DuckDB table.

        Args:
            table_name (str): Name of the table to insert data into.
            data (list): List of tuples representing rows to insert.
        """
        placeholders = ', '.join(['?'] * len(data[0]))
        self.connection.executemany(f"INSERT INTO {table_name} VALUES ({placeholders});", data)

    def query(self, sql: str):
        """Execute a query on the DuckDB database.

        Args:
            sql (str): SQL query to execute.

        Returns:
            list: Query results.
        """
        return self.connection.execute(sql).fetchall()

    def close(self):
        """Close the DuckDB connection."""
        self.connection.close()
