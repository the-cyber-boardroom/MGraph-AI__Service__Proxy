import json
import time
from http.server import BaseHTTPRequestHandler

class Local_Upstream__Handler(BaseHTTPRequestHandler):                                      # Mock upstream server for proxy testing

    def log_message(self, format, *args):                                               # Suppress default logging
        pass

    def do_GET(self):                                                                   # Handle GET requests
        if self.path == '/echo':
            self._handle_echo()
        elif self.path == '/echo/headers':
            self._handle_echo_headers()
        elif self.path.startswith('/delay'):
            self._handle_delay()
        elif self.path == '/timeout':
            self._handle_timeout()
        elif self.path == '/error/500':
            self._handle_error_500()
        elif self.path == '/large':
            self._handle_large_response()
        elif self.path == '/redirect':
            self._handle_redirect()
        else:
            self._handle_not_found()

    def do_POST(self):                                                                  # Handle POST requests
        if self.path == '/echo/post':
            self._handle_echo_post()
        elif self.path == '/validate':
            self._handle_validate_post()
        else:
            self._handle_not_found()

    def do_PUT(self):                                                                   # Handle PUT requests
        if self.path == '/update':
            self._handle_update()
        else:
            self._handle_not_found()

    def do_DELETE(self):                                                                # Handle DELETE requests
        if self.path.startswith('/delete'):
            self._handle_delete()
        else:
            self._handle_not_found()

    def _handle_echo(self):                                                            # Echo request details back
        self.send_response(200)
        self.send_header('Content-Type' , 'application/json')
        self.send_header('X-Test-Header', 'test-value'      )
        self.send_header('X-Echo-Path'  , self.path         )
        self.end_headers()

        response = {'method'  : 'GET'                      ,
                    'path'    : self.path                   ,
                    'query'   : self._get_query_string()    ,
                    'client'  : self.client_address[0]      }

        self.wfile.write(json.dumps(response).encode())

    def _handle_echo_headers(self):                                                    # Echo all headers back
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

        headers = {key: value for key, value in self.headers.items()}
        response = {'headers_received': headers}

        self.wfile.write(json.dumps(response).encode())

    def _handle_echo_post(self):                                                       # Echo POST data back
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length > 0 else b''

        self.send_response(201)
        self.send_header('Content-Type', 'application/json')
        self.send_header('X-Request-Method', 'POST')
        self.end_headers()

        response = {'method'      : 'POST'                              ,
                   'body'        : body.decode() if body else ''       ,
                   'content_type': self.headers.get('Content-Type')    ,
                   'length'      : content_length                      }

        self.wfile.write(json.dumps(response).encode())

    def _handle_validate_post(self):                                                   # Validate POST body structure
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length > 0 else b''

        try:
            data = json.loads(body)
            if 'required_field' in data:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'valid', 'data': data}).encode())
            else:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Missing required_field'}).encode())
        except json.JSONDecodeError:
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Invalid JSON'}).encode())

    def _handle_update(self):                                                          # Handle PUT update request
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length > 0 else b''

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

        response = {'method' : 'PUT'                         ,
                   'updated': True                          ,
                   'body'   : body.decode() if body else '' }

        self.wfile.write(json.dumps(response).encode())

    def _handle_delete(self):                                                          # Handle DELETE request
        resource_id = self.path.split('/')[-1] if '/' in self.path else None

        self.send_response(204)                                                        # No Content
        self.send_header('X-Deleted-Resource', resource_id or 'unknown')
        self.end_headers()

    def _handle_delay(self):                                                           # Delay response for testing
        delay_ms = 100                                                                 # Default delay
        if '/' in self.path:
            try:
                delay_ms = int(self.path.split('/')[-1])
            except ValueError:
                pass

        time.sleep(delay_ms / 1000.0)

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

        response = {'delayed_ms': delay_ms}
        self.wfile.write(json.dumps(response).encode())

    def _handle_timeout(self):                                                         # Simulate timeout (never responds)
        time.sleep(30)                                                                 # Sleep longer than any reasonable timeout

    def _handle_error_500(self):                                                       # Return 500 error
        self.send_response(500)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

        response = {'error': 'Internal Server Error', 'details': 'Simulated error'}
        self.wfile.write(json.dumps(response).encode())

    def _handle_large_response(self):                                                  # Return large response for testing
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

        large_data = {'data': 'x' * (1024 * 1024)}                                    # 1MB of data
        self.wfile.write(json.dumps(large_data).encode())

    def _handle_redirect(self):                                                        # Return redirect response
        self.send_response(302)
        self.send_header('Location', '/echo')
        self.end_headers()

    def _handle_not_found(self):                                                       # Return 404 for unknown paths
        self.send_response(404)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

        response = {'error': 'Not Found', 'path': self.path}
        self.wfile.write(json.dumps(response).encode())

    def _get_query_string(self):                                                       # Extract query string from path
        if '?' in self.path:
            return self.path.split('?', 1)[1]
        return ''