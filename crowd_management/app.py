from flask import Flask, render_template, request, jsonify, Response
import sqlite3
import math

from datetime import datetime
import os
import cv2
-/

from twilio.rest import Client
from alert import Alertmsg

app = Flask(__name__)
DB_NAME = "crowd.db"

# Camera Configuration
IP_CAMERA_IPV4 = "http://100.104.168.30:8080/video"
IP_CAMERA_IPV6 = "http://[2401:4900:7b59:cb18:2d91:2461:fefe:1f45]:8080/video"

# List of sources to try in order
camera_sources = [IP_CAMERA_IPV4, IP_CAMERA_IPV6, 0] 


# Initialize Alert System with specific credentials
alert_system = Alertmsg()
# Override with user provided creds to be sure
alert_system.account_sid = ""
alert_system.auth_token = ""
alert_system.from_number = ""

# Target for alerts
ADMIN_PHONE_NUMBER = os.environ.get(,)

# Threholds
CROWD_THRESHOLD_LOC = 5 
CROWD_THRESHOLD_CAM = 3
ALERT_COOLDOWN_SECONDS = 600 # 10 minutes to avoid spam

ALERT_MESSAGE = 'u are in heavy crowd so move away from it "your life is important to us "'


# Crowd Detection Settings
CROWD_RADIUS_KM = 0.02  # 20 meters for tight clustering, active users are close
# Using thresholds defined above (CROWD_THRESHOLD_LOC and CROWD_THRESHOLD_CAM)

# Global State
CAMERA_PERSON_COUNT = 0
LAST_CAMERA_UPDATE = None

# Initialize YOLO (Global to avoid reloading)
try:
    from ultralytics import YOLO
    yolo_model = YOLO("yolov8n.pt")
except ImportError:
    yolo_model = None

def generate_frames():
    global CAMERA_PERSON_COUNT, LAST_CAMERA_UPDATE
    
    cap = None
    # Try available sources
    for src in camera_sources:
        print(f"Attempting to connect to camera source: {src}")
        cap = cv2.VideoCapture(src)
        if cap.isOpened():
            print(f"Successfully connected to {src}")
            break
        cap.release()
    
    if not cap or not cap.isOpened():
        print("Error: Could not open any camera source.")
        return

    while True:
        success, frame = cap.read()
        if not success:
            # Re-try loop if stream breaks
            cap.release()
            for src in camera_sources:
                cap = cv2.VideoCapture(src)
                if cap.isOpened(): break
            continue

        count = 0
        if yolo_model:
            results = yolo_model(frame, conf=0.4, verbose=False)
            for r in results:
                for box in r.boxes:
                    cls = int(box.cls[0])
                    # YOLO counts both 'person' and 'face' if using a specific model, 
                    # but with yolov8n, we mainly look for 'person'.
                    if yolo_model.names[cls] == "person":
                        count += 1
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        # High visibility boxes
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        cv2.putText(frame, f"Person", (x1, y1 - 10), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            CAMERA_PERSON_COUNT = count
            LAST_CAMERA_UPDATE = datetime.now().strftime('%H:%M:%S')

            # Alert if CCTV shows >= 3 persons
            if CAMERA_PERSON_COUNT >= CROWD_THRESHOLD_CAM:
                # Trigger alerts to all recently active users
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT u.id, u.phone FROM Users u
                    JOIN (SELECT user_id, MAX(timestamp) as last_seen FROM Locations GROUP BY user_id) l
                    ON u.id = l.user_id
                    WHERE l.last_seen >= datetime('now', '-2 minute')
                ''')
                all_active = cursor.fetchall()
                
                for user in all_active:
                    user_id = user['id']
                    phone = user['phone']
                    zone_id = "CCTV_REGION_01"
                    
                    # Cooldown check
                    cursor.execute('SELECT timestamp FROM Alerts WHERE zone_id = ? AND user_id = ? ORDER BY timestamp DESC LIMIT 1', (zone_id, user_id))
                    last_alert = cursor.fetchone()
                    
                    should_alert = True
                    if last_alert:
                        last_time = datetime.strptime(last_alert['timestamp'], '%Y-%m-%d %H:%M:%S')
                        if (datetime.now() - last_time).total_seconds() < ALERT_COOLDOWN_SECONDS:
                            should_alert = False
                    
                    if should_alert:
                        sms_num = phone 
                        
                   f phone.startswith('+') else f"+91{phone}"
                        # Logging exactly who gets the message
                        print(f"CCTV ALERT: Sending message to {sms_num}")
                        alert_system.send_alert(sms_num, ALERT_MESSAGE)
                        cursor.execute('INSERT INTO Alerts (zone_id, user_id) VALUES (?, ?)', (zone_id, user_id))
                
                conn.commit()
                conn.close()

        # Add Overlay
        status = "NORMAL"
        color = (0, 255, 0)
        # Using CROWD_THRESHOLD_CAM (3) for CCTV alert logic as requested
        if CAMERA_PERSON_COUNT >= CROWD_THRESHOLD_CAM:
            status = "CROWD DETECTED!"
            color = (0, 0, 255)

            
        cv2.putText(frame, f"LIVE CCTV - Count: {CAMERA_PERSON_COUNT} Status: {status}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        # Encode frame
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')




def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if not os.path.exists(DB_NAME):
        conn = get_db_connection()
        with conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS Users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS Locations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    latitude REAL NOT NULL,
                    longitude REAL NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES Users (id)
                );
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS Alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    zone_id TEXT NOT NULL,
                    user_id INTEGER,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            ''')

        conn.close()

