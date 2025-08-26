import re
import pytest
import requests
import threading
from unittest                                                           import TestCase
from unittest.mock                                                      import Mock, patch
from osbot_utils.testing.__                                             import __
from osbot_utils.type_safe.primitives.safe_str.web.Safe_Str__IP_Address import Safe_Str__IP_Address
from osbot_utils.type_safe.primitives.safe_str.web.Safe_Str__Url        import Safe_Str__Url
from osbot_utils.utils.Objects                                          import base_classes
from mgraph_ai_service_proxy.schemas.Schema__Proxy__Config              import Schema__Proxy__Config
from mgraph_ai_service_proxy.schemas.Schema__Proxy__Request             import Schema__Proxy__Request
from mgraph_ai_service_proxy.schemas.Schema__Proxy__Response            import Schema__Proxy__Response
from mgraph_ai_service_proxy.schemas.http.Safe_Str__Http__Header_Name   import Safe_Str__Http__Header_Name
from mgraph_ai_service_proxy.schemas.http.Safe_Str__Http__Host          import Safe_Str__Http__Host
from mgraph_ai_service_proxy.schemas.http.Safe_Str__Http__Method        import Safe_Str__Http__Method
from mgraph_ai_service_proxy.schemas.http.Safe_Str__Http__Path          import Safe_Str__Http__Path
from mgraph_ai_service_proxy.service.proxy.Service__Proxy               import Service__Proxy
from mgraph_ai_service_proxy.service.proxy.Service__Proxy__Stats        import Service__Proxy__Stats
from mgraph_ai_service_proxy.service.proxy.Service__Proxy__Filter       import Service__Proxy__Filter
from osbot_utils.type_safe.Type_Safe                                    import Type_Safe
from osbot_utils.type_safe.primitives.safe_str.identifiers.Random_Guid  import Random_Guid

