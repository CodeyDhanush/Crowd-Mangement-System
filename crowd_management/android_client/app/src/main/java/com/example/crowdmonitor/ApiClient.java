package com.example.crowdmonitor;

import okhttp3.OkHttpClient;
import retrofit2.Call;
import retrofit2.Retrofit;
import retrofit2.converter.gson.GsonConverterFactory;
import retrofit2.http.Body;
import retrofit2.http.POST;

public class ApiClient {

    private static final String BASE_URL = "https://crowd-monitor-bxd0.onrender.com"; // Update to your PC's IP address

    private static Retrofit retrofit = null;

    public static ApiService getClient() {
        if (retrofit == null) {
            retrofit = new Retrofit.Builder()
                    .baseUrl(BASE_URL)
                    .addConverterFactory(GsonConverterFactory.create())
                    .build();
        }
        return retrofit.create(ApiService.class);
    }

    public interface ApiService {
        @POST("register")
        Call<RegistrationResponse> register(@Body User user);

        @POST("location")
        Call<Void> updateLocation(@Body LocationUpdate location);
    }

    public static class User {
        String name;
        String phone;

        public User(String name, String phone) {
            this.name = name;
            this.phone = phone;
        }
    }

    public static class RegistrationResponse {
        int user_id;
        String message;
    }

    public static class LocationUpdate {
        int user_id;
        double latitude;
        double longitude;

        public LocationUpdate(int user_id, double latitude, double longitude) {
            this.user_id = user_id;
            this.latitude = latitude;
            this.longitude = longitude;
        }
    }
}
