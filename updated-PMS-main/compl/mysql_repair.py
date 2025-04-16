"""
MySQL Repair and Diagnostics Script

This script helps diagnose and repair common MySQL issues.
It creates backup, checks for configuration problems, and helps reset MySQL.
"""
import os
import sys
import subprocess
import datetime
import time
import shutil

def log(message):
    """Print and log the message"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")
    
    # Also save to log file
    with open("mysql_repair.log", "a") as f:
        f.write(f"[{timestamp}] {message}\n")

def run_command(command):
    """Run a command and return the output"""
    try:
        result = subprocess.run(command, shell=True, check=True, 
                               capture_output=True, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        log(f"Error running command: {command}")
        log(f"Error: {e.stderr}")
        return None

def check_mysql_service():
    """Check if MySQL service is running"""
    log("Checking MySQL service status...")
    result = run_command("sc query MySQL")
    if result and "RUNNING" in result:
        log("MySQL service is running.")
        return True
    else:
        log("MySQL service is NOT running.")
        return False

def restart_mysql_service():
    """Attempt to restart the MySQL service"""
    log("Attempting to restart MySQL service...")
    
    # Stop service if it's running
    run_command("sc stop MySQL")
    time.sleep(5)
    
    # Start service
    result = run_command("sc start MySQL")
    time.sleep(5)
    
    if check_mysql_service():
        log("Successfully restarted MySQL service!")
        return True
    else:
        log("Failed to restart MySQL service.")
        return False

def backup_mysql_data():
    """Create a backup of the MySQL data directory"""
    mysql_data_dir = "C:\\xampp\\mysql\\data"
    if not os.path.exists(mysql_data_dir):
        log(f"MySQL data directory not found at {mysql_data_dir}")
        mysql_data_dir = input("Please enter the path to your MySQL data directory: ")
        
    if not os.path.exists(mysql_data_dir):
        log("Invalid MySQL data directory. Cannot continue with backup.")
        return False
    
    backup_dir = f"mysql_data_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    log(f"Creating backup of MySQL data at {backup_dir}...")
    
    try:
        # Create backup of key files only, not the entire data directory which could be huge
        os.makedirs(backup_dir, exist_ok=True)
        
        # Backup configuration file
        my_ini = os.path.join(os.path.dirname(mysql_data_dir), "my.ini")
        if os.path.exists(my_ini):
            shutil.copy2(my_ini, backup_dir)
            log(f"Backed up MySQL configuration: {my_ini}")
            
        # Backup ibdata files if they exist
        for file in os.listdir(mysql_data_dir):
            if file.startswith("ibdata") or file == "ib_logfile0" or file == "ib_logfile1":
                src = os.path.join(mysql_data_dir, file)
                dst = os.path.join(backup_dir, file)
                shutil.copy2(src, dst)
                log(f"Backed up {file}")
                
        log(f"Backup of critical MySQL files created in {backup_dir}")
        return True
    except Exception as e:
        log(f"Error creating backup: {str(e)}")
        return False

def check_port_conflict():
    """Check if there's anything using MySQL's port"""
    log("Checking for port conflicts on port 3306...")
    result = run_command("netstat -ano | findstr :3306")
    
    if result and len(result.strip()) > 0:
        log("Something is using port 3306. This might be causing conflicts.")
        log(result)
        return True
    else:
        log("Port 3306 appears to be free.")
        return False

def check_disk_space():
    """Check available disk space"""
    log("Checking available disk space...")
    result = run_command("wmic logicaldisk get deviceid, freespace, size")
    
    if result:
        log("Disk space information:")
        log(result)
    else:
        log("Could not retrieve disk space information.")

def reset_mysql_password():
    """Instructions for resetting MySQL root password"""
    log("MySQL Password Reset Instructions:")
    log("1. Stop the MySQL service")
    log("2. Open Command Prompt as Administrator")
    log("3. Navigate to MySQL bin directory (e.g., C:\\xampp\\mysql\\bin)")
    log("4. Run: mysqld --defaults-file=\"C:\\xampp\\mysql\\bin\\my.ini\" --init-file=C:\\reset-pw.txt --console")
    log("   Where reset-pw.txt contains: ALTER USER 'root'@'localhost' IDENTIFIED BY 'new_password';")
    log("5. Once MySQL starts, press Ctrl+C to stop it")
    log("6. Restart MySQL service normally")
    log("7. Try connecting with the new password")

def fix_corrupted_tables():
    """Attempt to fix corrupted MySQL tables"""
    log("To fix corrupted MySQL tables, try the following:")
    log("1. Try using the MySQL repair utility:")
    log("   - For MyISAM tables: mysqlcheck -r --all-databases -u root -p")
    log("   - For InnoDB tables: Start MySQL with the --innodb-force-recovery=1 option")
    log("2. If that doesn't work, restore from a backup")
    log("3. If no backup is available, try recreating the corrupted tables")

def main():
    log("=== MySQL Repair and Diagnostic Tool ===")
    log("Starting diagnostics...")
    
    # Check if MySQL service is running
    mysql_running = check_mysql_service()
    
    # Check for port conflicts
    port_conflict = check_port_conflict()
    
    # Check disk space
    check_disk_space()
    
    # Create backup if needed
    if not mysql_running:
        backup = input("Would you like to back up your MySQL data files before continuing? (y/n): ")
        if backup.lower() == 'y':
            backup_mysql_data()
    
    # Try restarting MySQL if it's not running
    if not mysql_running:
        restart = input("Would you like to attempt restarting the MySQL service? (y/n): ")
        if restart.lower() == 'y':
            if restart_mysql_service():
                log("MySQL service has been successfully restarted!")
                return
    
    # If the service is still not running, provide more detailed help
    if not mysql_running:
        log("\n=== MySQL Recovery Options ===")
        log("MySQL is still not running. Here are some additional steps to try:")
        
        log("\n1. Check the MySQL error log at C:\\xampp\\mysql\\data\\mysql_error.log")
        log("   Look for specific error messages that might indicate the problem.")
        
        if port_conflict:
            log("\n2. There appears to be a port conflict. Try changing MySQL's port in my.ini")
            log("   Find the line 'port=3306' and change it to another port like 3307")
        
        log("\n3. Try fixing corrupted tables:")
        fix_corrupted_tables()
        
        log("\n4. If you can't access MySQL at all, you might need to reset the password:")
        reset_mysql_password()
        
        log("\n5. As a last resort, you can reinstall MySQL or restore from a backup")
        log("   Make sure to back up your data directory first!")
    
    log("\nDiagnostic process completed. Check the log for details and recommended actions.")
    log("If the problem persists, consider checking the MySQL error log and Windows Event Viewer")
    log("for more detailed information about what's causing the shutdown.")

if __name__ == "__main__":
    main()
