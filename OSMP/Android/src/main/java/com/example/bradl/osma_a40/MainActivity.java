//Main Activity for GUI
package com.example.bradl.osma_a40;

import android.content.ComponentName;
import android.content.Intent;
import android.os.Build;
//import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.os.Handler;
import android.os.Message;
import android.support.v7.app.AppCompatActivity;
import android.support.v7.widget.Toolbar;
import android.view.Menu;
import android.view.MenuItem;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;
import android.widget.ToggleButton;

import com.example.bradl.osma_a40.R;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.MalformedURLException;
import java.net.URL;
import java.net.URLConnection;
import java.text.SimpleDateFormat;
import java.util.Date;

import static com.example.bradl.osma_a40.R.layout.activity_led_control;

public class MainActivity extends AppCompatActivity {

    TextView    tempValue, humiValue, soundValue, dustValue, redTxt, greenTxt, blueTxt;  //For current value
    TextView    tempMax, tempMin, humiMax, humiMin, soundMax, soundMin, dustMax, dustMin; //for maximum and minimum value
    Toolbar     mainToolbar;
    float       tempMaxValue=-90, tempMinValue=90, humiMaxValue=-90, humiMinValue=90;
    float       soundMaxValue=-90, soundMinValue=90, dustMaxValue=-90, dustMinValue=90;

    static public Handler handler; //for sub-thread and LedControl activity send back msg to GUI thread
    static public boolean keepConnected = false;  //for sub-thread to keep or not the connection with the sensor
    static public SensorData sd;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        handler = new MyHandler();
        mainToolbar = (Toolbar) findViewById(R.id.my_toolbar);

        tempValue = (TextView)findViewById(R.id.tempValue);
        humiValue = (TextView)findViewById(R.id.humiValue);
        soundValue = (TextView)findViewById(R.id.soundValue);
        dustValue = (TextView)findViewById(R.id.dustValue);

        tempMax = (TextView)findViewById(R.id.tempMax);
        tempMin = (TextView)findViewById(R.id.tempMin);

        humiMax = (TextView)findViewById(R.id.humiMax);
        humiMin = (TextView)findViewById(R.id.humiMin);

        soundMax = (TextView)findViewById(R.id.soundMax);
        soundMin = (TextView)findViewById(R.id.soundMin);

        dustMax = (TextView)findViewById(R.id.dustMax);
        dustMin = (TextView)findViewById(R.id.dustMin);

        redTxt = (TextView)findViewById(R.id.redTxt);
        greenTxt = (TextView)findViewById(R.id.greenTxt);
        blueTxt = (TextView)findViewById(R.id.blueTxt);

