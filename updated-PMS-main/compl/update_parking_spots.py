"""
Update Parking Spots Script

This script adds or updates parking spots in the database to ensure
there are 25 spots available with proper status indicators.
"""
import mysql.connector
from db import get_db_connection

def update_parking_spots():
    """Update parking spots to ensure 25 total spots with correct statuses"""
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to database")
        return False
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        # First check current spots
        cursor.execute("SELECT COUNT(*) as count FROM parking_spots")
        current_count = cursor.fetchone()['count']
        print(f"Current parking spots count: {current_count}")
        
        # Clear existing spots if not exactly 25
        if current_count != 25:
            # First check if any spots are in use (not available)
            cursor.execute("SELECT COUNT(*) as count FROM parking_spots WHERE status != 'available'")
            in_use_count = cursor.fetchone()['count']
            
            if in_use_count > 0:
                print(f"Warning: {in_use_count} spots are currently in use (reserved or occupied)")
                print("Will preserve these spots and add additional ones to reach 25 total")
                
                # Get the existing spots
                cursor.execute("SELECT * FROM parking_spots ORDER BY spot_id")
                existing_spots = cursor.fetchall()
                
                # Determine how many new spots to add
                spots_to_add = 25 - current_count
                
                if spots_to_add > 0:
                    # Get the highest spot ID
                    cursor.execute("SELECT MAX(spot_id) as max_id FROM parking_spots")
                    max_id = cursor.fetchone()['max_id'] or 0
                    
                    print(f"Adding {spots_to_add} new parking spots")
                    
                    # Add new spots
                    for i in range(1, spots_to_add + 1):
                        spot_number = current_count + i
                        location = f"Section {chr(64 + ((spot_number-1)//5) + 1)} - Spot {((spot_number-1)%5) + 1}"
                        price = 5.00
                        
                        cursor.execute("""
                            INSERT INTO parking_spots (location, status, price_per_hour)
                            VALUES (%s, 'available', %s)
                        """, (location, price))
                    
                    conn.commit()
                    print(f"Added {spots_to_add} new parking spots")
            else:
                # No spots in use, replace all spots
                print("No spots currently in use. Recreating all 25 parking spots...")
                
                # Delete all existing spots
                cursor.execute("DELETE FROM parking_spots")
                
                # Create 25 new spots
                sections = ['A', 'B', 'C', 'D', 'E']
                spots_per_section = 5
                
                for section_idx, section in enumerate(sections):
                    for spot in range(1, spots_per_section + 1):
                        location = f"Section {section} - Spot {spot}"
                        # Vary the price slightly by section
                        price = 5.00 - (section_idx * 0.25)
                        
                        cursor.execute("""
                            INSERT INTO parking_spots (location, status, price_per_hour)
                            VALUES (%s, 'available', %s)
                        """, (location, price))
                
                conn.commit()
                print("Created 25 new parking spots")
        else:
            print("Already have 25 parking spots, no changes needed")
            
        # Verify the final count
        cursor.execute("SELECT COUNT(*) as count FROM parking_spots")
        final_count = cursor.fetchone()['count']
        print(f"Final parking spots count: {final_count}")
        
        # Print out all spots for verification
        cursor.execute("SELECT spot_id, location, status, price_per_hour FROM parking_spots ORDER BY spot_id")
        all_spots = cursor.fetchall()
        
        print("\nCurrent Parking Spots:")
        print("=====================")
        for spot in all_spots:
            print(f"ID: {spot['spot_id']}, Location: {spot['location']}, " 
                  f"Status: {spot['status']}, Price: ${spot['price_per_hour']}/hr")
            
        return True
    
    except Exception as e:
        conn.rollback()
        print(f"Error updating parking spots: {str(e)}")
        return False
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("Updating parking spots to ensure there are 25 total spots...\n")
    success = update_parking_spots()
    
    if success:
        print("\nParking spots successfully updated!")
    else:
        print("\nFailed to update parking spots.")
