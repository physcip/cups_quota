import datetime
from config import *

def increasePagecountMonthly():
    current_time = datetime.datetime.now()
    current_month = current_time.month
    current_year = current_time.year
    this_month = datetime.datetime(current_year, current_month, 1, 0, 0, 0, 0)
    prevupdate = int(this_month.strftime("%s"))
    lastupdate = int( db_cursor.execute( 'SELECT value FROM config WHERE key == "lastupdate";' ).fetchone()[0] )
    if (lastupdate < prevupdate):
        # Increase pagequota for everyone by 100 if pagequota won't exceed 600, else set it to 600
        db_cursor.execute( 'UPDATE config SET value = ? WHERE key == "lastupdate";', (prevupdate, ) )
        db_cursor.execute( 'UPDATE users SET pagequota = CASE WHEN pagequota + 100 > 600 THEN 600 ELSE pagequota + 100 END;' )

increasePagecountMonthly()
db_conn.commit()
