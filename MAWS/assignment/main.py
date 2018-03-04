from flask import Flask, render_template, redirect, url_for, jsonify, request
from flask_bootstrap import Bootstrap 
from flask_script import Manager
from flask_wtf import FlaskForm
from werkzeug.utils import secure_filename

import xml.dom.minidom
from lxml import etree, objectify
import rdflib
import random
import os
#import datetime
#import sqlite3

from forms import IndexForm, PublishForm, ImportXMLForm, \
	EditForm, QueryForm, DisplayXMLForm, DisplayRDFForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
#UPLOAD_FOLDER = 'c:'
Bootstrap(app)
manager = Manager(app)

xmlHeadStr = '''<?xml version="1.0"?>
<DeviceList>
</DeviceList>
    '''
startfp = open('.\generated\DeviceList-a.xml', 'w')
startfp.write(xmlHeadStr)
startfp.close()


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
	form = IndexForm()

	if form.publish.data:
		return redirect(url_for('publish'))

	if form.myimport.data:
		return redirect(url_for('importxml'))

#	if form.edit.data:
#		return redirect(url_for('edit'))	

	if form.query.data:
		return redirect(url_for('query'))

	if form.xml.data:
		return redirect(url_for('displayxml'))

	if form.rdf.data:
		return redirect(url_for('displayrdf'))
	return render_template('MAWSIndex.html', form=form)

@app.route('/publish', methods=['GET', 'POST'])
def publish():
	form = PublishForm()
	if form.validate_on_submit():
		deviceName = str(form.name.data)
		deviceId  = str(form.did.data)
		location = str(form.location.data)
		deviceType  = str(form.dtype.data)
		
		deviceNode = objectify.Element("Device")
		deviceNode.name = deviceName
		deviceNode.id = deviceId
		deviceNode.location = location
		deviceNode.type = deviceType
		deviceNode.value = random.uniform(0,100)
		doc = etree.parse(".\generated\DeviceList-a.xml")
		xmlRoot=doc.getroot()

		xmlRoot.append(deviceNode)
		objectify.deannotate(xmlRoot)
		etree.cleanup_namespaces(xmlRoot)

		xmlfp = open('.\generated\DeviceList-a.xml', 'w')
		xmlstr = etree.tostring(xmlRoot, pretty_print=True, xml_declaration=True)
		xmlstr=xmlstr.decode("utf-8")
		xmlfp.write(xmlstr)
		xmlfp.close()
		return redirect(url_for('index'))	
	return render_template('MAWSPublish.html', form=form)

@app.route('/importxml', methods=['GET', 'POST'])
def importxml():
	form = ImportXMLForm()
	if form.validate_on_submit():
		fc = form.importXML.data
		#fileName = secure_filename(fc.filename)
		#xml schema check to be added and append to the curent xmlRoot
		fc.save(".\generated\DeviceList-temp.xml")
		fc.close()

		xmlschema_doc = etree.parse(".\static\device_schema.xsd")
		xmlschema = etree.XMLSchema(xmlschema_doc)
		try:
			importDoc = etree.parse(".\generated\DeviceList-temp.xml")
		except Exception:
			return render_template('ImportError.html')

		result = xmlschema.validate(importDoc)
		if (result!=True):
			return render_template('ImportError.html')
		
		importXmlRoot=importDoc.getroot()
		doc = etree.parse(".\generated\DeviceList-a.xml")
		xmlRoot = doc.getroot()
		for child in importXmlRoot:
			value = objectify.SubElement(child, "value")
			value.text = str(random.uniform(0,100))
			xmlRoot.append(child)

		objectify.deannotate(xmlRoot)
		etree.cleanup_namespaces(xmlRoot)

		xmlfp = open('.\generated\DeviceList-a.xml', 'w')
		xmlstr = etree.tostring(xmlRoot, pretty_print=True, xml_declaration=True)
		xmlstr=xmlstr.decode("utf-8")
		xmlfp.write(xmlstr)
		xmlfp.close()
		return redirect(url_for('index'))

	return render_template('MAWSImport.html', form=form)

@app.route('/diplayxml')
def displayxml():
	form = DisplayXMLForm()
	if(os.path.isfile('.\generated\DeviceList-a.xml') == False):
		return render_template("FileNotExist.html")
	myxml = xml.dom.minidom.parse('.\generated\DeviceList-a.xml') 
	xml_as_string = myxml.toprettyxml(indent="\t", newl="\r")
	form.xmlcontent.data = str(xml_as_string)		
	return render_template('MAWSXML.html', form=form)

@app.route('/diplayrdf')
def displayrdf():
	form = DisplayRDFForm()
	if(os.path.isfile('.\generated\DeviceList-a.xml') == False):
		return render_template("FileNotExist.html")

	doc = etree.parse(".\generated\DeviceList-a.xml")
	styledoc = etree.parse(".\static\Devicelist-myxsl.xsl")
	transform = etree.XSLT(styledoc)    
	resultdoc = str(transform(doc))
	fp = open('.\generated\DeviceList-a-rdf.xml','w')
	fp.write(resultdoc)
	fp.close()

	myxml = xml.dom.minidom.parse('.\generated\DeviceList-a-rdf.xml') 
	xml_as_string = myxml.toprettyxml(indent="\t", newl="\r")
	form.rdfcontent.data = str(xml_as_string)		
	return render_template('MAWSRDF.html', form=form)


