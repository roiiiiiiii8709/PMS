"""
Create a test pending booking to make the Accept/Decline buttons appear
"""
from db import get_db_connection
from datetime import datetime, timedelta

def create_test_pending_booking():
    """Create a test pending booking with status exactly 'pending'"""
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to database")
        return False
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Find an active user
        cursor.execute("SELECT user_id FROM users LIMIT 1")
        user_result = cursor.fetchone()
        
        if not user_result:
            print("No users found in the database")
            return False
        
        user_id = user_result['user_id']
        
        # Find an available spot
        cursor.execute("SELECT spot_id FROM parking_spots WHERE status = 'available' LIMIT 1")
        spot_result = cursor.fetchone()
        
        if not spot_result:
            print("No available parking spots found")
            return False
        
        spot_id = spot_result['spot_id']
        
        # Calculate start and end times (starting tomorrow)
        start_time = datetime.now() + timedelta(days=1)
        start_time = start_time.replace(hour=10, minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(hours=3)
        
        # Insert the booking with status exactly 'pending'
        cursor.execute("""
            INSERT INTO bookings (user_id, spot_id, start_time, end_time, status, payment_status, amount)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (user_id, spot_id, start_time, end_time, 'pending', 'unpaid', 50.00))
        
        booking_id = cursor.lastrowid
        
        # Update the spot status to reflect the booking
        cursor.execute("UPDATE parking_spots SET status = 'reserved' WHERE spot_id = %s", (spot_id,))
        
        conn.commit()
        print(f"Created test pending booking (ID: {booking_id}) for user {user_id} and spot {spot_id}")
        print(f"Booking time: {start_time.strftime('%Y-%m-%d %H:%M')} to {end_time.strftime('%Y-%m-%d %H:%M')}")
        print("The Accept/Decline buttons should now appear in the staff dashboard")
        
        return True
    
    except Exception as e:
        conn.rollback()
        print(f"Error creating test booking: {str(e)}")
        return False
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("Creating a test pending booking...\n")
    create_test_pending_booking()
    print("\nDone! Restart your Flask application to see the Accept/Decline buttons in the staff dashboard.")
