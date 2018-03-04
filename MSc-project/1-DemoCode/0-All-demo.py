from flask import Flask, render_template
from flask_httpauth import HTTPBasicAuth
from flask_bootstrap import Bootstrap 
from werkzeug.utils import secure_filename
from Daas_Demo_Forms import ITRT_Form, SDA_Form
from Daas_Demo_Forms import ImportRawDataForm, StatNoiseTestForm, \
                            DifferentionForm, GetPDQForm, \
                            SetModelForm, ResidualTestForm, \
                            ArimaPredictForm
from Daas_Demo_Forms import ImportTrainingForm, ImportTestForm, \
                            GpalPredictForm, FilePrepareForm
from Daas_Demo_Functions import CreateJs
import pandas as pd
import os
import time
import requests
import json
import base64
import urllib
import DAAS_DEF
import logging
logging.basicConfig(level=logging.INFO)

app=Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
Bootstrap(app)

mapfile = 'test'  # for SDA
# for ARIMA
raw_file_info = None
stat_noise_test_info = None
stat_noise_image = None
get_pdq_info = None
test_predict_image = None
residual_test_image = None

# for GPAL
train_info = None
test_info = None
train_para = None
train_response = None
test_response = None

@app.route('/sda_demo', methods=['GET','POST'])
def data_collect():
    global mapfile
    form = SDA_Form()
    res_info='DAAS response: '
    if form.startSubmit.data:
        req_body = {'type':DAAS_DEF.start}
        url = 'http://34.235.128.89:9999/daas/SDA_admin'
        header = {'Content-Type': 'application/json'}
        #auth=HTTPBasicAuth('Bradley-ZN00046', 'Bradley-ZN00046')
        res = requests.post(url, 
            headers=header, 
            json=req_body, 
            auth=('Bradley-ZN00046', 'Bradley-ZN00046'))

        res_info += 'status_code: '+str(res.status_code)+'\n'
        if res.status_code == 201:
            res = res.json()
            res_info += 'response content: '+ str(res['response']) +'\n\n'

        form.resText.data = res_info
        return render_template('get_data_SDA_alert_demo.html', form=form)

    if form.stopSubmit.data:
        req_body = {'type':DAAS_DEF.stop}
        url = 'http://34.235.128.89:9999/daas/SDA_admin'
        header = {'Content-Type': 'application/json'}
        auth=HTTPBasicAuth('Bradley-ZN00046', 'Bradley-ZN00046')
        res = requests.post(url, 
            headers=header, 
            json=req_body, 
            auth=('Bradley-ZN00046', 'Bradley-ZN00046'))

        res_info += 'status_code: '+str(res.status_code)+'\n'
        if res.status_code == 201:
            res = res.json()
            res_info += 'response content: '+ str(res['response']) +'\n\n'

        form.resText.data = res_info
        return render_template('get_data_SDA_alert_demo.html', form=form)

    if form.getSubmit.data:
        rptID = form.rptID.data
        numRecords = form.numRecords.data
        para = {'report_id':rptID,
                'latest_n':numRecords}
        req_body = {'type':DAAS_DEF.get_data,
                    'para':para}
        url = 'http://34.235.128.89:9999/daas/SDA_admin'
        header = {'Content-Type': 'application/json'}
        auth=HTTPBasicAuth('Bradley-ZN00046', 'Bradley-ZN00046')
        res = requests.post(url, 
            headers=header, 
            json=req_body, 
            auth=('Bradley-ZN00046', 'Bradley-ZN00046'))

        res_info += 'status_code: '+str(res.status_code)+'\n'
        temp=''
        if res.status_code == 201:
            res = res.json()
            res_info += 'response content: '+ str(res['response']) +'\n\n'
            #records=json.loads(res['response'])
            #temp = records['records'][1]['TIMESTAMP']
            #logging.info(temp)

        form.resText.data = res_info+temp
        return render_template('get_data_SDA_alert_demo.html', form=form)  

    if form.getAlertSubmit.data: 
        url = '' #tbu
        speed_max = 0 #tbu
        count_max = 0 #tbu
        rpt_id = 0 #tbu
        body={'version':'v1','para':{'url':url,
        'speed_max':speed_max,'count_max':count_max,'rpt_id':rpt_id}}

        url = 'http://34.235.128.89:9999/daas/SDA_alert'
        header = {'Content-Type': 'application/json'}
        res = requests.post(url, headers=header, json=body)        
        if(res.status_code !=201):
            result = 'DAAS response status_code:'+str(res.status_code)
        else:
            res = res.json()
            result = res['response']
            mapfile = CreateJs(result)  
            result = str(result)
        form.alertPointsText.data = result
        return render_template('get_data_SDA_alert_demo.html', form=form) 

    if form.showOnMapSubmit.data:     
        return render_template('showOnMap.html', form=form, mapfile=mapfile)

    if form.showSensorsSubmit.data:
        return render_template('showSensorsOnMap.html')
    return render_template('get_data_SDA_alert_demo.html', form=form)     

