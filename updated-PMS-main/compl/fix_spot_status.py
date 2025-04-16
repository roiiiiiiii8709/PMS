from db import get_db_connection

def fix_spot_status():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    print("===== DIRECT UPDATE FOR BLANK SPOT STATUS =====")
    
    # Use direct SQL to fix blank spot status for spots with bookings
    cursor.execute("""
        UPDATE parking_spots
        SET status = 'reserved'
        WHERE spot_id IN (12, 13, 14, 15)
    """)
    
    spots_updated = cursor.rowcount
    conn.commit()
    print(f"Updated {spots_updated} spots with blank status to 'reserved'")
    
    # Add a 'test-occupied' spot for demonstration
    cursor.execute("UPDATE parking_spots SET status = 'occupied' WHERE spot_id = 8")
    conn.commit()
    print("Set spot #8 to 'occupied' status for testing")
    
    # Create one booking with time conflict for another user to demonstrate conflict message
    cursor.execute("""
        INSERT INTO bookings (user_id, spot_id, start_time, end_time, status, payment_status, amount)
        VALUES (3, 9, '2025-04-07 12:00:00', '2025-04-07 14:00:00', 'confirmed', 'unpaid', 80.00)
    """)
    conn.commit()
    print("Created a confirmed booking for spot #9")
    
    # Verify parking spots
    cursor.execute("SELECT spot_id, location, status FROM parking_spots WHERE spot_id IN (8, 9, 12, 13, 14, 15)")
    spots = cursor.fetchall()
    
    print("\n----- UPDATED SPOTS -----")
    for spot in spots:
        print(f"Spot #{spot['spot_id']} - {spot['location']}: Status = '{spot['status']}'")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    fix_spot_status()
