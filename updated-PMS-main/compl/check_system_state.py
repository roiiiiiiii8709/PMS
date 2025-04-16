from db import get_db_connection

def check_system_state():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    print("===== CURRENT SYSTEM STATE =====")
    
    # Check all parking spots
    cursor.execute("SELECT * FROM parking_spots ORDER BY spot_id")
    spots = cursor.fetchall()
    
    print(f"\n----- PARKING SPOTS ({len(spots)}) -----")
    for spot in spots:
        print(f"ID: {spot['spot_id']}, Location: {spot['location']}, Status: '{spot['status']}', Price: {spot['price_per_hour']}")
    
    # Check all bookings
    cursor.execute("""
        SELECT b.*, u.username, p.location 
        FROM bookings b
        JOIN users u ON b.user_id = u.user_id
        JOIN parking_spots p ON b.spot_id = p.spot_id
        ORDER BY b.booking_id
    """)
    bookings = cursor.fetchall()
    
    print(f"\n----- BOOKINGS ({len(bookings)}) -----")
    for booking in bookings:
        print(f"ID: {booking['booking_id']}, User: {booking['username']}, " +
              f"Spot: {booking['location']} (ID: {booking['spot_id']}), " +
              f"Status: '{booking['status']}', Payment: '{booking['payment_status']}'")
    
    # Count bookings by status
    cursor.execute("SELECT status, COUNT(*) as count FROM bookings GROUP BY status")
    status_counts = cursor.fetchall()
    
    print("\n----- BOOKING STATUS COUNTS -----")
    for status in status_counts:
        print(f"Status '{status['status']}': {status['count']} bookings")
    
    # Get occupied spots that should be available
    cursor.execute("""
        SELECT p.* 
        FROM parking_spots p
        LEFT JOIN bookings b ON p.spot_id = b.spot_id AND b.status IN ('confirmed', 'entry', 'pending')
        WHERE p.status != 'available' AND b.booking_id IS NULL
    """)
    incorrect_spots = cursor.fetchall()
    
    print("\n----- SPOTS WITH INCORRECT STATUS -----")
    if incorrect_spots:
        for spot in incorrect_spots:
            print(f"Spot ID: {spot['spot_id']}, Location: {spot['location']}, " +
                  f"Current Status: '{spot['status']}', Should be: 'available'")
    else:
        print("No spots with incorrect status found")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    check_system_state()
