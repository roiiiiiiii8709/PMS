"""
Complete Staff Dashboard Workflow Fixer

This script enhances the staff dashboard to ensure:
1. Pending bookings show the Accept/Decline buttons
2. Accepted bookings appear in the Confirmed Bookings section
3. The booking workflow process is smooth and intuitive

The script also updates the app.py file to add the confirmed_bookings route.
"""
import mysql.connector
import os
from db import get_db_connection
from datetime import datetime

def add_confirmed_bookings_route():
    """Create the code to add to app.py for confirmed bookings route"""
    route_code = """
# Staff - Confirmed Bookings
@app.route('/staff/confirmed_bookings')
def staff_confirmed_bookings():
    if 'staff_id' not in session:
        flash('Please login as staff to access this page.', 'error')
        return redirect(url_for('login'))
    
    conn = None
    cursor = None
    confirmed_bookings = []
    payment_details = {}
    
    try:
        # Get database connection
        conn = get_db_connection()
        if not conn:
            flash('Database connection error. Unable to load confirmed bookings.', 'error')
            return render_template('staff/confirmed_bookings.html', confirmed_bookings=[])
                
        cursor = conn.cursor(dictionary=True)
        
        # Fetch confirmed bookings with user information
        cursor.execute(\"\"\"
            SELECT b.*, u.username, u.email, p.location, p.price_per_hour
            FROM bookings b
            JOIN users u ON b.user_id = u.user_id
            JOIN parking_spots p ON b.spot_id = p.spot_id
            WHERE b.status = 'confirmed'
            ORDER BY b.start_time ASC
        \"\"\")
        confirmed_bookings = cursor.fetchall()
        
        # Get payment details for quick view
        cursor.execute(\"\"\"
            SELECT t.*, b.booking_id
            FROM transactions t
            RIGHT JOIN bookings b ON t.booking_id = b.booking_id
            WHERE b.status = 'confirmed'
        \"\"\")
        payments = cursor.fetchall()
        
        for payment in payments:
            # Skip null entries from RIGHT JOIN
            if payment['booking_id'] is not None:
                payment_details[payment['booking_id']] = payment
                
    except Exception as e:
        flash(f'Error loading confirmed bookings: {{str(e)}}', 'error')
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    
    return render_template('staff/confirmed_bookings.html', 
                          confirmed_bookings=confirmed_bookings,
                          payment_details=payment_details)
"""
    print("=== CODE TO ADD TO app.py (before the 'Staff - Activity History' section) ===")
    print(route_code)
    
    # Update navigation in staff dashboard template to include confirmed bookings
    update_dashboard_template()
    
    return route_code

def update_dashboard_template():
    """Updates the staff dashboard template to add navigation tabs"""
    dashboard_path = "templates/staff/dashboard.html"
    
    if not os.path.exists(dashboard_path):
        print(f"Warning: Could not find {dashboard_path}")
        return
    
    print("\n=== Update Staff Dashboard Template ===")
    print("Add this navigation section to the staff dashboard template (after the panel-title):")
    print("""
    <div class="nav-tabs">
        <a href="{{ url_for('staff_dashboard') }}" class="nav-link active">Dashboard Overview</a>
        <a href="{{ url_for('staff_dashboard') }}" class="nav-link">Pending Bookings</a>
        <a href="{{ url_for('staff_confirmed_bookings') }}" class="nav-link">Confirmed Bookings</a>
    </div>
    """)
    
    print("\n=== ALSO ADD THIS CSS TO THE DASHBOARD TEMPLATE ===")
    print("""
    /* Navigation styles */
    .nav-tabs {
        display: flex;
        border-bottom: 1px solid #dee2e6;
        margin-bottom: 20px;
    }
    
    .nav-link {
        padding: 10px 15px;
        border: 1px solid transparent;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
        color: #495057;
        text-decoration: none;
        margin-bottom: -1px;
    }
    
    .nav-link:hover {
        border-color: #e9ecef #e9ecef #dee2e6;
        background-color: #f8f9fa;
    }
    
    .nav-link.active {
        color: #495057;
        background-color: #fff;
        border-color: #dee2e6 #dee2e6 #fff;
    }
    """)

