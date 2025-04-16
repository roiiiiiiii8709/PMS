from db import get_db_connection

def force_fix_issues():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("===== FORCING FIXES WITH DIRECT SQL =====")
    
    # 1. First, explicitly update the spots with blank status
    cursor.execute("UPDATE parking_spots SET status = 'reserved' WHERE spot_id = 12")
    cursor.execute("UPDATE parking_spots SET status = 'reserved' WHERE spot_id = 13")
    cursor.execute("UPDATE parking_spots SET status = 'reserved' WHERE spot_id = 14")
    cursor.execute("UPDATE parking_spots SET status = 'reserved' WHERE spot_id = 15")
    conn.commit()
    print("Directly updated spots 12, 13, 14, 15 to 'reserved' status")
    
    # 2. Make sure all bookings have pending status
    cursor.execute("UPDATE bookings SET status = 'pending', payment_status = 'unpaid' WHERE status IS NULL OR status = ''")
    conn.commit()
    print("Ensured all bookings with blank status are set to 'pending'")
    
    # 3. Check if it worked
    cursor = conn.cursor(dictionary=True)  # Switch to dictionary cursor for readable results
    cursor.execute("SELECT spot_id, location, status FROM parking_spots WHERE spot_id IN (12, 13, 14, 15)")
    updated_spots = cursor.fetchall()
    
    print("\n----- SPOT STATUS AFTER DIRECT UPDATE -----")
    for spot in updated_spots:
        print(f"Spot #{spot['spot_id']} - {spot['location']}: Status = '{spot['status']}'")
    
    # 4. Check all pending bookings
    cursor.execute("SELECT booking_id, user_id, spot_id, status FROM bookings WHERE status = 'pending'")
    pending_bookings = cursor.fetchall()
    
    print(f"\n----- PENDING BOOKINGS ({len(pending_bookings)}) -----")
    for booking in pending_bookings:
        print(f"Booking #{booking['booking_id']} - User #{booking['user_id']}, Spot #{booking['spot_id']}, Status: '{booking['status']}'")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    force_fix_issues()
