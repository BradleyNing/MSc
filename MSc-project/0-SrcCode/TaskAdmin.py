# -*- coding: utf-8 -*-
from flask import Flask, jsonify, request, abort, make_response
from flask_httpauth import HTTPBasicAuth
from API import ITRT, SDA_alert, SDA_admin, GPAL, DAAS_ARIMA
import base64
import logging
import paho.mqtt.publish as publish
import json
import SDA_Functions as sdaf
import DAAS_DEF
import sys, traceback
from time import gmtime, strftime

app = Flask(__name__)
auth = HTTPBasicAuth()
api_list = ('ITRT','TS','SDA','GPAL')
ver_list = ('1.0')

logging.basicConfig(level=logging.INFO)

@auth.get_password
def get_password(username):
    if username == 'Bradley-ZN00046':
        return 'Bradley-ZN00046'
    return None

@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'response': 'Bad request'}), 400)

#@auth.error_handler
#def unauthorized():
#    return make_response(jsonify({'error': 'Unauthorized access'}), 401)

#@app.before_request
#def before_request():
    #pass
    #app.logger.info("before_request,")
    #app.logger.info(request.headers)
    #return redirect(url_for('task_list'))

@app.route('/daas', methods=['GET'])
#@auth.login_required
def task_list():
    app.logger.info("In Get,")
    result = {"Result": "Your task list:"}
    #return make_response(jsonify({'response': result}),200)
    return (jsonify({'response': result}),200)

@app.route('/daas/ITRT', methods=['POST'])
#@auth.login_required
def task_ITRT():
    app.logger.info("In Post,")
    result = {"Result": "post done"}
    imageFile = request.json['content']

    version = 'V1'
    service = ITRT()
    result = service.Execute(version, imageFile)
    #UpdateDB(result)
    return jsonify({'response': result}), 201

@app.route('/daas/ITRT_m', methods=['POST'])
#@auth.login_required
def task_ITRT_m():
    fileName = request.form['name']
    base64Imag = request.form['image']
    
    image = base64.b64decode(base64Imag)
    fn = open('uploadImage.jpg', 'wb')
    fn.write(image)
    fn.close()
    
    version = 'V1'
    service = ITRT()
    result = service.Execute(version, base64Imag)
    #UpdateDB(result)    
    #txtRes = {'txt': 'Hello', 'TransTxt':'你好', 'Task':'done'}
    txtRes = json.dumps(result)
    app.logger.info(txtRes)
    return str(txtRes), 200

sda_task = {
    'url': "http://www.odaa.dk/api/action/datastore_search",
    'resource_id': 'b3eeb0ff-c8a8-4824-99d6-e0a3747c8b0d',
    #'rpt_id': '*',
    'max_velocity': 130,
    'max_vehicles': 60,
    'min_velocity': 0,
    'min_vehicles': 0,
}
'''url = 'http://www.odaa.dk/api/action/datastore_search?         resource_id=b3eeb0ff-c8a8-4824-99d6-e0a3747c8b0d'
   url='http://www.odaa.dk/api/action/datastore_search?offset=400&resource_id=b3eeb0ff-c8a8-4824-99d6-e0a3747c8b0d'
'''
#from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
#myMQTTClient = AWSIoTMQTTClient("DAAS-HP")
#host = "a2mxpvymzj1qjd.iot.eu-west-2.amazonaws.com"
#host = "a2mxpvymzj1qjd.iot.us-west-2.amazonaws.com"
#myMQTTClient.configureEndpoint(host, 8883)

#myMQTTClient.configureCredentials("static/root-CA.crt", 
#                                  "static/HP-PC.private.key", 
#                                  "static/HP-PC.cert.pem")
#myMQTTClient.configureCredentials("static/root-CA.crt", 
#                                  "static/EC2-IOT-LND.private.key", 
#                                  "static/EC2-IOT-LND.cert.pem")
#myMQTTClient.connect()
@app.route('/daas/SDA_alert', methods=['POST'])
#@auth.login_required
def task_SDA_alert():
    jcon = request.json
    #jcon = sda_task
    if( not jcon):
        abort(400)

    version = 'V1'
    service = SDA_alert()
    result = service.Execute(version, jcon)
    qttMsg = json.dumps(result)
    publish.single('daas/SDA_alert', qttMsg, hostname='iot.eclipse.org')
    #myMQTTClient.publish('daas/SDA_alert', qttMsg, 1)
    return jsonify({'response': result}), 201

SDA_admin_service =None
@app.route('/daas/SDA_admin', methods=['POST'])
@auth.login_required
def task_SDA_admin():
    global SDA_admin_service
    req = request.json
    if (not req):
        abort(400)

    version = 'V1'
    if SDA_admin_service==None:
        SDA_admin_service = SDA_admin()

    try:
        result = SDA_admin_service.Execute(version, req)
        if (result == DAAS_DEF.BAD_REQUEST) :
            abort(400)
    except:
        traceback.print_exc()

    return jsonify({'response': str(result)}), 201


@app.route('/daas/TS', methods=['POST'])
def task_TS():
    pass

GPAL_service=None
@app.route('/daas/GPAL', methods=['POST'])
def task_GPAL():
    global GPAL_service
    req = request.json    
    if req == None:
        abort(400)

    logging.info('In GPAL Admin')
    logging.info(strftime("%H:%M:%S", gmtime()))
    version = 'V1'
    if(GPAL_service is None):
        GPAL_service = GPAL()

    try:
        result = GPAL_service.Execute(version,req)
        if (result == DAAS_DEF.BAD_REQUEST) :
            abort(400)
    except:
        traceback.print_exc()
 
    return jsonify({'response': json.dumps(result)}), 201

ARIMA_service=None
@app.route('/daas/SDA_ARIMA', methods=['POST'])
def task_ARIMA():
    global ARIMA_service
    req = request.json    
    if req == None:
        abort(400)
    logging.info('In GPAL Admin')
    version = 'V1'
    result = 'Test'
    if(ARIMA_service == None):
        ARIMA_service = DAAS_ARIMA()
        logging.info('ARIMA_SERVICE:'+ str(type(ARIMA_service)))
    try:
        logging.info('ARIMA_SERVICE:'+ str(type(ARIMA_service)))
        result = ARIMA_service.Execute(version, req)
        if (result == DAAS_DEF.BAD_REQUEST) :
            abort(400)
    except:
        traceback.print_exc()
    #result = req['para']
    if result == 'Test':
        traceback.print_exc()
    return jsonify({'response': result}), 201


SERVER_PORT = 9999
if __name__ == '__main__':
    ARIMA_service=None
    app.run(debug=True, host='0.0.0.0', port=int(SERVER_PORT))
    #app.run(debug=True, port=int(9999))

def UpdateDB(result):
    pass
