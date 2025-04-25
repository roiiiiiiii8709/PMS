"""
Authentication routes for the Parking Management System
Implements separate registration for users, staff, and admin
Along with forgot password functionality
"""
from flask import redirect, url_for, render_template, request, flash, session
from db import get_db_connection
import random
import string

def register_routes(app):
    """Register all authentication routes with the Flask app"""
    
    @app.route('/register_user', methods=['GET', 'POST'])
    def register_user():
        if request.method == 'POST':
            username = request.form['username']
            email = request.form['email']
            phone = request.form['phone']
            password = request.form['password']
            confirm_password = request.form['confirm_password']
            
            # Validate phone number length
            if len(phone) < 11:
                flash('Phone number must be at least 11 digits', 'error')
                return render_template('register_user.html')
                
            if password != confirm_password:
                flash('Passwords do not match', 'error')
                return render_template('register_user.html')
            
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Check if username already exists
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                flash('Username already exists. Please choose a different one.', 'error')
                return render_template('register_user.html')
            
            # Check if email already exists
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                flash('Email already registered. Please use a different one.', 'error')
                return render_template('register_user.html')
            
            # Insert new user
            cursor.execute(
                "INSERT INTO users (username, email, phone, password) VALUES (%s, %s, %s, %s)",
                (username, email, phone, password)
            )
            
            conn.commit()
            cursor.close()
            conn.close()
            
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))
        
        return render_template('register_user.html')
    
    @app.route('/register_staff', methods=['GET', 'POST'])
    def register_staff():
        if request.method == 'POST':
            username = request.form['username']
            email = request.form['email']
            phone = request.form['phone']
            employee_id = request.form['employee_id']
            department = request.form['department']
            password = request.form['password']
            confirm_password = request.form['confirm_password']
            
            # Validate phone number length
            if len(phone) < 11:
                flash('Phone number must be at least 11 digits', 'error')
                return render_template('register_staff.html')
                
            if password != confirm_password:
                flash('Passwords do not match', 'error')
                return render_template('register_staff.html')
            
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Check if username already exists
            cursor.execute("SELECT * FROM staff WHERE username = %s", (username,))
            if cursor.fetchone():
                flash('Username already exists. Please choose a different one.', 'error')
                return render_template('register_staff.html')
            
            # Check if email already exists
            cursor.execute("SELECT * FROM staff WHERE email = %s", (email,))
            if cursor.fetchone():
                flash('Email already registered. Please use a different one.', 'error')
                return render_template('register_staff.html')
            
            # Check if employee ID already exists
            cursor.execute("SELECT * FROM staff WHERE employee_id = %s", (employee_id,))
            if cursor.fetchone():
                flash('Employee ID already registered. Please check with administrator.', 'error')
                return render_template('register_staff.html')
            
            # Insert new staff member
            cursor.execute(
                "INSERT INTO staff (username, email, phone, employee_id, department, password) VALUES (%s, %s, %s, %s, %s, %s)",
                (username, email, phone, employee_id, department, password)
            )
            
            conn.commit()
            cursor.close()
            conn.close()
            
            flash('Staff registration successful! Please wait for admin approval before logging in.', 'success')
            return redirect(url_for('login'))
        
        return render_template('register_staff.html')
    
    @app.route('/register_admin', methods=['GET', 'POST'])
    def register_admin():
        if request.method == 'POST':
            username = request.form['username']
            email = request.form['email']
            phone = request.form['phone']
            admin_level = request.form['admin_level']
            admin_code = request.form['admin_code']
            password = request.form['password']
            confirm_password = request.form['confirm_password']
            
            # Validate admin registration code (this should be a secure code known only to authorized personnel)
            valid_admin_code = "ADMIN123"  # In production, this should be stored securely
            if admin_code != valid_admin_code:
                flash('Invalid admin registration code', 'error')
                return render_template('register_admin.html')
            
            # Validate phone number length
            if len(phone) < 11:
                flash('Phone number must be at least 11 digits', 'error')
                return render_template('register_admin.html')
                
            if password != confirm_password:
                flash('Passwords do not match', 'error')
                return render_template('register_admin.html')
            
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Check if username already exists
            cursor.execute("SELECT * FROM admins WHERE username = %s", (username,))
            if cursor.fetchone():
                flash('Username already exists. Please choose a different one.', 'error')
                return render_template('register_admin.html')
            
            # Check if email already exists
            cursor.execute("SELECT * FROM admins WHERE email = %s", (email,))
            if cursor.fetchone():
                flash('Email already registered. Please use a different one.', 'error')
                return render_template('register_admin.html')
            
            # Insert new admin
            cursor.execute(
                "INSERT INTO admins (username, email, phone, admin_level, password) VALUES (%s, %s, %s, %s, %s)",
                (username, email, phone, admin_level, password)
            )
            
            conn.commit()
            cursor.close()
            conn.close()
            
            flash('Admin registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))
        
        return render_template('register_admin.html')
    
    @app.route('/forgot_password', methods=['GET', 'POST'])
    def forgot_password():
        if request.method == 'POST':
            email = request.form['email']
            user_type = request.form['user_type']
            
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Find user by email based on user type
            if user_type == 'user':
                cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            elif user_type == 'staff':
                cursor.execute("SELECT * FROM staff WHERE email = %s", (email,))
            elif user_type == 'admin':
                cursor.execute("SELECT * FROM admins WHERE email = %s", (email,))
            
            user = cursor.fetchone()
            
            if not user:
                flash('Email not found in our records.', 'error')
                return render_template('forgot_password.html')
            
            # Generate reset token (would be sent via email in a real application)
            reset_token = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
            
            # Save token with expiry time
            cursor.execute(
                "INSERT INTO password_resets (email, token, user_type, created_at) VALUES (%s, %s, %s, NOW())",
                (email, reset_token, user_type)
            )
            
            conn.commit()
            cursor.close()
            conn.close()
            
            # In a real application, you would send an email with the reset link
            # For testing, we'll just show the link
            reset_link = url_for('reset_password', token=reset_token, _external=True)
            
            flash('Password reset link has been generated. In a real application, this would be sent to your email.', 'success')
            flash(f'Reset link: {reset_link}', 'info')
            
            return redirect(url_for('login'))
        
        return render_template('forgot_password.html')
    
    @app.route('/reset_password/<token>', methods=['GET', 'POST'])
    def reset_password(token):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Find token in database
        cursor.execute(
            "SELECT * FROM password_resets WHERE token = %s AND created_at > DATE_SUB(NOW(), INTERVAL 1 DAY)",
            (token,)
        )
        
        reset_request = cursor.fetchone()
        
        if not reset_request:
            cursor.close()
            conn.close()
            flash('Invalid or expired password reset link.', 'error')
            return redirect(url_for('login'))
        
        if request.method == 'POST':
            new_password = request.form['new_password']
            confirm_password = request.form['confirm_password']
            
            if new_password != confirm_password:
                flash('Passwords do not match.', 'error')
                return render_template('reset_password.html', token=token)
            
            # Update password based on user type
            if reset_request['user_type'] == 'user':
                cursor.execute(
                    "UPDATE users SET password = %s WHERE email = %s",
                    (new_password, reset_request['email'])
                )
            elif reset_request['user_type'] == 'staff':
                cursor.execute(
                    "UPDATE staff SET password = %s WHERE email = %s",
                    (new_password, reset_request['email'])
                )
            elif reset_request['user_type'] == 'admin':
                cursor.execute(
                    "UPDATE admins SET password = %s WHERE email = %s",
                    (new_password, reset_request['email'])
                )
            
            # Delete used token
            cursor.execute("DELETE FROM password_resets WHERE token = %s", (token,))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            flash('Your password has been reset successfully. You can now log in with your new password.', 'success')
            return redirect(url_for('login'))
        
        cursor.close()
        conn.close()
        
        return render_template('reset_password.html', token=token)

# Add this code to your app.py to register these routes:
# from auth_routes import register_routes
# register_routes(app)
