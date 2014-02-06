#!/usr/bin/python
#--------------------------------------------------------------------
#History: Re written by Gagan J Sharma 5th Nov 2012 
#Version: 2.1.0
#
#
#--------------------------------------------------------------------

"""
The previous version is not modular. 
The idea is to rewrite for longer working and shelf life of the code.      


"""

###################################################
# Required import

import imaplib
import smtplib
import string
import time
import sys,time
import email
import datetime
from datetime import timedelta

#A.
###################################################

# Location Array
# 1. Every Location has to be in double quotes
# 2. Add new location if required in to the array. 

location = ["rmh","auckland","shdanrapapp01","st-vincent-sydney","royaladelaide","western","boxhill","Austin","SCG","Royal-Perth-RAPID","RBWH","gosford.localdomain","FMC-adelaide","EPWORTH","RNS"] 

#B. 
###################################################
# 1. Email address of Recipients, sender.
# 2. Password the account being used to send an email.  

fromadd = 'gagan.testpython@gmail.com'
toadd= ['gaganjyoti@gmail.com','rapid.rmh@gmail.com','ssalinas@unimelb.edu.au']
username = 'gagan.testpython'
password = 'perfuser'

#C.
###################################################
#1. Missing Servers :List for Missing Servers.
Missing_Servers=[] 

#2. Server Found    :List of Servers Found.
Server_Found=[] 


#D.
###################################################
#1. PACS responding to our Local test ping.

PACS_Found=[]

#2. PACS which we cannot ping

Missing_PACS=[]

#D.
##################################################
#1. Disk Warning i.e. Rapid computers where the hard drive is filling to 90% Mark.

DISK_warning=[] 

#E.
#################################################
#1. Calculating date and time

nowGoogle = datetime.datetime.now() - timedelta(days=1);  ## this is weird.
now = datetime.datetime.now();
date_time = now.strftime("%Y-%m-%d %H:%M");
only_date = nowGoogle.strftime("%d-%b-%Y");


def init_message():
	print "#######################################################################"
	print "Starting RAPID comprehensive daily Heart Beat reporting on:"+ date_time;
	

def read_message_assign(mail,item):
	
	for part in mail.walk():
   		if part.get_content_type() == 'text/plain':
        		payload = part.get_payload() 
		payload.find("PACS up")
        if payload.find("PACS up") >= 0:
         	PACS_Found.append(item)
        else:
         	Missing_PACS.append(item)            
        
        if payload.find("Disk will be full soon") >= 0 :
            DISK_warning.append(item)
            
	
	
def check_every_location():
	# Login in to gmail. I tried to login via a function and passing object but that failed.
	
	obj= imaplib.IMAP4_SSL('imap.gmail.com')
	obj.login(username,password)
	obj.select()
	for site in location:
		typ,data = obj.search(None,'(SINCE %s) (Subject "%s")' %(only_date,site,))
		temp=data[0].split(" ")
		if len(data[0])!=0:
				print "Checking Location:"+site
				Server_Found.append(site)
				resp, data_m = obj.FETCH(temp[len(temp)-1], '(RFC822)')
				message = email.message_from_string(data_m[0][1])
				read_message_assign(message,site)
		if len(data[0])==0:
				print "Misssing Locatoin:"+site
				Missing_Servers.append(site)
				DISK_warning.append(site)
				Missing_PACS.append(site)
			
		

def summary_message():

	S_Message = "\n Summary of email reporting for RAPID Servers\n"
	S_Message += "---------------------------------------------------------\n"
	S_Message += "1. Date of Reporting: " + date_time +"\n"
	S_Message += "2. Total Number of Servers to be reported: " + str(len(location)) + "\n"
	S_Message +="3. Number of Servers reported: "+ str(len(Server_Found))+"\n"
	S_Message +="4. Number of Missing Server(s): "+str(len(Missing_Servers))+"\n"
	S_Message +="5. Number of Sites with Disk Warning:"+str(len(DISK_warning))+"\n"
	S_Message +="---------------------------------------\n\n"	   
	return S_Message;

def server_up_running():
   if len(Server_Found)!=0:
    	F_Message = "\n\n List of Server response today\n"
     	F_Message += "----------------------------------------------\n"
     	for item in Server_Found:
	        F_Index = Server_Found.index(item)
	        F_Index +=1
	        F_Message+= str(F_Index)+". Server up at: "+item+".\n"
   else:
   	    F_Message="\n\n No Server Up and Running today\n ";
   	    F_Message += "----------------------------------------------\n"
   return F_Message	    
   
def down_servers():
	if len(Missing_Servers)!=0:
	    W_Message_Server = "\n\n Warning Generated For Servers\n"
	    W_Message_Server +=  "------------------------------------------\n"
	    for item in Missing_Servers:
        	M_Index= Missing_Servers.index(item) 
	        M_Index+=1
	        W_Message_Server += str(M_Index)+". Server down at: " + item + "\n"
	else:
		W_Message_Server = "\n No Warning for Servers Today\n"
		W_Message_Server +=  "-----------------------------------------------\n"
	return W_Message_Server

def pacs_summary():
	
	if len(Missing_PACS)!=0:
		W_Message_PACS ="\n\n Warning Generated for missing PAC(S)\n"
		W_Message_PACS +=   "-----------------------------------------------------------\n"
		for item in Missing_PACS:
			P_Index=Missing_PACS.index(item)
			P_Index+=1
			W_Message_PACS +=str(P_Index)+". PACS down at: "+item+".\n"  
	else:
		W_Message_PACS ="\n No PACS Warning Today\n"
		W_Message_PACS +="---------------------------------------------------\n"
	return W_Message_PACS

def disk_warning():
	
	if len(DISK_warning) !=0:
		DISK_warning_message="\n\nDisk Warning(S) response today\n"
		DISK_warning_message+=   "-----------------------------------------------\n"
    	for item in DISK_warning:
	        P_Index=DISK_warning.index(item)
	        P_Index+=1
	        DISK_warning_message +=str(P_Index)+". Disk Warning at: "+item+".\n"
	        
	if len(DISK_warning) ==0:  #Why my else is not working.So stupid..... 
		DISK_warning_message ="\n DISK Under Construction\n"
		DISK_warning_message +='-----------------------------------\n'    
	return DISK_warning_message
 
 
def create_send_email():
	Subject = str(len(Missing_Servers))+" -Servers missing out of Total:"+ str(len(location))+" Servers"
	PS="\n\n\n\n Note:The site shdanrapapp01 is Monash Medical Centre"
	   	
	Body = string.join((
        "From: %s" % fromadd,
        "To: %s" % toadd,
        "Subject: %s" %  Subject + "-" + date_time,
        "",
        summary_message()+server_up_running()+ down_servers()+pacs_summary()+disk_warning()+PS
                        
        ), "\r\n")

	server = smtplib.SMTP('smtp.gmail.com:587')  
	server.starttls()  
	server.login(username,password)  
	server.sendmail(fromadd,toadd,Body)  
	server.quit()
		
	print('Email sent to %s' %toadd)
	print "Please check your inbox...."
		
		
def main():
	init_message();
	check_every_location();
	create_send_email();
	
main();
