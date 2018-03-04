import numpy as np
import time

time_slot = {
	'Peak1': ['7:30:00', '9:30:00'],
	'Peak2': ['11:30:00', '13:30:00'],
	'Peak3': ['17:00:00', '19:00:00'],
	'Offpeak1': [['5:00:00','7:30:00'],['9:30:00','11:30:00'],
				 ['13:30:00','17:00:00'],['19:00:00','23:00:00']],
	'Offpeak2': ['23:00:00', '5:00:00'],
	'WEH1': ['7:00:00','24:00:00'],
	'WEH2': ['0:00:00','7:00:00']
}
I_SATURDAY = 6
I_SUNDAY = 7

def GetTimeSlot(mytime):
	mytime = mytime.replace('T', ' ')
	mytime = time.strptime(mytime, '%Y-%m-%d %H:%M:%S')
	#add validcheck(mytime)
	if (WeekendOrHoliday(mytime)):
		return GetWEHSlot(mytime)
	else:
		return GetWeekDaySlot(mytime)

def WeekendOrHoliday(mytime):
	#mytime = time.strptime(mytime, '%Y-%m-%d %H:%M:%S')
	if (mytime.tm_wday == I_SATURDAY or mytime.tm_wday == I_SUNDAY):
		return True
	else:
		return False

def GetWEHSlot(mytime):
	hms = int(time.strftime("%H%M%S", mytime))
	weh1_min = time_slot['WEH1'][0]
	weh1_max = time_slot['WEH1'][1]
	weh1_min = int(weh1_min.replace(':',''))
	weh1_max = int(weh1_max.replace(':',''))
	if ( hms>weh1_min and hms<weh1_max):
		return 'WEH1'
	else:
		return 'WEH2'

def GetWeekDaySlot(mytime):
	hms = int(time.strftime("%H%M%S", mytime))
	pk1_min = int((time_slot['Peak1'][0]).replace(':',''))
	pk1_max = int((time_slot['Peak1'][1]).replace(':',''))
	pk2_min = int((time_slot['Peak2'][0]).replace(':',''))
	pk2_max = int((time_slot['Peak2'][1]).replace(':',''))
	pk3_min = int((time_slot['Peak3'][0]).replace(':',''))
	pk3_max = int((time_slot['Peak3'][1]).replace(':',''))
	opk2_min = int((time_slot['Offpeak2'][0]).replace(':',''))
	opk2_max = int((time_slot['Offpeak2'][1]).replace(':',''))

	if( hms>pk1_min and hms<pk1_max):
		return 'Peak1'
	elif ( hms>pk2_min and hms<pk2_max ):
		return 'Peak2'
	elif (hms>pk3_min and hms<pk3_max):
		return 'Peak3'
	elif (hms>opk2_min or hms<opk2_max):
		return 'Offpeak2'
	else:
		return 'Offpeak1'

def CreateDict(list):
	ar = np.array(list)
	
	d_vehicleSpeed = {'min':0, 'max':0, 'mean':0, 'num':0}
	d_vehicleCount = {'min':0, 'max':0, 'mean':0, 'num':0}

	d_vehicleSpeed['min'] = ar[:,1].min()
	d_vehicleSpeed['max'] = ar[:,1].max()
	d_vehicleSpeed['mean'] = ar[:,1].mean()
	d_vehicleSpeed['num'] = len(ar[:,1])

	d_vehicleCount['min'] = ar[:,2].min()
	d_vehicleCount['max'] = ar[:,2].max()
	d_vehicleCount['mean'] = ar[:,2].mean()
	d_vehicleCount['num'] = len(ar[:,2])
	d_p = {'vehicleSpeed':d_vehicleSpeed, 'vehicleCount':d_vehicleCount}
	return d_p

def UpdateTable(conn, tableName, stype, dt):
	amin = [dt['p1'][stype]['min'], dt['p2'][stype]['min'],
		   dt['p3'][stype]['min'], dt['op1'][stype]['min'],
		   dt['op2'][stype]['min'], dt['weh1'][stype]['min'],
		   dt['weh2'][stype]['min']]

	amax = [dt['p1'][stype]['max'], dt['p2'][stype]['max'],
		   dt['p3'][stype]['max'], dt['op1'][stype]['max'],
		   dt['op2'][stype]['max'], dt['weh1'][stype]['max'],
		   dt['weh2'][stype]['max']]	

	amean = [dt['p1'][stype]['mean'], dt['p2'][stype]['mean'],
		   dt['p3'][stype]['mean'], dt['op1'][stype]['mean'],
		   dt['op2'][stype]['mean'], dt['weh1'][stype]['mean'],
		   dt['weh2'][stype]['mean']]

	anum = [dt['p1'][stype]['num'], dt['p2'][stype]['num'],
		   dt['p3'][stype]['num'], dt['op1'][stype]['num'],
		   dt['op2'][stype]['num'], dt['weh1'][stype]['num'],
		   dt['weh2'][stype]['num']]	
	ats = ['p1','p2','p3','op1','op2','weh1','weh2'] 
	tt = zip(amin, amax, amean, anum, ats)
	#print type(tt)
	labels = ['min', 'max', 'mean', 'num', 'slot_type']
	df = pd.DataFrame(tt, columns = labels)
	#print df, df.info()
	df.to_sql(tableName, conn, if_exists='append', index=False)
	conn.commit()
	return

def Statistic(aTSC):
	p1 = []
	p2 = []
	p3 = []
	op1 = []
	op2 = []
	weh1 = []
	weh2 = []

	for iTSC in aTSC:
		timestamp = iTSC[0]
		slot = GetTimeSlot(timestamp)
		if slot == 'Peak1':
			p1.append(iTSC)
		elif slot == 'Peak2':
			p2.append(iTSC)
		elif slot == 'Peak3':
			p3.append(iTSC)
		elif slot == 'Offpeak1':
			op1.append(iTSC)
		elif slot == 'Offpeak2':
			op2.append(iTSC)
		elif slot == 'WEH1':
			weh1.append(iTSC)
		else:
			weh2.append(iTSC)		

	d_p1=0
	d_p2=0
	d_p3=0
	d_op1=0
	d_op2=0
	d_weh1=0
	d_weh2=0
	if(len(p1)>0):
		d_p1 = CreateDict(list=p1)

	if(len(p2)>0):
		d_p2 = CreateDict(list=p2)

	if(len(p3)>0):
		d_p3 = CreateDict(list=p3)

	if(len(op1)>0):
		d_op1 = CreateDict(list=op1)

	if(len(op2)>0):
		d_op2 = CreateDict(list=op2)

	if(len(weh1)>0):
		d_weh1 = CreateDict(list=weh1)

	if(len(weh2)>0):
		d_weh2 = CreateDict(list=weh2)

	stat_table = { 'p1':d_p1, 'p2':d_p2, 'p3':d_p3, 'op1':d_op1, 
					'op2':d_op2, 'weh1':d_weh1, 'weh2':d_weh2}
	return stat_table
#end of functions