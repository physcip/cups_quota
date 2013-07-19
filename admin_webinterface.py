from wsgiref.simple_server import make_server
from wsgiref.util          import setup_testing_defaults
from cgi                   import parse_qs, escape
from config                import *


html_header = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html>
    <head>
        <style type="text/css">
            input { width:3em }
        </style>
    </head>
    <body>
        <b>General:</b> <input type="button" value="test" onclick="alert('test')">
        <hr>
"""

html_footer = """
    </body>
</html>
"""


def user_quota_list():

    html = []
    
    html.append( "<table>" )
    
    for entry in db_cursor.execute('SELECT username, pagecount, pagequota FROM users ORDER BY username ASC'):
    
        html.append( "<tr>" )
        
        html.append( "<td>" )
        html.append( str( entry[0] ) )
        html.append( "</td>" )
        
        html.append( "<td>" )
        html.append( "<form action=\"admin_webinterface.py\" method=\"post\">" )
        html.append( "<input type=\"text\" name=\"pagecount\" value=\"%s\"> / <input type=\"text\" name=\"pagequota\" value=\"%s\"> " % ( str( entry[1] ), str( entry[2] ) ) )
        html.append( "<input type=\"hidden\" name=\"username\" value=\"%s\">" % ( str( entry[0] ) ) )
        html.append( "<input type=\"submit\" value=\"save\">" )
        html.append( "</form>" )
        html.append( "</td>" )
        
        html.append( "</tr>" )
        
    html.append( "</table>" )

    return html


def application(env, start_response):

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

    status = '200 OK'
    headers = [ ('Content-type', 'text/html') ]

    start_response( status, headers )
    
    html = []
    html.append( html_header )
    
    html.extend( user_quota_list() )
    
    html.append( html_footer )
    
    return html
    

httpd = make_server( '', webinterface_port, application )
print "Serving on port 8000..."
httpd.serve_forever()
