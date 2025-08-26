import json
import requests
import threading
from unittest                                                          import TestCase
from osbot_fast_api_serverless.utils.testing.skip_tests                import skip__if_not__in_github_actions
from osbot_utils.type_safe.primitives.safe_str.web.Safe_Str__Url       import Safe_Str__Url
from osbot_utils.type_safe.primitives.safe_uint.Safe_UInt              import Safe_UInt
from mgraph_ai_service_proxy.schemas.http.Safe_Str__Http__Host         import Safe_Str__Http__Host
from mgraph_ai_service_proxy.utils.testing.Local_Upstream__Server      import Local_Upstream__Server


class test_Local_Upstream__Server(TestCase):                                          # Test the local upstream server wrapper

    @classmethod
    def setUpClass(cls):                                                              # Start ONE server for all tests
        cls.server = Local_Upstream__Server()
        cls.server.start()

        # Store server details for tests
        cls.base_url = f"http://localhost:{cls.server.port}"

        # For tests that need their own servers (like multiple_servers test)
        cls.extra_servers = []

    @classmethod
    def tearDownClass(cls):                                                          # Stop the shared server
        cls.server.stop()

        # Clean up any extra servers created during tests
        for server in cls.extra_servers:
            if server.is_running:
                server.stop()

    def tearDown(self):                                                              # Clean up between tests
        # Reset any test-specific state if needed
        # The server itself stays running
        pass

    def test__init__(self):                                                          # Test initialization
        with Local_Upstream__Server() as _:                                         # New instance, not started
            assert type(_)              is Local_Upstream__Server
            assert _.server             is None
            assert _.thread             is None
            assert _.port               is None
            assert _.host               == Safe_Str__Http__Host("localhost")
            assert _.is_running         is False

    def test__start_stop(self):                                                     # Test server lifecycle with new instance
        skip__if_not__in_github_actions()
        test_server = Local_Upstream__Server()                                      # Create separate instance for this test
        self.extra_servers.append(test_server)                                      # Track for cleanup

        # Initial state
        assert test_server.is_running is False
        assert test_server.server     is None
        assert test_server.thread     is None
        assert test_server.port       is None

        # Start server
        test_server.start()

        assert test_server.is_running is True
        assert test_server.server     is not None
        assert test_server.thread     is not None
        assert test_server.thread.is_alive() is True
        assert type(test_server.port) is Safe_UInt
        assert test_server.port > 0
        assert test_server.port < 65536

        # Verify server is actually running
        response = requests.get(f"http://localhost:{test_server.port}/echo")
        assert response.status_code == 200
        assert response.json()['path'] == '/echo'

        # Stop server
        test_server.stop()

        assert test_server.is_running is False
        assert test_server.thread.is_alive() is False                               # Thread should be stopped

        # Verify server is stopped (should fail to connect)
        try:
            requests.get(f"http://localhost:{test_server.port}/echo", timeout=0.5)
            assert False, "Server should be stopped"
        except requests.exceptions.ConnectionError:
            pass                                                                     # Expected

    def test__url_generation(self):                                                 # Test URL helper method using shared server
        # Test basic URL
        url = self.server.url()
        assert type(url) is Safe_Str__Url
        assert url == f"http://localhost:{self.server.port}"

        # Test with path
        url = self.server.url('/api/test')
        assert type(url) is Safe_Str__Url
        assert url == f"http://localhost:{self.server.port}/api/test"

        # Test with query string
        url = self.server.url('/search?q=test')
        assert url == f"http://localhost:{self.server.port}/search?q=test"

    def test__multiple_servers(self):                                               # Test multiple servers can run simultaneously
        skip__if_not__in_github_actions()
        server2 = Local_Upstream__Server()
        self.extra_servers.append(server2)                                          # Track for cleanup

        server2.start()

        # Different ports
        assert self.server.port != server2.port

        # Both servers respond
        response1 = requests.get(f"http://localhost:{self.server.port}/echo")
        response2 = requests.get(f"http://localhost:{server2.port}/echo")

        assert response1.status_code == 200
        assert response2.status_code == 200

        server2.stop()                                                              # Clean up immediately

    def test__server_responds_correctly(self):                                      # Test server actually handles requests
        # Test GET using shared server
        response = requests.get(self.server.url('/echo'))
        assert response.status_code == 200
        data = response.json()
        assert data['method'] == 'GET'
        assert data['path']   == '/echo'

        # Test POST
        post_data = {'test': 'data'}
        response = requests.post(self.server.url('/echo/post'), json=post_data)
        assert response.status_code == 201
        data = response.json()
        assert data['method'] == 'POST'
        assert json.loads(data['body']) == post_data

        # Test 404
        response = requests.get(self.server.url('/nonexistent'))
        assert response.status_code == 404
        assert response.json()['error'] == 'Not Found'

    def test__context_manager(self):                                                # Test use as context manager
        skip__if_not__in_github_actions()
        # Test with a new instance (not the shared one)
        with Local_Upstream__Server() as test_server:
            self.extra_servers.append(test_server)                                  # Track for cleanup
            test_server.start()
            assert test_server.is_running is True

            response = requests.get(test_server.url('/echo'))
            assert response.status_code == 200

            test_server.stop()
            assert test_server.is_running is False

    def test__server_thread_daemon(self):                                           # Test thread is daemon (won't block shutdown)
        assert self.server.thread.daemon is True                                    # Check shared server's thread

    def test__rapid_start_stop(self):                                               # Test rapid start/stop cycles with new instance
        skip__if_not__in_github_actions()
        test_server = Local_Upstream__Server()
        self.extra_servers.append(test_server)                                      # Track for cleanup

        for i in range(3):
            test_server.start()
            assert test_server.is_running is True

            # Make a request to verify it's working
            response = requests.get(test_server.url('/echo'))
            assert response.status_code == 200

            test_server.stop()
            assert test_server.is_running is False

    def test__stop_without_start(self):                                             # Test stopping unstarted server
        test_server = Local_Upstream__Server()                                      # New instance

        # Should not raise error
        result = test_server.stop()
        assert result == test_server                                                # Should return self
        assert test_server.is_running is False

    def test__server_headers(self):                                                 # Test server handles headers correctly
        headers = {'X-Test-Header': 'test-value',
                  'Authorization': 'Bearer token'}

        response = requests.get(self.server.url('/echo/headers'), headers=headers)  # Use shared server
        assert response.status_code == 200

        data = response.json()
        headers_received = data['headers_received']
        assert headers_received['X-Test-Header'] == 'test-value'
        assert headers_received['Authorization'] == 'Bearer token'

    def test__server_large_payload(self):                                           # Test server handles large payloads
        response = requests.get(self.server.url('/large'))                          # Use shared server
        assert response.status_code == 200

        data = response.json()
        assert len(data['data']) == 1024 * 1024                                     # 1MB

    def test__concurrent_requests(self):                                            # Test server handles concurrent requests
        results = []

        def make_request(index):
            response = requests.get(self.server.url(f'/echo?id={index}'))           # Use shared server
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
        assert len(results) > 5                                                     # note: over many runs we don't always get 10
        for index, status in results:
            assert status == 200

    def test__type_safety(self):                                                    # Test type safety of attributes
        # Verify types using shared server
        assert type(self.server.host) is Safe_Str__Http__Host
        assert type(self.server.port) is Safe_UInt

        # Type conversion on URL
        url = self.server.url('/test')
        assert type(url) is Safe_Str__Url