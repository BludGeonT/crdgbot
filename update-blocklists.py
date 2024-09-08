import json
import mysql.connector
import sys
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

    # Log the data before insertion
    print(f"Inserting filter: name={name}, action={action}, date_created={date_created}, type={filter_type}, info={info}")
    
    # Insert new filter
    cursor.execute("""
        INSERT INTO filters (name, action, date_created, type, info) 
        VALUES (%s, %s, %s, %s, %s)
    """, (name, action, date_created, filter_type, info))
    print(f"Inserted filter: {name}")

# Updated Function to parse the reason field, keeping everything as strings
def parse_reason(reason):
    try:
        # Split the reason into components using '|' as the delimiter
        parts = reason.split('|')
        
        # Ensure that the reason contains at least three parts
        if len(parts) < 3:
            print(f"Invalid reason format: {reason}")
            return None, None, None, None

        # Extract action, date (as string), type, and info
        # We will handle action separately to strip the '{}' properly
        action_part = parts[0]
        action = action_part.strip('{}').split()[0]  # Action is either sban or skick, without the date
        
        date_str = action_part.split()[1]  # Date comes right after the action (MMDDYYYY format)
        filter_type = parts[1]  # SPAM, BLANKET, etc.
        info = parts[2] if len(parts) > 2 else None  # Everything after the last "|"

        return action, date_str, filter_type, info
    except Exception as e:
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