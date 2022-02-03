package com.example.nieznany_numer;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.telephony.TelephonyManager;
import android.widget.Toast;



public class PhoneStateReceiver extends BroadcastReceiver {
    @Override
    public void onReceive(Context context, Intent intent) {
        try {
            String state = intent.getStringExtra(TelephonyManager.EXTRA_STATE);
            String incomingNumber = intent.getStringExtra(TelephonyManager.EXTRA_INCOMING_NUMBER);
            if (state.equals(TelephonyManager.EXTRA_STATE_RINGING)) {
                MainActivity.setPhoneNumber(incomingNumber);
                //MainActivity.getPhoneNumberInfo(incomingNumber);
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}

//public class PhoneStateReceiver extends BroadcastReceiver {
//    @Override
//    public void onReceive(Context context, Intent intent) {
//
//        try {
//            System.out.println("Receiver start");
//            String state = intent.getStringExtra(TelephonyManager.EXTRA_STATE);
//            String incomingNumber = intent.getStringExtra(TelephonyManager.EXTRA_INCOMING_NUMBER);
//            Log.e("Incoming Number", "Number is ," + incomingNumber);
//            Log.e("State", "State is ," + state);
//            if(state.equals(TelephonyManager.EXTRA_STATE_RINGING)){
//                Toast.makeText(context,"Incoming Call State",Toast.LENGTH_SHORT).show();
//                Toast.makeText(context,"Ringing State Number is -"+incomingNumber,Toast.LENGTH_SHORT).show();
//            }
//            if ((state.equals(TelephonyManager.EXTRA_STATE_OFFHOOK))){
//                Toast.makeText(context,"Call Received State",Toast.LENGTH_SHORT).show();
//            }
//            if (state.equals(TelephonyManager.EXTRA_STATE_IDLE)){
//                Toast.makeText(context,"Call Idle State",Toast.LENGTH_SHORT).show();
//            }
//        }
//        catch (Exception e){
//            e.printStackTrace();
//        }
//
//    }
//}
//public class PhoneStateReceiver extends BroadcastReceiver {
//
//    @Override
//    public void onReceive(Context context, Intent intent) {
//        Bundle extras = intent.getExtras();
//        if (extras != null) {
//            String state = intent.getStringExtra(TelephonyManager.EXTRA_STATE); //Change Here
//            Log.w("MY_DEBUG_TAG", state);
//            if (state.equals(TelephonyManager.EXTRA_STATE_RINGING)) {
//                //context.startActivity(new Intent(context, popup_.class));
//                //((MainActivity)context).finish();
//                String phoneNumber = intent.getStringExtra(TelephonyManager.EXTRA_INCOMING_NUMBER); //Change Here
//                Log.w("MY_DEBUG_TAG", phoneNumber);
//            }
//        }
//
//    }
//}
//public class PhoneStateReceiver extends BroadcastReceiver {
//    @Override
//    public void onReceive(Context context, Intent intent) {
//        try {
//            TelephonyManager telephony = (TelephonyManager) context.getSystemService(Context.TELEPHONY_SERVICE);
//            telephony.listen(new PhoneStateListener() {
//                @Override
//                public void onCallStateChanged(int state, String phoneNumber) {
//                    Log.e("MAMY_TO", phoneNumber);
//                }
//            }, PhoneStateListener.LISTEN_CALL_STATE);
//        } catch (Exception e) {
//            e.printStackTrace();
//        }
//    }
//}
//public class PhoneStateReceiver extends BroadcastReceiver {
//    private static final String INCOMING_CALL_INTENT = "android.intent.action.NEW_INCOMING_CALL";
//
//    @Override
//    public void onReceive(final Context context, Intent intent) {
//        TelephonyManager telephony = (TelephonyManager) context.getSystemService(Context.TELEPHONY_SERVICE);
//        telephony.listen(new PhoneStateListener() {
//            @Override
//            public void onCallStateChanged(int state, String incomingNumber) {
//                super.onCallStateChanged(state, incomingNumber);
//                System.out.println("incomingNumber : " + incomingNumber);
//                Log.e("YES", "Phone Number: " + incomingNumber);
//            }
//        }, PhoneStateListener.LISTEN_CALL_STATE);
//    }
//}