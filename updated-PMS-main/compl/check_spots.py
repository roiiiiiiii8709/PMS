from db import get_db_connection

def check_spots():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Check parking spots
    cursor.execute("SELECT * FROM parking_spots ORDER BY spot_id")
    spots = cursor.fetchall()
    
    print(f"Total parking spots: {len(spots)}")
    for spot in spots:
        print(f"ID: {spot['spot_id']}, Location: {spot['location']}, Status: {spot['status']}, Price: {spot['price_per_hour']}")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    check_spots()
