from db import get_db_connection

def check_bookings_table():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get table structure
    cursor.execute("DESCRIBE bookings")
    columns = cursor.fetchall()
    
    print("Bookings table structure:")
    for col in columns:
        print(f"Column: {col['Field']}, Type: {col['Type']}, Null: {col['Null']}, Key: {col['Key']}")
    
    # Get sample booking if any
    cursor.execute("SELECT * FROM bookings LIMIT 1")
    booking = cursor.fetchone()
    
    if booking:
        print("\nSample booking:")
        for key, value in booking.items():
            print(f"{key}: {value}")
    else:
        print("\nNo bookings found in the database.")
        
    # Check staff table
    print("\nChecking staff table:")
    try:
        cursor.execute("DESCRIBE staff")
        staff_columns = cursor.fetchall()
        print("Staff table structure:")
        for col in staff_columns:
            print(f"Column: {col['Field']}, Type: {col['Type']}, Null: {col['Null']}, Key: {col['Key']}")
            
        # Get sample staff
        cursor.execute("SELECT * FROM staff LIMIT 1")
        staff = cursor.fetchone()
        if staff:
            print("\nSample staff:")
            for key, value in staff.items():
                print(f"{key}: {value}")
        else:
            print("\nNo staff found in the database.")
    except Exception as e:
        print(f"Error checking staff table: {e}")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    check_bookings_table()
