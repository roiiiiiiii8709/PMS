"""
Fix Missing Tables Script

This script checks for missing tables in the Parking Management System
database and creates only the ones that are missing.
"""
import mysql.connector
from db import get_db_connection, full_db_config

def create_activity_log_tables():
    """Create the activity log tables if they don't exist"""
    print("Creating missing activity log tables...")
    
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to database")
        return False
    
    cursor = conn.cursor()
    
    # Check if admin_activity_log exists
    cursor.execute("SHOW TABLES LIKE 'admin_activity_log'")
    if not cursor.fetchone():
        print("Creating admin_activity_log table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin_activity_log (
                log_id INT AUTO_INCREMENT PRIMARY KEY,
                admin_id INT NOT NULL,
                action_type VARCHAR(50) NOT NULL,
                action_details TEXT,
                booking_id INT,
                action_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (admin_id) REFERENCES admins(admin_id)
            )
        """)
        print("Admin activity log table created successfully")
    else:
        print("Admin activity log table already exists")
    
    # Check if staff_activity_log exists
    cursor.execute("SHOW TABLES LIKE 'staff_activity_log'")
    if not cursor.fetchone():
        print("Creating staff_activity_log table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS staff_activity_log (
                log_id INT AUTO_INCREMENT PRIMARY KEY,
                staff_id INT NOT NULL,
                action_type VARCHAR(50) NOT NULL,
                action_details TEXT,
                booking_id INT,
                action_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (staff_id) REFERENCES staff(staff_id)
            )
        """)
        print("Staff activity log table created successfully")
    else:
        print("Staff activity log table already exists")
    
    # Ensure we have at least one admin user
    cursor.execute("SELECT COUNT(*) FROM admins")
    admin_count = cursor.fetchone()[0]
    if admin_count == 0:
        print("No admin users found. Creating default admin user...")
        cursor.execute("""
            INSERT INTO admins (username, password, email) VALUES 
            ('admin', 'admin123', 'admin@example.com')
        """)
        print("Default admin user created with username 'admin' and password 'admin123'")
    
    # Ensure we have at least one staff user
    cursor.execute("SELECT COUNT(*) FROM staff")
    staff_count = cursor.fetchone()[0]
    if staff_count == 0:
        print("No staff users found. Creating default staff user...")
        cursor.execute("""
            INSERT INTO staff (username, password, email, phone) VALUES 
            ('staff', 'staff123', 'staff@example.com', '1234567890')
        """)
        print("Default staff user created with username 'staff' and password 'staff123'")
    
    # Commit changes
    conn.commit()
    cursor.close()
    conn.close()
    
    print("All missing tables have been created successfully!")
    return True

if __name__ == "__main__":
    print("Fixing missing tables in the Parking Management System database...\n")
    success = create_activity_log_tables()
    
    if success:
        print("\nSUCCESS: Database setup is now complete!")
        print("You can now run the application with: python app.py")
    else:
        print("\nERROR: Failed to complete database setup.")
        print("Make sure MySQL is running in XAMPP and try again.")
