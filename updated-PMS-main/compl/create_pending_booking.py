from db import get_db_connection
import datetime
import random

def create_pending_booking():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # First, get a user from the users table
    cursor.execute("SELECT * FROM users LIMIT 1")
    user = cursor.fetchone()
    
    if not user:
        print("No users found. Please create a user first.")
        cursor.close()
        conn.close()
        return
    
    # Get an available parking spot
    cursor.execute("SELECT * FROM parking_spots WHERE status = 'available' LIMIT 1")
    spot = cursor.fetchone()
    
    if not spot:
        print("No available parking spots. Please create spots first.")
        cursor.close()
        conn.close()
        return
    
    # Calculate start and end times
    now = datetime.datetime.now()
    start_time = now + datetime.timedelta(hours=1)  # Starting in 1 hour
    end_time = start_time + datetime.timedelta(hours=3)  # 3 hour booking
    
    # Calculate amount
    amount = spot['price_per_hour'] * 3  # 3 hours
    
    # Create the pending booking
    try:
        cursor.execute("""
            INSERT INTO bookings 
            (user_id, spot_id, vehicle_number, start_time, end_time, status, payment_status, amount) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            user['user_id'], 
            spot['spot_id'], 
            'TEST-123', 
            start_time, 
            end_time, 
            'pending',  # Important: This is set to 'pending'
            'unpaid',
            amount
        ))
        conn.commit()
        booking_id = cursor.lastrowid
        print(f"Success! Created pending booking with ID: {booking_id}")
        print(f"User: {user['username']}, Vehicle: TEST-123")
        print(f"Start: {start_time}, End: {end_time}")
        print(f"Amount: Rs.{amount}, Status: pending, Payment: unpaid")
        print(f"Parking Spot: {spot['location']} (ID: {spot['spot_id']})")
    except Exception as e:
        print(f"Error creating booking: {str(e)}")
    
    # Check that we now have pending bookings
    cursor.execute("SELECT COUNT(*) as count FROM bookings WHERE status = 'pending'")
    count = cursor.fetchone()['count']
    print(f"\nTotal pending bookings in system: {count}")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    create_pending_booking()