@app.route('/itrt_demo', methods=['GET', 'POST'])
def itrt_demo():
    form = ITRT_Form()
    #form.myreq.data = 'Demo'
    result = ''
    if form.validate_on_submit():
        imageFile = form.imgFile.data
        Imgcontent = imageFile.read()
        base64_image = base64.b64encode(Imgcontent).decode()

        url = 'http://34.235.128.89:9999/daas/ITRT'
        header = {'Content-Type': 'application/json'}
        body = {'version':'v1','content':base64_image}
        res = requests.post(url, headers=header, json=body)
        #url = 'http://18.220.191.196:9000/daas'
        #res = requests.get(url)
        
        if(not res):
            text = "Not found!"
            text = text + ', status_code:'+str(res.status_code)
            result = text
        else:
            res = res.json()
            res = res['response']
            #print text
            ImageTxt = res['ImageTxt']
            TransTxt = res['TranslatedTxt']
            return render_template('ITRT_Demo.html', form=form, ImageTxt=ImageTxt, TransTxt=TransTxt)
    
    return render_template('ITRT_Demo.html', form=form, result=result)

@app.route('/arima_demo', methods=['GET','POST'])
def arima_demo():
    global raw_file_info, stat_noise_image, stat_noise_test_info
    global get_pdq_info, test_predict_image, residual_test_image
    importRawDataForm = ImportRawDataForm()
    statNoiseTestForm = StatNoiseTestForm()
    differentionForm = DifferentionForm()
    getPDQForm = GetPDQForm()
    residualTestForm = ResidualTestForm()
    setModelForm = SetModelForm()
    predictForm = ArimaPredictForm()
 
    if importRawDataForm.rawDataSubmit.data:
        rawFile = importRawDataForm.rawData.data    
        if(rawFile == None):
            return
        file_name = secure_filename(rawFile.filename)
        path_file_name = './upload/'+ file_name
        rawFile.save(path_file_name)
        rawFile.close()
        
        headOption = importRawDataForm.fileHeadOption.data
        if headOption == DAAS_DEF.no_hearder:
            df_raw = pd.read_csv(path_file_name, header=None)                   
        else:
            df_raw = pd.read_csv(path_file_name)

        myfile = open(path_file_name, 'r')
        file_content = myfile.read()
        file = {'file_name':file_name, 'file_content':file_content}
        myfile.close()

        indexCol = importRawDataForm.indexCol.data
        para = {'headOption': headOption,
                'indexCol': indexCol}

        req_body = {"version": "v1",
                    "command": DAAS_DEF.upload_raw_file,
                    "para": para,
                    "file": file}

        url = 'http://34.235.128.89:9999/daas/SDA_ARIMA'
        header = {'Content-Type': 'application/json'}
        res = requests.post(url, headers=header, json=req_body)

        raw_file_info = file_name+'\n'
        raw_file_info += 'DAAS response status_code: '+str(res.status_code)+'\n'
        if res.status_code == 201:
            res = res.json()
            raw_file_info += 'response content: '+ str(res['response']) +'\n\n'
        else:
            raw_file_info += '\n\n'
        raw_file_info += df_raw.to_string(index=False)
        importRawDataForm.trainText.data = raw_file_info

        return render_template("ARIMA_Demo.html",
                                importRawDataForm=importRawDataForm, 
                                statNoiseTestForm=statNoiseTestForm,
                                differentionForm=differentionForm,
                                getPDQForm = getPDQForm,
                                residualTestForm = residualTestForm,
                                setModelForm = setModelForm,
                                predictForm = predictForm)

    if statNoiseTestForm.statNoiseSubmit.data:
        testColumn = statNoiseTestForm.testColumn.data
        resampleInterval = statNoiseTestForm.resampleInterval.data
        para = {'testColumn': testColumn,
                'resampleInterval': resampleInterval}
        req_body = {"version": "v1",
                    "para": para,
                    "command": DAAS_DEF.stat_white_test
                    }

        url = 'http://34.235.128.89:9999/daas/SDA_ARIMA'
        header = {'Content-Type': 'application/json'}
        res = requests.post(url, headers=header, json=req_body)
        stat_noise_test_info = 'DAAS response status_code: '+str(res.status_code)+'\n'
        stat_noise_image = ''
        if res.status_code == 201:
            res = res.json()
            #res = json.loads(res['response'])
            res = res['response']
            if res == 'Test':
                stat_noise_test_info +='Get Unknown Error' +'\n'
            else:
                adf_test = res['adf_test']
                white_noise_test = res['white_noise_test']
                shape = res['shape']
                diffOrder = res['diffOrder']
                stat_noise_test_info += 'ADF Test: '+ str(adf_test)+ \
                    '\n'+'White Noise Test: '+str(white_noise_test)+ \
                    '\n'+'Shape of resample: '+str(shape) + ', '+ \
                    'Differention order: ' + str(diffOrder) + '\n'
                file_name = res['file']['file_name']
                stime = time.strftime('%H-%M-%S',time.localtime(time.time()))
                path_file_name = './static/images/'+stime+file_name
                file_content = res['file']['file_content']
                file_content = base64.b64decode(file_content)
                fp = open(path_file_name, 'wb')
                fp.write(file_content)
                fp.close()
                logging.info(file_name)
                stat_noise_image = 'images/'+stime+file_name
        else:
            stat_noise_test_info += '\n'
        
        importRawDataForm.trainText.data = raw_file_info
        statNoiseTestForm.statNoiseText.data = stat_noise_test_info
        logging.info(stat_noise_image)
        return render_template("ARIMA_Demo.html",
                                importRawDataForm=importRawDataForm, 
                                statNoiseTestForm=statNoiseTestForm,
                                differentionForm=differentionForm,
                                getPDQForm = getPDQForm,
                                residualTestForm = residualTestForm,
                                setModelForm = setModelForm,
                                predictForm = predictForm,
                                stat_noise_image = stat_noise_image)

    if differentionForm.diffSubmit.data:
        diffOrder = differentionForm.diffOrder.data
        para = {'diffOrder': diffOrder}
        req_body = {"version": "v1",
                "para": para,
                "command": DAAS_DEF.differentiation
                }
        url = 'http://34.235.128.89:9999/daas/SDA_ARIMA'
        header = {'Content-Type': 'application/json'}
        res = requests.post(url, headers=header, json=req_body)
        diff_info = 'DAAS response status_code: '+str(res.status_code)+'\n'
        if res.status_code == 201:
            res = res.json()
            res = res['response']
            if res == 'Test':
                stat_noise_test_info +='Get Unknown Error' +'\n'
            else:
                diff_order = res['diff_order']
                diff_shape = res['diff_shape']
                diff_info += 'diff_order: '+str(diff_order)+ ', ' + \
                            'diff_shape: ' +str(diff_shape)+ '\n'
                diff_info += 'Differention Finished, \
                Please Do Stationarity and White Noise Test Again'+'\n'
                
        differentionForm.diffText.data = diff_info
        importRawDataForm.trainText.data = raw_file_info
        statNoiseTestForm.statNoiseText.data = stat_noise_test_info
        return render_template("ARIMA_Demo.html",
                                importRawDataForm=importRawDataForm, 
                                statNoiseTestForm=statNoiseTestForm,
                                differentionForm=differentionForm,
                                getPDQForm = getPDQForm,
                                residualTestForm = residualTestForm,
                                setModelForm = setModelForm,
                                predictForm = predictForm,
                                stat_noise_image = stat_noise_image)

    if getPDQForm.pdqSubmit.data:
        p = getPDQForm.pValue.data
        d = getPDQForm.dValue.data
        q = getPDQForm.qValue.data
        para = {'p': p, 'd': d, 'q': q}
        req_body = {"version": "v1",
                "para": para,
                "command": DAAS_DEF.search_pdq
                }
        url = 'http://34.235.128.89:9999/daas/SDA_ARIMA'
        header = {'Content-Type': 'application/json'}
        res = requests.post(url, headers=header, json=req_body)
        get_pdq_info = 'DAAS response status_code: '+str(res.status_code)+'\n'
        if res.status_code == 201:
            res = res.json()
            res = res['response']
            if res == 'Test':
                get_pdq_info +='Get Unknown Error' +'\n'
            else:
                file_content = res['file']['file_content']
                get_pdq_info +=file_content+'\n'

        getPDQForm.pdqText.data = get_pdq_info
        importRawDataForm.trainText.data = raw_file_info
        statNoiseTestForm.statNoiseText.data = stat_noise_test_info
        return render_template("ARIMA_Demo.html",
                                importRawDataForm=importRawDataForm, 
                                statNoiseTestForm=statNoiseTestForm,
                                differentionForm=differentionForm,
                                getPDQForm = getPDQForm,
                                residualTestForm = residualTestForm,
                                setModelForm = setModelForm,
                                predictForm = predictForm,
                                stat_noise_image = stat_noise_image)

    if setModelForm.setModelSubmit.data:
        p = setModelForm.pValue.data
        d = setModelForm.dValue.data
        q = setModelForm.qValue.data
        sDateOfTest = setModelForm.startOfTest.data
        eDateOfTest = setModelForm.endOfTest.data
        para = {'p': p, 'd': d, 'q': q,
                'sDateOfTest':str(sDateOfTest),'eDateOfTest':str(eDateOfTest)
                }
        req_body = {"version": "v1",
                "para": para,
                "command": DAAS_DEF.create_model
                }
        logging.info('date:'+str(type(eDateOfTest))+str(eDateOfTest))
        url = 'http://34.235.128.89:9999/daas/SDA_ARIMA'
        header = {'Content-Type': 'application/json'}
        res = requests.post(url, headers=header, json=req_body)
        set_model_info = 'DAAS response status_code: '+str(res.status_code)+'\n'
        if res.status_code == 201:
            res = res.json()
            res = res['response']
            if res == 'Test':
                set_model_info +='Get Unknown Error' +'\n'
            else:
                model_report = res['model_report']
                set_model_info +=model_report+'\n'
                set_model_info += 'RMSE: '+str(res['RMSE'])+'\n'

                file_name = res['file']['file_name']
                stime = time.strftime('%H-%M-%S',time.localtime(time.time()))
                path_file_name = './static/images/'+stime+file_name
                file_content = res['file']['file_content']
                file_content = base64.b64decode(file_content)
                fp = open(path_file_name, 'wb')
                fp.write(file_content)
                fp.close()
                test_predict_image = 'images/'+stime+file_name

        setModelForm.setModelText.data = set_model_info
        importRawDataForm.trainText.data = raw_file_info
        statNoiseTestForm.statNoiseText.data = stat_noise_test_info
        getPDQForm.pdqText.data = get_pdq_info
        return render_template("ARIMA_Demo.html",
                                importRawDataForm=importRawDataForm, 
                                statNoiseTestForm=statNoiseTestForm,
                                differentionForm=differentionForm,
                                getPDQForm = getPDQForm,
                                residualTestForm = residualTestForm,
                                setModelForm = setModelForm,
                                predictForm = predictForm,
                                stat_noise_image = stat_noise_image,
                                test_predict_image = test_predict_image)
    
    if residualTestForm.residualTestSubmit.data:
        req_body = {"version": "v1",
                    "command": DAAS_DEF.residual_test
                    }
        url = 'http://34.235.128.89:9999/daas/SDA_ARIMA'
        header = {'Content-Type': 'application/json'}
        res = requests.post(url, headers=header, json=req_body)
        residual_test_info = 'DAAS response status_code: '+str(res.status_code)+'\n'
        if res.status_code == 201:
            res = res.json()
            res = res['response']
            if res == 'Test':
                residual_test_info +='Get Unknown Error' +'\n'
            else:
                white_noise_test = res['white_noise_test']
                shape = res['shape']
                residual_test_info += 'White Noise Test: '+str(white_noise_test)+ \
                    '\n'+'Shape of residual: '+str(shape) +'\n'

                file_name1 = res['file1']['file_name']
                file_content = res['file1']['file_content']
                file_content = base64.b64decode(file_content)
                stime = time.strftime('%H-%M-%S',time.localtime(time.time()))
                path_file_name1 = './static/images/'+stime+file_name1                
                fp = open(path_file_name1, 'wb')
                fp.write(file_content)
                fp.close()
                residual_test_image1 = 'images/'+stime+file_name1

                file_name2 = res['file2']['file_name']
                file_content = res['file2']['file_content']
                file_content = base64.b64decode(file_content)
                stime = time.strftime('%H-%M-%S',time.localtime(time.time()))
                path_file_name2 = './static/images/'+stime+file_name2               
                fp = open(path_file_name2, 'wb')
                fp.write(file_content)
                fp.close()
                residual_test_image2 = 'images/'+stime+file_name2
        else:
            residual_test_info += '\n'

        residualTestForm.residualTestText.data=residual_test_info
        getPDQForm.pdqText.data = get_pdq_info
        importRawDataForm.trainText.data = raw_file_info
        statNoiseTestForm.statNoiseText.data = stat_noise_test_info

        return render_template("ARIMA_Demo.html",
                                importRawDataForm=importRawDataForm, 
                                statNoiseTestForm=statNoiseTestForm,
                                differentionForm=differentionForm,
                                getPDQForm = getPDQForm,
                                residualTestForm = residualTestForm,
                                setModelForm = setModelForm,
                                predictForm = predictForm,
                                stat_noise_image = stat_noise_image,
                                test_predict_image = test_predict_image,
                                residual_test_image1 = residual_test_image1,
                                residual_test_image2 = residual_test_image2)

    return render_template("ARIMA_Demo.html",
                            importRawDataForm=importRawDataForm, 
                            statNoiseTestForm=statNoiseTestForm,
                            differentionForm=differentionForm,
                            getPDQForm = getPDQForm,
                            residualTestForm = residualTestForm,
                            setModelForm = setModelForm,
                            predictForm = predictForm)

