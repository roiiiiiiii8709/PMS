from db import get_db_connection

def check_admin_table():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Check if admin table exists
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = DATABASE() 
        AND table_name = 'admins'
    """)
    
    admin_table_exists = cursor.fetchone() is not None
    print(f"Admin table exists: {admin_table_exists}")
    
    if admin_table_exists:
        # Check if there are any admin users
        cursor.execute("SELECT * FROM admins")
        admins = cursor.fetchall()
        
        if admins:
            print(f"\nFound {len(admins)} admin accounts:")
            for admin in admins:
                print(f"  - ID: {admin['admin_id']}, Username: {admin['username']}")
        else:
            print("\nNo admin accounts found in the database.")
            
            # Create a default admin account
            print("\nCreating a default admin account...")
            try:
                cursor.execute("""
                    INSERT INTO admins (username, password, email)
                    VALUES ('admin', 'admin123', 'admin@example.com')
                """)
                conn.commit()
                print("Default admin account created successfully!")
                print("Username: admin")
                print("Password: admin123")
            except Exception as e:
                print(f"Error creating admin account: {str(e)}")
    else:
        # Create the admins table
        print("\nCreating admins table...")
        try:
            cursor.execute("""
                CREATE TABLE admins (
                    admin_id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) NOT NULL UNIQUE,
                    password VARCHAR(255) NOT NULL,
                    email VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            print("Admins table created successfully!")
            
            # Create a default admin account
            print("\nCreating a default admin account...")
            cursor.execute("""
                INSERT INTO admins (username, password, email)
                VALUES ('admin', 'admin123', 'admin@example.com')
            """)
            conn.commit()
            print("Default admin account created successfully!")
            print("Username: admin")
            print("Password: admin123")
        except Exception as e:
            print(f"Error creating admin table: {str(e)}")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    check_admin_table()
