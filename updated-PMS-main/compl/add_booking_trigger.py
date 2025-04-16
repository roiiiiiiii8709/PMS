from db import get_db_connection

def add_booking_trigger():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create a trigger to ensure status and payment_status are never blank
    try:
        # Drop the trigger if it already exists to avoid errors
        cursor.execute("DROP TRIGGER IF EXISTS before_booking_insert")
        
        # Create the trigger
        cursor.execute("""
            CREATE TRIGGER before_booking_insert
            BEFORE INSERT ON bookings
            FOR EACH ROW
            BEGIN
                IF NEW.status IS NULL OR NEW.status = '' THEN
                    SET NEW.status = 'pending';
                END IF;
                
                IF NEW.payment_status IS NULL OR NEW.payment_status = '' THEN
                    SET NEW.payment_status = 'unpaid';
                END IF;
            END
        """)
        
        conn.commit()
        print("Successfully created booking trigger!")
        print("All new bookings will automatically have 'pending' status if not specified.")
        
    except Exception as e:
        print(f"Error creating trigger: {str(e)}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    add_booking_trigger()
