from db import get_db_connection

def update_spot_names():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # First, check existing spots
    cursor.execute('SELECT * FROM parking_spots ORDER BY spot_id')
    existing_spots = cursor.fetchall()
    
    print("Current parking spots:")
    for spot in existing_spots:
        print(f"ID: {spot['spot_id']}, Name: {spot['location']}, Status: {spot['status']}")
    
    # Now update the names to Spot 1, Spot 2, etc.
    for i, spot in enumerate(existing_spots, 1):
        new_name = f"Spot {i}"
        cursor.execute('UPDATE parking_spots SET location = %s WHERE spot_id = %s', 
                      (new_name, spot['spot_id']))
        print(f"Updated spot {spot['spot_id']} from '{spot['location']}' to '{new_name}'")
    
    # Commit the changes
    conn.commit()
    
    # Verify the updates
    cursor.execute('SELECT * FROM parking_spots ORDER BY spot_id')
    updated_spots = cursor.fetchall()
    
    print("\nUpdated parking spots:")
    for spot in updated_spots:
        print(f"ID: {spot['spot_id']}, Name: {spot['location']}, Status: {spot['status']}")
    
    cursor.close()
    conn.close()
    
    print("\nAll parking spot names have been updated successfully!")

if __name__ == "__main__":
    update_spot_names()
