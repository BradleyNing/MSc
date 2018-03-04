from wtforms import StringField, SubmitField, DecimalField, \
					IntegerField, FileField, TextAreaField, SelectField
from wtforms.fields.html5 import DateField
from flask_wtf import FlaskForm
from wtforms.validators import Required
from wtforms.widgets import TextArea

class IndexForm(FlaskForm):
    publish = SubmitField('Publish a Device')
    myimport = SubmitField('Import Devices')
    #edit = SubmitField('Device Edit')
    xml = SubmitField('XML Content')
    rdf = SubmitField('RDF Content')
    query = SubmitField('Query')

class PublishForm(FlaskForm):
	name = StringField('Device Name:', validators=[Required()])
	did = IntegerField('Device ID:', validators=[Required()])
	location = StringField('Location:', validators=[Required()])
	#dtype = StringField('Device Type:', validators=[Required()])
	dtype = SelectField('Device Type:', choices=[
        ('Mobile Device','Mobile Device'), ('Sensor','Sensor'), 
        ('Actutor','Actutor'), ('Other','Other')], 
		validators=[Required()])
	#date = DateField('Publish Date:')	
	publish = SubmitField('Publish Device')

class ImportXMLForm(FlaskForm):
	importXML = FileField('Import XML File')
	submit = SubmitField('Confirm')

class EditForm(FlaskForm):
	confirm = SubmitField('Confirm')

class QueryForm(FlaskForm):
	query = TextAreaField('Enter your query')
	confirm = SubmitField('Confirm')
	result = TextAreaField('Result of the query')

class DisplayXMLForm(FlaskForm):
	xmlcontent = TextAreaField('Content of the Devices XML description')
	#content = StringField(u'Text', widget=TextArea())
	#confirm = SubmitField('Back to Index')	

class DisplayRDFForm(FlaskForm):
	rdfcontent = TextAreaField('Content of the Devices RDF description')