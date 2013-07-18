from wsgiref.simple_server import make_server
from wsgiref.util          import setup_testing_defaults
from config                import *


html_header = []
html_header.append( "<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Strict//EN\" \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd\">" )
html_header.append( "<html>" )
html_header.append( "<head>" )
html_header.append( "</head>" )
html_header.append( "<body>" )

html_footer = []
html_footer.append( "</body>" )
html_footer.append( "</html>" )


def application(environ, start_response):

    setup_testing_defaults(environ)

    status = '200 OK'
    headers = [ ('Content-type', 'text/html') ]

    start_response(status, headers)

    html = html_header
    
    for entry in db_cursor.execute('SELECT * FROM users ORDER BY username ASC'):
        print html.append( str( entry ) )
        
    html.extend( html_footer )
    
    return html
    

httpd = make_server('', webinterface_port, application)
print "Serving on port 8000..."
httpd.serve_forever()
