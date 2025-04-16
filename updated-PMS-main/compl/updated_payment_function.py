@app.route('/user/make_payment/<int:booking_id>', methods=['GET', 'POST'])
def make_payment(booking_id):
    if 'user_id' not in session:
        flash('Please login to make a payment.', 'error')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Get booking details
        cursor.execute("""
            SELECT b.*, p.location, p.price_per_hour 
            FROM bookings b
            JOIN parking_spots p ON b.spot_id = p.spot_id
            WHERE b.booking_id = %s AND b.user_id = %s
        """, (booking_id, session['user_id']))
        
        booking = cursor.fetchone()
        
        if not booking:
            flash('Booking not found.', 'error')
            return redirect(url_for('user_dashboard'))
        
        # Calculate duration and total cost
        # Convert database timestamps to datetime objects
        start_time = datetime.strptime(str(booking['start_time']), '%Y-%m-%d %H:%M:%S')
        end_time = datetime.strptime(str(booking['end_time']), '%Y-%m-%d %H:%M:%S')
        duration = (end_time - start_time).total_seconds() / 3600  # Convert to hours
        total_cost = float(booking['price_per_hour']) * duration
        
        if request.method == 'POST':
            payment_method = request.form.get('payment_method')
            
            # Use the normalize_payment_method function from app.py
            from app import normalize_payment_method
            normalized_payment_method = normalize_payment_method(payment_method)
            
            if normalized_payment_method:
                # Create transaction record
                payment_number = request.form.get('payment_number', '')
                
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
                
                # Update booking status and amount
                # Import normalize_payment_status to prevent data truncation errors
                from app import normalize_payment_status
                
                # Normalize payment status
                payment_status = normalize_payment_status('pending')
                booking_status = 'pending_payment'
                
                cursor.execute(
                    "UPDATE bookings SET payment_status = %s, status = %s, amount = %s WHERE booking_id = %s",
                    (payment_status, booking_status, round(total_cost, 2), booking_id)
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
