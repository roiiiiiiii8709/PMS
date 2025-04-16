"""
Fix Admin Dashboard Errors

This script addresses the 'Unknown column target_id' error in the admin dashboard
when deleting parking spots.
"""
import mysql.connector
from db import get_db_connection

def fix_admin_delete_spot_error():
    """Fixes the delete_spot function in app.py"""
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to database")
        return False
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Look for the issue in app.py
        print("Fixing delete_spot function in app.py...")
        
        # Correct approach: Update the app.py file
        print("\nTo fix the 'Unknown column target_id' error:")
        print("1. In app.py, find the delete_spot function (around line 1460-1470)")
        print("2. Replace the INSERT statement with:")
        print("""
            # Log admin activity
            action_details = f"Deleted parking spot - ID: {spot_id}, location: {spot['location']}, price: {spot['price_per_hour']}"
            cursor.execute(\"\"\"
                INSERT INTO admin_activity_log (admin_id, action_type, action_details, booking_id)
                VALUES (%s, %s, %s, %s)
            \"\"\", (session['admin_id'], 'delete', action_details, None))
        """)
        
        # Also fix add_spot and edit_spot
        print("\nAlso fix the add_spot function:")
        print("""
            # Log admin activity
            cursor.execute(\"\"\"
                INSERT INTO admin_activity_log (admin_id, action_type, action_details, booking_id)
                VALUES (%s, %s, %s, %s)
            \"\"\", (session['admin_id'], 'add', f"Added new parking spot - ID: {spot_id}, location: {location}, price: {price_per_hour}", None))
        """)
        
        print("\nAlso fix the edit_spot function:")
        print("""
            # Log admin activity
            cursor.execute(\"\"\"
                INSERT INTO admin_activity_log (admin_id, action_type, action_details, booking_id)
                VALUES (%s, %s, %s, %s)
            \"\"\", (session['admin_id'], 'edit', action_details, None))
        """)
        
        # Let's verify the actual admin_activity_log table structure
        print("\nVerifying admin_activity_log table structure...")
        try:
            cursor.execute("DESCRIBE admin_activity_log")
            columns = cursor.fetchall()
            print("admin_activity_log columns:")
            for col in columns:
                print(f"- {col['Field']}: {col['Type']}")
                
            # Check if any existing records might be using target_id
            cursor.execute("SELECT * FROM admin_activity_log LIMIT 5")
            records = cursor.fetchall()
            if records:
                print(f"\nFound {len(records)} existing records in admin_activity_log table")
            else:
                print("\nNo existing records found in admin_activity_log table")
                
        except mysql.connector.Error as err:
            print(f"Error checking table structure: {err}")
            
        return True
    
    except Exception as e:
        print(f"Error fixing admin dashboard: {str(e)}")
        return False
    
    finally:
        cursor.close()
        conn.close()

def fix_spot_status_management():
    """Fixes spot status management in the admin dashboard"""
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to database")
        return False
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Update all spots with blank or null status to 'available'
        cursor.execute("UPDATE parking_spots SET status = 'available' WHERE status = '' OR status IS NULL")
        updated = cursor.rowcount
        print(f"Updated {updated} parking spots with blank status to 'available'")
        
        # Update spots with bookings to 'reserved'
        cursor.execute("""
            UPDATE parking_spots p
            JOIN (
                SELECT DISTINCT spot_id
                FROM bookings
                WHERE status IN ('pending', 'confirmed', 'pending_payment') 
                AND end_time > NOW()
            ) b ON p.spot_id = b.spot_id
            SET p.status = 'reserved'
            WHERE p.status != 'occupied'
        """)
        reserved = cursor.rowcount
        print(f"Updated {reserved} parking spots with active bookings to 'reserved'")
        
        # Update spots with entry bookings to 'occupied'
        cursor.execute("""
            UPDATE parking_spots p
            JOIN (
                SELECT DISTINCT spot_id
                FROM bookings
                WHERE status = 'entry'
            ) b ON p.spot_id = b.spot_id
            SET p.status = 'occupied'
        """)
        occupied = cursor.rowcount
        print(f"Updated {occupied} parking spots with 'entry' bookings to 'occupied'")
        
        conn.commit()
        print("Successfully updated parking spot statuses")
        
        # Print current spot status distribution
        cursor.execute("""
            SELECT status, COUNT(*) as count
            FROM parking_spots
            GROUP BY status
        """)
        stats = cursor.fetchall()
        
        print("\nCurrent parking spot status distribution:")
        for stat in stats:
            print(f"- {stat['status'] or 'blank'}: {stat['count']} spots")
            
        return True
    
    except Exception as e:
        conn.rollback()
        print(f"Error fixing spot status: {str(e)}")
        return False
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("Fixing Admin Dashboard Errors...\n")
    
    print("=== Fixing 'Unknown column target_id' error ===")
    fix_admin_delete_spot_error()
    
    print("\n=== Fixing parking spot status management ===")
    fix_spot_status_management()
    
    print("\nDone! You need to manually update the app.py file with the suggested changes.")
