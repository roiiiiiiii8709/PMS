from db import get_db_connection

def fix_remaining_issues():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    print("===== FIXING REMAINING ISSUES =====")
    
    # Fix the specific spots that still have blank status
    cursor.execute("""
        UPDATE parking_spots 
        SET status = 'reserved' 
        WHERE spot_id IN (12, 13, 14, 15)
    """)
    updated_spots = cursor.rowcount
    conn.commit()
    print(f"Fixed {updated_spots} spots with specific IDs by setting status to 'reserved'")
    
    # Check conflicts between bookings
    cursor.execute("""
        SELECT b1.booking_id as booking1, b2.booking_id as booking2, 
               b1.spot_id, b1.start_time as start1, b1.end_time as end1,
               b2.start_time as start2, b2.end_time as end2
        FROM bookings b1
        JOIN bookings b2 ON b1.spot_id = b2.spot_id AND b1.booking_id != b2.booking_id
        WHERE b1.status = 'pending' AND b2.status = 'pending'
        AND ((b1.start_time <= b2.end_time AND b1.end_time > b2.start_time) 
             OR (b1.start_time < b2.end_time AND b1.end_time >= b2.start_time) 
             OR (b1.start_time >= b2.start_time AND b1.end_time <= b2.end_time))
    """)
    conflicts = cursor.fetchall()
    
    print("\n----- BOOKING CONFLICTS -----")
    if conflicts:
        for conflict in conflicts:
            print(f"Conflict between Booking #{conflict['booking1']} and #{conflict['booking2']} for Spot #{conflict['spot_id']}")
            print(f"  Booking #{conflict['booking1']}: {conflict['start1']} to {conflict['end1']}")
            print(f"  Booking #{conflict['booking2']}: {conflict['start2']} to {conflict['end2']}")
    else:
        print("No booking time conflicts detected")
    
    # Make sure the has_time_conflict flag is set properly for staff dashboard
    print("\n----- CHECKING STAFF DASHBOARD CONFLICT DETECTION -----")
    # Recreate the conflict detection query from staff_dashboard
    cursor.execute("""
        SELECT b1.booking_id, b1.spot_id, 
            (SELECT COUNT(*) FROM bookings b2 
             WHERE b2.spot_id = b1.spot_id 
             AND b2.booking_id != b1.booking_id
             AND ((b2.start_time <= b1.end_time AND b2.end_time > b1.start_time) OR 
                  (b2.start_time < b1.end_time AND b2.end_time >= b1.start_time) OR 
                  (b2.start_time >= b1.start_time AND b2.end_time <= b1.end_time))
             AND b2.status IN ('confirmed', 'entry', 'pending')
            ) as conflicts
        FROM bookings b1
        WHERE b1.status = 'pending'
    """)
    pending_with_conflicts = cursor.fetchall()
    
    for booking in pending_with_conflicts:
        print(f"Booking #{booking['booking_id']} (Spot #{booking['spot_id']}) has {booking['conflicts']} conflicts")

    # Verify all bookings have proper status
    cursor.execute("SELECT booking_id, status FROM bookings WHERE status != 'pending'")
    non_pending = cursor.fetchall()
    
    print("\n----- NON-PENDING BOOKINGS -----")
    if non_pending:
        for booking in non_pending:
            print(f"Booking #{booking['booking_id']} has status: '{booking['status']}'")
    else:
        print("All bookings are currently set to 'pending' status")
        
    cursor.close()
    conn.close()

if __name__ == "__main__":
    fix_remaining_issues()
