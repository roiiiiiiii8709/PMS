from db import get_db_connection
from datetime import datetime

def fix_orphaned_spots():
    """
    Fixes parking spots that are marked as occupied, reserved, or unavailable
    but don't have any active bookings associated with them.
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Find spots with non-available status
        cursor.execute("""
            SELECT * FROM parking_spots 
            WHERE status IN ('occupied', 'reserved')
        """)
        
        non_available_spots = cursor.fetchall()
        print(f"Found {len(non_available_spots)} spots that are not available")
        
        fixed_spots = 0
        
        for spot in non_available_spots:
            # Check if there are any active bookings for this spot
            cursor.execute("""
                SELECT COUNT(*) as count FROM bookings 
                WHERE spot_id = %s 
                AND status IN ('confirmed', 'entry', 'occupied')
                AND end_time > %s
            """, (spot['spot_id'], datetime.now()))
            
            result = cursor.fetchone()
            active_bookings = result['count']
            
            if active_bookings == 0:
                # No active bookings, so the spot should be available
                print(f"Fixing Spot ID {spot['spot_id']} from '{spot['status']}' to 'available'")
                cursor.execute("""
                    UPDATE parking_spots 
                    SET status = 'available' 
                    WHERE spot_id = %s
                """, (spot['spot_id'],))
                fixed_spots += 1
        
        conn.commit()
        print(f"Fixed {fixed_spots} spots that had incorrect status")
        
        # Now check to ensure all is well
        cursor.execute("SELECT spot_id, status FROM parking_spots WHERE spot_id = 2")
        spot2 = cursor.fetchone()
        print(f"Spot ID 2 now has status: {spot2['status']}")
        
    except Exception as e:
        conn.rollback()
        print(f"Error fixing orphaned spots: {e}")
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    fix_orphaned_spots()
