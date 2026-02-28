# Android Client for Crowd Monitor

This directory contains the source code for the Android client application.

## Setup Instructions

1.  **Open in Android Studio**:
    *   Open Android Studio and select "Open an existing project".
    *   Navigate to this `android_client` directory.

2.  **Dependencies**:
    *   Ensure your `build.gradle` (Module: app) includes:
        ```gradle
        implementation 'com.squareup.retrofit2:retrofit:2.9.0'
        implementation 'com.squareup.retrofit2:converter-gson:2.9.0'
        implementation 'com.google.android.gms:play-services-location:21.0.1'
        ```

3.  **Emulator Configuration**:
    *   The app is configured to connect to `http://10.0.2.2:5000/`.
    *   This works automatically if you run the Flask server on your local machine and the app in the Android Emulator.
    *   If using a physical device, update `ApiClient.java` with your computer's local IP address (e.g., `http://192.168.1.x:5000/`).

4.  **Deep Linking**:
    *   The app supports `crowdmonitor://login` custom scheme.
    *   From the web registration page, a button will appear to "Open in App" which auto-fills/logs in the user in the Android app.
    *   To test: `adb shell am start -W -a android.intent.action.VIEW -d "crowdmonitor://login?name=John&phone=123"`

5.  **Permissions**:
    *   The app requires Location permissions.
    *   On Android 10+, you may need to manually enable "Allow all the time" in Settings for background tracking to work reliably when the app is closed.

## Features

*   **Login**: Simple name/phone entry to register/login.
*   **Tracking**: Background service that sends location updates every 10 seconds.
*   **Status**: Dashboard showing connection status.
