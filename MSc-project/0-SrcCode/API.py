import numpy as np
import pandas as pd
import base64
import requests
import random
import md5
import urllib
import json
import httplib
import sqlite3
import SDA_Functions as SDA_F
import GPAL_Functions as GPAL_F
import ARIMA_Functions as ARIMA_F
import os
import time
from time import gmtime, strftime
import logging
import DAAS_DEF
from threading import Thread

from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import roc_auc_score
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import VotingClassifier
import pdb

from statsmodels.tsa.stattools import adfuller as ADF
from statsmodels.stats.diagnostic import acorr_ljungbox
from datetime import datetime, timedelta
import statsmodels.tsa.api as smt
import seaborn as sns
import matplotlib.pylab as plt
from statsmodels.tsa.arima_model import ARIMA
from sklearn.metrics import mean_squared_error
from math import sqrt
import warnings

error_count = 0


class ITRT(object):
    def __init__(self):
        self.vison_url = '''https://vision.googleapis.com/v1/images:annotate?key=AIzaSyDADkXhyTtCsXZ_Ce3kXWpkyhXiu8FWxxA'''
        self.trans_url = "/api/trans/vip/translate"
        self.trans_pwd = "uU3uMTSnkDDGhDtd3Nvf"
        self.trans_appid = "20170725000067675"

    def GetTxt(self, imageFile):
        #Imgcontent = imageFile.read()
        #base64_image = base64.b64encode(Imgcontent).decode()
        base64_image = imageFile
        body = {
            'requests': [{
                'image': {
                    'content': base64_image,
                },
                'features': [{
                    'type': 'TEXT_DETECTION',
                    'maxResults': 1,
                }]
            }]
        }
        header = {'Content-Type': 'application/json'}
        response = requests.post(self.vison_url, headers=header, json=body)
        if response.status_code != 200:
            text = "Not found"
            #text = self.vison_url
        else:
            response = response.json()
            text = response['responses'][0]['textAnnotations'][0]['description']
            text = text.encode('utf-8')
        return text

    def GetTransTxt(self, txt):
        text = str(txt)
        src = text.replace('\n', ' ')
        #print type(text), text
        salt = random.randint(32768, 65536)
        #salt = 45575

        httpClient = None
        sign = self.trans_appid+src+str(salt)+self.trans_pwd
        m1 = md5.new()
        m1.update(sign)
        sign = m1.hexdigest()

        trans_url = self.trans_url+ '?appid='+self.trans_appid + \
                    '&q='+urllib.quote(src)+ '&from=en&to=zh' +  \
                    '&salt='+str(salt) +'&sign='+sign
        
        try:
            httpClient = httplib.HTTPConnection('api.fanyi.baidu.com')
            #print myurl
            httpClient.request('GET', trans_url)
            response = httpClient.getresponse()

            res = response.read()

            #print res
            jres = json.loads(res)      
            mdst = jres['trans_result'][0]['dst']
            dst = mdst.encode('utf-8')
            #print type(dst), dst
            return dst

        except Exception, e:
            print e
        finally:
            if httpClient:
                httpClient.close() 
        
    def Execute(self, version, imageFile):
        Txt = self.GetTxt(imageFile)
        if not Txt: 
            return 'Not found text in Image'

        TransTxt = self.GetTransTxt(Txt)
        if not TransTxt:
            TransTxt = 'Not get translated text'
            
        TransTxt = TransTxt.replace('\n', ' ')
        Txt = Txt.replace('\n', ' ')
        Result = {
            "ImageTxt": Txt,
            "TranslatedTxt": TransTxt,
        }
        #print Txt, TransTxt
        return Result
#end of class ITRT

class SDA_admin(object):
    def __init__(self):
        self.bCollecting = False
        self.data_url = '''http://www.odaa.dk/api/action/datastore_search'''
        self.data_resource_id = 'resource_id=b3eeb0ff-c8a8-4824-99d6-e0a3747c8b0d'
        self.db_folder = './static'
        self.db_name = os.path.join(self.db_folder, "traffic_data_from201709.sqlite3")

    def Get_Data_From_Url(self):
        offsets = [100,200,300,400]
        url = self.data_url+'?'+self.data_resource_id
        res=requests.get(url)
        info = json.loads(str(res.text))
        stream_data = info['result']['records']
        for ofs in offsets:
            url = self.data_url+'?offset='+str(ofs)+'&'+self.data_resource_id
            res=requests.get(url)
            info = json.loads(str(res.text))
            stream_data = stream_data+info['result']['records']
        return stream_data

    def UpdateDb(self, db_conn_th, sd):
        if len(sd) == 0:
            return
        for idx in range(0, len(sd)):
            rpt_id = sd[idx]['REPORT_ID']
            tableName = 'trafficData'+str(rpt_id)
            sqlTxt ='INSERT INTO '+tableName+'''(status, 
                            avgMeasuredTime, 
                            avgSpeed, 
                            medianMeasuredTime, 
                            TIMESTAMP, 
                            vehicleCount, 
                            _id, 
                            REPORT_ID) VALUES (?,?,?,?,?,?,?,?)'''
            db_conn_th.execute(sqlTxt,(sd[idx]['status'], 
                            sd[idx]['avgMeasuredTime'], 
                            sd[idx]['avgSpeed'],
                            #sd[idx]['extID'],
                            sd[idx]['medianMeasuredTime'],
                            sd[idx]['TIMESTAMP'], 
                            sd[idx]['vehicleCount'], 
                            sd[idx]['_id'], 
                            sd[idx]['REPORT_ID']))

        db_conn_th.commit()

    def Get_Data_Thread(self):
        #global end_time
        logging.info('In thread')
        db_conn_th = sqlite3.connect(self.db_name)
        while self.bCollecting:
            sd = self.Get_Data_From_Url()
            self.UpdateDb(db_conn_th, sd)
            time.sleep(5.0*60) #5 minutes
        db_conn_th.close()

    def Data_Feed(self, rpt_id, latest_n):
        if latest_n<1 or rpt_id<1:
            return DAAS_DEF.BAD_REQUEST

        db_conn_read = sqlite3.connect(self.db_name)
        tableName = 'trafficData'+str(rpt_id)
        sqlTxt = 'SELECT * FROM ' + tableName
        df = pd.read_sql(sqlTxt, db_conn_read)
        records = list()
        if latest_n > len(df):
            records_len = len(df)
        else :
            records_len = latest_n

        for i in range(1,records_len+1):
            item = {'status':str(df['status'].iloc[-i]),
                    'avgMeasuredTime':df['avgMeasuredTime'].iloc[-i],
                    'avgSpeed':df['avgSpeed'].iloc[-i],
                    'medianMeasuredTime':df['medianMeasuredTime'].iloc[-i],
                    'TIMESTAMP':str(df['TIMESTAMP'].iloc[-i]),
                    'vehicleCount':df['vehicleCount'].iloc[-i],
                    'REPORT_ID':df['REPORT_ID'].iloc[-i]
                    }
            records.append(item)
            result = {'records':records}
        return result

    def Execute(self, version, req):
        logging.info(str(req))
        if req['type'] == DAAS_DEF.start :
            if self.bCollecting == False:
                #end_time = req['para']['end_time']
                #end_time = datetime.strptime(end_time, '%Y-%m-%d-%H-%M-%S')
                self.get_data_thread = Thread(target=self.Get_Data_Thread)
                self.get_data_thread.start()
                self.bCollecting = True
                result = {'start':DAAS_DEF.done}
            else:
                result = {'start':DAAS_DEF.duplicate_start}
            logging.info('bCollecting: '+str(self.bCollecting))
            return result

        elif req['type']==DAAS_DEF.stop :
            logging.info('bCollecting: '+str(self.bCollecting))
            if self.bCollecting == True:
                self.bCollecting = False
                result = {'stop':DAAS_DEF.done}
            else:
                result = {'stop':DAAS_DEF.duplicate_stop}
            logging.info('bCollecting: '+str(self.bCollecting))
            return result

        elif req['type']==DAAS_DEF.get_data:
            report_id=req['para']['report_id']
            latest_n = req['para']['latest_n']  
            result = self.Data_Feed(report_id,latest_n)
            #logging.info(str(result))
            return result  

        else:
            abort(400)        

