import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from app import app, init_db, get_db_connection

def test_crowd_simulation():
    # Setup
    app.config['TESTING'] = True
    client = app.test_client()
    
    # Clean DB for fresh test
    if os.path.exists("crowd.db"):
        os.remove("crowd.db")
    init_db()

    print("Registering users...")
    users = []
    for i in range(6):
        res = client.post('/register', json={
            "name": f"User {i}",
            "phone": f"555-00{i}"
        })
        user_id = res.json['user_id']
        users.append(user_id)
        
    print(f"Registered {len(users)} users.")

    # Simulate crowd at a location
    base_lat = 12.9716
    base_lon = 77.5946
    
    print("Posting locations (clustered)...")
    for i, uid in enumerate(users):
        # Slightly offset but very close (within meters)
        lat = base_lat + (i * 0.00001) 
        lon = base_lon + (i * 0.00001)
        client.post('/location', json={
            "user_id": uid,
            "latitude": lat,
            "longitude": lon
        })

    print("Checking crowd status...")
    res = client.get('/current-locations')
    data = res.json
    
    print(f"Total Active: {data['total_active']}")
    print(f"Crowd Zones: {data['crowd_zones']}")
    print(f"Red Zones Details: {json.dumps(data['red_zones'], indent=2)}")

    if data['crowd_zones'] > 0 and len(data['red_zones']) > 0:
        print("\nSUCCESS: Crowd detected and Red Zone created!")
        
        # Verify alert table has an entry (if we mock Twilio or just check DB side effect)
        with app.app_context():
            conn = get_db_connection()
            alert = conn.execute('SELECT * FROM Alerts').fetchone()
            if alert:
                print(f"Alert logged in DB: {dict(alert)}")
            else:
                print("WARNING: No alert found in DB.")
            conn.close()
    else:
        print("\nFAILURE: No crowd detected.")

if __name__ == "__main__":
    test_crowd_simulation()
