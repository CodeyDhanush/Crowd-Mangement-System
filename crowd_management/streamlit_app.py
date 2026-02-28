import streamlit as st
import sqlite3
import math
import time
from streamlit_js_eval import streamlit_js_eval
from streamlit_autorefresh import st_autorefresh
from alert import Alertmsg
from datetime import datetime, timedelta

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Crowd Monitoring System", page_icon="👥")

DB_NAME = "crowd.db"
CROWD_THRESHOLD = 5
CROWD_RADIUS_KM = 0.02  # 20 meters

# ---------------- DATABASE ----------------
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    with conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS Users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT
        )
        """)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS Locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            latitude REAL,
            longitude REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
    conn.close()

init_db()

# DISTANCE FUNCTION
def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c

#SESSION
if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "registered" not in st.session_state:
    st.session_state.registered = False

st.title("Smart Crowd Monitoring System")

#  REGISTRATION
if not st.session_state.registered:

    st.subheader("Register Once")

    with st.form("register_form"):
        name = st.text_input("Full Name")
        phone = st.text_input("Phone Number (10-digit Indian)")
        submitted = st.form_submit_button("Register")

    if submitted:

        if not name or not phone:
            st.error("Please fill all fields")


        else:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("INSERT INTO Users (name, phone) VALUES (?, ?)", (name, phone))
            conn.commit()
            user_id = cursor.lastrowid
            conn.close()

            st.session_state.user_id = user_id
            st.session_state.registered = True

            st.success("Registered Successfully")
            time.sleep(1)
            st.rerun()

#AUTO TRACKING
else:

    st.success("🟢 You are being monitored automatically")
    st.write("📡 Location updates every 30 seconds")

    # Auto refresh every 30 seconds
    st_autorefresh(interval=30000, key="location_refresh")

    # Automatically get GPS
    location = streamlit_js_eval(
        js_expressions="""
        new Promise((resolve, reject) => {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    resolve({
                        lat: position.coords.latitude,
                        lon: position.coords.longitude
                    });
                },
                (error) => {
                    resolve(null);
                }
            );
        });
        """,
        key="auto_gps"
    )

    if location:

        lat = location["lat"]
        lon = location["lon"]

        conn = get_db_connection()
        cursor = conn.cursor()

        # Save location
        cursor.execute(
            "INSERT INTO Locations (user_id, latitude, longitude) VALUES (?, ?, ?)",
            (st.session_state.user_id, lat, lon)
        )
        conn.commit()

        # Check nearby users (last 1 min)
        cursor.execute("""
            SELECT user_id, latitude, longitude, MAX(timestamp) as last_seen
            FROM Locations
            GROUP BY user_id
            HAVING last_seen >= datetime('now', '-1 minute')
        """)

        active_users = cursor.fetchall()

        nearby_count = 0
        for user in active_users:
            dist = haversine(lat, lon, user["latitude"], user["longitude"])
            if dist <= CROWD_RADIUS_KM:
                nearby_count += 1

        conn.close()

        st.write(f"Current Location: {lat}, {lon}")
        st.write(f"Nearby Users: {nearby_count}")

        if nearby_count >= CROWD_THRESHOLD:
            st.error("HEAVY CROWD DETECTED! Please move away!")
            nearby_users = []
            for user in active_users:
                dist = haversine(lat, lon, user["latitude"], user["longitude"])
                if dist <= CROWD_RADIUS_KM:
                    nearby_users.append(user)
                    nearby_count = len(nearby_users)
                    # Threshold Check

                if nearby_count >= CROWD_THRESHOLD:
                    alert_system = Alertmsg()
                    message = "Heavy crowd detected near you. Please move to safe area."

                    for user in nearby_users:   # LOOP HERE
                        phone = user["phone"]# Add +91 if missing
                        if not phone.startswith("+"):
                            phone = "+91" + phone
                            alert_system.send_alert(phone, message)
                            st.error("Heavy Crowd Detected! Alerts Sent.")

                        else:
                            st.success(f"✅ Safe Area. Nearby users: {nearby_count}")

        else:
            st.success("✅ Area is Safe")

    if st.button("Exit"):
        st.session_state.user_id = None
        st.session_state.registered = False
        st.rerun()