        mainToolbar.setTitle("Sensor Manager");
        mainToolbar.setTitleTextColor(getResources().getColor(R.color.colorWhite));
        mainToolbar.setLogo(R.drawable.sound);
        setSupportActionBar(mainToolbar);
        //myToolbar.setNavigationIcon(R.mipmap.ic_launcher);
        mainToolbar.setOnMenuItemClickListener(new Toolbar.OnMenuItemClickListener() {
            @Override
            public boolean onMenuItemClick(MenuItem item) {
                switch (item.getItemId()) {
                    case R.id.connectSensor:
                        keepConnected = true;
                        GetDataThread getDataThread = new GetDataThread();
                        getDataThread.start();  //create and start getdata thread to connect with sensor
                        Toast.makeText(MainActivity.this, "connectSensor!", Toast.LENGTH_LONG).show();
                        break;
                    case R.id.disconnect:
                        keepConnected = false;
                        Toast.makeText(MainActivity.this, "DisconnectSensor!", Toast.LENGTH_LONG).show();
                        break;
                    case R.id.controlLed:
                        Intent intent = new Intent();
                        intent.setClass(MainActivity.this, LedControl.class);
                        startActivity(intent);
                        //setContentView(R.layout.activity_led_control);
                        //Toast.makeText(MainActivity.this, "control Led !", Toast.LENGTH_SHORT).show();
                        break;
                    case R.id.jointAction:
                        Toast.makeText(MainActivity.this, "joint Action !", Toast.LENGTH_SHORT).show();
                        break;
                }
                return true;
            }
        });
    }

    class MyHandler extends Handler{
        @Override
        public void handleMessage(Message msg)
        {
            //System.out.println("In UI Thread: "+Thread.currentThread().getName());
            String s = msg.obj.toString();
            System.out.println(s);
            //statistic of the data
            if(sd.temprature>tempMaxValue)  tempMaxValue=sd.temprature;
            if(sd.temprature<tempMinValue)  tempMinValue=sd.temprature;
            if(sd.humid>humiMaxValue)   humiMaxValue = sd.humid;
            if(sd.humid<humiMinValue)   humiMinValue = sd.humid;
            if(sd.sound>soundMaxValue)   soundMaxValue = sd.sound;
            if(sd.sound<soundMinValue)   soundMinValue = sd.sound;
            if(sd.dust>dustMaxValue)    dustMaxValue = sd.dust;
            if(sd.dust<dustMinValue)    dustMinValue = sd.dust;

            tempValue.setText(""+sd.temprature);
            tempMax.setText(""+tempMaxValue);
            tempMin.setText(""+tempMinValue);

            humiValue.setText(""+sd.humid);
            humiMax.setText(""+humiMaxValue);
            humiMin.setText(""+humiMinValue);

            soundValue.setText(String.format("%.2f", sd.sound).toString());
            soundMax.setText(String.format("%.2f", soundMaxValue).toString());
            soundMin.setText(String.format("%.2f", soundMinValue).toString());

            dustValue.setText(String.format("%.2f", sd.dust).toString());
            dustMax.setText(String.format("%.2f", dustMaxValue).toString());
            dustMin.setText(String.format("%.2f", dustMinValue).toString());


            redTxt.setText("RED_OFF");
            greenTxt.setText("GRN_OFF");
            blueTxt.setText("BLU_OFF");
            if(sd.red == 1) redTxt.setText("RED_ON");
            if(sd.green == 1) greenTxt.setText("GRN_ON");
            if(sd.blue == 1) blueTxt.setText("BLU_ON");
        }
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu){
        getMenuInflater().inflate(R.menu.menu_main, menu);
        return true;
    }


    static class SensorData
    {//class for sensor and led data
        float temprature, humid, sound, dust;
        int   red, blue, green;
        String collectTime;
        public void SensorData() {
            temprature=humid=sound=dust=(float)0.0; red=blue=green=0; collectTime="";
        }
    }
    class GetDataThread extends Thread
    {//Get data thread which connect with IoT egg
        @Override
        public void run()
        {
            while(MainActivity.keepConnected)
            {
                try{
                    URL myUrl = new URL("http://192.168.4.1:8081/");
                    URLConnection tc = myUrl.openConnection();
                    BufferedReader in;
                    in = new BufferedReader(new InputStreamReader(tc.getInputStream()));
                    String inputLine;
                    SensorData sd;
                    while((inputLine = in.readLine()) != null)
                    {
                        SimpleDateFormat df = new SimpleDateFormat("yyyyMMddHHmmss");
                        String dstr = df.format(new Date());
                        System.out.println(dstr);
                        sd = ParseSDFromStr(inputLine);
                        sd.collectTime=dstr;
                        MainActivity.sd = sd;
                        System.out.println("child thread"+Thread.currentThread().getName());
                        String s = "From child thread of Service";

                        Message msg = handler.obtainMessage();
                        msg.obj = s;
                        handler.sendMessage(msg);
                    }
                    in.close();
                    Thread.sleep(500); //in case read too quickly
                } catch (MalformedURLException e)
                {System.out.println("MalformedURLException"+e);}
                catch (IOException e) {e.printStackTrace(); System.out.println("IOException"+e);} catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
            //Toast.makeText(MainActivity.this, "Get sensor data ended!", Toast.LENGTH_LONG).show();
        }

    }
    static SensorData ParseSDFromStr(String txtStr)
    { // parse reading string stream to sensor data
        String strTemp;
        SensorData sd;
        sd = new SensorData();
        sd.temprature = Float.parseFloat(txtStr.substring(29,31));
        sd.humid = Float.parseFloat(txtStr.substring(38,40));
        sd.sound = Float.parseFloat(txtStr.substring(52,61));
        sd.dust = Float.parseFloat(txtStr.substring(74,83));
        sd.red = Integer.parseInt(txtStr.substring(91,92));
        sd.blue = Integer.parseInt(txtStr.substring(102,103));
        sd.green = Integer.parseInt(txtStr.substring(112,113));
        return sd;
    }
}
