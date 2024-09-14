
import sqlite3
import json
import os
import coloring
import constants


class DB:
    """database class to act as a kind of API wrapper."""

    def __init__(self, filename="untitled") -> None:
        self.filename = os.path.join(constants.DB_DIR, filename)
        if not filename.endswith(".db"):
            self.filename += ".db"

        self.connect()

    def connect(self):
        """connect to the database."""
        if not os.path.exists(self.filename):
            open(self.filename, "w").close()  # create the file if it doesn't exist
        self.connection = sqlite3.connect(self.filename)
        self.cursor = self.connection.cursor()

    def close(self):
        """close the connection to the database."""
        self.connection.close()

    def create_table(self, table_name, columns):
        """create a table in the database."""
        self.connect()
        self.cursor.execute(f"CREATE TABLE {table_name} ({columns})")
        self.connection.commit()

    def insert(self, table_name, values):
        """insert values into a table in the database."""
        self.connect()
        self.cursor.execute(f"INSERT INTO {table_name} VALUES ({values})")
        self.connection.commit()

    def select(self, table_name, columns, condition=None):
        """select values from a table in the database."""
        self.connect()
        if condition:
            self.cursor.execute(f"SELECT {columns} FROM {table_name} WHERE {condition}")
        else:
            self.cursor.execute(f"SELECT {columns} FROM {table_name}")
        rows = self.cursor.fetchall()
        return rows

    def update(self, table_name, columns, condition):
        """update values in a table in the database."""
        self.connect()
        self.cursor.execute(f"UPDATE {table_name} SET {columns} WHERE {condition}")
        self.connection.commit()

    def delete(self, table_name, condition):
        """delete values from a table in the database."""
        self.connect()
        self.cursor.execute(f"DELETE FROM {table_name} WHERE {condition}")
        self.connection.commit()

    def drop_table(self, table_name):
        """drop a table from the database."""
        self.connect()
        self.cursor.execute(f"DROP TABLE {table_name}")
        self.connection.commit()

    def execute(self, query):
        """execute a query in the database."""
        self.connect()
        self.cursor.execute(query)
        self.connection.commit()

    def execute_many(self, query, values):
        """execute a query with multiple values in the database."""
        self.connect()
        self.cursor.executemany(query, values)
        self.connection.commit()

    def add_foreign_key(self, table, column, ref_table, ref_column):
        """
        Since SQLite does not support adding foreign key constraints to an existing table, we need to create a new table
        with the foreign key constraint and copy the data from the old table to the new table. Here's how you can do it
        in Python using the sqlite3 module:
            - Disable foreign key checks temporarily
            - Start a transaction
            - Get the existing table schema
            - Create a new table with the foreign key constraint
            - Copy data from the old table to the new table in batches
            - Drop the old table
            - Rename the new table to the original table name
            - Commit the transaction
            - Enable foreign key checks
        """

        # Disable foreign key checks temporarily
        self.cursor.execute("PRAGMA foreign_keys = OFF")

        # Start a transaction
        self.connection.execute("BEGIN TRANSACTION")

        # Get the existing table schema
        self.cursor.execute(f"PRAGMA table_info({table})")
        columns = self.cursor.fetchall()

        # Create a new table with the foreign key constraint
        new_table_columns = []
        for col in columns:
            new_table_columns.append(f"{col[1]} {col[2]}")
        new_table_columns.append(f"FOREIGN KEY ({column}) REFERENCES {ref_table} ({ref_column})")
        new_table_columns_str = ", ".join(new_table_columns)

        self.cursor.execute(f"CREATE TABLE {table}_new ({new_table_columns_str})")

        # Copy data from the old table to the new table in batches
        column_names = [col[1] for col in columns]
        column_names_str = ", ".join(column_names)

        self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
        total_rows = self.cursor.fetchone()[0]
        batch_size = 5  # Adjust batch size as needed

        for offset in range(0, total_rows, batch_size):
            self.cursor.execute(f"INSERT INTO {table}_new ({column_names_str}) SELECT {column_names_str} FROM {table} LIMIT {batch_size} OFFSET {offset}")

        # Drop the old table
        self.cursor.execute(f"DROP TABLE {table}")

        # Rename the new table to the original table name
        self.cursor.execute(f"ALTER TABLE {table}_new RENAME TO {table}")

        # Commit the transaction
        self.connection.execute("COMMIT")

        # Re-enable foreign key checks
        self.cursor.execute("PRAGMA foreign_keys = ON")

class PaperDB(DB):

    def __init__(self, filename="untitled") -> None:
        super().__init__(filename)

    def create_db(self):
        """
        This uses the db-config.json file to create the database.
        It uses the tables key to create the tables and the relations key to
        make relations between tables using the id columns.
        Assumes id columns for each table without specifying in the
        db-config.json file.
        """

        # load the db-config.json file as dict.
        db_conf: dict = json.load(open(os.path.join(constants.CONF_DIR, "db-config.json")))

        # create tables as specified.
        for table in db_conf["tables"]:
            t = db_conf["tables"][table]
            cols = ", ".join([f"{col} {t[col]}" for col in t])
            self.create_table(table, cols)

        # create relations as specified.
        for relation in db_conf["relations"]:
            rs = db_conf["relations"][relation]
            for r in rs:
                self.add_foreign_key(r["table"], r["column"], r["ref_table"], r["ref_column"])
