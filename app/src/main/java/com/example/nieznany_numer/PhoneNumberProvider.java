package com.example.nieznany_numer;

import android.content.Context;
import android.util.Log;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;

public class PhoneNumberProvider {

    private static final String TAG = "PhoneNumberProvider";
    private static final String API_BASE = "https://your-server.com/api/v1/numbers/";
    private static final int TIMEOUT_MS = 5_000;

    public interface Callback {
        void onResult(String displayText, String rating);
    }

    public void getPhoneNumberInfo(Context context, String phoneNumber, Callback callback) {
        new Thread(() -> {
            StringBuilder builder = new StringBuilder();
            String rating = "unknown";

            try {
                URL url = new URL(API_BASE + phoneNumber);
                HttpURLConnection conn = (HttpURLConnection) url.openConnection();
                conn.setRequestMethod("GET");
                conn.setConnectTimeout(TIMEOUT_MS);
                conn.setReadTimeout(TIMEOUT_MS);
                conn.setRequestProperty("Accept", "application/json");

                int code = conn.getResponseCode();
                if (code != 200) {
                    builder.append(context.getString(R.string.error_geting_pn_info))
                            .append("HTTP ").append(code);
                } else {
                    BufferedReader reader = new BufferedReader(
                            new InputStreamReader(conn.getInputStream()));
                    StringBuilder json = new StringBuilder();
                    String line;
                    while ((line = reader.readLine()) != null) {
                        json.append(line);
                    }
                    reader.close();

                    JSONObject data = new JSONObject(json.toString());
                    rating = data.optString("rating", "unknown");

                    JSONObject counts = data.getJSONObject("rating_counts");
                    String ratingLabel;
                    switch (rating) {
                        case "negative": ratingLabel = "Negatywna"; break;
                        case "positive": ratingLabel = "Pozytywna"; break;
                        case "neutral":  ratingLabel = "Neutralna"; break;
                        default:         ratingLabel = "Brak ocen"; break;
                    }

                    builder.append(context.getString(R.string.telephone_ocena)).append(ratingLabel);
                    builder.append(" (-)").append(counts.optInt("negative", 0));
                    builder.append(" (~)").append(counts.optInt("neutral", 0));
                    builder.append(" (+)").append(counts.optInt("positive", 0));

                    builder.append("\n").append(context.getString(R.string.telephone_searches))
                            .append(data.optInt("search_count", 0));
                    builder.append("\n").append(context.getString(R.string.telephone_comments))
                            .append(data.optInt("comment_count", 0));

                    String lastSearched = data.optString("last_searched", "");
                    if (!lastSearched.isEmpty() && lastSearched.length() >= 10) {
                        builder.append("\n").append(context.getString(R.string.telephone_last_checked))
                                .append(lastSearched.substring(0, 10));
                    }

                    JSONArray comments = data.optJSONArray("comments");
                    if (comments != null && comments.length() > 0) {
                        builder.append("\n\n").append(context.getString(R.string.telephone_user_comments));
                        for (int i = 0; i < comments.length(); i++) {
                            JSONObject c = comments.getJSONObject(i);
                            builder.append("\n- ").append(c.optString("text", ""));
                        }
                    }
                }
                conn.disconnect();
            } catch (Exception e) {
                Log.e(TAG, "Failed to fetch phone number info", e);
                builder.append(context.getString(R.string.error_geting_pn_info))
                        .append(e.getMessage());
            }

            final String finalRating = rating;
            final String finalText = builder.toString();
            if (callback != null) {
                callback.onResult(finalText, finalRating);
            }
        }).start();
    }
}
