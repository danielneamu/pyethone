import mysql.connector

# Database connection details
HOST = "localhost"
USER = "root"
PASSWORD = "Piedone76!"
DATABASE = "piedone"

try:
    # Connect to the MySQL database
    connection = mysql.connector.connect(
        host=HOST, user=USER, password=PASSWORD, database=DATABASE
    )

    # Create cursor object
    cursor = connection.cursor()

    # Create table (replace data types if needed)
    create_table_query = """
    CREATE TABLE IF NOT EXISTS test (
        name TEXT,
        age INTEGER
    )
    """

    cursor.execute(create_table_query)

    # Print success message
    print("Table 'test' created successfully!")

except mysql.connector.Error as err:
    print(f"Error creating table: {err}")

finally:
    # Close connection
    if connection:
        connection.close()
        print("Connection closed.")