import sqlite3

def create_connection():
    conn = sqlite3.connect('contacts.db')
    return conn




def create_tables():
    conn = create_connection()
    cursor = conn.cursor()
    # name, gender, phone, email, password
    user_table = """CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(100) NOT NULL,
        gender VARCHAR(7) CHECK(gender IN ("male", "female", "other")),
        phone VARCHAR(15) NOT NULL,
        email VARCHAR(100) NOT NULL UNIQUE,
        password VARCHAR(100) NOT NULL
    )"""
    cursor.execute(user_table)

    # contact_name, contact_phone, contact_email, contact_address, contact_gender, contact_favorite, user_id
    contact_table = """CREATE TABLE IF NOT EXISTS contacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        contact_name VARCHAR(100) NOT NULL,
        contact_phone VARCHAR(15) NOT NULL,
        contact_email VARCHAR(100) NOT NULL,
        contact_address VARCHAR(100),
        contact_gender VARCHAR(7) CHECK(contact_gender IN ("male", "female", "other")),
        contact_favorite INTEGER DEFAULT 0,
        user_id INTEGER NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
    )"""
    cursor.execute(contact_table)
    conn.commit()
    conn.close()




def view_table():
    conn = create_connection()
    cursor = conn.cursor()

    print("📄 Users Table Structure:")
    cursor.execute("PRAGMA table_info(users)")
    users_columns = cursor.fetchall()
    for col in users_columns:
        print(col)

    print("\n📄 Contacts Table Structure:")
    cursor.execute("PRAGMA table_info(contacts)")
    contacts_columns = cursor.fetchall()
    for col in contacts_columns:
        print(col)

    conn.close()





def view_data():
    conn = create_connection()
    cursor = conn.cursor()
    
    # View Users Data
    cursor.execute("SELECT * FROM users")
    users_data = cursor.fetchall()
    print("\n📄 Users Data:")
    for user in users_data:
        print(user)

    # View Contacts Data
    cursor.execute("SELECT * FROM contacts")
    contacts_data = cursor.fetchall()
    print("\n📄 Contacts Data:")
    for contact in contacts_data:
        print(contact)

    conn.close()




def modify_table():
    conn = create_connection()
    cursor = conn.cursor()

    # # Add 'createdAt' and 'updatedAt' columns without default value
    # cursor.execute("""
    #     ALTER TABLE users ADD COLUMN createdAt DATE;
    # """)

    # cursor.execute("""
    #     ALTER TABLE users ADD COLUMN updatedAt DATE;
    # """)

    # # Manually set the 'createdAt' and 'updatedAt' for existing records
    # cursor.execute("""
    #     UPDATE users SET createdAt = CURRENT_DATE, updatedAt = CURRENT_DATE;
    # """)

    cursor.execute("""
        ALTER TABLE contacts ADD COLUMN createdAt DATE;
    """)

    cursor.execute("""
        ALTER TABLE contacts ADD COLUMN updatedAt DATE;
    """)

    cursor.execute("""
        UPDATE contacts SET createdAt = CURRENT_DATE, updatedAt = CURRENT_DATE;
    """)

    conn.commit()
    conn.close()





def delete_all_data(table_name):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(f"DELETE FROM {table_name}")
        conn.commit()
        print(f"All data in {table_name} table deleted successfully.")
    except sqlite3.OperationalError as e:
        print(f"Error: {e}")
    finally:
        conn.close()




if __name__ == "__main__":
    view_data()