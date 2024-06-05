import json
from wsgiref.simple_server import make_server
from datetime import datetime
import pytz
from tzlocal import get_localzone

def application(env, start_response):
    path = env.get('PATH_INFO', '')
    method = env.get('REQUEST_METHOD', 'GET')
    
    if method == 'GET' and path.startswith('/'):
        tz_name = path[1:] if len(path) > 1 else 'GMT'
        try:
            current_time = datetime.now(pytz.timezone(tz_name))
            response_body = f"<html><body><h1>Current time in {tz_name}: {current_time.strftime('%Y-%m-%d %H:%M:%S')}</h1></body></html>"
            status = '200 OK'
        except pytz.UnknownTimeZoneError:
            response_body = "<html><body><h1>Unknown timezone</h1></body></html>"
            status = '400 Bad Request'
    
    elif method == 'POST' and path == '/api/v1/convert':
        try:
            request_body_size = int(env.get('CONTENT_LENGTH', 0))
            request_body = env['wsgi.input'].read(request_body_size)
            data = json.loads(request_body)
            date_str = data['date']
            original_tz = data['tz']
            target_tz = data['target_tz']

            original_time = datetime.strptime(date_str, '%m.%d.%Y %H:%M:%S')
            original_time = pytz.timezone(original_tz).localize(original_time)
            target_time = original_time.astimezone(pytz.timezone(target_tz))
            response_body = json.dumps({"converted_date": target_time.strftime('%Y-%m-%d %H:%M:%S')})
            status = '200 OK'
        except Exception as e:
            response_body = json.dumps({"error": str(e)})
            status = '400 Bad Request'
    
    elif method == 'POST' and path == '/api/v1/datediff':
        try:
            request_body_size = int(env.get('CONTENT_LENGTH', 0))
            request_body = env['wsgi.input'].read(request_body_size)
            data = json.loads(request_body)
            first_date_str = data['first_date']
            first_tz = data['first_tz']
            second_date_str = data['second_date']
            second_tz = data['second_tz']

            first_date = datetime.strptime(first_date_str, '%m.%d.%Y %H:%M:%S')
            first_date = pytz.timezone(first_tz).localize(first_date)
            second_date = datetime.strptime(second_date_str, '%I:%M%p %Y-%m-%d')
            second_date = pytz.timezone(second_tz).localize(second_date)

            diff_seconds = int((second_date - first_date).total_seconds())
            response_body = json.dumps({"difference_in_seconds": diff_seconds})
            status = '200 OK'
        except Exception as e:
            response_body = json.dumps({"error": str(e)})
            status = '400 Bad Request'
    
    else:
        response_body = "404 Not Found"
        status = '404 Not Found'
    
    start_response(status, [('Content-Type', 'text/html')])
    return [response_body.encode('utf-8')]

if __name__ == '__main__':
    with make_server('', 8000, application) as httpd:
        print("Serving on port 8000...")
        httpd.serve_forever()