init_db()

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    return R * c

def send_sms_alert(message):
    print(f"Attempting to send SMS to {ADMIN_PHONE_NUMBER}...")
    alert_system.send_alert(ADMIN_PHONE_NUMBER, message)


def cluster_users(users, radius_km):
    """
    Groups users into clusters based on distance.
    Returns a list of clusters, where each cluster is a list of user dicts.
    """
    clusters = []
    visited = set()
    
    for i in range(len(users)):
        if i in visited:
            continue
            
        cluster = [users[i]]
        visited.add(i)
        
        # Simple BFS/DFS for connected components
        stack = [i]
        while stack:
            current_idx = stack.pop()
            current_user = users[current_idx]
            
            for j in range(len(users)):
                if j not in visited:
                    dist = haversine(
                        current_user['latitude'], current_user['longitude'],
                        users[j]['latitude'], users[j]['longitude']
                    )
                    if dist <= radius_km:
                        visited.add(j)
                        cluster.append(users[j])
                        stack.append(j)
        
        if len(cluster) > 0:
            clusters.append(cluster)
            
    return clusters


@app.route('/')
def index():
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    name = data.get('name')
    phone = data.get('phone')
    
    if not name or not phone:
        return jsonify({"error": "Name and phone are required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if phone already registered (simple check)
    cursor.execute('SELECT id FROM Users WHERE phone = ?', (phone,))
    existing_user = cursor.fetchone()
    
    if existing_user:
        user_id = existing_user['id']
    else:
        cursor.execute('INSERT INTO Users (name, phone) VALUES (?, ?)', (name, phone))
        user_id = cursor.lastrowid
        conn.commit()
    
    conn.close()
    return jsonify({"user_id": user_id, "message": "Registered successfully"})

@app.route('/camera-update', methods=['POST'])
def update_camera_data():
    global CAMERA_PERSON_COUNT, LAST_CAMERA_UPDATE
    data = request.json
    CAMERA_PERSON_COUNT = data.get('person_count', 0)
    LAST_CAMERA_UPDATE = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # If camera count is high, we could trigger a general alert as well
    if CAMERA_PERSON_COUNT >= CROWD_THRESHOLD_CAM:

        msg = f"⚠ CAMERA ALERT: High crowd density detected via optical sensor. Count: {CAMERA_PERSON_COUNT} people."
        # send_sms_alert(msg) # Optional: Trigger SMS on camera count too
        
    return jsonify({"status": "success", "count": CAMERA_PERSON_COUNT})


@app.route('/location', methods=['POST'])
def update_location():
    data = request.json
    user_id = data.get('user_id')
    lat = data.get('latitude')
    lon = data.get('longitude')

    if not user_id or lat is None or lon is None:
        return jsonify({"error": "Invalid data"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # Log location
    cursor.execute('INSERT INTO Locations (user_id, latitude, longitude) VALUES (?, ?, ?)', (user_id, lat, lon))
    conn.commit()

    # Get active users (last 1 minute for simplicity) to calculate crowd
    # We only care about the MOST RECENT location of each active user
    cursor.execute('''
        SELECT user_id, latitude, longitude, MAX(timestamp) as last_seen
        FROM Locations
        GROUP BY user_id
        HAVING last_seen >= datetime('now', '-1 minute')
    ''')
    active_users = cursor.fetchall()
    
    nearby_count = 0
    # Include the current user in the count? "Count how many users are within 100 meters" usually means including self or excluding? 
    # Usually "crowd" implies number of people in an area. So including self makes sense if the threshold is for total people.
    # But usually creating a crowd requires > 1 person. Let's include self.


    for user in active_users:
        # Calculate distance
        dist = haversine(lat, lon, user['latitude'], user['longitude'])
        if dist <= CROWD_RADIUS_KM:
            nearby_count += 1
            
    is_crowded = nearby_count >= CROWD_THRESHOLD_LOC

    
    response = {
        "status": "success",
        "crowd_alert": is_crowded
    }
    
    if is_crowded:
        # Generate exit link (placeholder logic or a fixed point if not specified how to calculate exit)
        # Requirement: "Generate Google Maps exit link: ... destination=EVENT_EXIT_LAT,EVENT_EXIT_LON"
        # I'll use a placeholder exit location since none was provided
        # Let's assume exit is at 0,0 or ask user to configure. 
        # Actually the prompt says: "EVENT_EXIT_LAT,EVENT_EXIT_LON". I will define a constant for now.
        EXIT_LAT = 12.9716 # Example: Bangalore
        EXIT_LON = 77.5946 
        # But wait, the user's location is dynamic. The exit should be relative or fixed? Usually fixed for an event.
        response["message"] = "⚠ HEAVY CROWD DETECTED. Please move to a safer area."
        response["exit_link"] = f"https://www.google.com/maps/dir/?api=1&destination={EXIT_LAT},{EXIT_LON}"

    conn.close()
    return jsonify(response)

@app.route('/current-locations', methods=['GET'])
def get_current_locations():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get latest location for all active users (last 2 minutes)
    cursor.execute('''
        SELECT u.id, u.name, u.phone, l.latitude, l.longitude, MAX(l.timestamp) as last_seen
        FROM Locations l
        JOIN Users u ON l.user_id = u.id
        GROUP BY l.user_id
        HAVING last_seen >= datetime('now', '-2 minute')
    ''')

    active_users = cursor.fetchall()

    # Clustering Logic
    clusters = cluster_users(active_users, CROWD_RADIUS_KM)
    red_zones = []
    crowded_users_ids = set()

    for cluster in clusters:
        if len(cluster) >= CROWD_THRESHOLD_LOC:
            # Red Zone detected
            avg_lat = sum(u['latitude'] for u in cluster) / len(cluster)
            avg_lon = sum(u['longitude'] for u in cluster) / len(cluster)
            zone_id = f"{avg_lat:.4f}_{avg_lon:.4f}"
            
            red_zones.append({
                "lat": avg_lat, "lon": avg_lon,
                "count": len(cluster), "radius": CROWD_RADIUS_KM * 1000
            })
            
            for user in cluster:
                # Trigger individual SMS to each user in the crowd
                user_id = user['id']
                phone = user['phone'] # Need to ensure phone is in the select
                
                # Check cooldown per user/zone
                cursor.execute('''
                    SELECT timestamp FROM Alerts 
                    WHERE zone_id = ? AND user_id = ?
                    ORDER BY timestamp DESC LIMIT 1
                ''', (zone_id, user_id))
                last_alert = cursor.fetchone()
                
                should_alert = True
                if last_alert:
                    last_time = datetime.strptime(last_alert['timestamp'], '%Y-%m-%d %H:%M:%S')
                    if (datetime.now() - last_time).total_seconds() < ALERT_COOLDOWN_SECONDS:
                        should_alert = False
                
                if should_alert:
                    print(f"Sending heavy crowd alert to {phone}")
                    # Ensure Indian number format if not already (adding +91 if 10 digits)
                    sms_num = phone if phone.startswith('+') else f"+91{phone}"
                    alert_system.send_alert(sms_num, ALERT_MESSAGE)
                    
                    cursor.execute('INSERT INTO Alerts (zone_id, user_id) VALUES (?, ?)', (zone_id, user_id))
                    conn.commit()

    users_data = []
    for u in active_users:
        is_crowded = u['id'] in crowded_users_ids
        users_data.append({
            "id": u['id'], "name": u['name'],
            "latitude": u['latitude'], "longitude": u['longitude'],
            "is_crowded": is_crowded
        })

    
    conn.close()
    return jsonify({
        "users": users_data,
        "total_active": len(active_users),
        "crowd_zones": len(red_zones),
        "red_zones": red_zones,
        "camera_count": CAMERA_PERSON_COUNT,
        "last_camera_sync": LAST_CAMERA_UPDATE
    })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
