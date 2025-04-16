from db import get_db_connection

def fix_system_state():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    print("===== FIXING SYSTEM STATE =====")
    
    # 1. Fix parking spots with blank status
    cursor.execute("UPDATE parking_spots SET status = 'available' WHERE status IS NULL OR status = ''")
    updated_spots = cursor.rowcount
    conn.commit()
    print(f"Fixed {updated_spots} parking spots by setting status to 'available'")
    
    # 2. Fix bookings with blank status
    cursor.execute("UPDATE bookings SET status = 'pending', payment_status = 'unpaid' WHERE status IS NULL OR status = ''")
    updated_bookings = cursor.rowcount
    conn.commit()
    print(f"Fixed {updated_bookings} bookings by setting status to 'pending'")

    # 3. Update spot status for spots that have pending or confirmed bookings
    cursor.execute("""
        UPDATE parking_spots p
        JOIN bookings b ON p.spot_id = b.spot_id
        SET p.status = 'reserved'
        WHERE b.status IN ('pending', 'confirmed')
    """)
    reserved_spots = cursor.rowcount
    conn.commit()
    print(f"Set {reserved_spots} spots to 'reserved' status based on their bookings")
    
    # Check updated state
    print("\n===== UPDATED SYSTEM STATE =====")
    
    # Check all parking spots
    cursor.execute("SELECT * FROM parking_spots ORDER BY spot_id")
    spots = cursor.fetchall()
    
    print(f"\n----- PARKING SPOTS ({len(spots)}) -----")
    for spot in spots:
        print(f"ID: {spot['spot_id']}, Location: {spot['location']}, Status: '{spot['status']}'")
    
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
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    fix_system_state()
