from db import get_db_connection
from datetime import datetime

def check_expired_spots():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get current time
    now = datetime.now()
    print(f"Current time: {now}")
    
    # Check Spot ID 2
    cursor.execute("SELECT * FROM parking_spots WHERE spot_id = 2")
    spot = cursor.fetchone()
    print(f"Spot ID 2: {spot}")
    
    # Check associated bookings
    cursor.execute("""
        SELECT * FROM bookings 
        WHERE spot_id = 2 
        ORDER BY end_time DESC
    """)
    bookings = cursor.fetchall()
    print(f"Associated bookings (all): {len(bookings)}")
    
    for i, booking in enumerate(bookings):
        print(f"Booking {i+1}: ID={booking.get('booking_id')}, " +
              f"Status={booking.get('status')}, " +
              f"Start={booking.get('start_time')}, " +
              f"End={booking.get('end_time')}")
    
    # Check expired bookings that might still be marked as active
    cursor.execute("""
        SELECT * FROM bookings 
        WHERE end_time < %s 
        AND status IN ('confirmed', 'entry', 'occupied')
        ORDER BY end_time DESC
    """, (now,))
    
    expired_bookings = cursor.fetchall()
    print(f"\nExpired but still active bookings: {len(expired_bookings)}")
    
    for i, booking in enumerate(expired_bookings):
        print(f"Expired Booking {i+1}: ID={booking.get('booking_id')}, " +
              f"Spot ID={booking.get('spot_id')}, " +
              f"Status={booking.get('status')}, " +
              f"End Time={booking.get('end_time')}")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    check_expired_spots()
