from wsgiref.simple_server import make_server
from wsgiref.util          import setup_testing_defaults


def application(environ, start_response):

    setup_testing_defaults(environ)

    status = '200 OK'
    headers = [ ('Content-type', 'text/plain') ]

    start_response(status, headers)

    html = ["firstline\n"]
    html.append("secondline\n")
    
    return ret


httpd = make_server('', 8000, application)
print "Serving on port 8000..."
httpd.serve_forever()
