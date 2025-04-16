from db import get_db_connection
import datetime
import random

def create_test_booking():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # First, get a user
    cursor.execute("SELECT user_id FROM users WHERE role = 'user' LIMIT 1")
    user = cursor.fetchone()
    
    if not user:
        print("No users found. Creating a test user...")
        cursor.execute("""
            INSERT INTO users (username, password, email, phone, role)
            VALUES ('testuser', 'password', 'test@example.com', '1234567890', 'user')
        """)
        conn.commit()
        user_id = cursor.lastrowid
    else:
        user_id = user['user_id']
    
    # Get an available parking spot
    cursor.execute("SELECT spot_id, price_per_hour FROM parking_spots WHERE status = 'available' LIMIT 1")
    spot = cursor.fetchone()
    
    if not spot:
        print("No available parking spots. Please create spots first.")
        cursor.close()
        conn.close()
        return
    
    spot_id = spot['spot_id']
    price_per_hour = spot['price_per_hour']
    
    # Calculate start and end times
    now = datetime.datetime.now()
    start_time = now
    # Random duration between 1 and 5 hours
    duration_hours = random.randint(1, 5)
    end_time = now + datetime.timedelta(hours=duration_hours)
    
    # Calculate amount
    amount = price_per_hour * duration_hours
    
    # Create the booking
    try:
        cursor.execute("""
            INSERT INTO bookings 
            (user_id, spot_id, vehicle_number, start_time, end_time, status, payment_status, amount) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            user_id, 
            spot_id, 
            'TEST-123', 
            start_time, 
            end_time, 
            'pending',
            'unpaid',
            amount
        ))
        conn.commit()
        booking_id = cursor.lastrowid
        print(f"Successfully created test booking with ID: {booking_id}")
        print(f"Status: pending, Payment Status: unpaid")
        print(f"Duration: {duration_hours} hours, Amount: Rs.{amount}")
    except Exception as e:
        print(f"Error creating booking: {str(e)}")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    create_test_booking()
