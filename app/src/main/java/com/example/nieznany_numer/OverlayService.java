package com.example.nieznany_numer;

import android.annotation.SuppressLint;
import android.app.Service;
import android.content.Context;
import android.content.Intent;
import android.graphics.PixelFormat;
import android.os.Build;
import android.os.Handler;
import android.os.IBinder;
import android.os.Looper;
import android.telecom.TelecomManager;
import android.util.Log;
import android.view.Gravity;
import android.view.LayoutInflater;
import android.view.MotionEvent;
import android.view.View;
import android.view.WindowManager;
import android.widget.Button;
import android.widget.ImageButton;
import android.widget.TextView;

public class OverlayService extends Service {

    private static final String TAG = "OverlayService";
    public static final String EXTRA_PHONE_NUMBER = "phone_number";

    private WindowManager windowManager;
    private View overlayView;
    private final Handler mainHandler = new Handler(Looper.getMainLooper());

    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        if (intent == null) {
            stopSelf();
            return START_NOT_STICKY;
        }

        String phoneNumber = intent.getStringExtra(EXTRA_PHONE_NUMBER);
        if (phoneNumber == null || phoneNumber.isEmpty()) {
            stopSelf();
            return START_NOT_STICKY;
        }

        // Remove existing overlay if any
        removeOverlay();

