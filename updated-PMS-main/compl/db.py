import mysql.connector
from datetime import datetime

# Database Configuration
db_config = {
    'host': 'localhost',     # XAMPP uses localhost
    'user': 'root',          # Default XAMPP MySQL username
    'password': '',          # Default XAMPP empty password
    'port': 3306,            # Default MySQL port
    'connection_timeout': 10, # Longer timeout for XAMPP
    'raise_on_warnings': True,
    'auth_plugin': 'mysql_native_password'  # Ensures compatibility with XAMPP MySQL
}

# Create database if it doesn't exist
def create_database():
    try:
        conn = mysql.connector.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            port=db_config['port']
        )
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS parking_db")
        cursor.close()
        conn.close()
        print("Database 'parking_db' created or already exists.")
        return True
    except mysql.connector.Error as err:
        print(f"Error creating database: {err}")
        return False

# Full configuration with database
full_db_config = {
    **db_config,
    'database': 'parking_db'  # Database name
}

# Get Database Connection with improved error handling
def get_db_connection():
    attempts = 0
    max_attempts = 3
    last_error = None
    
    while attempts < max_attempts:
        try:
            # First try with full config
            try:
                conn = mysql.connector.connect(**full_db_config)
                conn.autocommit = True
                print("Database connected successfully!")
                return conn
            except mysql.connector.errors.ProgrammingError as pe:
                # Handle case where database doesn't exist yet
                if "Unknown database" in str(pe):
                    print(f"Database '{full_db_config['database']}' does not exist. Attempting to create it...")
                    create_database()
                    conn = mysql.connector.connect(**full_db_config)
                    conn.autocommit = True
                    print("Database created and connected successfully!")
                    # Initialize tables
                    initialize_tables(conn)
                    return conn
                else:
                    raise  # Re-raise if it's a different programming error
        except mysql.connector.Error as err:
            attempts += 1
            last_error = err
            print(f"Connection attempt {attempts} failed: {err}. {'Retrying...' if attempts < max_attempts else 'Giving up.'}")
            import time
            time.sleep(2)  # Give the server a moment to recover
            
    # All attempts failed
    error_msg = f"Failed to connect to MySQL after {max_attempts} attempts. Last error: {last_error}"
    print(error_msg)
    
    # Create an emergency fallback message
    with open("db_connection_error.log", "a") as f:
        import datetime
        f.write(f"{datetime.datetime.now()}: {error_msg}\n")
        
    return None

# Function to create users table
def create_users_table(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) NOT NULL,
            password VARCHAR(255) NOT NULL,
            email VARCHAR(100) NOT NULL,
            phone VARCHAR(15),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("Users table created or already exists.")

