import json
import time
from unittest                                                               import TestCase
from osbot_utils.type_safe.primitives.safe_str.identifiers.Random_Guid      import Random_Guid
from osbot_utils.type_safe.primitives.safe_str.web.Safe_Str__IP_Address     import Safe_Str__IP_Address
from osbot_utils.type_safe.primitives.safe_uint.Safe_UInt                   import Safe_UInt
from mgraph_ai_service_proxy.schemas.Schema__Proxy__Request                 import Schema__Proxy__Request
from mgraph_ai_service_proxy.schemas.http.Safe_Str__Http__Host              import Safe_Str__Http__Host
from mgraph_ai_service_proxy.schemas.http.Safe_Str__Http__Method            import Safe_Str__Http__Method
from mgraph_ai_service_proxy.schemas.http.Safe_Str__Http__Path              import Safe_Str__Http__Path
from mgraph_ai_service_proxy.service.proxy.Service__Proxy                   import Service__Proxy
from mgraph_ai_service_proxy.utils.testing.Local_Upstream__Server           import Local_Upstream__Server


class test_Service__Proxy__local_upstream_server(TestCase):                                      # Integration tests for proxy service

    @classmethod
    def setUpClass(cls):                                                               # One-time setup for all tests
        cls.upstream                             = Local_Upstream__Server()
        cls.proxy_service                        = Service__Proxy().setup()
        cls.proxy_service.config.verify_ssl      = False                               # Disable SSL for testing
        cls.proxy_service.config.connect_timeout = Safe_UInt(2)                        # Shorter timeouts for tests
        cls.proxy_service.config.read_timeout    = Safe_UInt(2)
        cls.upstream.start()
        cls.upstream_port                        = cls.upstream.port                   # once the upstream server has started we can capture the port that was used


    @classmethod
    def tearDownClass(cls):                                                           # Cleanup after all tests
        cls.upstream.stop()

    def test_proxy_get_echo(self):                                                    # Test basic GET request proxying
        request = Schema__Proxy__Request(method       = Safe_Str__Http__Method("GET")              ,
                                         path         = Safe_Str__Http__Path("/echo")              ,
                                         host         = Safe_Str__Http__Host(f"localhost:{self.upstream.port}"),
                                         client_ip    = Safe_Str__IP_Address("192.168.1.100")      ,
                                         use_https    = False                                      ,
                                         request_id   = Random_Guid()                              )

        response = self.proxy_service.execute_request(request)

        assert response.status_code == 200
        assert response.target_url  == f"http://localhost:{self.upstream.port}/echo"

        # Parse response content
        content = json.loads(response.content.decode())
        assert content['method'] == 'GET'
        assert content['path']   == '/echo'

    def test_proxy_post_with_body(self):                                              # Test POST request with JSON body
        test_data = {'key': 'value', 'number': 42}

        request = Schema__Proxy__Request(method      = Safe_Str__Http__Method("POST")             ,
                                        path         = Safe_Str__Http__Path("/echo/post")         ,
                                        host         = Safe_Str__Http__Host(f"localhost:{self.upstream.port}"),
                                        headers      = {"Content-Type": "application/json"}       ,
                                        body         = json.dumps(test_data).encode()             ,
                                        client_ip    = Safe_Str__IP_Address("10.0.0.1")           ,
                                        use_https    = False                                      ,
                                        request_id   = Random_Guid()                              )

        response = self.proxy_service.execute_request(request)

        assert response.status_code == 201

        content = json.loads(response.content.decode())
        assert content['method']       == 'POST'
        assert content['body']         == json.dumps(test_data)
        assert content['content_type'] == 'application/json'

    def test_proxy_header_forwarding(self):                                           # Test header forwarding and filtering
        custom_headers = { 'X-Custom-Header'  : 'custom-value'     ,
                           'Authorization'     : 'Bearer token123'  ,
                           'User-Agent'        : 'TestClient/1.0'   ,
                           'Host'              : 'should-be-filtered',                  # Should be filtered
                           'Connection'        : 'keep-alive'       ,                   # Should be filtered
                           'Proxy-Connection'  : 'keep-alive'       }                   # Should be filtered

        request = Schema__Proxy__Request(method       = Safe_Str__Http__Method("GET")                          ,
                                         path         = Safe_Str__Http__Path("/echo/headers")                  ,
                                         host         = Safe_Str__Http__Host(f"localhost:{self.upstream.port}"),
                                         headers      = custom_headers                                         ,
                                         client_ip    = Safe_Str__IP_Address("172.16.0.1")                     ,
                                         use_https    = False                                                  ,
                                         request_id   = Random_Guid()                                          )

        response = self.proxy_service.execute_request(request)

        assert response.status_code == 200

        content = json.loads(response.content.decode())
        headers_received = content['headers_received']

        # Verify forwarding headers were added
        assert 'X-Forwarded-For'   in headers_received
        assert 'X-Forwarded-Proto' in headers_received
        assert 'X-Forwarded-Host'  in headers_received

        assert headers_received['X-Forwarded-For']   == '172.16.0.1'
        assert headers_received['X-Forwarded-Proto'] == 'http'

        # Verify custom headers passed through
        assert headers_received.get('X-Custom-Header') == 'custom-value'
        assert headers_received.get('Authorization')   == 'Bearer token123'
        assert headers_received.get('User-Agent')      == 'TestClient/1.0'

        # Verify filtered headers were removed
        assert headers_received == { 'Accept'            : '*/*'                            ,
                                     'Accept-Encoding'   : 'gzip, deflate'                  ,
                                     'Authorization'     : 'Bearer token123'                ,
                                     'Connection'        : 'keep-alive'                     ,
                                     'Host'              : f'localhost:{self.upstream_port}',
                                     'User-Agent'        : 'TestClient/1.0'                 ,
                                     'X-Custom-Header'   : 'custom-value'                   ,
                                     'X-Forwarded-For'   : '172.16.0.1'                     ,
                                     'X-Forwarded-Host'  : f'localhost:{self.upstream_port}',
                                     'X-Forwarded-Proto' : 'http'                       }
        #assert 'Connection'       not in headers_received
        assert 'Connection'           in headers_received
        assert 'Proxy-Connection' not in headers_received

    def test_proxy_put_request(self):                                                 # Test PUT request proxying
        update_data = {'id': 123, 'status': 'updated'}

        request = Schema__Proxy__Request(method       = Safe_Str__Http__Method("PUT")              ,
                                        path         = Safe_Str__Http__Path("/update")            ,
                                        host         = Safe_Str__Http__Host(f"localhost:{self.upstream.port}"),
                                        body         = json.dumps(update_data).encode()           ,
                                        client_ip    = Safe_Str__IP_Address("192.168.10.1")       ,
                                        use_https    = False                                      ,
                                        request_id   = Random_Guid()                              )

        response = self.proxy_service.execute_request(request)

        assert response.status_code == 200

        content = json.loads(response.content.decode())
        assert content['method']  == 'PUT'
        assert content['updated'] == True
        assert content['body']    == json.dumps(update_data)

    def test_proxy_delete_request(self):                                              # Test DELETE request proxying
        request = Schema__Proxy__Request(method       = Safe_Str__Http__Method("DELETE")           ,
                                        path         = Safe_Str__Http__Path("/delete/resource-123"),
                                        host         = Safe_Str__Http__Host(f"localhost:{self.upstream.port}"),
                                        client_ip    = Safe_Str__IP_Address("10.10.10.10")        ,
                                        use_https    = False                                      ,
                                        request_id   = Random_Guid()                              )

        response = self.proxy_service.execute_request(request)

        assert response.status_code == 204                                            # No Content
        assert 'X-Deleted-Resource' in response.headers
        assert response.headers['X-Deleted-Resource'] == 'resource-123'

    def test_proxy_404_response(self):                                                # Test 404 error handling
        request = Schema__Proxy__Request(method       = Safe_Str__Http__Method("GET")              ,
                                        path         = Safe_Str__Http__Path("/non-existent")      ,
                                        host         = Safe_Str__Http__Host(f"localhost:{self.upstream.port}"),
                                        client_ip    = Safe_Str__IP_Address("192.168.1.1")        ,
                                        use_https    = False                                      ,
                                        request_id   = Random_Guid()                              )

        response = self.proxy_service.execute_request(request)

        assert response.status_code == 404

        content = json.loads(response.content.decode())
        assert content['error'] == 'Not Found'
        assert content['path']  == '/non-existent'

    def test_proxy_500_error(self):                                                   # Test 500 error response
        request = Schema__Proxy__Request(method       = Safe_Str__Http__Method("GET")              ,
                                        path         = Safe_Str__Http__Path("/error/500")         ,
                                        host         = Safe_Str__Http__Host(f"localhost:{self.upstream.port}"),
                                        client_ip    = Safe_Str__IP_Address("192.168.1.1")        ,
                                        use_https    = False                                      ,
                                        request_id   = Random_Guid()                              )

        response = self.proxy_service.execute_request(request)

        assert response.status_code == 500

        content = json.loads(response.content.decode())
        assert content['error']   == 'Internal Server Error'
        assert content['details'] == 'Simulated error'

    def test_proxy_delay_response(self):                                              # Test delayed response handling
        request = Schema__Proxy__Request(method       = Safe_Str__Http__Method("GET")              ,
                                        path         = Safe_Str__Http__Path("/delay/100")         ,
                                        host         = Safe_Str__Http__Host(f"localhost:{self.upstream.port}"),
                                        client_ip    = Safe_Str__IP_Address("192.168.1.1")        ,
                                        use_https    = False                                      ,
                                        request_id   = Random_Guid()                              )

        start_time = time.time()
        response = self.proxy_service.execute_request(request)
        duration = time.time() - start_time

        assert response.status_code == 200
        assert duration >= 0.1                                                        # At least 100ms delay

        content = json.loads(response.content.decode())
        assert content['delayed_ms'] == 100

    def test_proxy_large_response(self):                                              # Test large response handling
        request = Schema__Proxy__Request(method       = Safe_Str__Http__Method("GET")              ,
                                        path         = Safe_Str__Http__Path("/large")             ,
                                        host         = Safe_Str__Http__Host(f"localhost:{self.upstream.port}"),
                                        client_ip    = Safe_Str__IP_Address("192.168.1.1")        ,
                                        use_https    = False                                      ,
                                        request_id   = Random_Guid()                              )

        response = self.proxy_service.execute_request(request)

        assert response.status_code == 200

        content = json.loads(response.content.decode())
        assert len(content['data']) == 1024 * 1024                                    # 1MB of data

    def test_proxy_redirect_no_follow(self):                                          # Test redirect without following
        request = Schema__Proxy__Request(method       = Safe_Str__Http__Method("GET")              ,
                                        path         = Safe_Str__Http__Path("/redirect")          ,
                                        host         = Safe_Str__Http__Host(f"localhost:{self.upstream.port}"),
                                        client_ip    = Safe_Str__IP_Address("192.168.1.1")        ,
                                        use_https    = False                                      ,
                                        request_id   = Random_Guid()                              )

        response = self.proxy_service.execute_request(request)

        assert response.status_code == 302                                            # Redirect not followed
        assert 'Location' in response.headers
        assert response.headers['Location'] == '/echo'

    def test_proxy_stats_tracking(self):                                              # Test statistics tracking
        initial_requests = self.proxy_service.stats_service.total_requests

        # Make successful request
        request = Schema__Proxy__Request(method       = Safe_Str__Http__Method("GET")              ,
                                        path         = Safe_Str__Http__Path("/echo")              ,
                                        host         = Safe_Str__Http__Host(f"localhost:{self.upstream.port}"),
                                        client_ip    = Safe_Str__IP_Address("192.168.1.1")        ,
                                        use_https    = False                                      ,
                                        request_id   = Random_Guid()                              )

        self.proxy_service.execute_request(request)

        assert self.proxy_service.stats_service.total_requests == initial_requests + 1

        # Verify stats retrieval
        stats = self.proxy_service.stats_service.get_stats()
        assert stats['total_requests'] == initial_requests + 1
        assert 'total_errors'   in stats
        assert 'total_timeouts' in stats