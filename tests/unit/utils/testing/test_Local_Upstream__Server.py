import json
import time
import requests
import threading
from unittest                                                          import TestCase
from osbot_utils.type_safe.primitives.safe_str.web.Safe_Str__Url       import Safe_Str__Url
from osbot_utils.type_safe.primitives.safe_uint.Safe_UInt              import Safe_UInt
from mgraph_ai_service_proxy.schemas.http.Safe_Str__Http__Host         import Safe_Str__Http__Host
from mgraph_ai_service_proxy.utils.testing.Local_Upstream__Server      import Local_Upstream__Server


class test_Local_Upstream__Server(TestCase):                                          # Test the local upstream server wrapper

    def test__init__(self):                                                           # Test initialization
        with Local_Upstream__Server() as _:
            assert type(_)              is Local_Upstream__Server
            assert _.server             is None
            assert _.thread             is None
            assert _.port               is None
            assert _.host               == Safe_Str__Http__Host("localhost")
            assert _.is_running         is False

    def test__start_stop(self):                                                      # Test server lifecycle
        server = Local_Upstream__Server()

        # Initial state
        assert server.is_running is False
        assert server.server     is None
        assert server.thread     is None
        assert server.port       is None

        # Start server
        server.start()

        assert server.is_running is True
        assert server.server     is not None
        assert server.thread     is not None
        assert server.thread.is_alive() is True
        assert type(server.port) is Safe_UInt
        assert server.port > 0
        assert server.port < 65536

        # Verify server is actually running
        response = requests.get(f"http://localhost:{server.port}/echo")
        assert response.status_code == 200
        assert response.json()['path'] == '/echo'

        # Stop server
        server.stop()

        assert server.is_running is False
        assert server.thread.is_alive() is False                                     # Thread should be stopped

        # Verify server is stopped (should fail to connect)
        try:
            requests.get(f"http://localhost:{server.port}/echo", timeout=0.5)
            assert False, "Server should be stopped"
        except requests.exceptions.ConnectionError:
            pass                                                                      # Expected

    def test__url_generation(self):                                                  # Test URL helper method
        server = Local_Upstream__Server()
        server.start()

        try:
            # Test basic URL
            url = server.url()
            assert type(url) is Safe_Str__Url
            assert url == f"http://localhost:{server.port}"

            # Test with path
            url = server.url('/api/test')
            assert type(url) is Safe_Str__Url
            assert url == f"http://localhost:{server.port}/api/test"

            # Test with query string
            url = server.url('/search?q=test')
            assert url == f"http://localhost:{server.port}/search?q=test"

        finally:
            server.stop()

    def test__multiple_servers(self):                                                # Test multiple servers can run simultaneously
        server1 = Local_Upstream__Server()
        server2 = Local_Upstream__Server()

        try:
            server1.start()
            server2.start()

            # Different ports
            assert server1.port != server2.port

            # Both servers respond
            response1 = requests.get(f"http://localhost:{server1.port}/echo")
            response2 = requests.get(f"http://localhost:{server2.port}/echo")

            assert response1.status_code == 200
            assert response2.status_code == 200

        finally:
            server1.stop()
            server2.stop()

    def test__server_responds_correctly(self):                                       # Test server actually handles requests
        server = Local_Upstream__Server()
        server.start()

        try:
            # Test GET
            response = requests.get(server.url('/echo'))
            assert response.status_code == 200
            data = response.json()
            assert data['method'] == 'GET'
            assert data['path']   == '/echo'

            # Test POST
            post_data = {'test': 'data'}
            response = requests.post(server.url('/echo/post'), json=post_data)
            assert response.status_code == 201
            data = response.json()
            assert data['method'] == 'POST'
            assert json.loads(data['body']) == post_data

            # Test 404
            response = requests.get(server.url('/nonexistent'))
            assert response.status_code == 404
            assert response.json()['error'] == 'Not Found'

        finally:
            server.stop()

    def test__context_manager(self):                                                 # Test use as context manager
        # Test normal operation
        with Local_Upstream__Server() as server:
            server.start()
            assert server.is_running is True

            response = requests.get(server.url('/echo'))
            assert response.status_code == 200

            server.stop()
            assert server.is_running is False

        # Note: The current implementation doesn't have __enter__/__exit__
        # This test documents expected behavior if we add context manager support

    def test__server_thread_daemon(self):                                            # Test thread is daemon (won't block shutdown)
        server = Local_Upstream__Server()
        server.start()

        assert server.thread.daemon is True                                          # Thread should be daemon

        server.stop()

    def test__rapid_start_stop(self):                                                # Test rapid start/stop cycles
        server = Local_Upstream__Server()

        for i in range(3):
            server.start()
            assert server.is_running is True

            # Make a request to verify it's working
            response = requests.get(server.url('/echo'))
            assert response.status_code == 200

            server.stop()
            assert server.is_running is False

            # Small delay to ensure port is released
            time.sleep(0.1)

    def test__stop_without_start(self):                                              # Test stopping unstarted server
        server = Local_Upstream__Server()

        # Should not raise error
        result = server.stop()
        assert result == server                                                      # Should return self
        assert server.is_running is False

    def test__server_headers(self):                                                  # Test server handles headers correctly
        server = Local_Upstream__Server()
        server.start()

        try:
            headers = {'X-Test-Header': 'test-value',
                      'Authorization': 'Bearer token'}

            response = requests.get(server.url('/echo/headers'), headers=headers)
            assert response.status_code == 200

            data = response.json()
            headers_received = data['headers_received']
            assert headers_received['X-Test-Header'] == 'test-value'
            assert headers_received['Authorization'] == 'Bearer token'

        finally:
            server.stop()

    def test__server_large_payload(self):                                            # Test server handles large payloads
        server = Local_Upstream__Server()
        server.start()

        try:
            response = requests.get(server.url('/large'))
            assert response.status_code == 200

            data = response.json()
            assert len(data['data']) == 1024 * 1024                                  # 1MB

        finally:
            server.stop()

    def test__concurrent_requests(self):                                             # Test server handles concurrent requests
        server = Local_Upstream__Server()
        server.start()

        try:
            results = []

            def make_request(index):
                response = requests.get(server.url(f'/echo?id={index}'))
                results.append((index, response.status_code))

            # Create multiple threads
            threads = []
            for i in range(10):
                thread = threading.Thread(target=make_request, args=(i,))
                threads.append(thread)
                thread.start()

            # Wait for all to complete
            for thread in threads:
                thread.join()

            # Verify all succeeded
            assert len(results) == 10
            for index, status in results:
                assert status == 200

        finally:
            server.stop()

    def test__type_safety(self):                                                     # Test type safety of attributes
        server = Local_Upstream__Server()
        server.start()

        try:
            # Verify types
            assert type(server.host) is Safe_Str__Http__Host
            assert type(server.port) is Safe_UInt

            # Type conversion on URL
            url = server.url('/test')
            assert type(url) is Safe_Str__Url

        finally:
            server.stop()