import time
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email import errors
import sys

class sendMail:
    """
        Class to send a Logfile via Mail.
    """
    def __init__(self, smtp: str, port: int, logfile = "vpnconnection.log"):
        """
        Initiate the Class, Class requires:
        smtp = SMPTP Server to send the email, type = String
        port = Port of the SMTP Server, Type Int
        File "emailData.txt" looks like:
        Sender Email
        PW
        Receiver Addresse
        OPTIONAL: logfile = File witch you want to send, default is "vpnconnection.log"
        """
        if logfile.isspace():
            logfile = "vpnconnection.log"
        self.email_data = []
        self.logfile = logfile
        self.count = 0
        self.up = 0
        self.percentage = 0
        self.session = [smtp, port]
    
    def getEmailData(self):
        """
        Function to get User Email, Password and Receiver Addresse out of a file.
        File need to be in this format: "USEREMAIL,USER-PW,RECEIVERADDR"
        Saves the Data in a list
        """
        try:
            with open('emailData.txt', 'r') as f:
                for lines in f.readlines():
                    self.email_data.append(lines.rstrip('\n'))
        except OSError:
            print("Could not open file with login informations, maybe is the file emailData.txt empty")

    def getPercentage(self):
        try:
            summary = self.up+self.count
            online = 0.00
            offline = 0.00
            if self.up != 0:
                online = float(100)/summary*self.up
            if self.count != 0:
                offline = float(100)/summary*self.count
            txt = "UP: {0:.2f}%\nDown: {1:.2f}%"
            return (txt.format(online,offline))
        except(ArithmeticError, ZeroDivisionError):
            return ("Down: Unknown\nUp: Unknown")

    def getStats(self):
        """
        Counts how many times the Status "DOWN" is in the file "vpnconnection.log".
        """
        try:
            self.count = 0
            with open(self.logfile, 'r') as f:
                for lines in f.readlines():
                    timestamp, loglevel, fw_name, intern_name, status = lines.split(',')
                    status = status.strip()
                    if status.lower() == "down":
                        self.count += 1
                    if status.lower() == "up":
                        self.up += 1
        except OSError:
            print("Could not open logfile!")

    def clearLogfile(self):
        """
        Deletes the Content of a file
        """
        try:
            with open(self.logfile, 'w') as f:
                f.truncate()
        except OSError:
            print("Could not cleaer Logfile")

    def sendEmail(self):
        """
        Function that sends an Email. Function gets Sender, PW and Receiver from email_data list wich will be read from file with the function "getEmailData"
        """
        try:
            percent = self.getPercentage()
            if self.logfile == "vpnconnection.log":
                mail_content = "Automatic Notification:\nDowns: "+str(self.count)+"\nStatus Up: "+str(self.up)+"\n"+percent
                mail_subject = "Logfile Barracuda Firewalls"
            else:
                mail_content = "File is attached\n\nHave a nice Day!\n\nBest Regards!\nMario Lovric"
                mail_subject = "Report: "+self.logfile
            
            attach_file_name = self.logfile
            message = MIMEMultipart()
            message['From'] = self.email_data[0]
            message['To'] = self.email_data[1]
            message['Subject'] = self.email_data[2]
            message.attach(MIMEText(mail_content, 'plain'))
            attach_file = open(attach_file_name, 'rb')
            payload = MIMEBase('application','octate-stream')
            payload.set_payload((attach_file).read())
            encoders.encode_base64(payload)
            payload.add_header('Content-Decomposition', 'attachment', filename=attach_file_name)
            message.attach(payload)
            session = smtplib.SMTP(self.session[0], self.session[1])
            session.starttls()
            session.login(self.email_data[0], self.email_data[1])
            text = message.as_string()
            session.sendmail(self.email_data[0], self.email_data[2], text)
            session.quit()
            if attach_file_name == "vpnconnection.log":
                self.clearLogfile()
        except errors.MessageError:
            print("Message Error")
        except:
            print("Error occured in methode sendEmail()")
 
    def sending(self):
        self.getEmailData()
        if self.logfile == "vpnconnection.log":
            self.getStats()
        self.sendEmail()

def main():
    for i in range(len(sys.argv)):
        if len(sys.argv) == 1:
            x = sendMail("smtp.cablelink.at", 587, 'vpnconnection.log')
            x.sending()
            break
        if i == 0:
            continue
        x = sendMail("smtp.cablelink.at", 587, sys.argv[i])
        x.sending()

main()

