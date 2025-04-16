from db import get_db_connection

def check_bookings():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Check all bookings
    cursor.execute("SELECT * FROM bookings ORDER BY booking_id DESC LIMIT 10")
    bookings = cursor.fetchall()
    
    print(f"Total recent bookings: {len(bookings)}")
    for booking in bookings:
        print(f"ID: {booking['booking_id']}, Status: {booking['status']}, Payment: {booking['payment_status']}, Spot: {booking['spot_id']}")
    
    # Fix existing bookings with blank status
    cursor.execute("UPDATE bookings SET status = 'pending', payment_status = 'unpaid' WHERE status = '' OR status IS NULL")
    updated_count = cursor.rowcount
    print(f"\nFixed {updated_count} bookings with blank/null status")
    conn.commit()
    
    # Check specifically for pending bookings
    cursor.execute("SELECT COUNT(*) as count FROM bookings WHERE status = 'pending'")
    pending_count = cursor.fetchone()['count']
    print(f"\nTotal pending bookings after fix: {pending_count}")
    
    if pending_count > 0:
        cursor.execute("SELECT * FROM bookings WHERE status = 'pending'")
        pending_bookings = cursor.fetchall()
        print("\nPending bookings details:")
        for booking in pending_bookings:
            print(f"ID: {booking['booking_id']}, User ID: {booking['user_id']}, Start: {booking['start_time']}")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    check_bookings()
