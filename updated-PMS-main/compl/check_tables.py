from db import get_db_connection

def check_users_table():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get table structure
    cursor.execute("DESCRIBE users")
    columns = cursor.fetchall()
    
    print("Users table structure:")
    for col in columns:
        print(f"Column: {col['Field']}, Type: {col['Type']}, Null: {col['Null']}, Key: {col['Key']}")
    
    # Get sample user
    cursor.execute("SELECT * FROM users LIMIT 1")
    user = cursor.fetchone()
    
    if user:
        print("\nSample user:")
        for key, value in user.items():
            print(f"{key}: {value}")
    else:
        print("\nNo users found in the database.")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    check_users_table()
