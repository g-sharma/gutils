#!/usr/bin/python
#--------------------------------------------------------------------
#History: Written by Dr Soren Christensen and Gagan J Sharma on 29th of August 2011
#Version: 1.1.0
#
#To Do:  
# Handling exceptiongs.
#--------------------------------------------------------------------

"""
To do: If there is any problem with the internet or google is down, then what.
To do: This code has to be made more efficient, so that if sites names should be 
       more meaningfull. quickly changed the shad* something to Moansh Medical centre.
       But needs to revist this code. Get modular approach and add more modules for other purposes also.

"""

#ideal approach should be a modular one. will write this by the end of weekend.

import imaplib
import smtplib
import string
import time
import sys,time
import email
#from email.parser import HeaderParser
from datetime import datetime,timedelta



# Basic Email fields.
#----------------------------------
location = ["rmh","auckland","shdanrapapp01","st-vincent-sydney","royaladelaide","western","boxhill","austin","SCG","Royal-Perth-RAPID","RBWH","gosford.localdomain","FMC-adelaide","RN Sydney"] ##List of Location Subjects to be searched.

## For Servers
Missing_Servers=[] ## Empty list for Servers which has not responded today.
Server_Found=[] # Empty list for Servers which has sent an email today.

## For Pacs
PACS_Found=[]
Missing_PACS=[]


fromadd = 'gagan.testpython@gmail.com'
toadd= ['gaganjyoti@gmail.com','ssalinas@unimelb.edu.au','rapid.rmh@gmail.com']
#Subject = 'Daily Rapid Server Report'
username = 'gagan.testpython'
password = 'perfuser'


#Date and Time calculation

time = time.strftime("%a %b %d,%Y %-I:%M:%S %p",time.localtime(time.time()))
today = datetime.today()
today = today - timedelta(days=1)
dt = today.strftime('%d-%b-%Y')

#Email login and search opeartion.

#obj= imaplib.IMAP4_SSL('imap.gmail.com',993)
obj= imaplib.IMAP4_SSL('imap.gmail.com')
obj.login(username,password)
obj.select()

S_Message = "\n A.  Summary of email reporting for RAPID Servers\n"
S_Message += "---------------------------------------------------------\n"
S_Message += "1. Date of Reporting: " + dt +"\n"
S_Message += "2. Total Number of Servers to be reported: " + str(len(location)) + "\n"


Message = "\n\nArchived Email if found......\n"


for item in location:
	flag =0  
	print "Checking Email from:" + item
	typ,data = obj.search(None,'(SINCE %s) (Subject "%s")' %(dt,item,))
	temp=data[0].split(" ")
	if len(data[0])!=0:
		#server reported.
		
		#The below two lines are for changing the name of the Monash medical centre.
		test = cmp(item,'shdanrapapp01')
		if test == 0:
			item='Monash Medical Centre'
		
		Server_Found.append(item)
		resp, data_m = obj.FETCH(temp[len(temp)-1], '(RFC822)')
		mail = email.message_from_string(data_m[0][1])
		for part in mail.walk():
			# multipart are just containers, so we skip them
			if part.get_content_maintype() == 'multipart':
				continue

			# we are interested only in the simple text messages
			if part.get_content_subtype() != 'plain':
				continue
			payload = part.get_payload()
						
			## if the line is the multi line, then I need to split line and get the first line.
			payload.find("PACS up")
			if payload.find("PACS up") >= 0:
			   PACS_Found.append(item)
			else:
			   Missing_PACS.append(item)			

	elif len(data[0])==0:  ## if the string is empty or null string.
		
		flag = -1  ## if flag is -1, means this server has missed today an email.
		day_back_search = 1 
		not_find = True
		
		while not_find and day_back_search < 3: ## While there is no Email , Lets Search from past but not more than 16 days.
	   		print not_find	
			cutoff = today - timedelta(days=day_back_search)  ## Now rather than looking for only today, look since day_back_search value.
			dt1 = cutoff.strftime('%d-%b-%Y')
	   		
			typ,data = obj.search(None,'(SINCE %s) (Subject "%s")' %(dt1,item,)) ## Rather than using dt we are using dt1.
			if len(data[0]) == 0: # This is the way I am checking for the null string.
	  	 		day_back_search += 1
		 	else:  
				not_find = False #found the email. Lets get out of the loop.
				Message += "\nLast message from the "+ item+" server was recieved: " + str(day_back_search) + " day(s) ago"
					
		if not_find: #if loop cannot find the email in the specified time.
			day_back_search -= 1	
			Message += "\n No message recieved from the "+item+" server in the last: "+str(day_back_search)+" days"	
			
	if flag == -1:
		Missing_Servers.append(item) # Skipped email. Add it to the list of missing server.
		Missing_PACS.append(item)

 
# Missing server Report
if Missing_Servers:
	W_Message_Server = "\n\nB. Warning Generated For Servers\n"
	W_Message_Server +=  "---------------------------------\n"
	
	for item in Missing_Servers:
		M_Index= Missing_Servers.index(item) 
		M_Index+=1
		W_Message_Server += str(M_Index)+". Server down at: " + item + "\n"
else:
	W_Message_Server = "\nB. No Warning for Servers Today\n"

# Server repsponse Report

if Server_Found:
	F_Message = "\n\nD. List of Server response today\n"
	F_Message += "----------------------------------------------\n"
	for item in Server_Found:
		F_Index = Server_Found.index(item)
		F_Index +=1
		F_Message+= str(F_Index)+". Server up at: "+item+".\n"

# Missing Pacs Report
if Missing_PACS:
	W_Message_PACS ="\n\n C. Warning Generated for PAC(S) of the respective location\n"
	W_Message_PACS +=   "-----------------------------------------------------------\n"
	for item in Missing_PACS:
		P_Index=Missing_PACS.index(item)
		P_Index+=1
		W_Message_PACS +=str(P_Index)+". PACS down at: "+item+".\n"  
else:
	W_Message_PACS ="\nC. No PACS Warning Today\n"

if PACS_Found:
	F_Message_PACS="\n\n  C. List PAC(S) response today\n"
	F_Message_PACS+=   "-----------------------------------------------\n"
	for item in PACS_Found:
		P_Index=PACS_Found.index(item)
		P_Index+=1
		F_Message_PACS +=str(P_Index)+". PACS up at: "+item+".\n" 



S_Message +="3. Number of Servers reported: "+ str(len(Server_Found))+"\n"
S_Message +="4. Number of Missing Server report: "+str(len(Missing_Servers))+"\n"
S_Message +="---------------------------------------\n\n"

Subject = str(len(Missing_Servers))+" -Servers missing out of Total:"+ str(len(Server_Found))+" Servers"

PS_NOTE= "\n\n\n**** P.S If any server is down, no warning message is generated for the corresponding PACS location. So please make sure, PACS is running, once the server is back again"


Body = string.join((
        "From: %s" % fromadd,
        "To: %s" % toadd,
        "Subject: %s" %  Subject + "-" + time ,
        "",
        S_Message+W_Message_Server+W_Message_PACS +F_Message+F_Message_PACS+Message+PS_NOTE  
						
        ), "\r\n")


server = smtplib.SMTP('smtp.gmail.com:587')  
server.starttls()  
server.login(username,password)  
server.sendmail(fromadd,toadd,Body)  
server.quit()

print('Email sent to %s' %toadd)
print "Please check your inbox...."
