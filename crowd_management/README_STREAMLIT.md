# 🎪 Crowd Management System - Streamlit Version

A modern, beautiful crowd monitoring and management system built with Streamlit, featuring real-time location tracking, YOLO-based CCTV analysis, and SMS alerts.

## ✨ Features

### 👥 User Registration & Tracking
- Beautiful, modern UI with glassmorphism effects
- User registration with validation
- Real-time GPS location tracking
- Automatic crowd detection alerts
- Google Maps integration for exit routes

### 📊 Admin Dashboard
- Live monitoring of all active users
- Interactive map visualization
- Real-time CCTV feed with YOLOv8 person detection
- Crowd zone detection and visualization
- Auto-refresh capability
- SMS alerts for crowd situations

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- A camera (IP camera, webcam, or built-in camera)
- Twilio account for SMS alerts (optional)

### Installation

1. **Install Dependencies**
   ```bash
   pip install -r requirements_streamlit.txt
   ```

2. **Configure Camera Settings**
   Edit the camera sources in `streamlit_app.py`:
   ```python
   IP_CAMERA_IPV4 = "http://YOUR_CAMERA_IP:8080/video"
   ```

3. **Configure Alert System (Optional)**
   Update Twilio credentials in `streamlit_app.py`:
   ```python
   alert_system.account_sid = "YOUR_ACCOUNT_SID"
   alert_system.auth_token = "YOUR_AUTH_TOKEN"
   alert_system.from_number = 'YOUR_TWILIO_NUMBER'
   ```

### Running the Application

```bash
streamlit run streamlit_app.py
```

The application will open in your default web browser at `http://localhost:8501`

## 📱 Usage

### For Users (Event Attendees)
1. Navigate to "🏠 User Registration" page
2. Enter your name and phone number
3. Click "Register & Start Tracking"
4. Update your location periodically
5. Receive alerts if you're in a crowded area

### For Admins
1. Navigate to "📊 Admin Dashboard"
2. Monitor active users on the map
3. View live CCTV feed with person detection
4. Check crowd zones in real-time
5. Adjust alert threshold as needed

## 🎨 UI Features

- **Modern Design**: Beautiful gradients and glassmorphism effects
- **Responsive Layout**: Works on desktop and mobile
- **Real-time Updates**: Auto-refresh capabilities
- **Interactive Maps**: Live location visualization
- **Animations**: Smooth transitions and pulse effects for alerts

## ⚙️ Configuration

### Thresholds
```python
CROWD_THRESHOLD_LOC = 5  # Minimum users for location-based crowd alert
CROWD_THRESHOLD_CAM = 3  # Minimum persons for CCTV-based crowd alert
CROWD_RADIUS_KM = 0.02   # 20 meters clustering radius
ALERT_COOLDOWN_SECONDS = 600  # 10 minutes between alerts
```

## 🔧 Technical Stack

- **Frontend**: Streamlit with custom CSS
- **Backend**: Python 3.x
- **Database**: SQLite
- **Computer Vision**: YOLOv8 (Ultralytics)
- **Mapping**: Streamlit's built-in map component
- **Alerts**: Twilio SMS API

## 📦 Database Schema

### Users Table
- `id`: Primary key
- `name`: User's full name
- `phone`: Phone number
- `registration_date`: Timestamp

### Locations Table
- `id`: Primary key
- `user_id`: Foreign key to Users
- `latitude`: GPS latitude
- `longitude`: GPS longitude
- `timestamp`: Location update time

### Alerts Table
- `id`: Primary key
- `zone_id`: Identifier for crowd zone
- `user_id`: Foreign key to Users
- `timestamp`: Alert sent time

## 🚨 Alert System

The system sends SMS alerts when:
1. **Location-based**: 5+ users within 20 meters
2. **CCTV-based**: 3+ persons detected on camera
3. **Cooldown**: Alerts limited to once per 10 minutes per user/zone

## 🎯 Differences from Flask Version

| Feature | Flask Version | Streamlit Version |
|---------|--------------|-------------------|
| **UI Framework** | HTML/CSS/JS | Streamlit + Custom CSS |
| **Routing** | Multiple HTML templates | Single-page with tabs |
| **Real-time Updates** | JavaScript polling | Streamlit auto-refresh |
| **Map Integration** | Leaflet.js | Streamlit map component |
| **Video Feed** | Streaming endpoint | Frame-by-frame capture |
| **Deployment** | Traditional web hosting | Streamlit Cloud/Server |

## 🌐 Deployment

### Streamlit Cloud
1. Push code to GitHub
2. Connect to Streamlit Cloud
3. Configure secrets for API keys
4. Deploy!

### Local Server
```bash
streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0
```

## 📝 Notes

- The camera feed in Streamlit is frame-based (not continuous streaming)
- For production use, consider using Streamlit's session state for better performance
- GPS tracking requires browser permission (HTTPS recommended)
- Mobile responsiveness is built-in with Streamlit

## 🔐 Security Considerations

- Store API keys in environment variables or Streamlit secrets
- Use HTTPS for production deployment
- Implement proper authentication for admin dashboard
- Sanitize user inputs
- Follow GDPR/privacy guidelines for location data

## 📞 Support

For issues or questions, please check the documentation or raise an issue.

## 📄 License

This project is open source and available for educational purposes.

---

**Built with ❤️ using Streamlit**