# Function to create staff table
def create_staff_table(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS staff (
            staff_id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) NOT NULL,
            password VARCHAR(255) NOT NULL,
            email VARCHAR(100) NOT NULL,
            phone VARCHAR(15),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("Staff table created or already exists.")

# Function to create admins table
def create_admins_table(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            admin_id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) NOT NULL,
            password VARCHAR(255) NOT NULL,
            email VARCHAR(100) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("Admins table created or already exists.")

# Function to create parking spots table
def create_parking_spots_table(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS parking_spots (
            spot_id INT AUTO_INCREMENT PRIMARY KEY,
            location VARCHAR(100) NOT NULL,
            status ENUM('available', 'occupied', 'reserved') DEFAULT 'available',
            price_per_hour DECIMAL(5, 2) NOT NULL
        )
    """)
    print("Parking spots table created or already exists.")

# Function to create bookings table
def create_bookings_table(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            booking_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            spot_id INT NOT NULL,
            start_time DATETIME NOT NULL,
            end_time DATETIME NOT NULL,
            entry_time DATETIME NULL,
            exit_time DATETIME NULL,
            status ENUM('pending', 'confirmed', 'cancelled', 'pending_payment', 'completed') DEFAULT 'pending',
            payment_status ENUM('paid', 'unpaid', 'pending', 'rejected') DEFAULT 'unpaid',
            amount DECIMAL(10, 2) DEFAULT 0.00,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (spot_id) REFERENCES parking_spots(spot_id)
        )
    """)
    print("Bookings table created or already exists.")

# Function to create transactions table
def create_transactions_table(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id INT AUTO_INCREMENT PRIMARY KEY,
            booking_id INT NOT NULL,
            payment_method ENUM('cash', 'gcash', 'credit_card') NOT NULL,
            amount DECIMAL(10, 2) NOT NULL,
            payment_number VARCHAR(50),
            transaction_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (booking_id) REFERENCES bookings(booking_id)
        )
    """)
    print("Transactions table created or already exists.")

# Function to create activity logs table
def create_activity_logs_table(cursor):
    # Create admin activity log table
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
    print("Admin activity log table created or already exists.")
    
    # Create staff activity log table
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
    print("Staff activity log table created or already exists.")

# Function to insert default parking spots
def insert_default_parking_spots(cursor):
    cursor.execute("SELECT COUNT(*) FROM parking_spots")
    spot_count = cursor.fetchone()[0]
    if spot_count == 0:
        cursor.execute("""
            INSERT INTO parking_spots (location, price_per_hour) VALUES 
            ('Section A - Spot 1', 5.00),
            ('Section A - Spot 2', 5.00),
            ('Section B - Spot 1', 4.50),
            ('Section B - Spot 2', 4.50),
            ('Section C - Spot 1', 4.00),
            ('Section C - Spot 2', 4.00)
        """)
        print("Default parking spots created.")
    else:
        print(f"Parking spots table already has {spot_count} records, skipping default data creation.")

# Function to insert default admin
def insert_default_admin(cursor):
    cursor.execute("SELECT COUNT(*) FROM admins")
    admin_count = cursor.fetchone()[0]
    if admin_count == 0:
        cursor.execute("""
            INSERT INTO admins (username, password, email) VALUES 
            ('admin', 'admin123', 'admin@example.com')
        """)
        print("Default admin user created with username 'admin' and password 'admin123'.")
    else:
        print(f"Admin table already has {admin_count} records, skipping default admin creation.")

# Function to insert default staff
def insert_default_staff(cursor):
    cursor.execute("SELECT COUNT(*) FROM staff")
    staff_count = cursor.fetchone()[0]
    if staff_count == 0:
        cursor.execute("""
            INSERT INTO staff (username, password, email, phone) VALUES 
            ('staff', 'staff123', 'staff@example.com', '1234567890')
        """)
        print("Default staff user created with username 'staff' and password 'staff123'.")
    else:
        print(f"Staff table already has {staff_count} records, skipping default staff creation.")

# Initialize tables with a given connection
def initialize_tables(conn):
    if conn:
        cursor = conn.cursor()
        
        # Create all the necessary tables
        create_users_table(cursor)
        create_staff_table(cursor)
        create_admins_table(cursor)
        create_parking_spots_table(cursor)
        create_bookings_table(cursor)
        create_transactions_table(cursor)
        create_activity_logs_table(cursor)
        
        # Insert default data
        insert_default_parking_spots(cursor)
        insert_default_admin(cursor)
        insert_default_staff(cursor)
        
        conn.commit()
        cursor.close()
        print("All tables initialized successfully!")
    else:
        print("Failed to initialize tables - no connection.")

# Initialize Database (Optional)
def initialize_database():
    # First ensure database exists
    create_database()
    
    # Then get connection and initialize tables
    conn = get_db_connection()
    if conn:
        # Initialize all tables
        initialize_tables(conn)
        conn.close()
        print("Database initialized successfully!")
    else:
        print("Failed to initialize database.")

# Test Database Connection
if __name__ == '__main__':
    initialize_database()
