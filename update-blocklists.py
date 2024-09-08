import json
import mysql.connector
import sys
from datetime import datetime
from getpass import getpass  # For securely asking the password

# Function to connect to MySQL, prompting for username and password
def connect_to_db():
    db_user = input("Enter MySQL username: ")
    db_password = getpass("Enter MySQL password: ")
    return mysql.connector.connect(
        host="localhost",
        user=db_user,
        password=db_password,
        database="blockfilters"
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
        date_str = parts[1]
        filter_type = parts[2]
        info = parts[3] if len(parts) > 3 else None
        
        # Parse the date created (ensure it is a valid date format)
        date_created = datetime.strptime(date_str, "%m%d%Y").date()

        return action, date_created, filter_type, info
    except ValueError as e:
        print(f"Error parsing reason: {reason} -> {e}")
        return None, None, None, None

# Function to parse the JSON file and extract the filters
def parse_json_file(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
        return data['data']['blocklists']['filters']  # Extract only the 'filters' section

# Main function to process the filters and store them in the database
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

    # Commit and close the connections 
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