"""
Fix the foreign key constraint error when cancelling bookings in the user dashboard
"""
from db import get_db_connection

def fix_cancel_booking_function():
    """
    Fixes the cancel_booking function in app.py to prevent the foreign key constraint error
    The error occurs because we're trying to add a record to staff_activity_log with staff_id = 0,
    but 0 doesn't exist in the staff table
    """
    print("To fix the foreign key constraint error when cancelling bookings, update the cancel_booking function in app.py:")
    print("\nLocate this code in the function (around line 480-490):")
    print("""
    # Add history entry for the cancelled booking
    cursor.execute(\"""
        INSERT INTO staff_activity_log (staff_id, action_type, action_details, booking_id)
        VALUES (%s, %s, %s, %s)
    \""", (0, 'cancel', f"Booking #{booking_id} cancelled by user", booking_id))
    """)
    
    print("\nReplace it with this code:")
    print("""
    # Use a transaction type log instead of staff activity log for user cancellations
    cursor.execute(\"""
        INSERT INTO transactions (booking_id, payment_method, amount, payment_status, notes)
        VALUES (%s, %s, %s, %s, %s)
    \""", (booking_id, 'none', 0.00, 'cancelled', f"Booking cancelled by user"))
    """)
    
    # Alternatively, a more robust solution is to create a system_activity_log table
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Check if user_activity_log table exists
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM information_schema.tables 
            WHERE table_schema = DATABASE() 
            AND table_name = 'user_activity_log'
        """)
        
        table_exists = cursor.fetchone()['count'] > 0
        
        if not table_exists:
            print("\nAlternative solution - Create a user_activity_log table:")
            print("""
            # Execute this SQL to create a dedicated user activity log table:
            CREATE TABLE user_activity_log (
                log_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                action_type VARCHAR(50) NOT NULL,
                action_details TEXT,
                booking_id INT,
                action_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
            """)
            
            print("\nThen update the cancel_booking function to use the user_activity_log:")
            print("""
            # Add history entry for the cancelled booking
            cursor.execute(\"""
                INSERT INTO user_activity_log (user_id, action_type, action_details, booking_id)
                VALUES (%s, %s, %s, %s)
            \""", (session['user_id'], 'cancel', f"Booking #{booking_id} cancelled by user", booking_id))
            """)
        
        # Check if there's a valid staff member we can use
        cursor.execute("SELECT staff_id FROM staff LIMIT 1")
        staff = cursor.fetchone()
        
        if staff:
            print(f"\nAnother option - Use an existing staff ID:")
            print(f"""
            # Use a real staff ID instead of 0:
            cursor.execute(\"""
                INSERT INTO staff_activity_log (staff_id, action_type, action_details, booking_id)
                VALUES (%s, %s, %s, %s)
            \""", ({staff['staff_id']}, 'system', f"Booking #{booking_id} cancelled by user", booking_id))
            """)
            
    except Exception as e:
        print(f"Error checking database: {str(e)}")
        
    finally:
        cursor.close()
        conn.close()

def fix_booking_duration():
    """Fix the booking duration limit to allow 2-3 days instead of 24 hours"""
    print("\n\nTo change the booking duration limit from 24 hours to 2-3 days:")
    print("Locate the create_booking function in app.py and find the code that checks the duration (around line 380-390):")
    print("""
    # Calculate hours and check if exceeds 24 hours
    duration = (end_datetime - start_datetime).total_seconds() / 3600
    if duration > 24:
        flash('Booking duration cannot exceed 24 hours', 'error')
        return redirect(url_for('user_dashboard'))
    """)
    
    print("\nReplace it with this code to allow up to 72 hours (3 days):")
    print("""
    # Calculate hours and check if exceeds 72 hours (3 days)
    duration = (end_datetime - start_datetime).total_seconds() / 3600
    if duration > 72:
        flash('Booking duration cannot exceed 3 days', 'error')
        return redirect(url_for('user_dashboard'))
    """)

def update_user_profile_show_password():
    """Update the user profile template to show password toggle"""
    print("\n\nTo add a show/hide password toggle in the user profile page:")
    print("Add this JavaScript function to your user/profile.html template:")
    print("""
    <script>
        function togglePasswordVisibility(inputId) {
            var input = document.getElementById(inputId);
            if (input.type === "password") {
                input.type = "text";
            } else {
                input.type = "password";
            }
        }
    </script>
    """)
    
    print("\nThen update the password fields in your form to include show/hide buttons:")
    print("""
    <div class="form-group">
        <label for="current_password">Current Password</label>
        <div class="password-input-container">
            <input type="password" id="current_password" name="current_password">
            <button type="button" class="toggle-password" onclick="togglePasswordVisibility('current_password')">
                <i class="fa fa-eye"></i> Show
            </button>
        </div>
    </div>
    
    <div class="form-group">
        <label for="new_password">New Password</label>
        <div class="password-input-container">
            <input type="password" id="new_password" name="new_password">
            <button type="button" class="toggle-password" onclick="togglePasswordVisibility('new_password')">
                <i class="fa fa-eye"></i> Show
            </button>
        </div>
    </div>
    
    <div class="form-group">
        <label for="confirm_password">Confirm New Password</label>
        <div class="password-input-container">
            <input type="password" id="confirm_password" name="confirm_password">
            <button type="button" class="toggle-password" onclick="togglePasswordVisibility('confirm_password')">
                <i class="fa fa-eye"></i> Show
            </button>
        </div>
    </div>
    """)
    
    print("\nAdd this CSS for styling the password input container:")
    print("""
    <style>
        .password-input-container {
            position: relative;
            display: flex;
            align-items: center;
        }
        
        .toggle-password {
            margin-left: 10px;
            background: #f0f0f0;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 5px 10px;
            cursor: pointer;
        }
    </style>
    """)

def remove_pay_button_for_cancelled():
    """Remove the Pay button for cancelled bookings in user dashboard"""
    print("\n\nTo remove the Pay button for cancelled bookings in the user dashboard:")
    print("In the user/dashboard.html template, find the section that displays the Pay button in the Actions column (around line 150-170):")
    print("""
    <td>
        {% if booking.payment_status != 'paid' %}
            <a href="{{ url_for('payment', booking_id=booking.booking_id) }}" class="btn btn-primary btn-sm">Pay</a>
        {% endif %}
        
        {% if booking.status == 'pending' %}
            <a href="{{ url_for('cancel_booking', booking_id=booking.booking_id) }}" class="btn btn-danger btn-sm" onclick="return confirm('Are you sure you want to cancel this booking?')">Cancel</a>
        {% endif %}
    </td>
    """)
    
    print("\nReplace it with this code to also check if the booking is not cancelled:")
    print("""
    <td>
        {% if booking.payment_status != 'paid' and booking.status != 'cancelled' %}
            <a href="{{ url_for('payment', booking_id=booking.booking_id) }}" class="btn btn-primary btn-sm">Pay</a>
        {% endif %}
        
        {% if booking.status == 'pending' %}
            <a href="{{ url_for('cancel_booking', booking_id=booking.booking_id) }}" class="btn btn-danger btn-sm" onclick="return confirm('Are you sure you want to cancel this booking?')">Cancel</a>
        {% endif %}
    </td>
    """)

def fix_staff_dashboard_buttons():
    """Fix the staff dashboard to properly display Accept/Decline buttons"""
    print("\n\nTo ensure the staff dashboard always shows Accept/Decline buttons for pending bookings:")
    print("1. Update the staff dashboard query in the staff_dashboard function (around line 580):")
    print("""
    # Fetch pending bookings with user information
    cursor.execute(\"""
        SELECT b.*, u.username, u.email, p.location, p.price_per_hour
        FROM bookings b
        JOIN users u ON b.user_id = u.user_id
        JOIN parking_spots p ON b.spot_id = p.spot_id
        WHERE b.status = 'pending'
        ORDER BY b.start_time ASC  -- Show nearest upcoming bookings first
    \""")
    """)
    
    print("\n2. Make sure you have bookings with status exactly 'pending', not NULL or empty or 'pending_payment'")
    print("\n3. In the staff/dashboard.html template, modify the condition that shows the Accept/Decline buttons to include 'pending_payment' status:")
    print("""
    {% if booking.status == 'pending' or booking.status == 'pending_payment' %}
        {% if booking.spot_is_occupied or booking.has_time_conflict %}
            <!-- Only show Decline button for conflicts -->
            <button onclick="confirmAction('decline', '{{ booking.booking_id }}')" 
               class="action-button decline-button">
                ❌ Decline
            </button>
        {% else %}
            <button onclick="confirmAction('approve', '{{ booking.booking_id }}')" 
               class="action-button approve-button">
                ✅ Accept
            </button>
            <button onclick="confirmAction('decline', '{{ booking.booking_id }}')" 
               class="action-button decline-button">
                ❌ Decline
            </button>
        {% endif %}
    {% else %}
        <span class="text-muted">No actions available</span>
    {% endif %}
    """)
    
    print("\n4. Add separate section in the staff dashboard to display confirmed bookings:")
    print("""
    <div class="panel">
        <h3 class="panel-title">Confirmed Bookings</h3>
        {% if confirmed_bookings %}
            <div class="table-container">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Booking ID</th>
                            <th>User</th>
                            <th>Location</th>
                            <th>Start Time</th>
                            <th>End Time</th>
                            <th>Status</th>
                            <th>Payment</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for booking in confirmed_bookings %}
                            <tr>
                                <td>{{ booking.booking_id }}</td>
                                <td>{{ booking.username }}</td>
                                <td>{{ booking.location }}</td>
                                <td>{{ booking.start_time }}</td>
                                <td>{{ booking.end_time }}</td>
                                <td>
                                    <span class="status-badge status-{{ booking.status }}">{{ booking.status }}</span>
                                </td>
                                <td>
                                    <span class="status-badge status-{{ booking.payment_status }}">{{ booking.payment_status }}</span>
                                    <button onclick="showPaymentDetails('{{ booking.booking_id }}')" class="detail-button">Details</button>
                                </td>
                                <td>
                                    {% if booking.status == 'confirmed' and booking.payment_status == 'paid' %}
                                        <a href="{{ url_for('staff_handle_entry_exit', booking_id=booking.booking_id, action_type='entry', redirect_to='staff_dashboard') }}" class="btn btn-action align-center">
                                            <span class="icon-margin">🚗</span> Handle Entry/Exit
                                        </a>
                                    {% else %}
                                        <span class="text-muted">Waiting for payment</span>
                                    {% endif %}
                                </td>
                            </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        {% else %}
            <p>No confirmed bookings available.</p>
        {% endif %}
    </div>
    """)

if __name__ == "__main__":
    print("Fixing User Dashboard Issues...\n")
    
    print("=== 1. Fix Foreign Key Constraint Error when Cancelling Bookings ===")
    fix_cancel_booking_function()
    
    print("\n=== 2. Fix Booking Duration Limit ===")
    fix_booking_duration()
    
    print("\n=== 3. Show Password in Change Password Form ===")
    update_user_profile_show_password()
    
    print("\n=== 4. Remove Pay Button for Cancelled Bookings ===")
    remove_pay_button_for_cancelled()
    
    print("\n=== 5. Fix Staff Dashboard Accept/Decline Buttons ===")
    fix_staff_dashboard_buttons()
    
    print("\nAll fixes have been provided. Follow the instructions to implement each fix.")
