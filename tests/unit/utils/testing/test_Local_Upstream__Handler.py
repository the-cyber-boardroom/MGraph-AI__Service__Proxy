import json
import threading
import time
from http.server                                                       import HTTPServer
from http.client                                                       import HTTPConnection
from unittest                                                          import TestCase
from osbot_utils.helpers.duration.decorators.capture_duration          import capture_duration
from osbot_utils.utils.Misc                                            import random_port
from mgraph_ai_service_proxy.utils.testing.Local_Upstream__Handler     import Local_Upstream__Handler


class test_Local_Upstream__Handler(TestCase):                                          # Test the local upstream handler behavior

    @classmethod
    def setUpClass(cls):                                                               # Start test server once for all tests
        with capture_duration() as start_duration:
            cls.port   = random_port()
            cls.server = HTTPServer(('localhost', cls.port), Local_Upstream__Handler)
            cls.thread = threading.Thread(target=cls.server.serve_forever)
            cls.thread.daemon = True
            cls.thread.start()
            time.sleep(0.1)                                                            # this doesn't seem to be needed  # Allow server to start

            cls.client = HTTPConnection('localhost', cls.port)                          # Reusable HTTP client

        assert start_duration.seconds < 0.21                                            # should start in less than 10 milliseconds

    @classmethod
    def tearDownClass(cls):                                                           # Clean shutdown
        with capture_duration() as stop_duration:
            cls.server.shutdown()
            cls.server.server_close()
            cls.thread.join(timeout=5)
            cls.client.close()

        assert stop_duration.seconds < 0.8                                            # should start in less than 800 milliseconds (0.8 seconds)

    def _make_request(self, method: str                            ,                  # Helper to make HTTP requests
                            path  : str                             ,
                            body  : str    = None                   ,
                            headers: dict  = None
                      ) -> tuple:                                                      # Returns (status, headers, body)
        headers = headers or {}

        if body:
            headers['Content-Length'] = str(len(body))

        self.client.request(method, path, body=body, headers=headers)
        response = self.client.getresponse()

        status       = response.status
        resp_headers = dict(response.headers)
        resp_body    = response.read().decode()

        return status, resp_headers, resp_body

    def test__echo_endpoint(self):                                                    # Test basic echo functionality
        status, headers, body = self._make_request('GET', '/echo')

        assert status == 200
        assert headers['Content-Type'] == 'application/json'
        assert headers['X-Test-Header'] == 'test-value'
        assert headers['X-Echo-Path']   == '/echo'

        data = json.loads(body)
        assert data == { 'method' : 'GET'      ,
                         'path'   : '/echo'    ,
                         'query'  : ''         ,
                         'client' : '127.0.0.1'}

    def test__echo_with_query_string(self):                                          # Test query string extraction
        status, headers, body = self._make_request('GET', '/echo?foo=bar&test=123')

        assert status == 200
        data = json.loads(body)
        assert data['query'] == 'foo=bar&test=123'
        assert data['path']  == '/echo'                                              # Path without query

    def test__echo_headers_endpoint(self):                                           # Test header echoing
        custom_headers = {'X-Custom-1'    : 'value1'       ,
                         'X-Custom-2'    : 'value2'       ,
                         'Authorization' : 'Bearer token' }

        status, headers, body = self._make_request('GET', '/echo/headers', headers=custom_headers)

        assert status == 200
        data = json.loads(body)

        headers_received = data['headers_received']
        assert headers_received['X-Custom-1']    == 'value1'
        assert headers_received['X-Custom-2']    == 'value2'
        assert headers_received['Authorization'] == 'Bearer token'

    def test__echo_post_endpoint(self):                                              # Test POST echo
        post_data = json.dumps({'key': 'value', 'number': 42})

        status, headers, body = self._make_request('POST'                        ,
                                                   '/echo/post'                  ,
                                                   body=post_data               ,
                                                   headers={'Content-Type': 'application/json'})

        assert status == 201
        assert headers['X-Request-Method'] == 'POST'

        data = json.loads(body)
        assert data['method']       == 'POST'
        assert data['body']         == post_data
        assert data['content_type'] == 'application/json'
        assert data['length']       == len(post_data)

    def test__validate_post_success(self):                                           # Test POST validation success
        valid_data = json.dumps({'required_field': 'present', 'extra': 'data'})

        status, headers, body = self._make_request('POST', '/validate', body=valid_data)

        assert status == 200
        data = json.loads(body)
        assert data['status'] == 'valid'
        assert data['data']   == {'required_field': 'present', 'extra': 'data'}

    def test__validate_post_missing_field(self):                                     # Test POST validation failure
        invalid_data = json.dumps({'other_field': 'value'})

        status, headers, body = self._make_request('POST', '/validate', body=invalid_data)

        assert status == 400
        data = json.loads(body)
        assert data['error'] == 'Missing required_field'

    def test__validate_post_invalid_json(self):                                      # Test invalid JSON handling
        invalid_json = 'not json at all'

        status, headers, body = self._make_request('POST', '/validate', body=invalid_json)

        assert status == 400
        data = json.loads(body)
        assert data['error'] == 'Invalid JSON'

    def test__update_endpoint(self):                                                 # Test PUT update
        update_data = json.dumps({'id': 123, 'status': 'updated'})

        status, headers, body = self._make_request('PUT', '/update', body=update_data)

        assert status == 200
        data = json.loads(body)
        assert data == {'method' : 'PUT'       ,
                       'updated': True         ,
                       'body'   : update_data  }

    def test__delete_endpoint(self):                                                 # Test DELETE with resource ID
        status, headers, body = self._make_request('DELETE', '/delete/resource-456')

        assert status == 204                                                         # No Content
        assert headers['X-Deleted-Resource'] == 'resource-456'
        assert body == ''                                                            # No body for 204

    def test__delete_root(self):                                                     # Test DELETE without resource ID
        status, headers, body = self._make_request('DELETE', '/delete')

        assert status == 204
        assert headers['X-Deleted-Resource'] == 'delete'                             # Last path segment

    def test__delay_default(self):                                                   # Test default delay
        start = time.time()
        status, headers, body = self._make_request('GET', '/delay')
        duration = time.time() - start

        assert status == 200
        data = json.loads(body)
        assert data['delayed_ms'] == 100                                             # Default delay
        assert duration >= 0.1                                                       # At least 100ms
        assert duration < 0.5                                                        # But not too long

    def test__delay_custom(self):                                                    # Test custom delay
        start = time.time()
        status, headers, body = self._make_request('GET', '/delay/50')
        duration = time.time() - start

        assert status == 200
        data = json.loads(body)
        assert data['delayed_ms'] == 50
        assert duration >= 0.05                                                      # At least 50ms
        assert duration < 0.3                                                        # But reasonable

    def test__delay_invalid_number(self):                                            # Test invalid delay number
        status, headers, body = self._make_request('GET', '/delay/invalid')

        assert status == 200
        data = json.loads(body)
        assert data['delayed_ms'] == 100                                             # Falls back to default

    def test__error_500_endpoint(self):                                              # Test 500 error response
        status, headers, body = self._make_request('GET', '/error/500')

        assert status == 500
        data = json.loads(body)
        assert data == {'error'  : 'Internal Server Error' ,
                       'details': 'Simulated error'       }

    def test__large_response(self):                                                  # Test large response handling
        status, headers, body = self._make_request('GET', '/large')

        assert status == 200
        data = json.loads(body)
        assert len(data['data']) == 1024 * 1024                                      # 1MB of 'x' characters
        assert data['data'][:10] == 'xxxxxxxxxx'                                     # Verify content

    def test__redirect_endpoint(self):                                               # Test redirect response
        status, headers, body = self._make_request('GET', '/redirect')

        assert status == 302
        assert headers['Location'] == '/echo'
        assert body == ''                                                            # Redirect has no body

    def test__not_found_get(self):                                                   # Test 404 for unknown GET path
        status, headers, body = self._make_request('GET', '/unknown/path')

        assert status == 404
        data = json.loads(body)
        assert data == {'error': 'Not Found'   ,
                       'path' : '/unknown/path' }

    def test__not_found_post(self):                                                  # Test 404 for unknown POST path
        status, headers, body = self._make_request('POST', '/unknown')

        assert status == 404
        data = json.loads(body)
        assert data['error'] == 'Not Found'
        assert data['path']  == '/unknown'

    def test__not_found_put(self):                                                   # Test 404 for unknown PUT path
        status, headers, body = self._make_request('PUT', '/invalid')

        assert status == 404
        data = json.loads(body)
        assert data['error'] == 'Not Found'

    def test__not_found_delete(self):                                                # Test 404 for unknown DELETE path
        status, headers, body = self._make_request('DELETE', '/invalid')

        assert status == 404
        data = json.loads(body)
        assert data['error'] == 'Not Found'

    def test__timeout_endpoint(self):                                                # Test timeout behavior (with short timeout)
        # This test validates the endpoint exists but doesn't wait 30s
        # We'll use a short socket timeout to verify it hangs
        import socket

        temp_client = HTTPConnection('localhost', self.port, timeout=0.5)

        try:
            temp_client.request('GET', '/timeout')
            temp_client.getresponse()
            assert False, "Should have timed out"                                    # Should not reach here
        except socket.timeout:
            pass                                                                      # Expected behavior
        finally:
            temp_client.close()