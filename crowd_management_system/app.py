from flask import Flask, render_template, request, jsonify
import sqlite3
import math
from datetime import datetime
import os

app = Flask(__name__)
DB_NAME = "crowd.db"

# Crowd Detection Settings
CROWD_RADIUS_KM = 0.1  # 100 meters
CROWD_THRESHOLD = 5    # 5 users


# ---------------- DATABASE ---------------- #

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
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
    conn.close()


init_db()


# ---------------- UTILITY ---------------- #

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + \
        math.cos(math.radians(lat1)) * \
        math.cos(math.radians(lat2)) * \
        math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    return R * c


# ---------------- ROUTES ---------------- #

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
        return jsonify({"error": "Name and phone required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT id FROM Users WHERE phone = ?', (phone,))
    existing_user = cursor.fetchone()

    if existing_user:
        user_id = existing_user['id']
    else:
        cursor.execute(
            'INSERT INTO Users (name, phone) VALUES (?, ?)',
            (name, phone)
        )
        user_id = cursor.lastrowid
        conn.commit()

    conn.close()

    return jsonify({
        "user_id": user_id,
        "message": "Registered successfully"
    })


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

    cursor.execute(
        'INSERT INTO Locations (user_id, latitude, longitude) VALUES (?, ?, ?)',
        (user_id, lat, lon)
    )
    conn.commit()

    cursor.execute('''
        SELECT user_id, latitude, longitude, MAX(timestamp) as last_seen
        FROM Locations
        GROUP BY user_id
        HAVING last_seen >= datetime('now', '-1 minute')
    ''')

    active_users = cursor.fetchall()

    nearby_count = 0

    for user in active_users:
        dist = haversine(lat, lon, user['latitude'], user['longitude'])
        if dist <= CROWD_RADIUS_KM:
            nearby_count += 1

    is_crowded = nearby_count >= CROWD_THRESHOLD

    response = {
        "status": "success",
        "crowd_alert": is_crowded
    }

    if is_crowded:
        EXIT_LAT = 12.9716
        EXIT_LON = 77.5946
        response["message"] = "⚠ HEAVY CROWD DETECTED. Please move to a safer area."
        response["exit_link"] = f"https://www.google.com/maps/dir/?api=1&destination={EXIT_LAT},{EXIT_LON}"

    conn.close()
    return jsonify(response)


@app.route('/current-locations', methods=['GET'])
def get_current_locations():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT u.id, u.name, l.latitude, l.longitude, MAX(l.timestamp) as last_seen
        FROM Locations l
        JOIN Users u ON l.user_id = u.id
        GROUP BY l.user_id
        HAVING last_seen >= datetime('now', '-2 minute')
    ''')

    active_users = cursor.fetchall()

    users_data = []
    active_locations = [(u['id'], u['latitude'], u['longitude']) for u in active_users]
    crowded_users_ids = set()

    for i in range(len(active_locations)):
        u1_id, lat1, lon1 = active_locations[i]
        count = 0

        for j in range(len(active_locations)):
            u2_id, lat2, lon2 = active_locations[j]
            if haversine(lat1, lon1, lat2, lon2) <= CROWD_RADIUS_KM:
                count += 1

        is_crowded = count >= CROWD_THRESHOLD

        if is_crowded:
            crowded_users_ids.add(u1_id)

        users_data.append({
            "id": u1_id,
            "name": active_users[i]['name'],
            "latitude": lat1,
            "longitude": lon1,
            "is_crowded": is_crowded
        })

    conn.close()

    return jsonify({
        "users": users_data,
        "total_active": len(active_users),
        "crowd_zones": len(crowded_users_ids)
    })


# ---------------- RENDER PRODUCTION RUN ---------------- #

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)


