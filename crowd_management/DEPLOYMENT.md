# Deployment Guide for Crowd Management System

This guide covers how to deploy the **Flask Backend** and update the **Android App** for a cloud environment.

## 1. Backend Deployment (Render / Railway / Heroku)

This application is configured for deployment on platforms like Render or Railway.

### Prerequisites
*   GitHub Account
*   Account on Render.com or Railway.app
*   This code pushed to a GitHub repository

### Option A: Deploy to Render.com (Recommended for Free Tier)
1.  **Push Code to GitHub**: Ensure your project is in a GitHub repo.
2.  **Create New Web Service**:
    *   Go to dashboard.render.com.
    *   Click "New" > "Web Service".
    *   Connect your GitHub repository.
3.  **Configure Service**:
    *   **Name**: `crowd-monitor` (or unique name)
    *   **Runtime**: Python 3
    *   **Build Command**: `pip install -r requirements.txt`
    *   **Start Command**: `gunicorn app:app`
4.  **Create Service**:
    *   Click "Create Web Service".
    *   Wait for the deployment to finish.
    *   Copy your **Service URL** (e.g., `https://crowd-monitor.onrender.com`).

**Note on Database**: content in `crowd.db` (SQLite) will be reset every time the app restarts on the free tier. For persistent data, use a PostgreSQL database service (available on Render/Railway) and update `app.py` to use `psycopg2` and a database URL.

### Option B: Deploy to Railway.app
1.  **New Project**: Go to railway.app > "New Project" > "Deploy from GitHub repo".
2.  **Select Repo**: Choose your repo.
3.  **Deploy**: Railway automatically detects `requirements.txt` and `Procfile`.
4.  **Domain**: Go to Settings > Generate Domain to get your public URL.

---

## 2. Update Android Client

Once your backend is live (e.g., `https://your-app.onrender.com`), you must update the Android app to talk to this new URL instead of your local computer.

1.  Open `android_client/app/src/main/java/com/example/crowdmonitor/ApiClient.java`.
2.  Change the `BASE_URL`:
    ```java
    // OLD (Local)
    // private static final String BASE_URL = "http://192.168.x.x:5000/";

    // NEW (Cloud) - MUST end with a slash /
    private static final String BASE_URL = "https://your-app.onrender.com/";
    ```
3.  **Rebuild the App**:
    *   In Android Studio, go to **Build > Build Bundle(s) / APK(s) > Build APK(s)**.
    *   Install this new APK on your mobile device.

## 3. Threshold Alerts

The Admin Dashboard now includes an **Alert Threshold** input.
*   **Default**: 5 users.
*   **Action**: If the number of users in a crowd zone exceeds this number, the dashboard will:
    1.  Play a siren sound.
    2.  Show a Browser Notification (if allowed).
    3.  Highlight the zone in red on the map.
