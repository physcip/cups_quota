import sqlite3
import subprocess
import smtplib
import email.mime.text

#cups_pagelog_location       = './sample_page_log'
cups_pagelog_location       = '/var/log/cups/page_log'
default_page_quota          = 600
initial_page_number         = 400
monthly_pagenumber_decrease = 100
sleep_duration              = 10 #in seconds

ldap_node = '/LDAPv3/purple.physcip.uni-stuttgart.de'
ldap_user = 'phyregger'
ldap_password = 'abcdef'
noprinting_group = 'noprinting'

smtp_server = 'mailrelay.uni-stuttgart.de'
mail_from = 'root@robert.physcip.uni-stuttgart.de'
error_recipient = 'cip-service@physcip.uni-stuttgart.de'

def error_msg(msg):
    print "Send email to %s" % error_recipient
    s = smtplib.SMTP(smtp_server)
    s.sendmail(mail_from, error_recipient, "From: %s\nTo: %s\nSubject: CUPS Quota: User enable/disable error\n\n%s" % (mail_from, error_recipient,msg))
    print msg

def disablePrinting(username):
    print "Disabling printing for %s" % username
    try:
        subprocess.check_output(['dseditgroup', '-o', 'edit', '-n', ldap_node, '-u', ldap_user, '-P', ldap_password, '-a', username, '-t', 'user', noprinting_group], stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        error_msg(e.output + "\n\n" + str(e).replace(ldap_password, 'XXXXXXXX'))

def enablePrinting(username):
    print "Enabling printing for %s" % username
    try:
        subprocess.check_output(['dseditgroup', '-o', 'edit', '-n', ldap_node, '-u', ldap_user, '-P', ldap_password, '-d', username, '-t', 'user', noprinting_group], stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        error_msg(e.output + "\n\n" + str(e).replace(ldap_password, 'XXXXXXXX'))

webinterface_port        = 8000

db_conn   = sqlite3.connect( 'db/print_quota.db' )
db_cursor = db_conn.cursor()