class test_Service__Proxy(TestCase):

    @classmethod
    def setUpClass(cls):                                                      # ONE-TIME expensive setup
        cls.service = Service__Proxy().setup()                                # Initialize service once

        # Define reusable test data
        cls.test_request_simple = Schema__Proxy__Request( method       = Safe_Str__Http__Method("GET")             ,
                                                          path         = Safe_Str__Http__Path("/api/test")         ,
                                                          host         = Safe_Str__Http__Host("example.com")       ,
                                                          headers      = {"User-Agent": "test-client"}             ,
                                                          client_ip    = Safe_Str__IP_Address("192.168.1.1")       ,
                                                          request_id   = Random_Guid()                             )
        cls.test_request_post = Schema__Proxy__Request  ( method       = Safe_Str__Http__Method("POST")                       ,
                                                          path         = Safe_Str__Http__Path("/api/users")                 ,
                                                          host         = Safe_Str__Http__Host("api.example.com")            ,
                                                          headers      = {"Content-Type": "application/json"}   ,
                                                          body         = b'{"name": "test"}'                    ,
                                                          client_ip    = Safe_Str__IP_Address("10.0.0.1")                   ,
                                                          use_https    = True                                   ,
                                                          request_id   = Random_Guid()                          )

    def test__init__(self):                                                   # Test auto-initialization
        with Service__Proxy() as _:
            assert type(_)         is Service__Proxy
            assert base_classes(_) == [Type_Safe, object]

            # Before setup, services are None
            assert type(_.config)         is Schema__Proxy__Config
            assert type(_.stats_service)  is Service__Proxy__Stats
            assert type(_.filter_service) is Service__Proxy__Filter

    def test_setup(self):                                                     # Test service setup initialization
        with Service__Proxy() as _:
            result = _.setup()

            assert result is _                                                # Returns self for chaining
            assert type(_.config)         is Schema__Proxy__Config
            assert type(_.stats_service)  is Service__Proxy__Stats
            assert type(_.filter_service) is Service__Proxy__Filter

            # Verify config defaults with .obj()
            assert _.config.obj() == __(pool_connections = 10        ,
                                        pool_max_size    = 100       ,
                                        retry_count      = 3         ,
                                        retry_backoff    = 0.3       ,
                                        connect_timeout  = 5         ,
                                        read_timeout     = 25        ,
                                        verify_ssl       = False     ,
                                        max_content_size = 104857600 )

    def test_get_session(self):                                              # Test thread-local session pooling
        with self.service as _:
            session1 = _.get_session()
            session2 = _.get_session()

            assert session1                is session2                        # Same session (thread-local)
            assert type(session1).__name__ == 'Session'
            assert session1.timeout        == (5, 25)                         # (connect, read) timeouts

    def test_get_session__thread_isolation(self):                             # Test sessions are thread-isolated

        sessions = []

        def get_session_in_thread():
            with self.service as _:
                sessions.append(_.get_session())

        thread1 = threading.Thread(target=get_session_in_thread)
        thread2 = threading.Thread(target=get_session_in_thread)

        thread1.start()
        thread2.start()
        thread1.join()
        thread2.join()

        # Different threads should get different sessions
        assert len(sessions) == 2
        assert sessions[0] is not sessions[1]                                # Different sessions

    def test_build_target_url(self):                                         # Test basic URL construction
        with self.service as _:
            url = _.build_target_url(self.test_request_simple)
            assert type(url) is Safe_Str__Url
            assert url == "https://example.com/api/test"

    def test_build_target_url__with_https(self):                             # Test HTTPS URL construction
        with self.service as _:
            request = Schema__Proxy__Request(method    = "GET"                ,
                                             path      = "/secure/data"       ,
                                             host      = "secure.example.com" ,
                                             use_https = True                           )
            url = _.build_target_url(request)
            assert url == "https://secure.example.com/secure/data"

    def test_build_target_url__with_query_string(self):                      # Test URL with query parameters
        with self.service as _:
            request = Schema__Proxy__Request(method       = "GET"                    ,
                                             path         = "/search"                ,
                                             host         = "api.example.com"        ,
                                             query_string = "q=test&limit=10&page=2" ,
                                             use_https    = False                    )
            url = _.build_target_url(request)
            assert url == "http://api.example.com/search?q=test&limit=10&page=2"

    def test_build_target_url__full_url_in_path(self):                       # Test when path contains full URL
        with self.service as _:
            request = Schema__Proxy__Request(method = Safe_Str__Http__Method("GET")                            ,
                                             path   = Safe_Str__Http__Path  ("https://external.api.com/v1/data"))
            url = _.build_target_url(request)
            assert type(url) is Safe_Str__Url
            assert url == "https://external.api.com/v1/data"

    def test_build_target_url__http_full_url(self):                          # Test HTTP full URL in path
        with self.service as _:
            request = Schema__Proxy__Request(method = "GET"                          ,
                                             path   = "http://insecure.api.com/data" )
            url = _.build_target_url(request)
            assert url == "http://insecure.api.com/data"

    def test_build_target_url__missing_host(self):                          # Test error when host missing
        with self.service as _:
            request = Schema__Proxy__Request(method = Safe_Str__Http__Method("GET")                          ,
                                             path   = Safe_Str__Http__Path  ("/api/test")                    ,
                                             host   = None                              )

            error_message = "No target host specified in request"
            with pytest.raises(ValueError, match=re.escape(error_message)):
                _.build_target_url(request)

    def test_build_target_url__empty_host(self):                             # Test error with empty host
        with self.service as _:
            request = Schema__Proxy__Request(method = "GET"        ,
                                             path   = "/api/test"  ,
                                             host   = ""           )

            error_message = "No target host specified in request"
            with pytest.raises(ValueError, match=re.escape(error_message)):
                _.build_target_url(request)

    @patch('requests.Session.request')
    def test_execute_request(self, mock_request):                            # Test successful request execution
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.content = b'{"success": true}'
        mock_request.return_value = mock_response

        with self.service as _:
            response = _.execute_request(self.test_request_simple)

            assert type(response) is Schema__Proxy__Response
            assert response.status_code                        == 200
            assert response.content                            == b'{"success": true}'
            assert Safe_Str__Http__Header_Name("Content-Type") in response.headers
            assert type(response.target_url) is Safe_Str__Url

            mock_request.assert_called_once()                               # Verify request was made with correct parameters
            call_args = mock_request.call_args
            assert call_args[1]['method'] == 'GET'
            assert call_args[1]['url'   ] == 'https://example.com/api/test'

    @patch('requests.Session.request')
    def test_execute_request__with_body(self, mock_request):                 # Test POST request with body
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.headers = {"Location": "/api/users/123"}
        mock_response.content = b'{"id": "123"}'
        mock_request.return_value = mock_response

        with self.service as _:
            response = _.execute_request(self.test_request_post)

            assert response.status_code == 201
            assert response.content == b'{"id": "123"}'

            call_args = mock_request.call_args                              # Verify body was sent
            assert call_args[1]['data'] == b'{"name": "test"}'
            assert call_args[1]['method'] == 'POST'

    @patch('requests.Session.request')
    def test_execute_request__adds_forwarding_headers(self, mock_request):   # Test forwarding headers added
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.content = b''
        mock_request.return_value = mock_response

        with self.service as _:
            _.execute_request(self.test_request_simple)

            call_args = mock_request.call_args
            headers = call_args[1]['headers']

            assert 'X-Forwarded-For' in headers
            assert headers['X-Forwarded-For'] == '192.168.1.1'
            assert headers['X-Forwarded-Proto'] == 'https'
            assert headers['X-Forwarded-Host'] == 'example.com'

    @patch('requests.Session.request')
    def test_execute_request__timeout_error(self, mock_request):             # Test timeout handling
        mock_request.side_effect = requests.Timeout("Connection timeout")

        with self.service as _:
            error_message = "Gateway timeout for https://example.com/api/test"
            with pytest.raises(ValueError, match=re.escape(error_message)):
                _.execute_request(self.test_request_simple)

            # Verify stats were updated
            assert _.stats_service.total_timeouts == 1

    @patch('requests.Session.request')
    def test_execute_request__connection_error(self, mock_request):          # Test connection error handling
        mock_request.side_effect = requests.ConnectionError("Connection refused")

        with self.service as _:
            with pytest.raises(ValueError, match="Bad gateway - cannot connect to"):
                _.execute_request(self.test_request_simple)

            # Verify stats were updated
            assert _.stats_service.total_errors == 1

    @patch('requests.Session.request')
    def test_execute_request__stats_updated(self, mock_request):             # Test statistics tracking
        mock_response             = Mock()
        mock_response.status_code = 404
        mock_response.headers     = {}
        mock_response.content     = b'Not found'
        mock_request.return_value = mock_response

        with self.service as _:
            _.stats_service.total_requests = 0                              # Reset stats
            _.stats_service.total_errors   = 0

            _.execute_request(self.test_request_simple)                     # Make multiple requests
            _.execute_request(self.test_request_simple)

            assert _.stats_service.total_requests == 2
            assert _.stats_service.total_errors   == 0                      # 404 is not connection error
            assert _.stats_service.total_timeouts == 0