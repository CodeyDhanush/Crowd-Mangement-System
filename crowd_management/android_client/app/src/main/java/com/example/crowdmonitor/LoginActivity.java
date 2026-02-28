package com.example.crowdmonitor;

import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ProgressBar;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class LoginActivity extends AppCompatActivity {

    private EditText etName, etPhone;
    private Button btnLogin;
    private ProgressBar progressBar;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        
        // Check if already logged in
        SharedPreferences prefs = getSharedPreferences("AppPrefs", MODE_PRIVATE);
        int userId = prefs.getInt("user_id", -1);
        if (userId != -1) {
            startMainActivity(userId);
            return;
        }

        setContentView(R.layout.activity_login);

        etName = findViewById(R.id.etName);
        etPhone = findViewById(R.id.etPhone);
        btnLogin = findViewById(R.id.btnLogin);
        progressBar = findViewById(R.id.progressBar);

        btnLogin.setOnClickListener(v -> login());

        handleDeepLink(getIntent());
    }

    private void handleDeepLink(Intent intent) {
        if (intent != null && intent.getData() != null) {
            String scheme = intent.getData().getScheme();
            if ("crowdmonitor".equals(scheme)) {
                String name = intent.getData().getQueryParameter("name");
                String phone = intent.getData().getQueryParameter("phone");

                if (name != null) etName.setText(name);
                if (phone != null) etPhone.setText(phone);
                
                if (name != null && phone != null) {
                    login(); // Auto-login
                }
            }
        }
    }

    private void login() {
        String name = etName.getText().toString();
        String phone = etPhone.getText().toString();

        if (name.isEmpty() || phone.isEmpty()) {
            Toast.makeText(this, "Please fill all fields", Toast.LENGTH_SHORT).show();
            return;
        }

        progressBar.setVisibility(View.VISIBLE);
        btnLogin.setEnabled(false);

        ApiClient.User user = new ApiClient.User(name, phone);
        ApiClient.getClient().register(user).enqueue(new Callback<ApiClient.RegistrationResponse>() {
            @Override
            public void onResponse(Call<ApiClient.RegistrationResponse> call, Response<ApiClient.RegistrationResponse> response) {
                progressBar.setVisibility(View.GONE);
                btnLogin.setEnabled(true);

                if (response.isSuccessful() && response.body() != null) {
                    int userId = response.body().user_id; // Using field directly assuming public or standard getter
                    
                    // Save User ID
                    SharedPreferences prefs = getSharedPreferences("AppPrefs", MODE_PRIVATE);
                    prefs.edit().putInt("user_id", userId).apply();
                    prefs.edit().putString("user_name", name).apply();

                    startMainActivity(userId);
                } else {
                    Toast.makeText(LoginActivity.this, "Login failed: " + response.message(), Toast.LENGTH_SHORT).show();
                }
            }

            @Override
            public void onFailure(Call<ApiClient.RegistrationResponse> call, Throwable t) {
                progressBar.setVisibility(View.GONE);
                btnLogin.setEnabled(true);
                Toast.makeText(LoginActivity.this, "Network error: " + t.getMessage(), Toast.LENGTH_SHORT).show();
            }
        });
    }

    @Override
    protected void onNewIntent(Intent intent) {
        super.onNewIntent(intent);
        setIntent(intent);
        handleDeepLink(intent);
    }

    private void startMainActivity(int userId) {
        Intent intent = new Intent(this, MainActivity.class);
        intent.putExtra("user_id", userId);
        startActivity(intent);
        finish();
    }
}
