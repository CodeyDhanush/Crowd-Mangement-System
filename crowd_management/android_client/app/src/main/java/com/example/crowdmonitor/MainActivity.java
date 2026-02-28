package com.example.crowdmonitor;

import android.Manifest;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.os.Build;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;

import androidx.activity.result.ActivityResultLauncher;
import androidx.activity.result.contract.ActivityResultContracts;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.content.ContextCompat;

public class MainActivity extends AppCompatActivity {

    private static final String PERMISSION_FINE = Manifest.permission.ACCESS_FINE_LOCATION;
    private static final String PERMISSION_BG = Manifest.permission.ACCESS_BACKGROUND_LOCATION;

    private TextView tvStatus, tvUserId;
    private Button btnLogout;
    private int userId;

    private final ActivityResultLauncher<String[]> locationPermissionLauncher =
            registerForActivityResult(new ActivityResultContracts.RequestMultiplePermissions(), permissions -> {
                if (Boolean.TRUE.equals(permissions.get(PERMISSION_FINE)) || 
                    Boolean.TRUE.equals(permissions.get(Manifest.permission.ACCESS_COARSE_LOCATION))) {
                    startTrackingService();
                } else {
                    Toast.makeText(this, "Location permission required", Toast.LENGTH_LONG).show();
                    tvStatus.setText("Status: Permission Denied");
                }
            });

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main); // Assuming layout exists

        tvStatus = findViewById(R.id.tvStatus);
        tvUserId = findViewById(R.id.tvUserId);
        btnLogout = findViewById(R.id.btnLogout);

        userId = getIntent().getIntExtra("user_id", -1);
        if (userId == -1) {
            // Check prefs
            SharedPreferences prefs = getSharedPreferences("AppPrefs", MODE_PRIVATE);
            userId = prefs.getInt("user_id", -1);
            if (userId == -1) {
                // Return to Login
                startActivity(new Intent(this, LoginActivity.class));
                finish();
                return;
            }
        }

        tvUserId.setText("User ID: " + userId);
        tvStatus.setText("Status: Initializing...");

        btnLogout.setOnClickListener(v -> logout());

        checkPermissionsAndStart();
    }

    private void checkPermissionsAndStart() {
        if (ContextCompat.checkSelfPermission(this, PERMISSION_FINE) == PackageManager.PERMISSION_GRANTED) {
            startTrackingService();
        } else {
            locationPermissionLauncher.launch(new String[]{PERMISSION_FINE, Manifest.permission.ACCESS_COARSE_LOCATION});
        }
    }

    private void startTrackingService() {
        tvStatus.setText("Status: Tracking Active");
        Intent serviceIntent = new Intent(this, TrackingService.class);
        serviceIntent.putExtra("user_id", userId);
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            startForegroundService(serviceIntent);
        } else {
            startService(serviceIntent);
        }
    }

    private void stopTrackingService() {
        Intent serviceIntent = new Intent(this, TrackingService.class);
        stopService(serviceIntent);
        tvStatus.setText("Status: Stopped");
    }

    private void logout() {
        stopTrackingService();
        SharedPreferences prefs = getSharedPreferences("AppPrefs", MODE_PRIVATE);
        prefs.edit().clear().apply();
        startActivity(new Intent(this, LoginActivity.class));
        finish();
    }
}
