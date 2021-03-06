#!/usr/bin/python

import sqlite3
import subprocess
import smtplib
import email.mime.text

# Read settings from config file
from ConfigParser import RawConfigParser
settings = RawConfigParser()
settings.read("cups_quota.conf")

cups_pagelog_location  = settings.get("general", "cups_pagelog_location")
default_page_quota = settings.getint("general", "default_page_quota")
initial_page_number = settings.getint("general", "initial_page_number")
monthly_pagenumber_decrease = settings.getint("general", "monthly_pagenumber_decrease")
color_factor = settings.getfloat("general", "color_factor")
sleep_duration = settings.getfloat("general", "sleep_duration")

ldap_server = settings.get("ldap", "server")
ldap_base = settings.get("ldap", "base")
ldap_user = settings.get("ldap", "user")
ldap_password = settings.get("ldap", "password")
noprinting_group = settings.get("ldap", "noprinting_group")
ldap_uid_attribute = settings.get("ldap", "uid_attribute")

smtp_server = settings.get("mail", "smtp_server")
mail_from = settings.get("mail", "from")
error_recipient = settings.get("mail", "error_recipient")

def error_msg(msg):
    print "Send email to %s" % error_recipient
    s = smtplib.SMTP(smtp_server)
    s.sendmail(mail_from, error_recipient, "From: %s\nTo: %s\nSubject: CUPS Quota: User enable/disable error\n\n%s" % (mail_from, error_recipient,msg))
    print msg

webinterface_port = 8000

db_conn   = sqlite3.connect( 'db/print_quota.db' )
db_cursor = db_conn.cursor()
