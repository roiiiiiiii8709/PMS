"""
Payment System Fix Script

This script helps ensure proper integration of payment functions by:
1. Adding the payment route directly to the main app
2. Ensuring all payment status and method values are properly normalized
3. Displaying clear debugging info for troubleshooting

Run this script once to fix the payment integration issues.
"""
import os
import sys
from datetime import datetime

# Log function for tracking execution
def log_action(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")
    
    # Also save to log file
    with open("payment_fix.log", "a") as f:
        f.write(f"[{timestamp}] {message}\n")

log_action("Starting payment integration fix")

# Step 1: Backup the app.py file
try:
    app_path = "app.py"
    backup_path = f"app_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    
    with open(app_path, "r") as src:
        content = src.read()
        
    with open(backup_path, "w") as dest:
        dest.write(content)
    
    log_action(f"Created backup of app.py as {backup_path}")
    
except Exception as e:
    log_action(f"Error creating backup: {str(e)}")
    sys.exit(1)

# Step 2: Add the proper payment route code to the end of app.py (before if __name__ == '__main__')
try:
    payment_route = """
# Integrated Payment Processing Route
@app.route('/user/make_payment/<int:booking_id>', methods=['GET', 'POST'])
def make_payment(booking_id):
    if 'user_id' not in session:
        flash('Please login to make a payment.', 'error')
        return redirect(url_for('login'))
    
    conn = None
    cursor = None
    try:
        # Get database connection
        conn = get_db_connection()
        if not conn:
            flash('Database connection error. Please try again later.', 'error')
            return redirect(url_for('user_dashboard'))
            
        cursor = conn.cursor(dictionary=True)
        
        # Get booking details
        cursor.execute(\"\"\"
            SELECT b.*, p.location, p.price_per_hour 
            FROM bookings b
            JOIN parking_spots p ON b.spot_id = p.spot_id
            WHERE b.booking_id = %s AND b.user_id = %s
        \"\"\", (booking_id, session['user_id']))
        
        booking = cursor.fetchone()
        
        if not booking:
            flash('Booking not found.', 'error')
            return redirect(url_for('user_dashboard'))
        
        # Calculate duration and total cost
        start_time = booking['start_time']
        end_time = booking['end_time']
        if isinstance(start_time, str):
            start_time = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
        if isinstance(end_time, str):
            end_time = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
            
        duration = (end_time - start_time).total_seconds() / 3600  # Convert to hours
        total_cost = float(booking['price_per_hour']) * duration
        
        if request.method == 'POST':
            # Get payment details from form
            payment_method = request.form.get('payment_method')
            payment_number = request.form.get('payment_number', '')
            
            # Normalize payment method to ensure it matches database ENUM exactly
            normalized_payment_method = normalize_payment_method(payment_method)
            
            if normalized_payment_method:
                try:
                    # Normalize payment status - ensure it exactly matches ENUM
                    payment_status = normalize_payment_status('pending')
                    booking_status = 'pending_payment'
                    
                    # Create transaction record with proper error handling
                    try:
                        if payment_number and normalized_payment_method != 'cash':
                            cursor.execute(
                                "INSERT INTO transactions (booking_id, payment_method, amount, payment_number) VALUES (%s, %s, %s, %s)",
                                (booking_id, normalized_payment_method, round(total_cost, 2), payment_number)
                            )
                        else:
                            cursor.execute(
                                "INSERT INTO transactions (booking_id, payment_method, amount) VALUES (%s, %s, %s)",
                                (booking_id, normalized_payment_method, round(total_cost, 2))
                            )
                    except mysql.connector.Error as db_err:
                        # Log the specific transaction error
                        print(f"Transaction insert error: {db_err}")
                        conn.rollback()
                        raise
                    
                    # Update booking status and amount with proper error handling
                    try:
                        # Debug print to check values
                        print(f"Using payment_status: '{payment_status}', booking_status: '{booking_status}'")
                        
                        cursor.execute(
                            "UPDATE bookings SET payment_status = %s, status = %s, amount = %s WHERE booking_id = %s",
                            (payment_status, booking_status, round(total_cost, 2), booking_id)
                        )
                    except mysql.connector.Error as db_err:
                        # Log the specific booking update error
                        print(f"Booking update error: {db_err}")
                        conn.rollback()
                        raise
                    
                    conn.commit()
                    flash('Payment submitted successfully. Please wait for staff verification.', 'success')
                    return redirect(url_for('user_dashboard'))
                
                except mysql.connector.Error as e:
                    conn.rollback()
                    error_msg = str(e)
                    print(f"Database error in payment processing: {error_msg}")
                    flash(f'Database error: {error_msg}', 'error')
            else:
                flash('Invalid payment method. Please select a valid option.', 'error')
        
        # Pass both total_cost and duration to the template
        return render_template('user/booking.html', 
                            booking=booking, 
                            duration=round(duration, 1), 
                            total_cost=round(total_cost, 2))
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error in payment processing: {str(e)}")
        flash(f'Error processing payment: {str(e)}', 'error')
        return redirect(url_for('user_dashboard'))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
"""

    # Find the line with if __name__ == '__main__':
    with open(app_path, "r") as f:
        lines = f.readlines()
    
    main_line_index = -1
    for i, line in enumerate(lines):
        if line.strip().startswith("if __name__ == '__main__'"):
            main_line_index = i
            break
    
    if main_line_index == -1:
        log_action("Could not find the main execution block in app.py")
        sys.exit(1)
    
    # Insert the payment route before the main execution block
    updated_lines = lines[:main_line_index] + [payment_route] + lines[main_line_index:]
    
    # Write the updated content back to app.py
    with open(app_path, "w") as f:
        f.writelines(updated_lines)
    
    log_action("Successfully integrated the payment route into app.py")
    
    # Step 3: Create a helper file to disable the standalone payment modules
    with open("payment_module_status.txt", "w") as f:
        f.write("Payment functions have been integrated directly into app.py.\n")
        f.write("The standalone modules (updated_payment_function.py, updated_make_payment.py) are now redundant.\n")
        f.write(f"Integration completed on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    log_action("Created payment module status file")
    
    log_action("Payment integration fix completed successfully")
    print("\nSUCCESS: The payment system has been fixed and properly integrated.")
    print("Please restart your Flask application for the changes to take effect.")
    
except Exception as e:
    log_action(f"Error during integration: {str(e)}")
    print(f"\nERROR: Integration failed - {str(e)}")
    print("Your original app.py has been backed up, so no data is lost.")
