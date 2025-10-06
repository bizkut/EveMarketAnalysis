import sqlite3

def inspect_database():
    """
    Connects to the SQLite database and prints the contents of the 'items' table.
    """
    try:
        conn = sqlite3.connect('/tmp/test.db')
        cursor = conn.cursor()

        print("Schema for 'items' table:")
        cursor.execute("PRAGMA table_info(items)")
        print(cursor.fetchall())

        print("\nContents of 'items' table:")
        cursor.execute("SELECT * FROM items")
        rows = cursor.fetchall()
        for row in rows:
            print(row)

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    inspect_database()