import smtplib
import os
import datetime
from datetime import date
from optparse import OptionParser


# Here are the email package modules we'll need
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email import Encoders

def buildMessage(options):
    msg = MIMEMultipart()
    dt=datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")
    msg['Subject'] = 'RNS Rapid Images'+':'+dt
    msg['From'] = options.user
    msg['To'] = options.recipients
    msg.preample = 'Your mail attacment follows'
    return msg;
    
def attachFileToPart(option):

    fp = open(option, 'rb')
    part = MIMEBase('application', "octet-stream")
    part.set_payload( fp.read() )
    fp.close()
    Encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(option))
    return part;

def attachFile(file):
    
    fp = open(file, 'rb')
    part = MIMEBase('application', "octet-stream")
    part.set_payload( fp.read() )
    fp.close()
    Encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(file))
    return part;

def doTransport(msg, options):
    # Send the email via our own SMTP server.
    s = smtplib.SMTP('smtp.gmail.com',587)
    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login(options.user,options.password)
    s.sendmail(options.user, options.recipients.split(','), msg.as_string())
    s.quit()

def main():
    parser = OptionParser()
    parser.add_option("-u","--user", dest="user", help="Username for the mail account")
    parser.add_option("-p","--password", dest="password", help="Password for the mail account")
    parser.add_option("-r","--recipients", dest="recipients", help="Recipient email addresses (comma separated)")
    parser.add_option("-f","--file",dest="file", help="Path to the file to attach")
    
    (options, args) = parser.parse_args()
    
    if not options.user or not options.password:
        parser.error("user and password are required")
    if not options.recipients:
        parser.error("At least one recipient must be defined")
    if not options.file:
        parser.error("You must specify a file attachment")

    msg = buildMessage(options);
    list=options.file.split(',');
    
    for each in list:
        print "Attaching "+each+" to an email"	
        part = attachFileToPart(each);
        msg.attach(part)

    doTransport(msg,options);

main()