class SDA_alert(object):
    def __init__(self):
        self.url = '''http://www.odaa.dk/api/action/datastore_search'''
        self.resource_id = 'resource_id=b3eeb0ff-c8a8-4824-99d6-e0a3747c8b0d'
        self.db_folder = './static'
        self.db_name = os.path.join(self.db_folder, "WholeDB0803.sqlite3")

    def UpdateRawDB(self, sd):
        if len(sd) == 0:
            return
        con = sqlite3.connect(self.db_name)
        for idx in range(0, len(sd)):
            rpt_id = sd[idx]['REPORT_ID']
            tableName = 'trafficData'+str(rpt_id)
            #con.execute('DROP TABLE IF EXISTS '+ tableName)
            #sqlTxt = 'CREATE TABLE IF NOT EXISTS ' + tableName +  ''' (status TEXT, 
            #avgMeasuredTime INTEGER, avgSpeed INTEGER, medianMeasuredTime INTEGER, 
            #TIMESTAMP TEXT, vehicleCount INTEGER, _id INTEGER, REPORT_ID INTEGER)'''
            #con.execute(sqlTxt)
            #con.commit()
            sqlTxt ='INSERT INTO '+tableName+'''(status, avgMeasuredTime, 
                    avgSpeed, medianMeasuredTime, TIMESTAMP, vehicleCount, _id, 
                    REPORT_ID) VALUES (?,?,?,?,?,?,?,?)'''
            con.execute(sqlTxt,(sd[idx]['status'], sd[idx]['avgMeasuredTime'], 
                sd[idx]['avgSpeed'],sd[idx]['medianMeasuredTime'],sd[idx]['TIMESTAMP'], 
                sd[idx]['vehicleCount'], sd[idx]['_id'], sd[idx]['REPORT_ID']))
        con.commit()

    def UpdateModel(self, con, tableName, field, time_slot, value):
        if field == 'max':
            sqlTxt = 'UPDATE '+tableName+' SET max =? ' +' WHERE slot_type =?'
            con.execute(sqlTxt, (value, time_slot))
            con.commit()
        if field == 'mean':
            sqlTxt = 'SELECT mean, num from '+tableName +" where slot_type ='"+time_slot+"'"
            df = pd.read_sql(sqlTxt, con)
            mean = float(df['mean'])
            #print mean, type(mean)
            num = int(df['num'])
            #print num, type(num)
            mean = (mean*num+value)/(num+1.0)
            sqlTxt = 'UPDATE '+tableName+' SET mean =? ' +' WHERE slot_type =?'
            con.execute(sqlTxt, (mean, time_slot))
            sqlTxt = 'UPDATE '+tableName+' SET num =? ' +' WHERE slot_type =?'
            con.execute(sqlTxt, (num+1, time_slot))
            con.commit()
#end UpdateModel
    def AlertCheck_ModelUpdate(self, sd, jcon):
        if len(sd) == 0:
            return
        result = {'num':0, 'a_rpt_id':[], 'a_speed':[], 'a_count':[]}
        con = sqlite3.connect(self.db_name)
        num = 0
        a_rpt_id = []
        a_speed = []
        a_count = []
        for idx in range(0, len(sd)):
            rpt_id = sd[idx]['REPORT_ID']
            if rpt_id == 1164:
                continue
            # 1164 to be updated in the DB
            tableName = 'VehicleCount'+str(rpt_id)
            stime = sd[idx]['TIMESTAMP']
            time_slot = SDA_F.GetTimeSlot(stime)
            sqlTxt = 'SELECT max, slot_type FROM '+ tableName
            df = pd.read_sql(sqlTxt, con)
            max = df['max'][df['slot_type']==time_slot]
            max = int(max)
            # throw exception if not max
            if sd[idx]['vehicleCount'] > max:
                num = num+1
                a_rpt_id.append(rpt_id)
                a_speed.append(sd[idx]['avgSpeed'])
                a_count.append(sd[idx]['vehicleCount'])
                self.UpdateModel(con, tableName, 'max', time_slot, sd[idx]['vehicleCount'])
            self.UpdateModel(con, tableName, 'mean', time_slot, sd[idx]['vehicleCount'])

            tableName = 'VehicleSpeed'+str(rpt_id)
            sqlTxt = 'SELECT max, slot_type FROM '+ tableName
            df = pd.read_sql(sqlTxt, con)
            max = df['max'][df['slot_type']==time_slot]
            max = int(max)
            if sd[idx]['avgSpeed'] > max:
                num = num+1
                a_rpt_id.append(rpt_id)
                a_speed.append(sd[idx]['avgSpeed'])
                a_count.append(sd[idx]['vehicleCount'])
                self.UpdateModel(con, tableName, 'max', time_slot, sd[idx]['avgSpeed'])
            self.UpdateModel(con, tableName, 'mean', time_slot, sd[idx]['avgSpeed'])

        result['num'] = num
        result['a_rpt_id'] = a_rpt_id
        result['a_speed'] = a_speed
        result['a_count'] = a_count
        return result
