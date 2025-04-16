from db import get_db_connection

def add_amount_column():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if amount column already exists
        cursor.execute("SHOW COLUMNS FROM bookings LIKE 'amount'")
        column_exists = cursor.fetchone()
        
        if not column_exists:
            # Add amount column to bookings table
            cursor.execute("ALTER TABLE bookings ADD COLUMN amount DECIMAL(10, 2) NULL")
            conn.commit()
            print("Successfully added 'amount' column to bookings table.")
        else:
            print("The 'amount' column already exists in the bookings table.")
            
    except Exception as e:
        conn.rollback()
        print(f"Error adding amount column: {str(e)}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    add_amount_column()
