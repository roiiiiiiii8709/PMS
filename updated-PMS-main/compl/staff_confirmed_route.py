"""
Add this route to your app.py file to handle confirmed bookings view
"""
from flask import Flask, render_template, redirect, url_for, flash, session
from db import get_db_connection

def staff_confirmed_bookings():
    """Route for staff to view all confirmed bookings"""
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
        cursor.execute("""
            SELECT b.*, u.username, u.email, p.location, p.price_per_hour
            FROM bookings b
            JOIN users u ON b.user_id = u.user_id
            JOIN parking_spots p ON b.spot_id = p.spot_id
            WHERE b.status = 'confirmed'
            ORDER BY b.start_time ASC
        """)
        confirmed_bookings = cursor.fetchall()
        
        # Get payment details for quick view
        cursor.execute("""
            SELECT t.*, b.booking_id
            FROM transactions t
            RIGHT JOIN bookings b ON t.booking_id = b.booking_id
            WHERE b.status = 'confirmed'
        """)
        payments = cursor.fetchall()
        
        for payment in payments:
            # Skip null entries from RIGHT JOIN
            if payment['booking_id'] is not None:
                payment_details[payment['booking_id']] = payment
                
    except Exception as e:
        flash(f'Error loading confirmed bookings: {str(e)}', 'error')
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    
    return render_template('staff/confirmed_bookings.html', 
                          confirmed_bookings=confirmed_bookings,
                          payment_details=payment_details)
