import unittest
import json
from main import application
from wsgiref.util import setup_testing_defaults
from io import BytesIO

class TestApp(unittest.TestCase):

    def test_get_time_gmt(self):
        env = {}
        setup_testing_defaults(env)
        env['PATH_INFO'] = '/'
        env['REQUEST_METHOD'] = 'GET'

        def start_response(status, headers):
            self.assertEqual(status, '200 OK')

        result = application(env, start_response)
        self.assertIn(b'Current time in GMT', result[0])

    def test_post_convert(self):
        env = {}
        setup_testing_defaults(env)
        env['PATH_INFO'] = '/api/v1/convert'
        env['REQUEST_METHOD'] = 'POST'
        payload = json.dumps({"date":"12.20.2021 22:21:05", "tz": "EST", "target_tz": "Europe/Moscow"})
        env['CONTENT_LENGTH'] = str(len(payload))
        env['wsgi.input'] = BytesIO(payload.encode('utf-8'))

        def start_response(status, headers):
            self.assertEqual(status, '200 OK')

        result = application(env, start_response)
        response = json.loads(result[0])
        self.assertIn('converted_date', response)

    def test_post_datediff(self):
        env = {}
        setup_testing_defaults(env)
        env['PATH_INFO'] = '/api/v1/datediff'
        env['REQUEST_METHOD'] = 'POST'
        payload = json.dumps({"first_date":"12.06.2024 22:21:05", "first_tz": "EST", "second_date":"12:30pm 2024-02-01", "second_tz": "Europe/Moscow"})
        env['CONTENT_LENGTH'] = str(len(payload))
        env['wsgi.input'] = BytesIO(payload.encode('utf-8'))

        def start_response(status, headers):
            self.assertEqual(status, '200 OK')

        result = application(env, start_response)
        response = json.loads(result[0])
        self.assertIn('difference_in_seconds', response)

if __name__ == '__main__':
    unittest.main()