from db import get_db_connection

def check_all_bookings():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get all bookings with details
    cursor.execute("""
        SELECT b.*, u.username, p.location
        FROM bookings b
        JOIN users u ON b.user_id = u.user_id
        JOIN parking_spots p ON b.spot_id = p.spot_id
        ORDER BY b.booking_id
    """)
    bookings = cursor.fetchall()
    
    print(f"Total bookings: {len(bookings)}")
    for booking in bookings:
        print(f"ID: {booking['booking_id']}, User: {booking['username']}, " +
              f"Start: {booking['start_time']}, End: {booking['end_time']}, " +
              f"Status: '{booking['status']}', Payment: '{booking['payment_status']}', " +
              f"Spot: {booking['location']}")
    
    # Count pending bookings
    cursor.execute("SELECT COUNT(*) as count FROM bookings WHERE status = 'pending'")
    pending_count = cursor.fetchone()['count']
    print(f"\nPending bookings count: {pending_count}")
    
    # Check what the dashboard query retrieves
    cursor.execute("""
        SELECT b.*, u.username, p.location
        FROM bookings b
        JOIN users u ON b.user_id = u.user_id
        JOIN parking_spots p ON b.spot_id = p.spot_id
        WHERE b.status = 'pending'
    """)
    pending_bookings = cursor.fetchall()
    print(f"\nBookings with pending status that would appear on dashboard: {len(pending_bookings)}")
    for booking in pending_bookings:
        print(f"ID: {booking['booking_id']}, User: {booking['username']}")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    check_all_bookings()
