"""
Staff Booking Workflow Routes

This module contains the routes for handling booking approvals and rejections
by staff members. These routes should be imported into your main app.py file.
"""
from flask import redirect, url_for, flash, session
from db import get_db_connection
from datetime import datetime

def register_staff_routes(app):
    """Register all staff routes with the Flask app"""
    
    @app.route('/staff/approve_booking/<int:booking_id>')
    def staff_approve_booking(booking_id):
        """Approve a pending booking"""
        if 'staff_id' not in session:
            flash('Please login as staff to access this page.', 'error')
            return redirect(url_for('login'))
        
        conn = None
        cursor = None
        
        try:
            conn = get_db_connection()
            if not conn:
                flash('Database connection error.', 'error')
                return redirect(url_for('staff_dashboard'))
                    
            cursor = conn.cursor(dictionary=True)
            
            # First check if the booking exists and is in pending status
            cursor.execute("""
                SELECT b.*, p.spot_id, p.status as spot_status
                FROM bookings b
                JOIN parking_spots p ON b.spot_id = p.spot_id
                WHERE b.booking_id = %s AND b.status = 'pending'
            """, (booking_id,))
            
            booking = cursor.fetchone()
            
            if not booking:
                flash('Booking not found or already processed.', 'error')
                return redirect(url_for('staff_dashboard'))
            
            # Check for conflicts with other confirmed bookings
            cursor.execute("""
                SELECT COUNT(*) as count FROM bookings 
                WHERE spot_id = %s AND status = 'confirmed'
                AND ((start_time <= %s AND end_time >= %s) OR 
                     (start_time <= %s AND end_time >= %s) OR
                     (start_time >= %s AND end_time <= %s))
                AND booking_id != %s
            """, (booking['spot_id'], booking['start_time'], booking['start_time'], 
                  booking['end_time'], booking['end_time'], booking['start_time'], 
                  booking['end_time'], booking_id))
            
            result = cursor.fetchone()
            has_conflict = result['count'] > 0
            
            # Check if spot is currently occupied
            cursor.execute("""
                SELECT COUNT(*) as count FROM bookings 
                WHERE spot_id = %s AND status = 'entry'
                AND booking_id != %s
            """, (booking['spot_id'], booking_id))
            
            result = cursor.fetchone()
            is_occupied = result['count'] > 0
            
            if has_conflict:
                flash('Cannot approve booking due to time conflict with another confirmed booking.', 'error')
                return redirect(url_for('staff_dashboard'))
            
            if is_occupied and booking['start_time'] <= datetime.now():
                flash('Cannot approve booking as the spot is currently occupied.', 'error')
                return redirect(url_for('staff_dashboard'))
            
            # Update booking status to confirmed
            cursor.execute("""
                UPDATE bookings 
                SET status = 'confirmed'
                WHERE booking_id = %s
            """, (booking_id,))
            
            # Update parking spot status to reserved
            cursor.execute("""
                UPDATE parking_spots 
                SET status = 'reserved' 
                WHERE spot_id = %s
            """, (booking['spot_id'],))
            
            # Log staff activity
            cursor.execute("""
                INSERT INTO staff_activity_log 
                (staff_id, action_type, action_details, booking_id)
                VALUES (%s, %s, %s, %s)
            """, (session['staff_id'], 'approve', f"Approved booking #{booking_id}", booking_id))
            
            conn.commit()
            flash(f'Booking #{booking_id} has been approved successfully.', 'success')
            
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
    
    @app.route('/staff/decline_booking/<int:booking_id>')
    def staff_decline_booking(booking_id):
        """Decline a pending booking"""
        if 'staff_id' not in session:
            flash('Please login as staff to access this page.', 'error')
            return redirect(url_for('login'))
        
        conn = None
        cursor = None
        
        try:
            conn = get_db_connection()
            if not conn:
                flash('Database connection error.', 'error')
                return redirect(url_for('staff_dashboard'))
                    
            cursor = conn.cursor(dictionary=True)
            
            # First check if the booking exists and is in pending status
            cursor.execute("""
                SELECT b.*, p.spot_id
                FROM bookings b
                JOIN parking_spots p ON b.spot_id = p.spot_id
                WHERE b.booking_id = %s AND b.status = 'pending'
            """, (booking_id,))
            
            booking = cursor.fetchone()
            
            if not booking:
                flash('Booking not found or already processed.', 'error')
                return redirect(url_for('staff_dashboard'))
            
            # Update booking status to declined
            cursor.execute("""
                UPDATE bookings 
                SET status = 'cancelled' 
                WHERE booking_id = %s
            """, (booking_id,))
            
            # Update the spot status to available if there are no other active bookings
            cursor.execute("""
                SELECT COUNT(*) as active_count
                FROM bookings
                WHERE spot_id = %s
                AND status IN ('confirmed', 'pending', 'entry')
                AND booking_id != %s
            """, (booking['spot_id'], booking_id))
            
            result = cursor.fetchone()
            if result['active_count'] == 0:
                cursor.execute("""
                    UPDATE parking_spots 
                    SET status = 'available' 
                    WHERE spot_id = %s
                """, (booking['spot_id'],))
            
            # Log staff activity
            cursor.execute("""
                INSERT INTO staff_activity_log 
                (staff_id, action_type, action_details, booking_id)
                VALUES (%s, %s, %s, %s)
            """, (session['staff_id'], 'decline', f"Declined booking #{booking_id}", booking_id))
            
            conn.commit()
            flash(f'Booking #{booking_id} has been declined.', 'success')
            
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

# Add a route to view all confirmed bookings separately
    @app.route('/staff/confirmed_bookings')
    def staff_confirmed_bookings():
        """View all confirmed bookings"""
        if 'staff_id' not in session:
            flash('Please login as staff to access this page.', 'error')
            return redirect(url_for('login'))
        
        conn = None
        cursor = None
        confirmed_bookings = []
        
        try:
            conn = get_db_connection()
            if not conn:
                flash('Database connection error.', 'error')
                return redirect(url_for('staff_dashboard'))
                    
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
            
        except Exception as e:
            flash(f'Error loading confirmed bookings: {str(e)}', 'error')
        
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
                
        return render_template('staff/confirmed_bookings.html', 
                              confirmed_bookings=confirmed_bookings)
