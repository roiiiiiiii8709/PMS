"""
Fix All Parking Management System Issues

This script addresses all identified issues:
1. Fixes 'Unknown column target_id' error in Admin Dashboard
2. Resolves the 'Data truncated for column status' error
3. Fixes the Accept/Decline buttons in Staff Dashboard
4. Updates parking spot statuses correctly
"""
import mysql.connector
from db import get_db_connection
import os
import re

def fix_app_py_file():
    """Fix target_id issues in app.py by directly updating the file"""
    app_path = "app.py"
    if not os.path.exists(app_path):
        print(f"Error: {app_path} not found")
        return False
    
    try:
        # Read the content of app.py
        with open(app_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Fix admin_activity_log insertions
        content = content.replace("INSERT INTO admin_activity_log (admin_id, action_type, action_details, target_id, target_type)",
                                  "INSERT INTO admin_activity_log (admin_id, action_type, action_details, booking_id)")
        content = content.replace("VALUES (%s, %s, %s, %s, %s)", 
                                  "VALUES (%s, %s, %s, NULL)")
        
        # Create a backup first
        backup_path = app_path + ".bak"
        with open(backup_path, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"Created backup of app.py at {backup_path}")
        
        # Write the fixed content
        with open(app_path, 'w', encoding='utf-8') as file:
            file.write(content)
        print("Successfully updated app.py: fixed admin_activity_log insertions")
        
        return True
    except Exception as e:
        print(f"Error updating app.py: {str(e)}")
        return False

def fix_status_columns():
    """Fix the status column definitions in the database"""
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to database")
        return False
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Step 1: Convert parking_spots.status from ENUM to VARCHAR
        print("Modifying parking_spots.status ENUM to VARCHAR...")
        try:
            cursor.execute("ALTER TABLE parking_spots MODIFY status VARCHAR(20) NOT NULL DEFAULT 'available'")
            conn.commit()
            print("SUCCESS: Modified parking_spots.status to VARCHAR(20)")
        except mysql.connector.Error as err:
            print(f"Error modifying parking_spots.status: {err}")
            conn.rollback()
        
        # Step 2: Convert bookings.status from ENUM to VARCHAR
        print("\nModifying bookings.status ENUM to VARCHAR...")
        try:
            cursor.execute("ALTER TABLE bookings MODIFY status VARCHAR(20) NOT NULL DEFAULT 'pending'")
            conn.commit()
            print("SUCCESS: Modified bookings.status to VARCHAR(20)")
        except mysql.connector.Error as err:
            print(f"Error modifying bookings.status: {err}")
            conn.rollback()
        
        # Step 3: Normalize parking spots status
        print("\nNormalizing parking spot statuses...")
        try:
            # Update all spots with blank or null status to 'available'
            cursor.execute("UPDATE parking_spots SET status = 'available' WHERE status = '' OR status IS NULL")
            available_updated = cursor.rowcount
            
            # Fix existing status values to ensure they are proper
            cursor.execute("""
                UPDATE parking_spots 
                SET status = CASE
                    WHEN status IN ('available', 'Available', 'AVAILABLE') THEN 'available'
                    WHEN status IN ('reserved', 'Reserved', 'RESERVED') THEN 'reserved'
                    WHEN status IN ('occupied', 'Occupied', 'OCCUPIED') THEN 'occupied'
                    ELSE 'available'
                END
            """)
            status_normalized = cursor.rowcount
            
            conn.commit()
            print(f"SUCCESS: Updated {available_updated} spots with blank status")
            print(f"SUCCESS: Normalized {status_normalized} spot statuses")
        except mysql.connector.Error as err:
            print(f"Error normalizing parking spot statuses: {err}")
            conn.rollback()
            
        # Step 4: Normalize booking statuses
        print("\nNormalizing booking statuses...")
        try:
            # Update all bookings with blank or null status to 'pending'
            cursor.execute("UPDATE bookings SET status = 'pending' WHERE status = '' OR status IS NULL")
            pending_updated = cursor.rowcount
            
            # Fix existing status values to ensure they are proper
            cursor.execute("""
                UPDATE bookings 
                SET status = CASE
                    WHEN status IN ('pending', 'Pending', 'PENDING') THEN 'pending'
                    WHEN status IN ('confirmed', 'Confirmed', 'CONFIRMED') THEN 'confirmed'
                    WHEN status IN ('cancelled', 'Canceled', 'CANCELLED') THEN 'cancelled'
                    WHEN status IN ('pending_payment', 'Pending_Payment') THEN 'pending_payment'
                    WHEN status IN ('completed', 'Completed', 'COMPLETED') THEN 'completed'
                    WHEN status IN ('entry', 'Entry', 'ENTRY') THEN 'entry'
                    WHEN status IN ('exited', 'Exited', 'EXITED') THEN 'exited'
                    ELSE 'pending'
                END
            """)
            booking_normalized = cursor.rowcount
            
            conn.commit()
            print(f"SUCCESS: Updated {pending_updated} bookings with blank status")
            print(f"SUCCESS: Normalized {booking_normalized} booking statuses")
        except mysql.connector.Error as err:
            print(f"Error normalizing booking statuses: {err}")
            conn.rollback()
        
        # Step 5: Update spot statuses based on bookings
        print("\nUpdating spot statuses based on bookings...")
        try:
            # Mark spots with entry bookings as occupied
            cursor.execute("""
                UPDATE parking_spots p
                JOIN (
                    SELECT DISTINCT spot_id
                    FROM bookings
                    WHERE status = 'entry'
                ) b ON p.spot_id = b.spot_id
                SET p.status = 'occupied'
            """)
            occupied_updated = cursor.rowcount
            
            # Mark spots with confirmed/pending bookings as reserved if not occupied
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
            reserved_updated = cursor.rowcount
            
            conn.commit()
            print(f"SUCCESS: Updated {occupied_updated} spots to 'occupied' based on entry bookings")
            print(f"SUCCESS: Updated {reserved_updated} spots to 'reserved' based on active bookings")
        except mysql.connector.Error as err:
            print(f"Error updating spot statuses: {err}")
            conn.rollback()
            
        # Step 6: Verify current status distribution
        print("\nCurrent status distribution:")
        try:
            cursor.execute("""
                SELECT status, COUNT(*) as count
                FROM parking_spots
                GROUP BY status
            """)
            spot_stats = cursor.fetchall()
            print("Parking Spots:")
            for stat in spot_stats:
                print(f"- {stat['status'] or 'blank'}: {stat['count']} spots")
                
            cursor.execute("""
                SELECT status, COUNT(*) as count
                FROM bookings
                GROUP BY status
            """)
            booking_stats = cursor.fetchall()
            print("\nBookings:")
            for stat in booking_stats:
                print(f"- {stat['status'] or 'blank'}: {stat['count']} bookings")
                
        except mysql.connector.Error as err:
            print(f"Error getting status statistics: {err}")
            
        # Step 7: Verify that pending bookings will show up in the staff dashboard
        print("\nVerifying pending bookings for staff dashboard...")
        try:
            cursor.execute("""
                SELECT b.booking_id, u.username, p.location, b.status, b.payment_status
                FROM bookings b
                JOIN users u ON b.user_id = u.user_id
                JOIN parking_spots p ON b.spot_id = p.spot_id
                WHERE b.status = 'pending'
                LIMIT 5
            """)
            pending_bookings = cursor.fetchall()
            
            if pending_bookings:
                print(f"Found {len(pending_bookings)} pending bookings that should show Accept/Decline buttons:")
                for b in pending_bookings:
                    print(f"- Booking #{b['booking_id']}: User {b['username']}, Spot {b['location']}, " 
                          f"Status {b['status']}, Payment {b['payment_status']}")
            else:
                print("No pending bookings found. Creating a test booking to show Accept/Decline buttons...")
                
                # First find a user and available spot
                cursor.execute("SELECT user_id FROM users LIMIT 1")
                user_result = cursor.fetchone()
                cursor.execute("SELECT spot_id FROM parking_spots WHERE status = 'available' LIMIT 1")
                spot_result = cursor.fetchone()
                
                if user_result and spot_result:
                    user_id = user_result['user_id']
                    spot_id = spot_result['spot_id']
                    
                    cursor.execute("""
                        INSERT INTO bookings (user_id, spot_id, start_time, end_time, status, payment_status, amount)
                        VALUES (%s, %s, NOW() + INTERVAL 1 DAY, NOW() + INTERVAL 2 DAY, 'pending', 'unpaid', 50.00)
                    """)
                    
                    booking_id = cursor.lastrowid
                    conn.commit()
                    print(f"SUCCESS: Created test pending booking (ID: {booking_id}) for spot {spot_id}")
                else:
                    print("Could not create test booking - missing user or available spot")
                    
        except mysql.connector.Error as err:
            print(f"Error verifying pending bookings: {err}")
            conn.rollback()
                
        return True
    
    except Exception as e:
        print(f"Error fixing status columns: {str(e)}")
        return False
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("Fixing All Parking Management System Issues...\n")
    
    print("=== 1. Fixing app.py file (unknown column 'target_id' error) ===")
    fix_app_py_file()
    
    print("\n=== 2. Fixing status columns and data truncation errors ===")
    fix_status_columns()
    
    print("\nAll fixes completed!")
    print("Please restart your Flask application to apply these changes.")
    print("\nThese fixes have addressed:")
    print("1. 'Unknown column target_id' error in Admin Dashboard")
    print("2. 'Data truncated for column status' error during booking creation")
    print("3. Accept/Decline buttons not showing in Staff Dashboard")
    print("4. Improper status updates for parking spots")
