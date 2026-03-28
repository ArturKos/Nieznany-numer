package com.example.nieznany_numer;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.telephony.TelephonyManager;

public class PhoneStateReceiver extends BroadcastReceiver {
    @Override
    public void onReceive(Context context, Intent intent) {
        try {
            String state = intent.getStringExtra(TelephonyManager.EXTRA_STATE);
            if (state == null) return;

            if (TelephonyManager.EXTRA_STATE_RINGING.equals(state)) {
                String incomingNumber = intent.getStringExtra(TelephonyManager.EXTRA_INCOMING_NUMBER);
                if (incomingNumber != null && !incomingNumber.isEmpty()) {
                    Intent serviceIntent = new Intent(context, OverlayService.class);
                    serviceIntent.putExtra(OverlayService.EXTRA_PHONE_NUMBER, incomingNumber);
                    context.startService(serviceIntent);
                }
            } else if (TelephonyManager.EXTRA_STATE_IDLE.equals(state)
                    || TelephonyManager.EXTRA_STATE_OFFHOOK.equals(state)) {
                // Call ended or answered — remove overlay
                context.stopService(new Intent(context, OverlayService.class));
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
