from db import get_db_connection

def fix_booking_status():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Update bookings with blank status to 'pending'
    cursor.execute("""
        UPDATE bookings 
        SET status = 'pending', payment_status = 'unpaid' 
        WHERE status IS NULL OR status = ''
    """)
    
    rows_updated = cursor.rowcount
    conn.commit()
    
    print(f"Updated {rows_updated} bookings to 'pending' status")
    
    # Check bookings with pending status now
    cursor.execute("SELECT * FROM bookings WHERE status = 'pending'")
    pending_bookings = cursor.fetchall()
    
    print(f"\nPending bookings (after update): {len(pending_bookings)}")
    for booking in pending_bookings:
        print(f"ID: {booking['booking_id']}, User: {booking['user_id']}, Status: {booking['status']}, Payment: {booking['payment_status']}")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    fix_booking_status()
