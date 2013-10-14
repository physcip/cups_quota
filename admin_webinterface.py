#!/usr/bin/env python

from cgi                   import parse_qs, escape
import re

import sys
import os
import datetime

if os.path.dirname(__file__) != '':
    sys.path.append(os.path.dirname(__file__))
    os.chdir(os.path.dirname(__file__))

from config                import *


html_header = \
"""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html>
    <head>
        <style type="text/css">
            .pageinput{ width:3em }
        </style>
    </head>
    <body>
"""

html_footer = \
"""
    </body>
</html>
"""


def user_interface(env, start_response):

    setup_testing_defaults(env)
    
    try:
      request_body_size = int( env.get( 'CONTENT_LENGTH', 0 ) )
    except ValueError:
      request_body_size = 0
      
    request_body = env['QUERY_STRING']
    d = parse_qs( request_body )
    
    username = escape( d.get( 'username', [''] )[0] )
    pagecount, pagequota = ('', '')
    current_time = datetime.datetime.now()
    first_of_next_month = datetime.datetime(current_time.year +current_time.month//12, (current_time.month+1) % 12, 1, 0, 0, 0, 0)

    if len( username ) > 0:
    
        try:
            pagecount, pagequota = db_cursor.execute( 'SELECT pagecount, pagequota FROM users WHERE username = ?;', [username] ).fetchone()
            no_such_user = False
        except:
            no_such_user = True
    else:
        no_such_user = True

    status = '200 OK'
    headers = [ ('Content-type', 'text/html') ]

    start_response( status, headers )
    
    html = []
    html.append( html_header )
    html.append( """<form method="get">""" )
    html.append( """<p>Please input your username to query your leftover page quota.</p>""" )
    html.append( """<input type="text" name="username" value="%s"/>""" % (username)	 )
    if (pagecount != '' and pagequota != ''):
        html.append( """<p>User <b>%s</b> has <b>%s</b> pages left for this month.</p>""" % (username, pagequota-pagecount) )
        html.append( "<p>Your quota will be increased by %d pages on %s.</p>" % ( monthly_pagenumber_decrease if int(pagecount)-monthly_pagenumber_decrease>0 else pagecount, first_of_next_month.strftime('%Y-%m-%d')))
    elif (no_such_user and len(username) > 0):
        html.append( """<p>User <b>%s</b> is not in our system.</p>""" % (username) )
    html.append( """</form>""" )
    
    html.append( html_footer )
    
    return html


def admin_interface(env, start_response):

    setup_testing_defaults(env)
    
    try:
      request_body_size = int( env.get( 'CONTENT_LENGTH', 0 ) )
    except ValueError:
      request_body_size = 0
      
    request_body = env['wsgi.input'].read( request_body_size )
    d = parse_qs( request_body )
    
    username = escape( d.get( 'username', [''] )[0] )

    try:
        pagecount = int( d.get( 'pagecount', [''] )[0] )
    except ValueError:
        pagecount = 0

    try:
        pagequota = int( d.get( 'pagequota', [''] )[0] )
    except ValueError:
        pagequota = 0
    
    if len( username ) > 0:
    
        db_cursor.execute( 'UPDATE users set pagequota = ?, pagecount = ? WHERE username = ?;', ( pagequota, pagecount, username ) );
        db_conn.commit()
        if pagequota > pagecount:
            enablePrinting(username)
        else:
            disablePrinting(username)

    status = '200 OK'
    headers = [ ('Content-type', 'text/html') ]

    start_response( status, headers )
    
    html = []
    html.append( html_header )
    
    html.append( """<table>""" )
    
    for entry in db_cursor.execute('SELECT username, pagecount, pagequota FROM users ORDER BY username ASC'):
    
        if entry[1] > entry[2]:
            html.append( """<tr style='background-color: red'>""" )
        else:
            html.append( """<tr>""" )
        
        html.append( """<td>""" )
        html.append( str( entry[0] ) )
        html.append( """</td>""" )
        
        html.append( """<td>""" )
        html.append( """<form method="post">""" )
        html.append( """<input type="text" name="pagecount" value="%s" class="pageinput"> / <input type="text" name="pagequota" value="%s" class="pageinput"> """ % ( str( entry[1] ), str( entry[2] ) ) )
        html.append( """<input type="hidden" name="username" value="%s">""" % ( str( entry[0] ) ) )
        html.append( """<input type="submit" value="save">""" )
        html.append( """</form>""" )
        html.append( """</td>""" )
        
        html.append( """</tr>""" )
        
    html.append( """</table>""" )
    
    html.append( html_footer )

    return html
    
    
def not_found(env, start_response):

    start_response('404 NOT FOUND', [('Content-Type', 'text/plain')])
    return ['Not Found']
    

def application(env, start_response):
    
    urls = [
        (r'^$', user_interface),
        (r'admin/?$', admin_interface)
    ]

    path = env.get('PATH_INFO', '').lstrip('/')
    
    for regex, callback in urls:
    
        match = re.search(regex, path)

        if match is not None:
        
            env['myapp.url_args'] = match.groups()
            return callback(env, start_response)
            
    return not_found(env, start_response)
    
if __name__ == '__main__':

	from wsgiref.simple_server import make_server
	from wsgiref.util          import setup_testing_defaults
	httpd = make_server( '', webinterface_port, application )
	print "Serving on port 8000..."
	httpd.serve_forever()

else:
	def setup_testing_defaults(env):
		pass