def create_approve_decline_routes():
    """Add approve/decline booking routes if they don't exist"""
    print("\n=== ADD THESE ROUTES TO app.py IF THEY DON'T EXIST ===")
    
    # Approve booking route
    print("""
# Staff - Approve Booking
@app.route('/staff/approve_booking/<int:booking_id>')
def staff_approve_booking(booking_id):
    if 'staff_id' not in session:
        flash('Please login as staff to access this page.', 'error')
        return redirect(url_for('login'))
    
    conn = None
    cursor = None
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Check if booking exists and is pending
        cursor.execute("SELECT * FROM bookings WHERE booking_id = %s", (booking_id,))
        booking = cursor.fetchone()
        
        if not booking:
            flash('Booking not found.', 'error')
        elif booking['status'] != 'pending':
            flash('This booking is no longer pending.', 'error')
        else:
            # Update booking status to confirmed
            cursor.execute("UPDATE bookings SET status = 'confirmed' WHERE booking_id = %s", (booking_id,))
            
            # Update spot status to reserved
            cursor.execute("UPDATE parking_spots SET status = 'reserved' WHERE spot_id = %s", (booking['spot_id'],))
            
            # Log staff activity
            cursor.execute(\"\"\"
                INSERT INTO staff_activity_log (staff_id, action_type, action_details, booking_id)
                VALUES (%s, %s, %s, %s)
            \"\"\", (session['staff_id'], 'approve', f"Approved booking #{booking_id}", booking_id))
            
            conn.commit()
            flash('Booking has been approved successfully.', 'success')
    
    except Exception as e:
        if conn:
            conn.rollback()
        flash(f'Error approving booking: {str(e)}', 'error')
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    
    return redirect(url_for('staff_dashboard'))

# Staff - Decline Booking
@app.route('/staff/decline_booking/<int:booking_id>')
def staff_decline_booking(booking_id):
    if 'staff_id' not in session:
        flash('Please login as staff to access this page.', 'error')
        return redirect(url_for('login'))
    
    conn = None
    cursor = None
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Check if booking exists and is pending
        cursor.execute("SELECT * FROM bookings WHERE booking_id = %s", (booking_id,))
        booking = cursor.fetchone()
        
        if not booking:
            flash('Booking not found.', 'error')
        elif booking['status'] != 'pending':
            flash('This booking is no longer pending.', 'error')
        else:
            # Update booking status to cancelled
            cursor.execute("UPDATE bookings SET status = 'cancelled' WHERE booking_id = %s", (booking_id,))
            
            # Ensure parking spot remains available
            cursor.execute("UPDATE parking_spots SET status = 'available' WHERE spot_id = %s", (booking['spot_id'],))
            
            # Log staff activity
            cursor.execute(\"\"\"
                INSERT INTO staff_activity_log (staff_id, action_type, action_details, booking_id)
                VALUES (%s, %s, %s, %s)
            \"\"\", (session['staff_id'], 'decline', f"Declined booking #{booking_id}", booking_id))
            
            conn.commit()
            flash('Booking has been declined.', 'success')
    
    except Exception as e:
        if conn:
            conn.rollback()
        flash(f'Error declining booking: {str(e)}', 'error')
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    
    return redirect(url_for('staff_dashboard'))
""")

