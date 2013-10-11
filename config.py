import sqlite3
import subprocess

cups_pagelog_location       = './sample_page_log'
default_page_quota          = 600
initial_page_number         = 500
monthly_pagenumber_decrease = 100
sleep_duration              = 10 #in seconds

def disablePrinting(username):
    subprocess.call( ['touch', 'disable_' + username] )

def enablePrinting(username):
    subprocess.call( ['touch', 'enable_' + username] )

webinterface_port        = 8000

db_conn   = sqlite3.connect( 'db/print_quota.db' )
db_cursor = db_conn.cursor()
