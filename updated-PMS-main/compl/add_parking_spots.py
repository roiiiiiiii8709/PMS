from db import get_db_connection
import random

def add_parking_spots():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Define different locations and their base prices
    locations = [
        {"name": "Main Building", "base_price": 50},
        {"name": "West Wing", "base_price": 45},
        {"name": "East Wing", "base_price": 45},
        {"name": "North Block", "base_price": 40},
        {"name": "South Block", "base_price": 40}
    ]
    
    # Define spot types
    spot_types = ["Regular", "Premium", "Compact", "Accessible"]
    
    spots_added = 0
    
    # Create at least 10 spots across different locations
    for i in range(1, 11):
        # Select a random location from our list
        location_info = random.choice(locations)
        location_name = location_info["name"]
        
        # Add variation to the spot name by adding a number
        spot_number = i
        
        # Select a random spot type
        spot_type = random.choice(spot_types)
        
        # Create a descriptive location name
        location = f"{location_name} - {spot_type} Spot #{spot_number}"
        
        # Vary the price slightly based on spot type
        price_adjustment = 0
        if spot_type == "Premium":
            price_adjustment = 10
        elif spot_type == "Accessible":
            price_adjustment = -5
            
        price_per_hour = location_info["base_price"] + price_adjustment
        
        # Insert the spot
        try:
            cursor.execute("""
                INSERT INTO parking_spots (location, status, price_per_hour) 
                VALUES (%s, %s, %s)
            """, (location, 'available', price_per_hour))
            spots_added += 1
            print(f"Added spot: {location} (Rs.{price_per_hour}/hour)")
        except Exception as e:
            print(f"Error adding spot {location}: {str(e)}")
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"\nTotal spots added: {spots_added}")
    
if __name__ == "__main__":
    add_parking_spots()