#end of SDA.AlertCheck_ModelUpdate

    def Execute(self, version, jcon):
        offsets = [100,200,300,400]
        url = self.url+'?'+self.resource_id
        res=requests.get(url)
        info = json.loads(str(res.text))
        stream_data = info['result']['records']
        for ofs in offsets:
            url = self.url+'?offset='+str(ofs)+'&'+self.resource_id
            res=requests.get(url)
            info = json.loads(str(res.text))
            stream_data = stream_data+info['result']['records']

        #self.UpdateRawDB(stream_data)
        result = {'num':0, 'a_rpt_id':[], 'a_speed':[], 'a_count':[]}
        result = self.AlertCheck_ModelUpdate(stream_data,jcon)
        return result
#end of SDA.Execute()
#end of class SDA

#begin of GPAL
import logging
logging.basicConfig(level=logging.INFO)
class GPAL(object):
    def __init__(self):
        self.trainLabelCol = None
        self.testLabelCol = None
        self.algorithm = None
        self.headOption = None
        self.preProcessOption = None
        self.runOption = None
        self.scalerOption = None
        self.train_file_name = None
        self.test_file_name = None
        self.train_para = None
        self.df_train = None
        self.df_test = None
        self.df_test_raw = None        
        self.df_prediction = None
        self.X_train = None
        self.y_train = None
        self.X_test = None
        self.y_test = None
        self.b_y_testIncluded = False
        self.gs_lr = None
        self.gs_rfc = None
        self.gs_knn = None


    def ValidCheck_TrainingSave(self, req):
        file_name = None
        if not req['file'] is None:
            self.__init__()
            file_name = req['file']['file_name']
            self.train_file_name = file_name

            csv_file = req['file']['file_content']

            file_name = './upload/'+file_name
            fn = open(file_name,'w')
            fn.write(csv_file)
            fn.close()

        self.trainLabelCol = int(req['train_para']['trainLabelCol'])
        self.algorithm = req['train_para']['algorithm']
        self.headOption = req['train_para']['headOption']
        self.preProcessOption = req['train_para']['preProcessOption']
        self.scalerOption = req['train_para']['scalerOption']
        self.runOption = req['train_para']['runOption']

        self.train_para = {"trainLabelCol": self.trainLabelCol, 
                      "algorithm": self.algorithm, 
                      "headOption": self.headOption,
                      "preProcessOption": self.preProcessOption, 
                      "scalerOption": self.scalerOption, 
                      "runOption": self.runOption}

        logging.info('self.preProcessOption: '+self.preProcessOption)

        if not file_name is None:
            if(self.headOption == DAAS_DEF.no_hearder):
                self.df_train = pd.read_csv(file_name, header=None)

            elif(self.headOption == DAAS_DEF.with_header):
                self.df_train = pd.read_csv(file_name)

        if self.df_train is None:
            return 'Please upload train file'

        bClassifier = (self.algorithm == DAAS_DEF.alg_svc or 
                       self.algorithm == DAAS_DEF.alg_lr or
                       self.algorithm == DAAS_DEF.alg_knn or
                       self.algorithm == DAAS_DEF.alg_rfc or
                       self.algorithm == DAAS_DEF.alg_gnb)

        bLabelCol_outRange = (int(self.trainLabelCol)<0 or int(self.trainLabelCol)>=self.df_train.shape[1])
        if (bClassifier and bLabelCol_outRange):
            logging.info('bClassifier: '+str(bClassifier))
            logging.info('Classifier: '+str(self.algorithm))
            logging.info('bLabelCol_outRange: '+str(bLabelCol_outRange))
            logging.info('trainLabelCol: '+str(self.trainLabelCol))
            logging.info('shape: '+str(self.df_train.shape[1]))
            #assert(False)
            pdb.set_trace()
            return DAAS_DEF.BAD_REQUEST

        return DAAS_DEF.SUCCESS
 
    def TrainArima(self):
        return 'TBU...'
        
    def TrainKM(self):
        return 'TBU...'

    def Pre_wdbc(self):
        pass
    def Pre_drop(self, df):
        columns = df.columns
        for col in columns:            
            tt = df[col].dtype
            if str(tt) == "object":
                df = df.drop([col], axis=1)
        df = df.dropna(axis=0, how='any')
        return df

    def Pre_titanic(self, df):
        df = GPAL_F.clean_and_munge_data(df)
        return df

    def Pre_banking(self, df):
        df = GPAL_F.Pre_aws_banking(df)
        return df

    def Get_Scores(self, estimator):
        scores = cross_val_score(estimator = estimator,
                                 X = self.X_train,
                                 y = self.y_train,
                                 cv = DAAS_DEF.cv_num)
        logging.info('In score, X_train shape: '+str(self.X_train.shape))
        mean_score = np.mean(scores)

        result = {'train_file_name': self.train_file_name,
                  'X_train_shape': str(self.X_train.shape),
                  'mean_score': mean_score,
                  'scores': str(scores),
                  'train_para': self.train_para}
        return result

    def RunCrossValidation(self):
        if self.algorithm == DAAS_DEF.alg_svc:
            estimator = SVC(random_state=DAAS_DEF.random_state)
            result = self.Get_Scores(estimator)
            return result
        elif self.algorithm == DAAS_DEF.alg_lr:
            estimator = LogisticRegression(random_state=DAAS_DEF.random_state)
            result = self.Get_Scores(estimator)
            return result
        elif self.algorithm == DAAS_DEF.alg_knn:
            estimator = KNeighborsClassifier(n_neighbors=3)
            result = self.Get_Scores(estimator)
            return result
        elif self.algorithm == DAAS_DEF.alg_rfc:
            estimator = RandomForestClassifier(random_state=DAAS_DEF.random_state)
            result = self.Get_Scores(estimator)
            return result
        elif self.algorithm == DAAS_DEF.alg_gnb:
            estimator = GaussianNB()
            result = self.Get_Scores(estimator)
            return result
        else :
            assert(False)
            pdb.set_trace()
            return DAAS_DEF.BAD_REQUEST

    def GetResult(self, estimator, X, y_label, param_range=None):
        y_pred = estimator.predict(X)
        ###
        debug_score = accuracy_score(y_label,y_pred)
        logging.info('debug_score: '+str(debug_score))
        ###
        confmat = confusion_matrix(y_true=y_label, y_pred=y_pred)
        allnum = confmat.sum()
        #accuracy = (confmat[0][0]+confmat[1][1])/allnum
        precison = float(confmat[1][1])/(confmat[1][1]+confmat[0][1])
        recall = float(confmat[1][1])/(confmat[1][1]+confmat[1][0])
        FPR = float(confmat[0][1])/(confmat[0][1]+confmat[0][0])
        F1 = 2.0*precison*recall/(precison+recall)
        accuracy = float(confmat[1][1]+confmat[0][0])/allnum
        accuracy = '%.3f' % accuracy
        metrics = {'precison': '%.3f' % precison,
                   'recall': '%.3f' % recall,
                   'FPR': '%.3f' % FPR,
                   'F1': '%.3f' % F1}
        y_pred = estimator.predict_proba(X)[:, 1]
        roc_auc = roc_auc_score(y_label, y_pred)
        auc = '%.3f' % roc_auc
        if param_range is None:
            result = {'accuracy': accuracy,
                      'auc': auc,
                      'confusion_matrix': str(confmat),
                      'metrics': metrics}
        else:
            best_score = '%.3f' % estimator.best_score_
            result = {'parameters': param_range,
                      'best parameters': str(estimator.best_params_),
                      'cv accuracy': best_score,
                      'accuracy': accuracy,
                      'auc': auc,
                      'confusion_matrix': str(confmat),
                      'metrics': metrics}
        return result    

    def RunGridSearch(self):
        if self.algorithm == DAAS_DEF.alg_lr:
            start = time.time()
            logging.info('LogisticRegression grid searching...')
            lr = LogisticRegression(random_state=DAAS_DEF.random_state)
            param_range = [0.1, 1.0, 10.0]
            param_grid = dict(C=param_range)
            gs_lr = GridSearchCV(estimator=lr, 
                                 param_grid=param_grid, 
                                 cv=DAAS_DEF.cv_num)
            gs_lr.fit(self.X_train, self.y_train)
            result_lr = self.GetResult(gs_lr, self.X_train, self.y_train, param_range)
            end = time.time()
            duration = str('%.1f' % (end-start)) + ' seconds'
            result = {'train_file_name': self.train_file_name,
                      'X_train_shape': str(self.X_train.shape),
                      'result': result_lr,
                      'train_para': self.train_para,
                      'grid_search_duration': duration}
            self.gs_lr = gs_lr
            return result

        elif self.algorithm == DAAS_DEF.alg_knn:
            start = time.time()
            logging.info('KNeighborsClassifier grid searching...')
            knn = KNeighborsClassifier(n_neighbors=3)
            param_range = [3,4,5]
            param_grid = dict(n_neighbors=param_range)
            gs_knn = GridSearchCV(estimator=knn, 
                                  param_grid=param_grid, 
                                  cv=DAAS_DEF.cv_num)
            gs_knn.fit(self.X_train, self.y_train)
            result_knn = self.GetResult(gs_knn, self.X_train, self.y_train, param_range)
            end = time.time()
            duration = str('%.1f' % (end-start)) + ' seconds'
            result = {'train_file_name': self.train_file_name,
                      'X_train_shape': str(self.X_train.shape),
                      'result': result_knn,
                      'train_para': self.train_para,
                      'grid_search_duration': duration}
            self.gs_knn = gs_knn
            return result

        elif self.algorithm == DAAS_DEF.alg_rfc:
            start = time.time()
            logging.info('RandomForestClassifier grid searching...')
            rfc = RandomForestClassifier(random_state=DAAS_DEF.random_state)
            param_grid = { 
                #'n_estimators': [200, 300],
                'max_features': ['sqrt', 'log2']}
            gs_rfc = GridSearchCV(estimator=rfc, 
                                  param_grid=param_grid, 
                                  cv=DAAS_DEF.cv_num)
            gs_rfc.fit(self.X_train, self.y_train)
            result_rfc = self.GetResult(gs_rfc, self.X_train, self.y_train, param_grid)
            end = time.time()
            duration = str('%.1f' % (end-start)) + ' seconds'
            result = {'train_file_name': self.train_file_name,
                      'X_train_shape': str(self.X_train.shape),
                      'result': result_rfc,
                      'train_para': self.train_para,
                      'grid_search_duration': duration}
            self.gs_rfc = gs_rfc
            return result

        else :
            assert(False)
            return DAAS_DEF.BAD_REQUEST        
 

    def RunCombiningModel(self):
        start = time.time()
        lr_info = ''
        if self.gs_lr is None:
            logging.info('LogisticRegression grid searching...')
            logging.info(strftime("%H:%M:%S", gmtime()))
            lr = LogisticRegression(penalty='l2', random_state=10)

            param_range = [0.1, 1.0, 10.0]
            param_grid = dict(C=param_range)
            gs_lr = GridSearchCV(estimator=lr, 
                                 param_grid=param_grid, 
                                 cv=DAAS_DEF.cv_num)
            gs_lr = gs_lr.fit(self.X_train, self.y_train)
            result_lr = self.GetResult(gs_lr, self.X_train, self.y_train, param_range)
            lr_info = {'alalgorithm': 'LogisticRegression',
                        'result': result_lr}
            self.gs_lr = gs_lr
        ##############################################
        knn_info = ''
        if self.gs_knn is None:
            logging.info('KNeighborsClassifier grid searching...')
            logging.info(strftime("%H:%M:%S", gmtime()))
            knn = KNeighborsClassifier(n_neighbors=3)
            param_range = [3,4,5]

            param_grid = dict(n_neighbors=param_range)
            gs_knn = GridSearchCV(estimator=knn, 
                                  param_grid=param_grid, 
                                  cv=DAAS_DEF.cv_num)
            gs_knn = gs_knn.fit(self.X_train, self.y_train)
            result_knn = self.GetResult(gs_knn, self.X_train, self.y_train, param_range)
            knn_info = {'alalgorithm': 'KNeighborsClassifier',
                        'result': result_knn}
            self.gs_knn = gs_knn
        #################################################
        rfc_info = ''
        if self.gs_rfc is None:
            logging.info('RandomForestClassifier grid searching...')
            logging.info(strftime("%H:%M:%S", gmtime()))
            rfc = RandomForestClassifier(random_state=DAAS_DEF.random_state)
            param_grid = { 
                #'n_estimators': [100, 200, 300],
                'max_features': ['sqrt', 'log2']}
            gs_rfc = GridSearchCV(estimator=rfc, 
                                  param_grid=param_grid, 
                                  cv=DAAS_DEF.cv_num)
            gs_rfc = gs_rfc.fit(self.X_train, self.y_train)
            result_rfc = self.GetResult(gs_rfc, self.X_train, self.y_train, param_grid)
            rfc_info = {'alalgorithm': 'RandomForestClassifier',
                        'result': result_rfc}
            self.gs_rfc = gs_rfc
        ###############################################
        logging.info('VotingClassifier grid searching...')
        logging.info(strftime("%H:%M:%S", gmtime()))
        ensemble_voting = VotingClassifier(estimators=[('lgr', self.gs_lr), 
            ('rfc', self.gs_rfc),('knn', self.gs_knn)], voting='soft') 
 
        ensemble_voting.fit(self.X_train, self.y_train)
        result_ens = self.GetResult(ensemble_voting, self.X_train, self.y_train)
        ensemble_info = {'algorithm': 'VotingClassifier', 
                         'result': result_ens}
        end = time.time()
        duration = str('%.1f' % (end-start)) + ' seconds'
        result = {'train_file_name': self.train_file_name,
                  'X_train_shape': str(self.X_train.shape),
                  'result':[lr_info,knn_info,rfc_info,ensemble_info],
                  'run_time': duration,
                  'train_para': self.train_para}
        # svc_info has been deleted as too slow
        logging.info(strftime("%H:%M:%S", gmtime()))
        return result


    def TrainObj2Num(self):  
    # except titanic, only support col is the last col
        if self.preProcessOption == DAAS_DEF.pre_banking:
            self.df_train = GPAL_F.Code_banking(self.df_train)
            label_col = self.trainLabelCol
            y_column = self.df_train.columns[label_col]
            X_columns = self.df_train.columns[0:label_col]
            self.y_train = self.df_train[y_column].values
            self.X_train = self.df_train[X_columns].values

        elif self.preProcessOption == DAAS_DEF.pre_titanic :
            self.df_train = self.Pre_titanic(self.df_train)
            y_column = self.df_train.columns[0] #
            self.y_train = self.df_train[y_column].values
            X_columns = self.df_train.columns[1:]
            self.X_train = self.df_train[X_columns].values

        elif self.preProcessOption == DAAS_DEF.pre_drop:
            self.df_train = self.Pre_drop(self.df_train)
            label_col = self.trainLabelCol
            if label_col == len(self.df_train.columns):
                # label_col is at the right of the data table
                y_column = self.df_train.columns[label_col]
                X_columns = self.df_train.columns[0:label_col]
                self.y_train = self.df_train[y_column].values
                self.X_train = self.df_train[X_columns].values
            else:
                # lable_col is at the left of the data table
                y_column = self.df_train.columns[label_col]
                X_columns = self.df_train.columns[label_col+1:]
                self.y_train = self.df_train[y_column].values
                self.X_train = self.df_train[X_columns].values


        elif self.preProcessOption == DAAS_DEF.pre_wdbc:
            self.Pre_wdbc()  # tbu

        else: 
            logging.info(str(label_col)+','+str(y_column))
            logging.info(self.X_train.shape)
            logging.info(self.preProcessOption)
            assert(False)
            return DAAS_DEF.BAD_REQUEST

        return DAAS_DEF.SUCCESS
        #pre-processing end        

    def Scaler(self, ndata):
        # scaler
        if self.scalerOption == DAAS_DEF.min_max_scaler:
            scaler = MinMaxScaler()
            ndata = scaler.fit_transform(ndata)
        elif self.scalerOption == DAAS_DEF.standard_scaler:
            scaler = StandardScaler()
            ndata = scaler.fit_transform(ndata)
        else:
            ndata = ndata
        
        return ndata
        #scaler end

    def ClassifierRun(self):
        #runOption begin
        if self.runOption == DAAS_DEF.run_cross_validation:
            result = self.RunCrossValidation()
            return result
        elif self.runOption == DAAS_DEF.run_grid_search:
            result = self.RunGridSearch()
            return result
        elif self.runOption == DAAS_DEF.run_combining_model:
            result = self.RunCombiningModel()
            return result
        else :
            assert(False)
            return DAAS_DEF.BAD_REQUEST
        #runOption end                                


    def ClassifierTraining(self):
        result = self.TrainObj2Num()
        if result == DAAS_DEF.BAD_REQUEST:
            return DAAS_DEF.BAD_REQUEST

        self.X_train = self.Scaler(self.X_train)

        result = self.ClassifierRun()
        return result

    def ModelTraining(self, req):
        result = self.ValidCheck_TrainingSave(req)
        if result != DAAS_DEF.SUCCESS:
            return result

        if self.algorithm == DAAS_DEF.alg_arima:
            result = self.TrainArima()
            return result
        
        elif self.algorithm == DAAS_DEF.alg_km:
            result = self.TrainKM()
            return result

        elif self.trainLabelCol>=0:
            result = self.ClassifierTraining()
            #logging.info('result of ClassifierTraining: '+str(result))
            return result
        else:
            assert(False)
            return DAAS_DEF.BAD_REQUEST

    def TestObj2Num(self):
        label_col = self.testLabelCol
        if label_col<-1 :  # -1 for no label
            logging.info('label_col: '+str(label_col))
            return DAAS_DEF.BAD_REQUEST

        if self.preProcessOption == DAAS_DEF.pre_banking:
            self.df_test = GPAL_F.Code_banking(self.df_test_raw)
            if label_col == -1:
                # no label provided
                self.y_test = None
                self.b_y_testIncluded = False
                self.X_test = self.df_test.values            
            else:
                y_column = self.df_test.columns[label_col]
                X_columns = self.df_test.columns[0:label_col]
                # assume banking data label at the end of the table
                self.y_test = self.df_test[y_column].values
                self.X_test = self.df_test[X_columns].values 
                self.b_y_testIncluded = True

        elif self.preProcessOption == DAAS_DEF.pre_titanic:
            self.df_test = self.Pre_titanic(self.df_test_raw)

            if label_col == -1:
                self.y_test = None
                self.b_y_testIncluded = False
                self.X_test = self.df_test.values
            else:
                y_column = self.df_test.columns[0] 
                # assume label_col=0 for titanic data after coding
                self.y_test = self.df_test[y_column].values
                X_columns = self.df_test.columns[1:]
                self.X_test = self.df_test[X_columns].values
                self.b_y_testIncluded = True


        elif self.preProcessOption == DAAS_DEF.pre_drop:
            self.df_test = self.Pre_drop(self.df_test_raw)

            if label_col == -1:
                self.y_test = None
                self.b_y_testIncluded = False
                self.X_test = self.df_test.values

            else:
                self.b_y_testIncluded = True
                if label_col == len(self.df_test.columns):
                    # label_col is at the right of the data table
                    y_column = self.df_test.columns[label_col]
                    X_columns = self.df_test.columns[0:label_col]
                    # only support label_col at the end
                    self.y_test = self.df_test[y_column].values
                    self.X_test = self.df_test[X_columns].values 
                else:
                    # label_col is at the left of the data table
                    y_column = self.df_test.columns[label_col]
                    X_columns = self.df_test.columns[label_col+1:]
                    # only support label_col at the end
                    self.y_test = self.df_test[y_column].values
                    self.X_test = self.df_test[X_columns].values 


        elif self.preProcessOption == DAAS_DEF.pre_wdbc :
            self.Pre_wdbc(self.df_test_raw)
            # tbu
        else:
            logging.info('preProcessOption: '+self.preProcessOption)
            return DAAS_DEF.BAD_REQUEST
        
        return DAAS_DEF.SUCCESS
        #pre-processing end

    def SaveTestInfo(self, req):
        file_name = req['file']['file_name']
        csv_file = req['file']['file_content']

        path_file_name = './upload/'+file_name
        fn = open(path_file_name,'w')
        fn.write(csv_file)
        fn.close()

        self.test_file_name = file_name
        logging.info('In Test save')
        if(self.headOption == DAAS_DEF.no_hearder):
            self.df_test_raw = pd.read_csv(path_file_name, header=None)
        else:
            self.df_test_raw = pd.read_csv(path_file_name)

        self.testLabelCol = int(req['testLabelCol'])
        result = self.TestObj2Num()
        if not result == DAAS_DEF.SUCCESS:
            return result

        self.X_test = self.Scaler(self.X_test)

        shape = self.X_test.shape
        if shape[1] != self.X_train.shape[1]:
            logging.info('X_test shape: '+str(shape))
            logging.info('X_train.shape: '+str(self.X_train.shape))
            logging.info('pre-Process: '+str(self.preProcessOption))
            temp_test = str(self.df_test.columns)
            logging.info('self.df_test.columns: '+temp_test)
            temp_train = str(self.df_train.columns)
            logging.info('self.df_train.columns: '+temp_train)
            
            #assert(False)
            return DAAS_DEF.BAD_REQUEST

        test_file_load = {'testLabelCol': self.testLabelCol,
                          'file_name': file_name,
                          'X_test shape': str(shape)}
        return test_file_load        
 
    def Predict(self, req):
        start = time.time()
        if req['algorithm'] == DAAS_DEF.alg_lr:
            if self.gs_lr is None:
                estimator = LogisticRegression(C=1.0, random_state=DAAS_DEF.random_state)
            else:
                estimator = self.gs_lr
        elif req['algorithm'] == DAAS_DEF.alg_knn:
            if self.gs_knn is None:
                estimator = KNeighborsClassifier(n_neighbors=5)
            else:
                estimator = self.gs_knn
        elif req['algorithm'] == DAAS_DEF.alg_rfc:
            if self.gs_rfc is None:
                estimator = RandomForestClassifier(n_estimators=300, 
                                     max_features='auto', 
                                     random_state=DAAS_DEF.random_state)
            else:
                estimator = self.gs_rfc
        elif req['algorithm'] == DAAS_DEF.alg_combine:
            if self.gs_lr is None:
                lr = LogisticRegression(C=1.0, random_state=DAAS_DEF.random_state)
            else:
                lr = self.gs_lr

            if self.gs_rfc is None:
                rfc = RandomForestClassifier(n_estimators=300, 
                                     max_features='auto', 
                                     random_state=DAAS_DEF.random_state)
            else:
                rfc = self.gs_rfc

            if self.gs_knn is None:
                knn = KNeighborsClassifier(n_neighbors=5)
            else:
                knn = self.gs_knn

            estimator = VotingClassifier(estimators=[('lr', lr), 
                            ('rfc', rfc),('knn',knn)], voting='soft')
        else:
            #assert(False)
            return DAAS_DEF.BAD_REQUEST

        #logging.info(str(estimator))
        estimator.fit(self.X_train, self.y_train)

        logging.info('self.y_train[0:3]: '+ str(self.y_train[0])+ \
            ','+str(self.y_train[1])+','+str(self.y_train[2]))

        predictions = estimator.predict(self.X_test)

        score = None
        if self.b_y_testIncluded:
            score = self.GetResult(estimator, self.X_test, self.y_test)
        
        fn = './predictions/prediction.csv'

        if self.preProcessOption == DAAS_DEF.pre_titanic:
            self.df_test['Survived'] = predictions
            self.df_test.to_csv(fn, index=False)

        else:
            self.df_test['Prediction'] = predictions
            self.df_test.to_csv(fn, index=False)
                
        fn = open(fn, 'r')
        fn_content = fn.read()
        end = time.time()
        duration = str(end-start)+' seconds'
        result = {'score': score,
                  'run_time': duration,
                  'prediction': fn_content}
        return result

    def Execute(self, version, req):
        #logging.info('execute')
        if req == None:
            return DAAS_DEF.BAD_REQUEST

        if req['type'] == DAAS_DEF.predict :
            result = self.Predict(req)
            return result
        elif req['type']==DAAS_DEF.train_file:
            #self.__init__()
            result = self.ModelTraining(req)
            #logging.info('modeltraining call:'+str(result))
            return result
        elif req['type']==DAAS_DEF.test_file :
            result = self.SaveTestInfo(req)
            return result
        else:
            assert(False)
            return DAAS_DEF.BAD_REQUEST



