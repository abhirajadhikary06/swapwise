import sqlite3

# Connect to the database
connection = sqlite3.connect('skill_swap.db')

# Open and read the schema.sql file
with open('schema.sql') as f:
    connection.executescript(f.read())

# Commit the changes and close the connection
connection.commit()
connection.close()

print("Database has been initialized successfully.")