@app.route('/query', methods=['GET', 'POST'])
def query():
	form = QueryForm()
	g = rdflib.Graph()
	if(os.path.isfile('.\generated\DeviceList-a-rdf.xml') == False):
		return render_template("FileNotExist.html")
	g.parse(".\generated\DeviceList-a-rdf.xml")
	#form.query.data = '''SELECT DISTINCT ?name
	      # WHERE {
	        #  ?a MAWSDevice:hasLocation ?name.}'''
	if form.confirm.data:
		queryStr = str(form.query.data)
		qres = g.query(queryStr)
		resutlStr =''
		for row in qres:
			resutlStr = resutlStr+str(row)
		form.result.data = resutlStr
		form.query.data = queryStr
	return render_template('MAWSQuery.html', form=form)

@app.route('/get/<deviceID>', methods=['GET'])
def Get(deviceID):
	if(os.path.isfile('.\generated\DeviceList-a.xml') == False):
		return render_template("FileNotExist.html")

	doc = etree.parse(".\generated\DeviceList-a.xml")
	#xmlRoot = doc.getroot()
	deviceID = str(deviceID)
	lst = doc.findall('Device')
	idstr = ''
	device ={}
	for item in lst:
		idstr = str(item.find('id').text)
		if(deviceID==idstr):
			device['name'] = item.find('name').text
			device['id'] = idstr
			device['location'] = item.find('location').text
			device['type'] = item.find('type').text
			device['value'] = item.find('value').text
			return jsonify({'Device':device})
	else:
		return '''I can't find it'''


@app.route('/post', methods=['POST'])
def AddOneDevice():
	deviceNode = objectify.Element("Device")
	if request.json['name']:
		deviceNode.name = request.json['name']
		deviceNode.id = request.json['id']
		deviceNode.location = request.json['location']
		deviceNode.type = request.json['type']
		deviceNode.value = random.uniform(0,100)

		doc = etree.parse(".\generated\DeviceList-a.xml")
		xmlRoot=doc.getroot()
		xmlRoot.append(deviceNode)
		objectify.deannotate(xmlRoot)
		etree.cleanup_namespaces(xmlRoot)

		xmlfp = open('.\generated\DeviceList-a.xml', 'w')
		xmlstr = etree.tostring(xmlRoot, pretty_print=True, xml_declaration=True)
		xmlstr=xmlstr.decode("utf-8")
		xmlfp.write(xmlstr)
		xmlfp.close()
		return 'Added one device'
	else:
		return 'Self defined error'

@app.route('/delete/<deviceID>', methods=['DELETE'])
def Delete(deviceID):
	doc = etree.parse(".\generated\DeviceList-a.xml")
	xmlRoot = doc.getroot()
	deviceID = str(deviceID)
	lst = doc.findall('Device')
	idstr = ''
	device ={}
	flag = 0
	for item in lst:
		idstr = str(item.find('id').text)
		if(deviceID==idstr):
			device['name'] = item.find('name').text
			device['id'] = idstr
			device['location'] = item.find('location').text
			device['type'] = item.find('type').text
			device['value'] = item.find('value').text
			xmlRoot.remove(item)
			flag = 1
	if(flag==1):
		xmlfp = open('.\generated\DeviceList-a.xml', 'w')
		xmlstr = etree.tostring(xmlRoot, pretty_print=True, xml_declaration=True)
		xmlstr=xmlstr.decode("utf-8")
		xmlfp.write(xmlstr)
		xmlfp.close()
		return jsonify({'Deleted device':device})
	else:
		return '''I can't find a device with the id provided'''

@app.route('/put/<deviceID>', methods=['PUT'])
def Put(deviceID):
	deviceID = str(deviceID)
	doc = etree.parse(".\generated\DeviceList-a.xml")
	xmlRoot = doc.getroot()
	#code = root.xpath('//DeviceList/Device/id')
	lst = doc.findall('Device')
	idstr = ''
	device ={}
	flag = 0
	for item in lst:
		idstr = str(item.find('id').text)
		if(deviceID==idstr):
			if request.json['name']:
				item.find('name').text = request.json['name']
			if request.json['type']:
				item.find('type').text = request.json['type']
			if request.json['location']:
				item.find('location').text = request.json['location']				
			device['name'] = item.find('name').text
			device['id'] = deviceID
			device['location'] = item.find('location').text
			device['type'] = item.find('type').text
			device['value'] = item.find('value').text	
			xmlfp = open('.\generated\DeviceList-a.xml', 'w')
			xmlstr = etree.tostring(xmlRoot, pretty_print=True, xml_declaration=True)
			xmlstr=xmlstr.decode("utf-8")
			xmlfp.write(xmlstr)
			xmlfp.close()					
			return jsonify({'Updated Device':device})
	else:
		return '''I can't find a device of the id provided'''

if __name__ == '__main__':
    app.run(debug=True, port=int(9000))
    #manager.run()

'''
post json format:
{
    "id": "8",
    "location": "Wokingham1",
    "name": "st crispins",
    "type": "actutor"
}
Query format:
	"SELECT DISTINCT ?name
	       WHERE {?a MAWSDevice:hasLocation ?name.}"

DeviceLise xml file Name: DeviceList-a.xml
generated rdf file: DeviceList-a-rdf.xml
stylesheet file name: Devicelist-myxsl.xsl
schema file name: Device_schema.xsd
python main.py runserver --host 192.168.1.193
'''