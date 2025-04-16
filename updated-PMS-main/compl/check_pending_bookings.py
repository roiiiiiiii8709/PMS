from db import get_db_connection

def check_pending_bookings():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Check bookings with pending status
    cursor.execute("SELECT * FROM bookings WHERE status = 'pending'")
    pending_bookings = cursor.fetchall()
    
    print(f"Total pending bookings: {len(pending_bookings)}")
    for booking in pending_bookings:
        print(f"ID: {booking['booking_id']}, Status: {booking['status']}, Payment Status: {booking['payment_status']}")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    check_pending_bookings()