@app.route('/gpal_demo', methods=['GET','POST'])
def DemoIndex():
    global train_info
    global train_para
    global train_response
    global test_info
    global test_response
    trainingForm = ImportTrainingForm()
    testForm = ImportTestForm()
    predictForm = GpalPredictForm()
    filePrepareForm = FilePrepareForm()
    #form.myreq.data = 'Demo'
    if trainingForm.trainSubmit.data:
        trainingFile = trainingForm.trainingFile.data   

        file_name = secure_filename(trainingFile.filename)
        path_file_name = './upload/'+ file_name
        if(trainingFile == None):
            return
        trainingFile.save(path_file_name)
        
        if trainingForm.headOption.data == DAAS_DEF.no_hearder:
            df_training = pd.read_csv(path_file_name, header=None)                  
        else:
            df_training = pd.read_csv(path_file_name)

        train_info = file_name+', shape: '+str(df_training.shape)

        trainLabelCol = trainingForm.trainLabelCol.data
        algorithm = trainingForm.trainAlgoSelect.data
        headOption = trainingForm.headOption.data
        preProcessOption = trainingForm.preProcessOption.data
        runOption = trainingForm.runOption.data
        scalerOption = trainingForm.scalerOption.data
        train_para = {'trainLabelCol': trainLabelCol,
                      'algorithm': algorithm,
                      'headOption': headOption,
                      'preProcessOption': preProcessOption,
                      'scalerOption': scalerOption,             
                      'runOption': runOption}

        myfile = open(path_file_name)
        file_content = myfile.read()
        file = {'file_name':file_name, 'file_content':file_content}
        myfile.close()
        req_body = {"version": "v1",
                "type": DAAS_DEF.train_file,
                "train_para": train_para,
                "file": file}

        #train_info += '\n'+'train_para: '+json.dumps(req_body['train_para'])#myfile.read()
        train_info += '\n\n'+df_training.to_string(index=False)#myfile.read()
        
        trainingForm.trainText.data = train_info
        trainingFile.close()

        url = 'http://34.235.128.89:9999/daas/GPAL'
        header = {'Content-Type': 'application/json'}
        res = requests.post(url, headers=header, json=req_body)
        if (not res):
            train_response = 'No response from server, status_code='+str(res.status_code)
        
        else:   
            res = res.json()
            train_response = str(res['response'])   
        trainingForm.resTrainText.data = train_response
        #print urllib.unquote(str(s)).decode('utf8')
        return render_template('GPAL_Demo.html',
                            trainingForm=trainingForm, 
                            testForm=testForm,
                            predictForm=predictForm,
                            filePrepareForm=filePrepareForm)

    if testForm.testSubmit.data:
        testFile = testForm.testFile.data   
        testLabelCol = testForm.testLabelCol.data
        file_name = secure_filename(testFile.filename)
        path_file_name = './upload/'+ file_name
        #path_file_name = os.path.join(path,file_name)
        testFile.save(path_file_name)
        testFile.close()

        if train_para['headOption'] == DAAS_DEF.no_hearder:
            df_test = pd.read_csv(path_file_name, header=None)                  
        else:
            df_test = pd.read_csv(path_file_name)
        
        test_info = file_name+', shape: '+str(df_test.shape)+'\n'
        #test_info += 'train_para: '+json.dumps(train_para)
        test_info = test_info+'\n'+df_test.to_string(index=False)

        trainingForm.trainText.data = train_info
        testForm.testText.data = test_info

        myfile = open(path_file_name)
        file_content = myfile.read()
        file = {'file_name':file_name, 'file_content':file_content}
        req_body = {"version": "v1",
                "type": DAAS_DEF.test_file,
                "train_para": train_para,
                "testLabelCol": testLabelCol,
                "file": file}
        url = 'http://34.235.128.89:9999/daas/GPAL'
        header = {'Content-Type': 'application/json'}
        res = requests.post(url, headers=header, json=req_body)
        if (not res):
            test_response = 'No response from server, status_code='+str(res.status_code)
        
        else:   
            res = res.json()
            test_response = str(res['response'])    
        testForm.resTestText.data = test_response
        trainingForm.trainText.data = train_info
        trainingForm.resTrainText.data = train_response
        return render_template('GPAL_Demo.html',
                            trainingForm=trainingForm, 
                            testForm=testForm,
                            predictForm=predictForm,
                            filePrepareForm=filePrepareForm)

    if predictForm.predictSubmit.data:
        algorithm = predictForm.predAlgoSelect.data
        req_body = {"version": "v1",
                    "type": DAAS_DEF.predict,
                    "algorithm": algorithm}
        url = 'http://34.235.128.89:9999/daas/GPAL'
        header = {'Content-Type': 'application/json'}
        res = requests.post(url, headers=header, json=req_body)
        if (not res):
            predict_response = 'No response from server, status_code='+str(res.status_code)
            predictForm.predictText.data = predict_response
        else:   
            res = res.json()
            prediction = str(res['response'])   
            prediction = json.loads(prediction)
            score = prediction['score']
            fn = './predictions/prediction.csv'
            fp = open(fn, 'w')
            fp.write(prediction['prediction'])
            fp.close()
            df_prediction = pd.read_csv(fn)
            strPre = df_prediction.to_string(index=False)
            strPre = 'Score: '+str(score)+'\n\n'+strPre
            predictForm.predictText.data = strPre

        testForm.testText.data = test_info
        testForm.resTestText.data = test_response
        trainingForm.trainText.data = train_info
        trainingForm.resTrainText.data = train_response
        return render_template('GPAL_Demo.html',
                            trainingForm=trainingForm, 
                            testForm=testForm,
                            predictForm=predictForm,
                            filePrepareForm=filePrepareForm)
        
    return render_template('GPAL_Demo.html',
                            trainingForm=trainingForm, 
                            testForm=testForm,
                            predictForm=predictForm,
                            filePrepareForm=filePrepareForm)

import traceback
SVR_PORT=8899
if __name__ == '__main__':  
    try:
        #app.run(debug=True, port=int(SVR_PORT))
        app.run(debug=True, host='0.0.0.0', port=int(SVR_PORT))
    except:
        traceback.print_exc()