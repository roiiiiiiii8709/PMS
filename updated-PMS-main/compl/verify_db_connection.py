"""
Database Connection Verification Script

This script checks the connection to the MySQL database in XAMPP,
creates the database and tables if needed, and verifies the overall
configuration of the Parking Management System.

Run this script before starting the main application to ensure
everything is set up correctly.
"""
import os
import sys
import time
from db import get_db_connection, initialize_database

def print_section(title):
    """Print a section header to make output more readable"""
    separator = "=" * 60
    print(f"\n{separator}")
    print(f" {title} ".center(60))
    print(f"{separator}\n")

def test_connection():
    """Test the database connection and report status"""
    print_section("TESTING DATABASE CONNECTION")
    print("Attempting to connect to MySQL...")
    
    # Try to connect to the database
    conn = get_db_connection()
    
    if conn:
        print("\n[SUCCESS] Connected to MySQL database!")
        
        # Check if all required tables exist
        cursor = conn.cursor()
        tables = [
            "users", "staff", "admins", "parking_spots", 
            "bookings", "transactions", 
            "admin_activity_log", "staff_activity_log"
        ]
        
        all_tables_exist = True
        for table in tables:
            cursor.execute(f"SHOW TABLES LIKE '{table}'")
            result = cursor.fetchone()
            if result:
                print(f"  [OK] Table '{table}' exists")
            else:
                print(f"  [MISSING] Table '{table}' is missing!")
                all_tables_exist = False
        
        if all_tables_exist:
            print("\n[SUCCESS] All required tables exist!")
        else:
            print("\n[WARNING] Some tables are missing. Attempting to create them...")
            initialize_database()
        
        # Close connection
        conn.close()
        
        return True
    else:
        print("\n[ERROR] Failed to connect to MySQL database!")
        print("\nPossible causes:")
        print("  1. MySQL service is not running in XAMPP")
        print("  2. MySQL username/password is incorrect")
        print("  3. MySQL port is different or blocked")
        
        return False

def check_xampp():
    """Check if XAMPP is likely to be running"""
    print_section("CHECKING XAMPP STATUS")
    
    # Check common XAMPP processes
    import subprocess
    try:
        # Check for the MySQL process
        result = subprocess.run("tasklist | findstr mysql", shell=True, text=True, capture_output=True)
        if "mysqld.exe" in result.stdout:
            print("[OK] MySQL process is running in XAMPP")
        else:
            print("[ERROR] MySQL process not detected! Start MySQL in XAMPP Control Panel")
        
        # Check for the Apache process
        result = subprocess.run("tasklist | findstr apache", shell=True, text=True, capture_output=True)
        if "httpd.exe" in result.stdout:
            print("[OK] Apache process is running in XAMPP")
        else:
            print("[WARNING] Apache process not detected. This is needed if using phpMyAdmin")
    except Exception as e:
        print(f"Error checking XAMPP processes: {str(e)}")

def check_app_requirements():
    """Check if all requirements for the PMS application are met"""
    print_section("CHECKING APPLICATION REQUIREMENTS")
    
    # Check for templates directory
    if os.path.exists("templates"):
        print("[OK] Templates directory exists")
    else:
        print("[ERROR] Templates directory is missing!")
    
    # Check for static directory
    if os.path.exists("static"):
        print("[OK] Static files directory exists")
    else:
        print("[ERROR] Static files directory is missing!")
    
    # Check for essential Python files
    essential_files = ["app.py", "db.py"]
    for file in essential_files:
        if os.path.exists(file):
            print(f"[OK] {file} exists")
        else:
            print(f"[ERROR] {file} is missing!")

def show_instructions():
    """Display instructions for starting the application"""
    print_section("NEXT STEPS")
    
    print("To start the Parking Management System:")
    print("1. Make sure MySQL is running in XAMPP Control Panel")
    print("2. Run the Flask application with:")
    print("   > python app.py")
    print("\nLogin credentials:")
    print("- Admin: username 'admin', password 'admin123'")
    print("- Staff: username 'staff', password 'staff123'")
    print("- Users: Register new accounts through the application")

if __name__ == "__main__":
    print_section("PARKING MANAGEMENT SYSTEM - VERIFICATION UTILITY")
    print("This utility verifies your database connection and application setup.")
    
    # Check XAMPP status
    check_xampp()
    
    # Test database connection and tables
    db_ok = test_connection()
    
    # Check app requirements
    check_app_requirements()
    
    # Show next steps
    show_instructions()
    
    # Final status
    print_section("VERIFICATION COMPLETE")
    if db_ok:
        print("[SUCCESS] Your system appears to be configured correctly!")
        print("   You can now start the application with 'python app.py'")
    else:
        print("[ERROR] Database connection issues need to be resolved!")
        print("   Make sure MySQL is running in XAMPP before starting the application.")
