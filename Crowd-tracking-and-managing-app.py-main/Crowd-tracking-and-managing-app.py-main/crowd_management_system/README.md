# Crowd Management & Event Monitoring System

A real-time crowd tracking and event monitoring system built with Python Flask and SQLite.

## Features
- **User Registration**: Simple web interface for attendees to check-in.
- **Live Tracking**: Monitors user locations via GPS.
- **Crowd Detection**: Automatically detects high-density areas (more than 5 people within 100m).
- **Safety Alerts**: Sends instant warnings to users in crowded zones with an exit route link.
- **Admin Dashboard**: Live map visualization of all attendees and crowd status.

## Prerequisites
- Python 3.x
- Modern web browser with Geolocation support

## Installation

1. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Mac/Linux
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python app.py
   ```

4. Access the application:
   - **Registration Page**: http://localhost:5000/
   - **Admin Dashboard**: http://localhost:5000/dashboard

## Testing Locally
To simulate a crowd, open the registration page in multiple browser tabs (Incognito mode helps simulate different users) or use multiple devices on the same network (you'll need to use your local IP address instead of localhost, e.g., `http://192.168.1.5:5000`).

## Notes
- Browser Geolocation requires HTTPS or `localhost`. If checking via local IP from mobile, some browsers might block geolocation unless you set up SSL or use a tunneling service like ngrok.
- `crowd.db` is automatically created on first run.

