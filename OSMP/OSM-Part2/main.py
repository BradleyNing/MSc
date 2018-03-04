from flask import Flask, render_template, request, redirect, url_for

import pyupm_th02 as Th02
import mraa     # For accessing the GPIO
import time     # For sleeping between blinks
from threading import Thread

app = Flask(__name__)

#Temperature and humidity sensor data initialization
tempMax=0
tempMin=100
humiMax=0
humiMin=100
soundMax=0
soundMin=100

#LED control data initialization
LED_GPIO = 13                  
Led = mraa.Gpio(LED_GPIO) 
Led.dir(mraa.DIR_OUT)     
Led.write(0)
ledState = False        #LED is off at beginning
bKeepBlinking = False	#Not blinking at beginning
blinkValue = 1000       #if sensor value>blinkValue, then blinking
blinkType = ''			#to identify the criteria for which sensor
blinkFreq = 1.0 		#default blinking frequency=1Hz

def Blinking():
    # Blinking thread
    global Led
    global ledState
    global bKeepBlinking
    global blinkFreq

    while bKeepBlinking:
        if ledState == False:
            Led.write(1)
            ledState = True    
        else:
            Led.write(0)
            ledState = False
        time.sleep(1.0/blinkFreq)  #Wait for a while 

@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
	global tempMax,tempMin,humiMax,humiMin
	global blinkValue, blinkType, bKeepBlinking

	th02_sensor = Th02.TH02(1)
	temp = th02_sensor.getTemperature()
	if(temp>tempMax): 
		tempMax = temp
	if(temp<tempMin): 
		tempMin = temp
	
	if((float(temp)>float(blinkValue)) and (blinkType=='temp')):
		if(bKeepBlinking==False):
			bKeepBlinking = True
			b1 = Thread(target=Blinking)
			b1.start()
	
	humi = th02_sensor.getHumidity()
	if(humi>humiMax): 
		humiMax = humi
	if(humi<humiMin): 
		humiMin = humi	

	if((float(humi)>float(blinkValue)) and (blinkType=='humi')):
		if(bKeepBlinking==False):
			bKeepBlinking = True
			b1 = Thread(target=Blinking)
			b1.start()

	return render_template('Index.html', temp=temp, tempMax=tempMax, tempMin=tempMin, 
		humi=humi, humiMax=humiMax, humiMin=humiMin)

@app.route('/post', methods=['POST'])
def post():
	global bKeepBlinking, blinkValue, blinkType, blinkFreq

	if request.method == 'POST':
		if (request.form['submit'] == 'Blink'):
			if(bKeepBlinking==False):
				bKeepBlinking = True
				b1 = Thread(target=Blinking)
				b1.start()

		if (request.form['submit'] == 'NoBlink'):
			bKeepBlinking = False
			Led.write(0)
			ledState = False  
			blinkType=''
			blinkValue=1000

		if (request.form['submit'] == 'ThresholdConfirm'):
			blinkValue = request.form['threshold']
			blinkType = request.form['sType']
		
		if (request.form['submit'] == 'FreqConfirm'):
			blinkFreq = (float(request.form['freq']))/10
			if(blinkFreq<=0.0):
				blinkFreq = 0.1
			if(blinkFreq>10.0):
				blinkFreq = 10.0
				
			#mLcd.write(blinkType)
	return redirect(url_for('index'))

if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True, port=int(8000))
	#manager.run()
