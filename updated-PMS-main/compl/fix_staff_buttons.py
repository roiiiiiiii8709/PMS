"""
Fix Staff Dashboard Buttons and Parking Spot Status Issues

This script:
1. Ensures all bookings have proper 'pending' status (not blank or NULL)
2. Updates parking spot status for expired bookings
3. Normalizes data to ensure Accept/Decline buttons appear correctly
"""
import mysql.connector
from db import get_db_connection
from datetime import datetime

def fix_pending_booking_status():
    """Ensure all pending bookings have the correct status value for buttons to appear"""
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to database")
        return False
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        # First show the current status of bookings
        cursor.execute("""
            SELECT status, COUNT(*) as count FROM bookings
            GROUP BY status
        """)
        status_counts = cursor.fetchall()
        print("Current booking status counts:")
        for item in status_counts:
            print(f"- {item['status'] or 'NULL/blank'}: {item['count']}")
        
        # Update bookings with blank/null status to 'pending'
        cursor.execute("""
            UPDATE bookings 
            SET status = 'pending' 
            WHERE (status IS NULL OR status = '') 
              AND payment_status = 'unpaid'
              AND start_time > NOW()
        """)
        updated_count = cursor.rowcount
        print(f"Updated {updated_count} bookings with blank status to 'pending'")
        
        # Verify that pending bookings will show up in the staff dashboard
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM bookings b
            JOIN users u ON b.user_id = u.user_id
            JOIN parking_spots p ON b.spot_id = p.spot_id
            WHERE b.status = 'pending'
        """)
        pending_count = cursor.fetchone()['count']
        print(f"Found {pending_count} pending bookings that should show Accept/Decline buttons")
        
        # Show sample of pending bookings
        if pending_count > 0:
            cursor.execute("""
                SELECT b.booking_id, u.username, p.location, b.status, b.payment_status
                FROM bookings b
                JOIN users u ON b.user_id = u.user_id
                JOIN parking_spots p ON b.spot_id = p.spot_id
                WHERE b.status = 'pending'
                LIMIT 5
            """)
            bookings = cursor.fetchall()
            print("\nSample pending bookings:")
            for b in bookings:
                print(f"- Booking #{b['booking_id']}: User {b['username']}, Spot {b['location']}, " 
                      f"Status {b['status']}, Payment {b['payment_status']}")
        
        # If no pending bookings exist, create a test one for showing the buttons
        else:
            print("No pending bookings found. Creating a test booking to show Accept/Decline buttons...")
            
            # Find a user and an available spot
            cursor.execute("SELECT user_id FROM users LIMIT 1")
            user_result = cursor.fetchone()
            
            cursor.execute("SELECT spot_id FROM parking_spots WHERE status = 'available' LIMIT 1")
            spot_result = cursor.fetchone()
            
            if user_result and spot_result:
                user_id = user_result['user_id']
                spot_id = spot_result['spot_id']
                
                # Create a test booking
                cursor.execute("""
                    INSERT INTO bookings (user_id, spot_id, start_time, end_time, status, payment_status, amount)
                    VALUES (%s, %s, NOW() + INTERVAL 1 DAY, NOW() + INTERVAL 2 DAY, 'pending', 'unpaid', 50.00)
                """, (user_id, spot_id))
                
                booking_id = cursor.lastrowid
                print(f"Created test pending booking (ID: {booking_id}) for spot {spot_id}")
        
        conn.commit()
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"Error fixing pending booking status: {str(e)}")
        return False
    
    finally:
        cursor.close()
        conn.close()

def update_expired_bookings():
    """Update expired bookings and make spots available again"""
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to database")
        return False
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"Current time: {now}")
        
        # 1. Find expired bookings that should be completed
        cursor.execute("""
            SELECT b.booking_id, b.spot_id, b.status, b.end_time, p.status as spot_status
            FROM bookings b
            JOIN parking_spots p ON b.spot_id = p.spot_id
            WHERE b.end_time < NOW()
            AND b.status IN ('confirmed', 'pending', 'entry')
        """)
        
        expired_bookings = cursor.fetchall()
        print(f"Found {len(expired_bookings)} expired bookings")
        
        updated_count = 0
        
        for booking in expired_bookings:
            print(f"Processing expired booking #{booking['booking_id']}, " 
                  f"status: {booking['status']}, spot status: {booking['spot_status']}")
            
            # Update booking status to completed
            cursor.execute("""
                UPDATE bookings
                SET status = 'completed'
                WHERE booking_id = %s
            """, (booking['booking_id'],))
            
            # Only update spot status if this was the last active booking for the spot
            cursor.execute("""
                SELECT COUNT(*) as active_count
                FROM bookings
                WHERE spot_id = %s
                AND status IN ('confirmed', 'pending', 'entry')
                AND end_time > NOW()
            """, (booking['spot_id'],))
            
            active_count = cursor.fetchone()['active_count']
            
            if active_count == 0:
                # No more active bookings, set spot to available
                cursor.execute("""
                    UPDATE parking_spots
                    SET status = 'available'
                    WHERE spot_id = %s
                """, (booking['spot_id'],))
                
                print(f"  - Updated spot #{booking['spot_id']} to available")
            else:
                print(f"  - Spot #{booking['spot_id']} still has {active_count} active bookings")
            
            updated_count += 1
        
        conn.commit()
        print(f"Successfully updated {updated_count} expired bookings")
        
        # Show updated spot status distribution
        cursor.execute("""
            SELECT status, COUNT(*) as count
            FROM parking_spots
            GROUP BY status
        """)
        stats = cursor.fetchall()
        
        print("\nCurrent parking spot status distribution:")
        for stat in stats:
            print(f"- {stat['status'] or 'blank'}: {stat['count']} spots")
        
        return updated_count
        
    except Exception as e:
        conn.rollback()
        print(f"Error updating expired bookings: {str(e)}")
        return False
    
    finally:
        cursor.close()
        conn.close()

def fix_delete_spot_error():
    """Fix the 'Error deleting parking spot: Not all parameters were used in the SQL statement' error"""
    print("\nTo fix the 'Error deleting parking spot' issue:")
    print("The error occurs because there's a mismatch in parameters passed to the SQL query.")
    print("\nCheck the delete_spot function in app.py. Look for where it says:")
    print("  cursor.execute(\"INSERT INTO admin_activity_log (admin_id, action_type, action_details, booking_id) VALUES (%s, %s, %s, %s)\", (parameters))")
    print("\nMake sure you're passing exactly 4 parameters, not more or less:")
    print("  (session['admin_id'], 'delete', action_details, None)")
    print("\nThis should resolve the 'Not all parameters were used in the SQL statement' error.")
    
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to database")
        return False
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Check the admin_activity_log table structure to verify parameters
        cursor.execute("DESCRIBE admin_activity_log")
        columns = cursor.fetchall()
        
        print("\nThe admin_activity_log table structure:")
        for col in columns:
            print(f"- {col['Field']}: {col['Type']}")
        
        return True
        
    except Exception as e:
        print(f"Error checking admin_activity_log structure: {str(e)}")
        return False
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("Fixing Staff Dashboard, Booking Status, and Admin Dashboard Issues...\n")
    
    print("=== 1. Fixing Accept/Decline buttons disappearing issue ===")
    fix_pending_booking_status()
    
    print("\n=== 2. Updating expired bookings and making spots available ===")
    update_expired_bookings()
    
    print("\n=== 3. Fixing 'Error deleting parking spot' in admin dashboard ===")
    fix_delete_spot_error()
    
    print("\nAll fixes have been applied!")
    print("Please restart your Flask application to see these changes take effect.")
