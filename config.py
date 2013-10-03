import sqlite3

cups_pagelog_location    = './sample_page_log'
default_page_quota       = 400
disable_printing_command = [ 'touch', 'user_disabled' ] #command and one entry per argument
sleep_duration           = 10 #in seconds

webinterface_port        = 8000

db_conn   = sqlite3.connect( 'db/print_quota.db' )
db_cursor = db_conn.cursor()
