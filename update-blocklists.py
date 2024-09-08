import json
import mysql.connector
import sys
from datetime import datetime

# MySQL connection details
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = ""
DB_NAME = "blockfilters"

# Function to connect to MySQL
def connect_to_db():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

# Function to insert filter data into the database
def insert_filter(cursor, name, action, date_created, filter_type, info):
    # Check if the filter already exists
    cursor.execute("SELECT id FROM filters WHERE name = %s", (name,))
    result = cursor.fetchone()
    if result:
        print(f"Filter '{name}' already exists. Skipping.")
        return

    # Insert new filter
    cursor.execute("""
        INSERT INTO filters (name, action, date_created, type, info) 
        VALUES (%s, %s, %s, %s, %s)
    """, (name, action, date_created, filter_type, info))
    print(f"Inserted filter: {name}")

# Function to parse the reason field
def parse_reason(reason):
    try:
        # Split the reason into components
        parts = reason.split('|')
        action = parts[0].strip('{}')  # {sban} or {skick}
        date_created = datetime.strptime(parts[1], "%m%d%Y").date()  # Date in MMDDYYYY format
        filter_type = parts[2]
        info = parts[3] if len(parts) > 3 else None
        return action, date_created, filter_type, info
    except Exception as e:
        print(f"Error parsing reason: {reason} -> {e}")
        return None, None, None, None

# Function to parse the JSON file
def parse_json_file(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
        return data['filters']

# Main function to process the filters and store in the database
def process_filters(filename):
    filters = parse_json_file(filename)

    # Connect to the database
    db = connect_to_db()
    cursor = db.cursor()

    for filter_entry in filters:
        name = filter_entry['name']
        reason = filter_entry['reason']
        
        action, date_created, filter_type, info = parse_reason(reason)
        if action and date_created and filter_type:
            insert_filter(cursor, name, action, date_created, filter_type, info)

    # Commit and close the connection
    db.commit()
    cursor.close()
    db.close()

# Main script entry
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 filter_importer.py <json_filename>")
        sys.exit(1)

    filename = sys.argv[1]
    process_filters(filename)