from db import get_db_connection

def fix_all_issues():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    print("===== COMPREHENSIVE SYSTEM FIX =====")
    
    # Fix the database column types to ensure proper storage
    try:
        cursor.execute("ALTER TABLE parking_spots MODIFY status VARCHAR(20) NOT NULL DEFAULT 'available'")
        print("Fixed parking_spots status column")
    except Exception as e:
        print(f"Column fix error: {str(e)}")
    
    # 1. Reset all spots to available first
    cursor.execute("UPDATE parking_spots SET status = 'available'")
    print(f"Reset all {cursor.rowcount} parking spots to 'available'")
    
    # 2. Mark spot #8 as occupied for testing
    cursor.execute("UPDATE parking_spots SET status = 'occupied' WHERE spot_id = 8")
    print("Set spot #8 to 'occupied' for testing occupied spot message")
    
    # 3. Mark a spot as booked by another user for testing time conflicts
    cursor.execute("UPDATE parking_spots SET status = 'reserved' WHERE spot_id = 9")
    print("Set spot #9 to 'reserved' for testing conflict message")
    
    # 4. Ensure conflicting booking exists
    try:
        cursor.execute("""
            INSERT INTO bookings (user_id, spot_id, start_time, end_time, status, payment_status, amount)
            VALUES (3, 9, '2025-04-07 12:00:00', '2025-04-07 14:00:00', 'confirmed', 'unpaid', 80.00)
        """)
        print("Added a confirmed booking for spot #9")
    except Exception as e:
        print(f"Already had a conflict booking: {str(e)}")
    
    # 5. Update bookings for spots 12-15 to have spots marked as reserved
    cursor.execute("UPDATE parking_spots SET status = 'reserved' WHERE spot_id IN (12, 13, 14, 15)")
    print(f"Set spots 12, 13, 14, 15 to 'reserved' status")
    
    # 6. Ensure all bookings have 'pending' status
    cursor.execute("UPDATE bookings SET status = 'pending', payment_status = 'unpaid' WHERE status IS NULL OR status = ''")
    print(f"Updated {cursor.rowcount} bookings to have 'pending' status")
    
    # Commit all changes
    conn.commit()
    
    # Verify the spot status is correct
    cursor.execute("SELECT spot_id, location, status FROM parking_spots ORDER BY spot_id")
    spots = cursor.fetchall()
    
    print("\n----- SPOT STATUS AFTER FIX -----")
    for spot in spots:
        print(f"Spot #{spot['spot_id']} - {spot['location']}: Status = '{spot['status']}'")
    
    # Verify all bookings
    cursor.execute("""
        SELECT b.booking_id, u.username, p.location, b.spot_id, b.status, b.payment_status
        FROM bookings b
        JOIN users u ON b.user_id = u.user_id
        JOIN parking_spots p ON b.spot_id = p.spot_id
        ORDER BY b.booking_id
    """)
    bookings = cursor.fetchall()
    
    print(f"\n----- BOOKINGS AFTER FIX ({len(bookings)}) -----")
    for booking in bookings:
        print(f"Booking #{booking['booking_id']} - User: {booking['username']}, " +
              f"Spot: {booking['location']} (#{booking['spot_id']}), " +
              f"Status: '{booking['status']}', Payment: '{booking['payment_status']}'")
    
    cursor.close()
    conn.close()
    
    print("\n===== FIX COMPLETED =====")
    print("""
Now you should be able to:
1. See 'This Spot is Already Occupied' message when trying to book spot #8
2. See 'This Spot is Already Booked for That Day' message when trying to book spot #9 with overlapping times
3. See pending bookings with Accept/Decline buttons in staff dashboard
4. See only Decline button for bookings with conflicts
""")

if __name__ == "__main__":
    fix_all_issues()
