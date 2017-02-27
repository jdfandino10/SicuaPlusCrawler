import requests, zipfile, io
import os
import sys
import shutil
import getpass
from bs4 import BeautifulSoup
from requests.auth import HTTPBasicAuth
from selenium import webdriver
SICUA='https://sicuaplus.uniandes.edu.co'

def trade_spider(courseUrl, assignmentName, username, password):
	num=0
	courseId=getCourseId(courseUrl)
	driver = webdriver.PhantomJS(executable_path='.\\node_modules\\phantomjs\\lib\\phantom\\bin\\phantomjs.exe') 
	s=requests.Session()
	s.post(SICUA+'/webapps/login/',{'user_id':username,'password':password})
	driver.get(SICUA+'/webapps/login/')
	driver.find_element_by_id('user_id').send_keys(username)
	driver.find_element_by_id('password').send_keys(password)
	form = driver.find_element_by_name('login')
	form.submit()
	url=(SICUA+courseUrl)
	while True:
		print('Url: '+url)
		source_code=s.get(url)
		plain_text=source_code.text
		soup = BeautifulSoup(plain_text, "html.parser",from_encoding="iso-8859-1")
		table = soup.find('table',{'title':'Intentos de este curso que necesitan calificación'})
		table2 = table.find('tbody')
		table3 = table2.findAll('tr')
		for row in table3:
			assignment=row.findAll('td')[1]
			if assignment.contents[0].strip()==assignmentName:
				src = row.find('a',{'class':'gradeAttempt'})
				groupAttemptId=src.get('groupattemptid')
				attemptId=src.get('attemptid')
				link = gradeAttemptURL(attemptId,groupAttemptId,courseId)
				link = s.get(SICUA+link).url
				print('link: '+link)
				driver.get(link) 
				next_src_code=driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
				next_text=next_src_code.encode(sys.stdout.encoding, errors='replace')
				num+=1
				download(s,next_text,num)
		siguiente = soup.find('a',{'title':'Página siguiente'})
		if siguiente is None:
			break
		else:
			url=SICUA+siguiente.get('href')
	print('Se descargaron '+str(num)+' archivos')

def gradeAttemptURL(attemptId, groupAttemptId,courseId):    
	return ('/webapps/gradebook/do/instructor/performGrading?course_id='+courseId+
	'&source=cp_gradebook_needs_grading&cancelGradeUrl=%2Fwebapps%2Fgradebook%2Fdo%2Finstructor'+
	'%2FviewNeedsGrading%3Fcourse_id%3D_84600_1&mode=invokeFromNeedsGrading&viewInfo=Necesita+calificaci%C3%B3n'+
	'&attemptId='+attemptId+'&groupAttemptId='+groupAttemptId)

def getCourseId(courseUrl):
	return courseUrl.split("=")[-1]

def download(s,pageText, num):
	soup = BeautifulSoup(pageText, "html.parser",from_encoding="iso-8859-1")
	file_name = soup.find('a',{'class':'genericFile'}).text.replace(" ","").replace("\n","")
	button = soup.find('a',{'class':'dwnldBtn'})
	link = SICUA + button.get('href')
	print('File name: '+file_name)
	file_name='('+str(num)+')'+file_name
	print('Downloading from: '+link)
	r = s.get(link, stream=True)
	with open(file_name, 'wb') as f:
		for chunk in r.iter_content(chunk_size=1024):
			if chunk: # filter out keep-alive new chunks
				f.write(chunk)
	print('Se proceso '+file_name)


url = input("Insertar link de sicua con listado de ejercicios: ")
hmk = input("Insertar el nombre de la tarea: ")
usr = input("Insertar nombre de usuario: ")
pswd = getpass.getpass("Ingresa clave: ")
trade_spider(url, hmk, usr, pswd)
#/webapps/gradebook/do/instructor/viewNeedsGrading?course_id=_84600_1
#Taller Quiz 6 - Redes de Petri