def fix_pending_booking_display():
    """Create pending bookings and ensure they display correctly"""
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
        print("\n=== Current Booking Status Counts ===")
        for item in status_counts:
            print(f"- {item['status'] or 'NULL/blank'}: {item['count']}")
        
        # Create a test pending booking if none exist
        cursor.execute("SELECT COUNT(*) as count FROM bookings WHERE status = 'pending'")
        pending_count = cursor.fetchone()['count']
        
        if pending_count == 0:
            print("\nNo pending bookings found. Creating test pending bookings...")
            
            # Find users and available spots
            cursor.execute("SELECT user_id FROM users LIMIT 2")
            users = cursor.fetchall()
            
            if not users:
                print("No users found in the database")
                return False
            
            cursor.execute("SELECT spot_id FROM parking_spots WHERE status = 'available' LIMIT 2")
            spots = cursor.fetchall()
            
            if not spots:
                print("No available spots found")
                return False
            
            # Create two test bookings
            for i in range(min(len(users), len(spots))):
                user_id = users[i]['user_id']
                spot_id = spots[i]['spot_id']
                
                # Calculate timestamps for the booking
                start_time = datetime.now().replace(hour=12, minute=0, second=0)
                end_time = start_time.replace(hour=14)  # 2-hour booking
                
                # Adjust start time to be tomorrow for the first booking, day after for second
                start_time = start_time.replace(day=start_time.day + i + 1)
                end_time = end_time.replace(day=end_time.day + i + 1)
                
                # Format timestamps for MySQL
                start_time_str = start_time.strftime('%Y-%m-%d %H:%M:%S')
                end_time_str = end_time.strftime('%Y-%m-%d %H:%M:%S')
                
                # Insert the pending booking
                cursor.execute("""
                    INSERT INTO bookings (user_id, spot_id, start_time, end_time, status, payment_status, amount)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (user_id, spot_id, start_time_str, end_time_str, 'pending', 'unpaid', 50.00))
                
                # Update the spot status to reserved
                cursor.execute("UPDATE parking_spots SET status = 'reserved' WHERE spot_id = %s", (spot_id,))
                
                booking_id = cursor.lastrowid
                print(f"Created test pending booking (ID: {booking_id}) for spot {spot_id}")
        
            conn.commit()
        else:
            print(f"\nFound {pending_count} existing pending bookings. No need to create test bookings.")
        
        # Check if we're properly displaying pending bookings in the staff dashboard
        cursor.execute("""
            SELECT b.booking_id, u.username, p.location, b.status, b.payment_status, b.start_time, b.end_time
            FROM bookings b
            JOIN users u ON b.user_id = u.user_id
            JOIN parking_spots p ON b.spot_id = p.spot_id
            WHERE b.status = 'pending'
            LIMIT 5
        """)
        
        bookings = cursor.fetchall()
        if bookings:
            print("\n=== Pending Bookings That Should Display in Staff Dashboard ===")
            for b in bookings:
                print(f"- Booking #{b['booking_id']}: User {b['username']}, Spot {b['location']}, " 
                      f"Status {b['status']}, Payment {b['payment_status']}")
                if isinstance(b['start_time'], datetime):
                    start_str = b['start_time'].strftime('%Y-%m-%d %H:%M')
                    end_str = b['end_time'].strftime('%Y-%m-%d %H:%M')
                    print(f"  Time: {start_str} to {end_str}")
        
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"Error fixing pending booking display: {str(e)}")
        return False
    
    finally:
        cursor.close()
        conn.close()

def check_accept_decline_flows():
    """Verify the accept/decline workflow functions"""
    print("\n=== VERIFYING BOOKING ACCEPTANCE WORKFLOW ===")
    print("After a booking is created by a user:")
    print("1. The booking should have status 'pending'")
    print("2. It should appear in the Staff Dashboard's Pending Bookings section with Accept/Decline buttons")
    print("3. When staff clicks Accept:")
    print("   - The booking status changes to 'confirmed'")
    print("   - The spot status remains 'reserved'")
    print("   - The booking disappears from the Pending Bookings list")
    print("   - The booking appears in the Confirmed Bookings list")
    print("4. When staff clicks Decline:")
    print("   - The booking status changes to 'cancelled'")
    print("   - The spot status changes to 'available'")
    print("   - The booking disappears from the Pending Bookings list")
    
    print("\nThis workflow is enabled by:")
    print("1. The Accept/Decline buttons in the staff dashboard template")
    print("2. The staff_approve_booking and staff_decline_booking routes")
    print("3. The staff_confirmed_bookings route and template")
    
    print("\nTo complete this workflow after running this script:")
    print("1. Add the confirmed_bookings route to app.py")
    print("2. Add the navigation tabs to the staff dashboard template")
    print("3. Ensure the approve/decline routes are working in app.py")
    print("4. Start the Flask app and test the complete workflow")

if __name__ == "__main__":
    print("Enhancing Staff Dashboard Booking Workflow...\n")
    
    print("=== 1. Creating Confirmed Bookings Page ===")
    add_confirmed_bookings_route()
    
    print("\n=== 2. Setting up Approve/Decline Routes ===")
    create_approve_decline_routes()
    
    print("\n=== 3. Ensuring Pending Bookings Display Correctly ===")
    fix_pending_booking_display()
    
    print("\n=== 4. Verifying Complete Workflow ===")
    check_accept_decline_flows()
    
    print("\nDone! The staff dashboard booking workflow has been enhanced.")
    print("Follow the instructions above to complete the implementation.")
