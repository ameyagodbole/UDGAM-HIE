package com.aanv.grabgarbage;

import android.app.Activity;
import android.app.ProgressDialog;
import android.content.Intent;
import android.graphics.Bitmap;
import android.os.Handler;
import android.support.v4.widget.ImageViewCompat;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.support.v7.widget.LinearLayoutCompat;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.Toast;

public class MainActivity extends AppCompatActivity {
    private static final int CAMERA_REQUEST = 0;
    LinearLayout screen;
    ImageView capture;
    Button tryAgain, confirm;
    SessionManager manager;

    private void launchCamera(){
        Intent cameraIntent = new Intent(android.provider.MediaStore.ACTION_IMAGE_CAPTURE);
        startActivityForResult(cameraIntent, CAMERA_REQUEST);
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        manager = new SessionManager(this);
        screen = findViewById(R.id.linear_layout);
        tryAgain = findViewById(R.id.try_again);
        confirm = findViewById(R.id.confirm);
        capture = findViewById(R.id.capture);

        screen.setVisibility(View.GONE);
        launchCamera();

        tryAgain.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                screen.setVisibility(View.GONE);
                launchCamera();
            }
        });

        confirm.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
//                Toast.makeText(MainActivity.this, "Chal raha hai!!!", Toast.LENGTH_SHORT).show();
                final ProgressDialog dialog = new ProgressDialog(MainActivity.this);
                dialog.setMessage("Verifying Trash...");
                dialog.setCancelable(true);
                dialog.show();

                Handler handler = new Handler();
                handler.postDelayed(new Runnable() {
                    public void run() {
                        dialog.dismiss();
                        manager.increaseCount();
                        int count = manager.getCount();
                        if(count % 2 != 0){
                            Toast.makeText(MainActivity.this, "Captured image is not a trash!!",
                                    Toast.LENGTH_SHORT).show();
                            launchCamera();
                        }else {
                            final ProgressDialog messageDialog = new ProgressDialog(MainActivity.this);
                            messageDialog.setMessage("Sending coordinates...");
                            messageDialog.setCancelable(true);
                            messageDialog.show();

                            Handler mhandler = new Handler();
                            mhandler.postDelayed(new Runnable() {
                                public void run() {
                                    messageDialog.dismiss();
                                    Toast.makeText(MainActivity.this, "Sent, thank you!!",
                                            Toast.LENGTH_SHORT).show();
                                    launchCamera();
                                }
                            }, 2000);



                        }
                    }
                }, 2000);

            }
        });


    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        screen.setVisibility(View.VISIBLE);
        if (requestCode == CAMERA_REQUEST && resultCode == Activity.RESULT_OK) {
            Bitmap photo = (Bitmap) data.getExtras().get("data");
            capture.setImageBitmap(photo);
        }

    }
}
