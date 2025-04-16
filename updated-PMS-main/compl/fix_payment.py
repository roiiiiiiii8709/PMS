# In app.py, find the make_payment function and replace the SQL INSERT statement with this:

# REMOVE THIS LINE:
# cursor.execute(
#    "INSERT INTO transactions (booking_id, payment_method, amount, payment_number) VALUES (%s, %s, %s, %s)",
#    (booking_id, payment_method, round(total_cost, 2), payment_number)
# )

# USE THIS LINE INSTEAD:
cursor.execute(
    "INSERT INTO transactions (booking_id, payment_method, amount) VALUES (%s, %s, %s)",
    (booking_id, payment_method, round(total_cost, 2))
)

# Also, remove the payment_number variable:
# payment_number = request.form.get('payment_number')  # Remove or comment this line

# The complete function with these changes should look like this:
"""
@app.route('/user/make_payment/<int:booking_id>', methods=['GET', 'POST'])
def make_payment(booking_id):
    if 'user_id' not in session:
        flash('Please login to make a payment.', 'error')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Get booking details
        cursor.execute('''
            SELECT b.*, p.location, p.price_per_hour 
            FROM bookings b
            JOIN parking_spots p ON b.spot_id = p.spot_id
            WHERE b.booking_id = %s AND b.user_id = %s
        ''', (booking_id, session['user_id']))
        
        booking = cursor.fetchone()
        
        if not booking:
            flash('Booking not found.', 'error')
            return redirect(url_for('user_dashboard'))
        
        # Calculate duration and total cost
        duration = (booking['end_time'] - booking['start_time']).total_seconds() / 3600  # Convert to hours
        total_cost = float(booking['price_per_hour']) * duration
        
        if request.method == 'POST':
            payment_method = request.form.get('payment_method')
            
            if payment_method in ['cash', 'gcash', 'credit_card']:
                # Create transaction record
                cursor.execute(
                    "INSERT INTO transactions (booking_id, payment_method, amount) VALUES (%s, %s, %s)",
                    (booking_id, payment_method, round(total_cost, 2))
                )
                
                # Update booking status and amount
                cursor.execute(
                    "UPDATE bookings SET payment_status = 'pending', status = 'pending_payment', amount = %s WHERE booking_id = %s",
                    (round(total_cost, 2), booking_id)
                )
                
                conn.commit()
                flash('Payment submitted successfully. Please wait for staff verification.', 'success')
                return redirect(url_for('user_dashboard'))
            else:
                flash('Invalid payment method.', 'error')
        
        # Pass both total_cost and duration to the template
        return render_template('user/booking.html', 
                            booking=booking, 
                            duration=round(duration, 1), 
                            total_cost=round(total_cost, 2))
        
    except Exception as e:
        conn.rollback()
        flash(f'Error processing payment: {str(e)}', 'error')
        return redirect(url_for('user_dashboard'))
    finally:
        cursor.close()
        conn.close()
"""
