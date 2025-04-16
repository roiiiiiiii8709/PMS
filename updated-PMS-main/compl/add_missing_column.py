"""
Add Missing Amount Column

This script adds the missing 'amount' column to the bookings table.
"""
import mysql.connector
from db import get_db_connection

def add_amount_column():
    conn = get_db_connection()
    if not conn:
        print("Error: Could not connect to database")
        return False
    
    cursor = conn.cursor()
    
    try:
        # Check if the amount column already exists
        cursor.execute("SHOW COLUMNS FROM bookings LIKE 'amount'")
        if cursor.fetchone():
            print("The 'amount' column already exists in the bookings table.")
        else:
            # Add the amount column to the bookings table
            cursor.execute("""
                ALTER TABLE bookings 
                ADD COLUMN amount DECIMAL(10, 2) DEFAULT 0.00
            """)
            conn.commit()
            print("Successfully added 'amount' column to the bookings table!")
            
        # Verify all the columns in the bookings table
        cursor.execute("DESCRIBE bookings")
        columns = cursor.fetchall()
        print("\nCurrent columns in the bookings table:")
        for column in columns:
            print(f"- {column[0]}: {column[1]}")
        
        # Also, let's fix any existing bookings that might have null amounts
        cursor.execute("""
            UPDATE bookings 
            SET amount = 0.00 
            WHERE amount IS NULL
        """)
        rows_updated = cursor.rowcount
        conn.commit()
        if rows_updated > 0:
            print(f"\nUpdated {rows_updated} bookings with default amount value.")
        
        return True
        
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return False
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("Adding missing 'amount' column to bookings table...\n")
    success = add_amount_column()
    
    if success:
        print("\nOperation completed successfully!")
        print("You should now be able to create bookings without errors.")
    else:
        print("\nOperation failed. Please check the error messages above.")
