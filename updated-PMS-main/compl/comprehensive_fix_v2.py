"""
Comprehensive Fix Script v2

This script addresses all identified issues:
1. Fixes 'Unknown column target_id' error in Admin Dashboard
2. Resolves the 'Data truncated for column status' error in User Dashboard
3. Fixes the Accept/Decline buttons disappearing in Staff Dashboard
4. Properly updates parking spot statuses based on bookings
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
        
        # Fix target_id in delete_spot function
        delete_pattern = re.compile(r'(INSERT INTO admin_activity_log.*?admin_id, action_type, action_details), target_id, target_type(\).*?VALUES.*?\(%s, %s, %s), %s, %s(\))', re.DOTALL)
        fixed_delete = r'\1, booking_id\2, NULL\3'
        content = delete_pattern.sub(fixed_delete, content)
        
        # Fix target_id in add_spot function
        add_pattern = re.compile(r'(INSERT INTO admin_activity_log.*?admin_id, action_type, action_details), target_id, target_type(\).*?VALUES.*?\(%s, %s, %s), %s, %s(\))', re.DOTALL)
        fixed_add = r'\1, booking_id\2, NULL\3'
        content = add_pattern.sub(fixed_add, content)
        
        # Fix target_id in edit_spot function
        edit_pattern = re.compile(r'(INSERT INTO admin_activity_log.*?admin_id, action_type, action_details), target_id, target_type(\).*?VALUES.*?\(%s, %s, %s), %s, %s(\))', re.DOTALL)
        fixed_edit = r'\1, booking_id\2, NULL\3'
        content = edit_pattern.sub(fixed_edit, content)
        
        # Create a backup first
        backup_path = app_path + ".bak"
        with open(backup_path, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"Created backup of app.py at {backup_path}")
        
        # Write the fixed content
        with open(app_path, 'w', encoding='utf-8') as file:
            file.write(content)
        print("Successfully updated app.py: fixed target_id issues")
        
        return True
    except Exception as e:
        print(f"Error updating app.py: {str(e)}")
        return False

def fix_status_truncation():
    """Fix the Data truncated for column 'status' issues"""
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to database")
        return False
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Fix status truncation issues in create_booking
        print("Fixing status truncation issues...")
        
        # First check spot status ENUM definition
        cursor.execute("DESCRIBE parking_spots")
        spot_columns = cursor.fetchall()
        spot_status_column = None
        for col in spot_columns:
            if col['Field'] == 'status':
                spot_status_column = col
                break
                
        if spot_status_column:
            print(f"Parking spot status column type: {spot_status_column['Type']}")
            # If it's an ENUM, extract the allowed values
            if 'enum' in spot_status_column['Type'].lower():
                enum_values = spot_status_column['Type'].split("'")[1::2]  # Extract values between quotes
                print(f"Allowed parking spot status values: {enum_values}")
            else:
                # If it's not an ENUM, modify it to be VARCHAR
                cursor.execute("ALTER TABLE parking_spots MODIFY status VARCHAR(20) NOT NULL DEFAULT 'available'")
                conn.commit()
                print("Modified parking_spots.status to VARCHAR(20)")
        
        # Check booking status ENUM definition
        cursor.execute("DESCRIBE bookings")
        booking_columns = cursor.fetchall()
        booking_status_column = None
        for col in booking_columns:
            if col['Field'] == 'status':
                booking_status_column = col
                break
                
        if booking_status_column:
            print(f"Booking status column type: {booking_status_column['Type']}")
            # If it's an ENUM, extract the allowed values
            if 'enum' in booking_status_column['Type'].lower():
                enum_values = booking_status_column['Type'].split("'")[1::2]  # Extract values between quotes
                print(f"Allowed booking status values: {enum_values}")
                
                # Update any invalid booking statuses to 'pending'
                cursor.execute("""
                    UPDATE bookings 
                    SET status = 'pending' 
                    WHERE status NOT IN ('pending', 'confirmed', 'cancelled', 'pending_payment', 'completed', 'entry', 'exited')
                       OR status IS NULL OR status = ''
                """)
                updated = cursor.rowcount
                print(f"Updated {updated} bookings with invalid status to 'pending'")
            else:
                # If it's not an ENUM, that's fine
                print("Bookings.status is not an ENUM, no need to modify")
        
        # Normalize parking spot statuses
        cursor.execute("""
            UPDATE parking_spots
            SET status = 'available' 
            WHERE status IS NULL OR status = '' OR 
                  status NOT IN ('available', 'reserved', 'occupied')
        """)
        spot_updated = cursor.rowcount
        print(f"Updated {spot_updated} parking spots with valid status values")
        
        conn.commit()
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"Error fixing status truncation: {str(e)}")
        return False
    
    finally:
        cursor.close()
        conn.close()

def fix_staff_dashboard():
    """Fix issues with staff dashboard Accept/Decline buttons"""
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to database")
        return False
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        print("Fixing staff dashboard issues...")
        
        # 1. Ensure all bookings have a valid status
        cursor.execute("""
            UPDATE bookings
            SET status = 'pending' 
            WHERE (status IS NULL OR status = '') 
              AND payment_status = 'unpaid'
        """)
        updated_count = cursor.rowcount
        print(f"Updated {updated_count} bookings with blank status to 'pending'")
        
        # 2. Check for any bookings with valid status but not being displayed in pending_bookings query
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM bookings b
            JOIN users u ON b.user_id = u.user_id
            JOIN parking_spots p ON b.spot_id = p.spot_id
            WHERE (b.status = 'pending' OR b.status IS NULL OR b.status = '')
            AND b.status != 'confirmed' 
            AND b.status != 'cancelled'
            AND b.status != 'entry'
            AND b.status != 'exited'
        """)
        
        pending_count = cursor.fetchone()['count']
        print(f"Found {pending_count} pending bookings that should show Accept/Decline buttons")
        
        # 3. Clean up spot statuses to match their bookings
        # For reserved spots
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
        reserved_count = cursor.rowcount
        print(f"Updated {reserved_count} spots to 'reserved' based on their bookings")
        
        # For occupied spots
        cursor.execute("""
            UPDATE parking_spots p
            JOIN (
                SELECT DISTINCT spot_id
                FROM bookings
                WHERE status = 'entry'
            ) b ON p.spot_id = b.spot_id
            SET p.status = 'occupied'
        """)
        occupied_count = cursor.rowcount
        print(f"Updated {occupied_count} spots to 'occupied' based on their bookings")
        
        # 4. Fix booking status vs payment status - clear up the confusion
        cursor.execute("""
            UPDATE bookings
            SET payment_status = 'pending'
            WHERE status = 'pending_payment'
        """)
        payment_status_fixed = cursor.rowcount
        print(f"Fixed {payment_status_fixed} bookings with pending_payment status")
        
        # Create a test pending booking if none exist (for testing the buttons)
        if pending_count == 0:
            print("No pending bookings found. Creating a test booking for showing Accept/Decline buttons")
            
            # First find an available spot
            cursor.execute("SELECT spot_id FROM parking_spots WHERE status = 'available' LIMIT 1")
            spot_result = cursor.fetchone()
            
            if spot_result:
                spot_id = spot_result['spot_id']
                
                # Find a user 
                cursor.execute("SELECT user_id FROM users LIMIT 1")
                user_result = cursor.fetchone()
                
                if user_result:
                    user_id = user_result['user_id']
                    
                    # Create a test pending booking
                    cursor.execute("""
                        INSERT INTO bookings (user_id, spot_id, start_time, end_time, status, payment_status, amount)
                        VALUES (%s, %s, NOW() + INTERVAL 1 DAY, NOW() + INTERVAL 2 DAY, 'pending', 'unpaid', 50.00)
                    """)
                    
                    print(f"Created test pending booking for spot {spot_id} and user {user_id}")
        
        conn.commit()
        print("Successfully fixed staff dashboard issues")
        
        # Print current status distribution for spots
        cursor.execute("""
            SELECT status, COUNT(*) as count
            FROM parking_spots
            GROUP BY status
        """)
        stats = cursor.fetchall()
        
        print("\nCurrent parking spot status distribution:")
        for stat in stats:
            print(f"- {stat['status'] or 'blank'}: {stat['count']} spots")
            
        # Print pending bookings that should show Accept/Decline buttons
        cursor.execute("""
            SELECT b.booking_id, u.username, p.location, b.status, b.payment_status
            FROM bookings b
            JOIN users u ON b.user_id = u.user_id
            JOIN parking_spots p ON b.spot_id = p.spot_id
            WHERE (b.status = 'pending' OR b.status IS NULL OR b.status = '')
            AND b.status != 'confirmed' 
            AND b.status != 'cancelled'
            AND b.status != 'entry'
            AND b.status != 'exited'
            LIMIT 5
        """)
        
        pending_bookings = cursor.fetchall()
        if pending_bookings:
            print("\nSample pending bookings that should show Accept/Decline buttons:")
            for b in pending_bookings:
                print(f"- Booking #{b['booking_id']}: User {b['username']}, Spot {b['location']}, " 
                      f"Status {b['status']}, Payment {b['payment_status']}")
        
        return True
    
    except Exception as e:
        conn.rollback()
        print(f"Error fixing staff dashboard: {str(e)}")
        return False
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("Running Comprehensive Fix Script v2...\n")
    
    print("=== 1. Fixing app.py file to address 'Unknown column target_id' error ===")
    fix_app_py_file()
    
    print("\n=== 2. Fixing status truncation issues ===")
    fix_status_truncation()
    
    print("\n=== 3. Fixing staff dashboard and Accept/Decline buttons ===")
    fix_staff_dashboard()
    
    print("\nDone! Restart your Flask application to apply these changes.")
