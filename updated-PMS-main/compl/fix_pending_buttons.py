"""
Fix Staff Dashboard Accept/Decline Buttons

This script:
1. Checks if there are any pending bookings in the database
2. Creates a test pending booking if needed
3. Fixes the condition for showing the Accept/Decline buttons
"""
from db import get_db_connection
from datetime import datetime, timedelta

def check_pending_bookings():
    """Check for pending bookings in the database"""
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to database")
        return False
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Check all booking statuses
        cursor.execute("""
            SELECT status, COUNT(*) as count 
            FROM bookings 
            GROUP BY status
        """)
        
        status_counts = cursor.fetchall()
        print("Current booking status counts:")
        for status in status_counts:
            print(f"- {status['status'] or 'NULL/blank'}: {status['count']}")
        
        # Check specifically for pending bookings
        cursor.execute("""
            SELECT b.booking_id, u.username, p.location, b.status, b.payment_status,
                   b.start_time, b.end_time
            FROM bookings b
            JOIN users u ON b.user_id = u.user_id
            JOIN parking_spots p ON b.spot_id = p.spot_id
            WHERE b.status = 'pending'
        """)
        
        pending_bookings = cursor.fetchall()
        if pending_bookings:
            print(f"\nFound {len(pending_bookings)} pending bookings that should show Accept/Decline buttons:")
            for booking in pending_bookings:
                print(f"- Booking #{booking['booking_id']}: User {booking['username']}, Spot {booking['location']}, " 
                      f"Status: {booking['status']}, Payment: {booking['payment_status']}")
        else:
            print("\nNo pending bookings found - this is why the Accept/Decline buttons are not showing.")
            
        return True
    
    except Exception as e:
        print(f"Error checking pending bookings: {str(e)}")
        return False
    
    finally:
        cursor.close()
        conn.close()

def create_test_pending_booking():
    """Create a test pending booking to show the Accept/Decline buttons"""
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to database")
        return False
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Find an active user
        cursor.execute("SELECT user_id FROM users LIMIT 1")
        user_result = cursor.fetchone()
        
        if not user_result:
            print("No users found in the database")
            return False
        
        user_id = user_result['user_id']
        
        # Find an available spot
        cursor.execute("SELECT spot_id FROM parking_spots WHERE status = 'available' LIMIT 1")
        spot_result = cursor.fetchone()
        
        if not spot_result:
            print("No available parking spots found")
            return False
        
        spot_id = spot_result['spot_id']
        
        # Calculate start and end times (starting tomorrow)
        start_time = datetime.now() + timedelta(days=1)
        start_time = start_time.replace(hour=10, minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(hours=3)
        
        # Insert the booking with status 'pending'
        cursor.execute("""
            INSERT INTO bookings (user_id, spot_id, start_time, end_time, status, payment_status, amount)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (user_id, spot_id, start_time, end_time, 'pending', 'unpaid', 50.00))
        
        booking_id = cursor.lastrowid
        
        # Update the spot status to reflect the booking
        cursor.execute("UPDATE parking_spots SET status = 'reserved' WHERE spot_id = %s", (spot_id,))
        
        conn.commit()
        print(f"Created test pending booking (ID: {booking_id}) for user {user_id} and spot {spot_id}")
        print(f"Booking time: {start_time.strftime('%Y-%m-%d %H:%M')} to {end_time.strftime('%Y-%m-%d %H:%M')}")
        print("The Accept/Decline buttons should now appear in the staff dashboard")
        
        return True
    
    except Exception as e:
        conn.rollback()
        print(f"Error creating test booking: {str(e)}")
        return False
    
    finally:
        cursor.close()
        conn.close()

def verify_staff_dashboard_data():
    """Check what data is being passed to the staff dashboard template"""
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to database")
        return False
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        print("\nVerifying staff dashboard query data...")
        
        # This is the exact query used in staff_dashboard function
        cursor.execute("""
            SELECT b.*, u.username, u.email, p.location, p.price_per_hour
            FROM bookings b
            JOIN users u ON b.user_id = u.user_id
            JOIN parking_spots p ON b.spot_id = p.spot_id
            WHERE b.status = 'pending'
            ORDER BY b.start_time ASC  -- Show nearest upcoming bookings first
        """)
        
        pending_bookings = cursor.fetchall()
        
        if pending_bookings:
            print(f"The dashboard query returned {len(pending_bookings)} pending bookings.")
            print("The buttons should appear if the template is rendering correctly.")
        else:
            print("The dashboard query returned NO pending bookings.")
            print("This is why the Accept/Decline buttons are not showing.")
        
        return True
    
    except Exception as e:
        print(f"Error verifying dashboard data: {str(e)}")
        return False
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("Checking and fixing Staff Dashboard Accept/Decline buttons...\n")
    
    print("=== Current Booking Status ===")
    if check_pending_bookings():
        print("\n=== Verifying Staff Dashboard Data ===")
        verify_staff_dashboard_data()
        
        print("\n=== Creating Test Pending Booking ===")
        answer = input("Would you like to create a test pending booking to make the buttons appear? (y/n): ")
        if answer.lower() == 'y':
            create_test_pending_booking()
        else:
            print("Skipped creating test booking.")
            
    print("\n=== How to Fix Staff Dashboard Accept/Decline Buttons ===")
    print("The most common reasons why Accept/Decline buttons are missing:")
    print("1. No bookings with status 'pending' in the database")
    print("2. The condition in the template only shows buttons for status exactly equal to 'pending'")
    print("\nTo fix this permanently:")
    print("1. Create bookings with status 'pending'")
    print("2. Make sure to set the status exactly to 'pending', not NULL or empty or different case")
    print("3. Check the template condition at line 669 to ensure it matches your actual booking status values")
    print("\nAfter running this script, restart your Flask application to see the changes.")
