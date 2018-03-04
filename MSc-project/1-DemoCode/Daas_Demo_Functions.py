import pandas as pd
import time

def CreateJs(Points):
    df=pd.read_csv("./static/metaSensorData-Download.csv")
    #print df.info()
    
    stime = time.strftime('%H-%M-%S',time.localtime(time.time()))
    mapfile_name = stime+'map_markers.js'
    whole_name = './static/'+mapfile_name
    fp=open(whole_name, 'w')
    fp.write('var markers = [\n')

    len_all = len(df)
    len_points = len(Points['a_rpt_id'])
    for i in range(len_all):
        long1 = df['POINT_1_LNG'][i]
        lat1 = df['POINT_1_LAT'][i]
        long2 = df['POINT_2_LNG'][i]
        lat2 = df['POINT_2_LAT'][i]

        fp.write('{\n')
        rid = df['REPORT_ID'][i]    
        if rid in Points['a_rpt_id']:
            fp.write('\t"color": "red",\n')
        else :
            fp.write('\t"color": "blue",\n')
        fp.write('\t"reportId": '+str(rid)+',\n')
        fp.write('\t"lng": '+str(long1)+',\n')
        fp.write('\t"lat": '+str(lat1)+',\n')
        fp.write('},\n')

        fp.write('{\n')
        if rid in Points['a_rpt_id']:
            fp.write('\t"color": "red",\n')
        else :
            fp.write('\t"color": "blue",\n')
        fp.write('\t"reportId": '+str(rid)+',\n')
        fp.write('\t"lng": '+str(long2)+',\n')
        fp.write('\t"lat": '+str(lat2)+',\n')
        #fp.write('\t"speed": '+str(speed)+',\n')
        #fp.write('\t"count": '+str(count)+',\n')
        fp.write('},\n')

    fp.write('];') 
    fp.close()
    return mapfile_name
#end of CreateJs