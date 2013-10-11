#!/usr/bin/env python

import datetime
import os
import subprocess
import time
import sys
from config import *

script_start_time = time.time()


def increasePagecountGetState(username, pagenumber, jobtime):

    state = db_cursor.execute( 'SELECT pagecount, pagequota, lastjob FROM users where username = ?', ( username, ) ).fetchone();
    
    if state == None:
    
        db_cursor.execute( 'INSERT INTO users (username, pagequota, pagecount, lastjob ) VALUES (?, ?, ?, ? );', ( username, default_page_quota, pagenumber, jobtime ) );
        print "Creating user %s with quota=%d, pages=%d" % (username, default_page_quota, pagenumber)
        return ( username, pagenumber, default_page_quota )
    
    else:
    
        if jobtime > state[2] or (jobtime >= state[2] and (time.time() > script_start_time+60)):
        
            db_cursor.execute( 'UPDATE users SET pagecount = pagecount + ?, lastjob = ? WHERE username = ?;', ( pagenumber, jobtime, username ) );
            print "Updating user %s with pages+=%d" % (username, pagenumber)
            return ( username, state[0] + pagenumber, state[1] );
        
        else:
        
            return ( username, state[0], state[1] );


pagelog   = open( cups_pagelog_location, 'r' )

while True:

    line = pagelog.readline()

    if len( line ) == 0:

        if os.path.exists( cups_pagelog_location ):

            if os.fstat( pagelog.fileno() ).st_ino != os.stat( cups_pagelog_location ).st_ino or \
               os.fstat( pagelog.fileno() ).st_dev != os.stat( cups_pagelog_location ).st_dev:

                pagelog.close()
                pagelog = open( cups_pagelog_location, 'r' )
                
                continue

        db_conn.commit();
        
        time.sleep( sleep_duration )

    else:

        line = line.split()
        
        if len( line ) >= 12:
        
            if line[5].isdigit() and line[6].isdigit():
            
                #TODO take time zone into account
                log_username = line[1]
                log_pages    = int( line[6] )
                log_datetime = int( datetime.datetime.strptime( line[3], '[%d/%b/%Y:%H:%M:%S' ).strftime("%s") )
                
                username, pagecount, pagequota = increasePagecountGetState( log_username, log_pages, log_datetime )
                
                if pagecount >= pagequota:
                    print "Disabling user %s with quota=%d, pages=%d" % (username, pagequota, pagecount)
                    disablePrinting( username )
