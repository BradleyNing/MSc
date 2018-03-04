from flask_wtf import FlaskForm
from wtforms import SubmitField, FileField, TextAreaField, \
                    RadioField, DecimalField, SelectField, \
                    DateField, StringField, IntegerField, FloatField
import DAAS_DEF

class ITRT_Form(FlaskForm):
    imgFile = FileField('Import Image File')
    submit = SubmitField('Confirm')

class SDA_Form(FlaskForm):
    startSubmit = SubmitField('Start Collecting Data')
    stopSubmit = SubmitField('Stop Collecting Data')
    getSubmit = SubmitField('Get Data (Input REPORT_ID and how many records)')
    rptID = IntegerField('REPORT_ID')
    numRecords = IntegerField('How Many Latest Records')
    resText = TextAreaField('Information from Data Collecting Server')
    getAlertSubmit = SubmitField('Get abnormal traffic points')
    alertPointsText = TextAreaField('Information of abnormal traffic points')
    showOnMapSubmit = SubmitField('Show abnormal traffic points on Map')
    showSensorsSubmit = SubmitField('Show all sensors on Map')

#ARIMA Forms begin
class ImportRawDataForm(FlaskForm):
    rawData = FileField('Upload raw data file')
    rawDataSubmit = SubmitField('Upload Confirm')
    trainText = TextAreaField('Information of raw data file')
    indexCol = IntegerField('Column of Index')
    fileHeadOption = SelectField('File Head Option', choices=[
                                  (DAAS_DEF.with_header,'File With Header'),
                                  (DAAS_DEF.no_hearder,'File Without Header')])

class StatNoiseTestForm(FlaskForm):
    testColumn = IntegerField('Column to be tested')
    statNoiseSubmit = SubmitField('Stationarity and White Noise Test Confirm')
    statNoiseText = TextAreaField('Response from DAAS')
    resampleInterval = SelectField('Resample Interval', choices=[
                (DAAS_DEF.resample_no, 'No Resample'), 
                (DAAS_DEF.resample_H, 'Resample in Hour'), 
                (DAAS_DEF.resample_D, 'Resample in Day')])

class DifferentionForm(FlaskForm):
    diffOrder = IntegerField('Order of differentiation')
    diffSubmit = SubmitField('Differentiation Confirm')
    diffText = TextAreaField('Response from DAAS')

class GetPDQForm(FlaskForm):
    pValue = IntegerField('Maximum p Value')
    dValue = IntegerField('Maximum d Value')
    qValue = IntegerField('Maximum q Value')
    pdqSubmit = SubmitField('pdq Searching Confirm')
    pdqText = TextAreaField('Response from DAAS about searching p, d, q')

class SetModelForm(FlaskForm):
    pValue = IntegerField('p Value')
    dValue = IntegerField('d Value')
    qValue = IntegerField('q Value')
    startOfTest = DateField('Start date of test data set(yyyy-mm-dd)')
    endOfTest = DateField('End date of test data set(yyyy-mm-dd)')
    setModelSubmit = SubmitField('Create Model Confirm')
    setModelText = TextAreaField('Trained Model Report from DAAS')

class ResidualTestForm(FlaskForm):
    residualTestSubmit = SubmitField('Residual Test Confirm')
    residualTestText = TextAreaField('Response from DAAS')

class ArimaPredictForm(FlaskForm):
    urlField = StringField('Data treaming URL: ')
    sampleInterval = IntegerField('Sample Interval(5,10 or 15 ... minutes)')
    reportID = IntegerField('ReportID of Prediction')
    predictionSubmit = SubmitField('Prediction Confirm')
    predictionText = TextAreaField('Prediction from DAAS')
#ARIMA Forms end

#GPAL Forms begin
class ImportTrainingForm(FlaskForm):
	trainingFile = FileField('Import Training File')
	trainSubmit = SubmitField('Training Configuration Confirm')
	trainText = TextAreaField('Information of Train File')
	resTrainText = TextAreaField('Response from DAAS for Train file')
	headOption = RadioField('headOption', 
							choices=[(DAAS_DEF.with_header,'With Header'),
							(DAAS_DEF.no_hearder,'Without Header')])

	preProcessOption = RadioField('preProcessOption', 
							choices=[(DAAS_DEF.pre_drop,'Drop all lines of NaN and text columns'),
							(DAAS_DEF.pre_wdbc,'Fill mean value for WDBC'),
							(DAAS_DEF.pre_titanic,'Fill and Coding for Titanic'),
							(DAAS_DEF.pre_banking, 'Coding for AWS banking')])
	
	scalerOption = RadioField('scalerOption', 
							choices=[(DAAS_DEF.no_scaler,'No Scaler'),
									(DAAS_DEF.min_max_scaler,'MinMaxScaler'),
									(DAAS_DEF.standard_scaler,'StandardSaler')])

	runOption = RadioField('runOption', 
							choices=[(DAAS_DEF.run_cross_validation,'Cross Validation'),
							(DAAS_DEF.run_grid_search, 'Grid Search'),
							(DAAS_DEF.run_combining_model, 'Combing five Model')])

	trainLabelCol = IntegerField('Column of Label(-1 for no Label included)')
	trainAlgoSelect = SelectField('Training Algorithm', choices=[
		        (DAAS_DEF.alg_lr, 'Logistic Regression'), 
		        (DAAS_DEF.alg_knn, 'K-Nearest Neighbors'), 
		        (DAAS_DEF.alg_rfc, 'Random Forest Classifier'),
				(DAAS_DEF.alg_svc, 'SVM'),
		        (DAAS_DEF.alg_gnb, 'Gaussian Naive Bayes'),
		        (DAAS_DEF.alg_km, 'K-Means Clustering'),
		        (DAAS_DEF.alg_arima, 'ARIMA')])
		#validators=[Required()])
	
class ImportTestForm(FlaskForm):
	testFile = FileField('Import Test File')
	testLabelCol = IntegerField('Column of Label(-1 for no Label included)')
	testSubmit = SubmitField('Test File Upload Confirm')
	testText = TextAreaField('Information of test file')
	resTestText = TextAreaField('Response from DAAS for test file')

class GpalPredictForm(FlaskForm):
	predAlgoSelect = SelectField('Prediction Algorithm', choices=[
		        (DAAS_DEF.alg_lr, 'Logistic Regression'), 
		        (DAAS_DEF.alg_knn, 'K-Nearest Neighbors'), 
		        (DAAS_DEF.alg_rfc, 'Random Forest Classifier'),
				(DAAS_DEF.alg_svc, 'SVM'),
		        (DAAS_DEF.alg_gnb, 'Gaussian Naive Bayes'),
		        (DAAS_DEF.alg_combine, 'Combining Five Models'),
		        (DAAS_DEF.alg_km, 'K-Means')])	
	predictSubmit = SubmitField('Predict Confirm')
	predictText = TextAreaField('Prediction from DAAS')

class FilePrepareForm(FlaskForm):
	rawFile = FileField('File to be splitted')
	headSelect = SelectField('Has Head or Not:', choices=[
		        (DAAS_DEF.with_header, 'Has Head Line'), 
		        (DAAS_DEF.no_hearder, 'Has no Head Line')])
	labelCol = IntegerField('Column of Label (-1 for no label)')
	testRatio = FloatField('Ratio of test size')
	splitSubmit = SubmitField('Split Confirm')
#GPAL Forms end