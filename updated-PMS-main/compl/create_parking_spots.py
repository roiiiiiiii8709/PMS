from db import get_db_connection

# Sample parking spot data with diverse locations and pricing
parking_spots = [
    # Ground Floor - Standard Spots (A Section)
    {"location": "Ground Floor - A1", "price_per_hour": 2.50},
    {"location": "Ground Floor - A2", "price_per_hour": 2.50},
    {"location": "Ground Floor - A3", "price_per_hour": 2.50},
    {"location": "Ground Floor - A4", "price_per_hour": 2.50},
    {"location": "Ground Floor - A5", "price_per_hour": 2.50},
    
    # Ground Floor - Premium Spots (B Section - Near Entrance)
    {"location": "Ground Floor - B1 (Near Entrance)", "price_per_hour": 3.50},
    {"location": "Ground Floor - B2 (Near Entrance)", "price_per_hour": 3.50},
    {"location": "Ground Floor - B3 (Near Entrance)", "price_per_hour": 3.50},
    
    # First Floor - Standard Spots
    {"location": "First Floor - C1", "price_per_hour": 2.00},
    {"location": "First Floor - C2", "price_per_hour": 2.00},
    {"location": "First Floor - C3", "price_per_hour": 2.00},
    
    # Second Floor - Economy Spots
    {"location": "Second Floor - D1", "price_per_hour": 1.50},
    {"location": "Second Floor - D2", "price_per_hour": 1.50},
    
    # Special Spots
    {"location": "Ground Floor - HC1 (Handicap)", "price_per_hour": 2.00},
    {"location": "Ground Floor - EV1 (Electric Vehicle)", "price_per_hour": 3.00}
]

def create_parking_spots():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # First, check if spots already exist to avoid duplicates
    cursor.execute("SELECT COUNT(*) FROM parking_spots")
    count = cursor.fetchone()[0]
    
    if count > 0:
        print(f"There are already {count} parking spots in the database.")
        proceed = input("Do you want to add 15 more parking spots? (yes/no): ")
        if proceed.lower() != 'yes':
            print("Operation cancelled.")
            cursor.close()
            conn.close()
            return
    
    # Add new parking spots
    for spot in parking_spots:
        cursor.execute(
            "INSERT INTO parking_spots (location, status, price_per_hour) VALUES (%s, %s, %s)",
            (spot["location"], "available", spot["price_per_hour"])
        )
    
    conn.commit()
    print(f"Successfully created {len(parking_spots)} new parking spots!")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    create_parking_spots()
