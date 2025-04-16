from db import get_db_connection

def fix_new_bookings():
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
    
    # Check all bookings now
    cursor.execute("""
        SELECT b.*, u.username, p.location
        FROM bookings b
        JOIN users u ON b.user_id = u.user_id
        JOIN parking_spots p ON b.spot_id = p.spot_id
        ORDER BY b.booking_id
    """)
    bookings = cursor.fetchall()
    
    print(f"\nCurrent bookings status:")
    for booking in bookings:
        print(f"ID: {booking['booking_id']}, User: {booking['username']}, " +
              f"Status: '{booking['status']}', Payment: '{booking['payment_status']}'")
    
    # Count pending bookings
    cursor.execute("SELECT COUNT(*) as count FROM bookings WHERE status = 'pending'")
    pending_count = cursor.fetchone()['count']
    print(f"\nPending bookings count: {pending_count}")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    fix_new_bookings()