class DAAS_ARIMA(object):
    def __init__(self):
        self.url = '''http://www.odaa.dk/api/action/datastore_search'''
        self.resource_id = 'resource_id=b3eeb0ff-c8a8-4824-99d6-e0a3747c8b0d'
        self.raw_file_name = None
        self.headOption = None
        self.resampleInterval = None
        self.indexCol = None
        self.df_raw = None
        self.df_test_col_resample = None

        self.df_diff = None
        self.test_column_no = None
        self.b_diffrentiated = False 
        self.diffOrder = 0
        self.diffOrder_onetime = 0

        self.best_pdq = None
        self.df_model_train = None
        self.df_model_test = None
        self.df_model_predictions=None

    def SaveRawFile(self, req):
        self.__init__()
        file_name = req['file']['file_name']
        csv_file = req['file']['file_content']

        path_file_name = './upload/'+file_name
        fn = open(path_file_name,'w')
        fn.write(csv_file)
        fn.close()

        self.raw_file_name = file_name
        self.headOption = req['para']['headOption']
        self.indexCol = req['para']['indexCol']
        if(self.headOption == DAAS_DEF.no_hearder):
            self.df_raw = pd.read_csv(path_file_name, parse_dates=True, 
                                    index_col=self.indexCol, header=None)
        else:
            self.df_raw = pd.read_csv(path_file_name, parse_dates=True, 
                                    index_col=self.indexCol)
        
        result = {'shape of raw data': str(self.df_raw.shape)}
        logging.info('In save raw:'+str(result))
        return result

    def StatWhiteTest(self,req):
        logging.info('shape of df_raw: '+str(self.df_raw.shape))
        if self.diffOrder == 0:
            self.resampleInterval = req['para']['resampleInterval']
            self.test_column_no = int(req['para']['testColumn'])
            column = self.df_raw.columns[self.test_column_no]
            logging.info(str(column))
            self.df_test_col = self.df_raw[column]

            if self.resampleInterval == DAAS_DEF.resample_H:
                self.df_test_col_resample = self.df_test_col.resample('H').mean()

            elif self.resampleInterval == DAAS_DEF.resample_D:
                self.df_test_col_resample = self.df_test_col.resample('D').mean()

            else:
                self.df_test_col_resample = self.df_test_col
                logging.info('shape of df_raw: '+str(self.df_raw.shape))
            df_test_col = self.df_test_col_resample
        else:
            df_test_col = self.df_diff

        df_test_col = df_test_col.dropna()
        logging.info('shape of df before adf'+str(df_test_col.shape))
        adf_test = str(ADF(df_test_col))
        white_noise_test = str(acorr_ljungbox(df_test_col, lags=1)[1])

        column = self.df_raw.columns[self.test_column_no]
        ARIMA_F.tsplot(df_test_col, title=column, lags=36);
        plt.savefig('./output/stat_white_test.png') 
        fp = open('./output/stat_white_test.png','rb')
        Imgcontent = fp.read()
        base64_image = base64.b64encode(Imgcontent)
        file = {'file_name': 'stat_white_test.png',
                'file_content': base64_image}
        fp.close()
        shape = str(df_test_col.shape)
        
        result = {'adf_test': adf_test,
                  'white_noise_test': white_noise_test,
                  'shape': shape,
                  'diffOrder': self.diffOrder,
                  'file': file}
        return result

    def Differentiation(self, req):
        if self.diffOrder == 0:
            self.df_diff = self.df_test_col_resample

        self.diffOrder_onetime = req['para']['diffOrder']
        for i in range(self.diffOrder_onetime):
            self.df_diff = self.df_diff.diff()
            self.df_diff = self.df_diff.dropna()
            self.diffOrder +=1
            logging.info('Diff one time')

        self.df_diff = self.df_diff.dropna()
        result = {'diff_order':self.diffOrder,
                  'diff_shape':str(self.df_diff.shape)}
        return result

    def Search_pdq(self, req):
        p = req['para']['p']
        d = req['para']['d']
        q = req['para']['q']
        if p<0 or d<0 or q<0:
            return DAAS_DEF.BAD_REQUEST
        fp = open('./output/ARIMA.txt','w')
        dataset = self.df_test_col_resample.values
        dataset = dataset.astype('float64')
        best_score, best_pdq = float("inf"), None
        p_values = range(0, p)
        d_values = range(0, d)
        q_values = range(0, q)
        
        for p in p_values:
            for d in d_values:
                for q in q_values:
                    order = (p,d,q)
                    try:
                        #logging.info(str(order))
                        mse = ARIMA_F.evaluate_arima_model(dataset, order)
                        fp.write('order:%s, MSE=%.3f\n' % (order,mse))
                        #logging.info(str(order)+str(mse))
                        if mse < best_score:
                            best_score, best_pdq = mse, order
                            fp.write('Best best pdq so far:%s, MSE=%.3f\n' % (order,mse))
                    except:
                        fp.write('MSE excepted when calculating with this pdq\n')
                        continue
        fp.write('Best pdq:%s, MSE=%.3f\n' % (best_pdq, best_score))
        fp.close()
        fp = open('./output//ARIMA.txt','r')
        file_content = fp.read()
        file = {'file_name': 'ARIMA.txt', 
                'file_content': file_content}
        fp.close()
        self.best_pdq = best_pdq
        result = {'best_pdq': best_pdq,
                  'best_score': best_score,
                  'file': file}
        return result      

    def CreateModel(self, req):
        p = req['para']['p']
        d = req['para']['d']
        q = req['para']['q']
        if p<0 or d<0 or q<0:
            return DAAS_DEF.BAD_REQUEST

        self.sDateOfTest = req['para']['sDateOfTest']
        self.eDateOfTest = req['para']['eDateOfTest']
        eDateOfTrain = datetime.strptime(self.sDateOfTest, '%Y-%m-%d')
        logging.info('sDateOfTest: '+str(eDateOfTrain))
        if self.resampleInterval == DAAS_DEF.resample_no:
            eDateOfTrain += timedelta(minutes = -5)
        elif self.resampleInterval == DAAS_DEF.resample_H:
            eDateOfTrain += timedelta(hours = -1)
            
        elif self.resampleInterval == DAAS_DEF.resample_D:
            eDateOfTrain += timedelta(days = -1)
        else:
            return DAAS.BAD_REQUEST

        logging.info('eDateOfTrain: '+str(eDateOfTrain))
        self.df_model_train = self.df_test_col_resample[:eDateOfTrain]
        self.df_model_test = self.df_test_col_resample[self.sDateOfTest:self.eDateOfTest]
        logging.info(str(self.df_model_train.tail()))
        logging.info(str(self.df_model_test.head()))

        train = self.df_model_train.values
        test = self.df_model_test.values
        logging.info('Length of train: '+str(len(train)))
        logging.info('Length of test: '+str(len(test)))

        pdq_order = (p,d,q)
        history = [x for x in train]
        predictions = list()
        for i in range(len(test)):
        # predict
            model = ARIMA(history, order=pdq_order)
            model_fit = model.fit(disp=0)
            yhat = model_fit.forecast()[0]
            predictions.append(yhat)
        # observation
            obs = test[i]
            history.append(obs)

        self.df_model_predictions = pd.Series(predictions)
        mse = mean_squared_error(test, predictions)
        rmse = sqrt(mse)
        fp = open('./output/model_report.txt', 'w')
        fp.write(str(model_fit.summary()))
        fp.close

        fp = open('./output/model_report.txt','r')
        model_report = fp.read()
        fp.close()

        fig = plt.figure()
        plt.plot(test, color='blue')
        plt.plot(predictions, color='red')
        plt.title('Test(blue) and Prediction(red)')
        plt.savefig('./output/test_predict.png') 
        plt.close('all')

        fp = open('./output/test_predict.png','rb')
        Imgcontent = fp.read()
        base64_image = base64.b64encode(Imgcontent)
        file = {'file_name': 'test_predict.png',
                'file_content': base64_image}
        fp.close()
                
        result = {'RMSE': rmse,
                  'model_report': model_report,
                  'file':file}
        return result

    def ResidualTest(self, req):
        test = self.df_model_test.values
        logging.info('shape of test:'+str(test.shape)+str(test.dtype))
        predictions = self.df_model_predictions.values
        residuals = [test[i]-predictions[i] for i in range(len(test))]
        residuals = pd.DataFrame(residuals)
        white_noise_test = str(acorr_ljungbox(residuals, lags=1)[1])
        shape = str(residuals.shape)

        fig = plt.figure()
        axh=plt.subplot(211)
        axh.set_title('Histogram of residuals')
        residuals.hist(ax=plt.gca())
        axk=plt.subplot(212)
        axk.set_title('KDE of residuals')
        residuals.plot(kind='kde', ax=plt.gca())
        plt.tight_layout()
        plt.savefig('./output/residual_test1.png') 
        plt.close('all')

        fp = open('./output/residual_test1.png','rb')
        Imgcontent = fp.read()
        base64_image = base64.b64encode(Imgcontent)
        file1 = {'file_name': 'residual_test.png',
                'file_content': base64_image}
        fp.close()
        
        lags=9
        ncols=3
        nrows=int(np.ceil(lags/ncols))

        fig, axes = plt.subplots(ncols=ncols, nrows=nrows, figsize=(4*ncols, 4*nrows))

        for ax, lag in zip(axes.flat, np.arange(1,lags+1, 1)):
            lag_str = 't-{}'.format(lag)
            X = (pd.concat([residuals, residuals.shift(-lag)], axis=1,
                           keys=['y'] + [lag_str]).dropna())

            X.plot(ax=ax, kind='scatter', y='y', x=lag_str);
            corr = X.corr().as_matrix()[0][1]
            ax.set_ylabel('Original')
            ax.set_title('Lag: {} (corr={:.2f})'.format(lag_str, corr));
            ax.set_aspect('equal');
            sns.despine();
        
        fig.tight_layout();
        plt.savefig('./output/residual_test2.png') 
        plt.close('all')

        fp = open('./output/residual_test2.png','rb')
        Imgcontent = fp.read()
        base64_image = base64.b64encode(Imgcontent)
        file2 = {'file_name': 'residual_test2.png',
                'file_content': base64_image}
        fp.close()
        #plt.show()
        result = {'white_noise_test': white_noise_test,
                  'shape': shape,
                  'file1':file1,
                  'file2':file2}
        return result
    
    def Execute(self, version, req):
        #logging.info('execute')
        if req == None:
            return DAAS_DEF.BAD_REQUEST

        if (req['command'] == DAAS_DEF.upload_raw_file) :
            logging.info('In Execute before save raw')
            result = self.SaveRawFile(req)
            logging.info('df_raw.shape:'+str(self.df_raw.shape))
            return result

        elif (req['command'] == DAAS_DEF.stat_white_test) :
            logging.info('df_raw.shape:'+str(self.df_raw.shape))
            result = self.StatWhiteTest(req)
            return result

        elif (req['command'] == DAAS_DEF.differentiation) :
            result = self.Differentiation(req)
            return result

        elif (req['command'] == DAAS_DEF.search_pdq) :
            result = self.Search_pdq(req)
            return result

        elif (req['command'] == DAAS_DEF.create_model) :
            result = self.CreateModel(req)
            return result

        elif (req['command'] == DAAS_DEF.residual_test) :
            result = self.ResidualTest(req)
            return result

        else:
            return DAAS_DEF.BAD_REQUEST

