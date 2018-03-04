//LedControl activity
package com.example.bradl.osma_a40;

import android.content.Intent;
import android.os.Handler;
import android.os.Message;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.support.v7.widget.Toolbar;
import android.view.View;
import android.widget.Toast;
import android.widget.ToggleButton;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.MalformedURLException;
import java.net.URL;
import java.net.URLConnection;
import java.text.SimpleDateFormat;
import java.util.Date;

import static com.example.bradl.osma_a40.MainActivity.ParseSDFromStr;


public class LedControl extends AppCompatActivity {
    static public String ledStr;  //control command str
    ToggleButton swRed, swGreen, swBlue;
    Toolbar ledControlToolbar;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_led_control);
        ledControlToolbar = (Toolbar) findViewById(R.id.led_toolbar);
        ledControlToolbar.setTitle("Led Control");
        ledControlToolbar.setTitleTextColor(getResources().getColor(R.color.colorWhite));
        setSupportActionBar(ledControlToolbar);
    }

    public void setLed(View v){
        swRed = (ToggleButton)findViewById(R.id.swRed);
        swGreen = (ToggleButton)findViewById(R.id.swGreen);
        swBlue = (ToggleButton)findViewById(R.id.swBlue);

        LedThread getLedStatus = new LedThread();
        String sRed="redLed=0", sGreen="greenLed=0", sBlue="blueLed=0";
        if(swRed.isChecked())   sRed="redLed=1";
        if(swGreen.isChecked()) sGreen="greenLed=1";
        if(swBlue.isChecked()) sBlue="blueLed=1";

        ledStr = sRed + "," + sGreen + "," + sBlue;  //generate the comand string for url connection
        System.out.println(ledStr);
        getLedStatus.start();
        Toast.makeText(LedControl.this, "Confirmed change of LED", Toast.LENGTH_LONG).show();
    }

    public void backHome(View v){
        Intent intent = new Intent();
        intent.setClass(this, MainActivity.class);
        startActivity(intent);
    }

    class LedThread extends Thread
    { //Led control thread
        @Override
        public void run()
        {
            boolean bFinished = false;
            while(!bFinished)
            {//incase failure during the setting, exit loop until set sucessfully;
                // will sleep sometime in case occupy too much resourse when no connection
                try {
                    String urlStr = "http://192.168.4.1:8081/" + ledStr;
                    System.out.println(urlStr);
                    URL myUrl = new URL(urlStr);

                    URLConnection tc = myUrl.openConnection();
                    BufferedReader in;
                    in = new BufferedReader(new InputStreamReader(tc.getInputStream()));
                    String inputLine;
                    //MainActivity.SensorData sd;
                    while ((inputLine = in.readLine()) != null) {
                        SimpleDateFormat df = new SimpleDateFormat("yyyyMMddHHmmss");
                        String dstr = df.format(new Date());
                        System.out.println(dstr);
                        MainActivity.sd = ParseSDFromStr(inputLine);
                        MainActivity.sd.collectTime = dstr;
                        //.sd = sd;
                        System.out.println("child thread" + Thread.currentThread().getName());
                        String s = "From child thread of Service";
                        bFinished = true;

                        Message msg = MainActivity.handler.obtainMessage();
                        msg.obj = s;
                        MainActivity.handler.sendMessage(msg);
                    }
                    in.close();
                } catch (MalformedURLException e) {
                    System.out.println("MalformedURLException" + e);
                } catch (IOException e) {
                    e.printStackTrace();
                    System.out.println("IOException" + e);
                }
                try {
                    Thread.sleep(600);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
        }
    }
}