        showOverlay(phoneNumber);
        return START_NOT_STICKY;
    }

    @SuppressLint("ClickableViewAccessibility")
    private void showOverlay(String phoneNumber) {
        windowManager = (WindowManager) getSystemService(WINDOW_SERVICE);

        int layoutType;
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            layoutType = WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY;
        } else {
            layoutType = WindowManager.LayoutParams.TYPE_PHONE;
        }

        WindowManager.LayoutParams params = new WindowManager.LayoutParams(
                WindowManager.LayoutParams.WRAP_CONTENT,
                WindowManager.LayoutParams.WRAP_CONTENT,
                layoutType,
                WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE
                        | WindowManager.LayoutParams.FLAG_SHOW_WHEN_LOCKED,
                PixelFormat.TRANSLUCENT
        );
        params.gravity = Gravity.TOP | Gravity.CENTER_HORIZONTAL;
        params.y = 100;

        LayoutInflater inflater = (LayoutInflater) getSystemService(LAYOUT_INFLATER_SERVICE);
        overlayView = inflater.inflate(R.layout.overlay_caller, null);

        // Set phone number
        TextView phoneText = overlayView.findViewById(R.id.overlay_phone_number);
        phoneText.setText(phoneNumber);

        // Close button
        ImageButton closeBtn = overlayView.findViewById(R.id.overlay_close);
        closeBtn.setOnClickListener(v -> {
            removeOverlay();
            stopSelf();
        });

        // Reject button (hidden by default, shown when rating is negative)
        Button rejectBtn = overlayView.findViewById(R.id.overlay_reject_btn);
        rejectBtn.setOnClickListener(v -> {
            rejectCall();
            removeOverlay();
            stopSelf();
        });

        // Make overlay draggable
        setupDragging(overlayView, params);

        windowManager.addView(overlayView, params);

        // Fetch phone number info
        fetchPhoneInfo(phoneNumber);
    }

    @SuppressLint("ClickableViewAccessibility")
    private void setupDragging(View view, WindowManager.LayoutParams params) {
        final float[] touchX = new float[1];
        final float[] touchY = new float[1];
        final int[] initialX = new int[1];
        final int[] initialY = new int[1];

        View dragHandle = view.findViewById(R.id.overlay_root);
        dragHandle.setOnTouchListener((v, event) -> {
            switch (event.getAction()) {
                case MotionEvent.ACTION_DOWN:
                    initialX[0] = params.x;
                    initialY[0] = params.y;
                    touchX[0] = event.getRawX();
                    touchY[0] = event.getRawY();
                    return true;
                case MotionEvent.ACTION_MOVE:
                    params.x = initialX[0] + (int) (event.getRawX() - touchX[0]);
                    params.y = initialY[0] + (int) (event.getRawY() - touchY[0]);
                    if (overlayView != null && overlayView.isAttachedToWindow()) {
                        windowManager.updateViewLayout(overlayView, params);
                    }
                    return true;
                case MotionEvent.ACTION_UP:
                    float dx = event.getRawX() - touchX[0];
                    float dy = event.getRawY() - touchY[0];
                    if (Math.abs(dx) < 10 && Math.abs(dy) < 10) {
                        v.performClick();
                    }
                    return true;
            }
            return false;
        });
    }

    private void fetchPhoneInfo(String phoneNumber) {
        PhoneNumberProvider provider = new PhoneNumberProvider();
        provider.getPhoneNumberInfo(this, phoneNumber, new PhoneNumberProvider.Callback() {
            @Override
            public void onResult(String displayText, String rating) {
                mainHandler.post(() -> updateOverlay(phoneNumber, displayText, rating));
            }
        });
    }

    private void updateOverlay(String phoneNumber, String displayText, String rating) {
        if (overlayView == null || !overlayView.isAttachedToWindow()) return;

        TextView loadingText = overlayView.findViewById(R.id.overlay_loading);
        loadingText.setVisibility(View.GONE);

        // Rating badge
        TextView ratingView = overlayView.findViewById(R.id.overlay_rating);
        ratingView.setVisibility(View.VISIBLE);
        switch (rating) {
            case "negative":
                ratingView.setText(R.string.rating_negative);
                ratingView.setBackgroundResource(R.drawable.badge_negative);
                break;
            case "positive":
                ratingView.setText(R.string.rating_positive);
                ratingView.setBackgroundResource(R.drawable.badge_positive);
                break;
            case "neutral":
                ratingView.setText(R.string.rating_neutral);
                ratingView.setBackgroundResource(R.drawable.badge_neutral);
                break;
            default:
                ratingView.setText(R.string.rating_unknown);
                ratingView.setBackgroundResource(R.drawable.badge_unknown);
                break;
        }

        // Info text
        TextView infoView = overlayView.findViewById(R.id.overlay_info);
        infoView.setText(displayText);
        infoView.setVisibility(View.VISIBLE);

        // Show reject button for negative ratings
        Button rejectBtn = overlayView.findViewById(R.id.overlay_reject_btn);
        if ("negative".equals(rating)) {
            rejectBtn.setVisibility(View.VISIBLE);
        }
    }

    @SuppressLint("MissingPermission")
    private void rejectCall() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
            TelecomManager telecomManager = (TelecomManager) getSystemService(Context.TELECOM_SERVICE);
            if (telecomManager != null) {
                try {
                    telecomManager.endCall();
                } catch (Exception e) {
                    Log.e(TAG, "Failed to reject call", e);
                }
            }
        } else {
            rejectCallLegacy();
        }
    }

    private void rejectCallLegacy() {
        try {
            @SuppressLint("PrivateApi")
            Class<?> telephonyClass = Class.forName("android.telephony.TelephonyManager");
            android.telephony.TelephonyManager tm =
                    (android.telephony.TelephonyManager) getSystemService(Context.TELEPHONY_SERVICE);
            @SuppressLint("DiscouragedPrivateApi")
            java.lang.reflect.Method getITelephony = telephonyClass.getDeclaredMethod("getITelephony");
            getITelephony.setAccessible(true);
            Object iTelephony = getITelephony.invoke(tm);
            if (iTelephony != null) {
                java.lang.reflect.Method endCall = iTelephony.getClass().getMethod("endCall");
                endCall.invoke(iTelephony);
            }
        } catch (Exception e) {
            Log.e(TAG, "Failed to reject call (legacy)", e);
        }
    }

    private void removeOverlay() {
        if (overlayView != null && windowManager != null) {
            try {
                if (overlayView.isAttachedToWindow()) {
                    windowManager.removeView(overlayView);
                }
            } catch (Exception e) {
                Log.e(TAG, "Error removing overlay", e);
            }
            overlayView = null;
        }
    }

    @Override
    public void onDestroy() {
        removeOverlay();
        super.onDestroy();
    }
}
