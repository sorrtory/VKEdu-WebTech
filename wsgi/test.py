# This is a test WSGI application that handles GET and POST requests,
# extracts parameters from the query string or request body, and returns
# them in an HTML response.

# To run with gunicorn:
# gunicorn -w 1 -b 127.0.0.1:8081 test:simple_app

# Example curl commands to test the WSGI app:

# Test GET request with parameters
# Access: http://127.0.0.1:8081/?name=Alice&age=30
# Or use curl:
# curl "http://127.0.0.1:8081/?name=Alice&age=30"

# Test POST request with parameters
# curl -X POST -d "name=Bob&age=25" http://127.0.0.1:8081/

from urllib.parse import parse_qs

def simple_app(environ, start_response):

    method = environ.get('REQUEST_METHOD', 'GET')
    if method == 'GET':
        params = parse_qs(environ.get('QUERY_STRING', ''))
    elif method == 'POST':
        try:
            size = int(environ.get('CONTENT_LENGTH', 0))
        except (ValueError, TypeError):
            size = 0
        body = environ['wsgi.input'].read(size).decode('utf-8')
        params = parse_qs(body)
    else:
        params = {}

    response_body = "<h1>Parameters:</h1><ul>"
    for key, values in params.items():
        for value in values:
            response_body += f"<li>{key}: {value}</li>"
    response_body += "</ul>"

    status = '200 OK'
    headers = [('Content-type', 'text/html; charset=utf-8')]
    start_response(status, headers)
    return [response_body.encode('utf-8')]

