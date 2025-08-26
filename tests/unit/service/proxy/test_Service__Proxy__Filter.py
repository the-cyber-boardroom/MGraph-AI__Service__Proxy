from unittest                                                       import TestCase
from osbot_utils.utils.Objects                                      import base_classes, __
from mgraph_ai_service_proxy.service.proxy.Service__Proxy__Filter   import Service__Proxy__Filter
from osbot_utils.type_safe.Type_Safe                                import Type_Safe

class test_Service__Proxy__Filter(TestCase):

    def test__init__(self):                                                   # Test auto-initialization
        with Service__Proxy__Filter() as _:
            assert type(_)         is Service__Proxy__Filter
            assert base_classes(_) == [Type_Safe, object]

            # Verify constants are defined
            assert len(_.REQUEST_SKIP_HEADERS) > 0
            assert len(_.RESPONSE_SKIP_HEADERS) > 0
            assert 'host' in _.REQUEST_SKIP_HEADERS
            assert 'connection' in _.RESPONSE_SKIP_HEADERS

    def test_filter_request_headers(self):                                   # Test basic request filtering
        with Service__Proxy__Filter() as _:
            input_headers = {
                'Host'             : 'example.com'                ,
                'User-Agent'       : 'test-client'                ,
                'Accept'           : 'application/json'           ,
                'Authorization'    : 'Bearer token123'
            }

            filtered = _.filter_request_headers(input_headers)

            assert filtered == {'User-Agent'    : 'test-client'              ,
                              'Accept'        : 'application/json'           ,
                              'Authorization' : 'Bearer token123'            }
            assert 'Host' not in filtered                                    # Host removed

    def test_filter_request_headers__removes_proxy_headers(self):            # Test proxy header removal
        with Service__Proxy__Filter() as _:
            input_headers = {
                'User-Agent'        : 'Mozilla/5.0'               ,
                'Connection'        : 'keep-alive'                ,           # Should be removed
                'Proxy-Connection'  : 'keep-alive'                ,           # Should be removed
                'Proxy-Authorization': 'Basic abc123'              ,           # Should be removed
                'Accept'            : '*/*'
            }

            filtered = _.filter_request_headers(input_headers)

            assert filtered == {'User-Agent' : 'Mozilla/5.0'                 ,
                              'Accept'     : '*/*'                           }

    def test_filter_request_headers__removes_forwarding_headers(self):       # Test forwarding header removal
        with Service__Proxy__Filter() as _:
            input_headers = {
                'Cookie'          : 'session=abc123'              ,
                'X-Forwarded-For' : '1.2.3.4'                     ,           # Should be removed
                'X-Forwarded-Proto': 'https'                       ,           # Should be removed
                'X-Forwarded-Host': 'original.com'                 ,           # Should be removed
                'X-Real-IP'       : '5.6.7.8'                     ,           # Should be removed
                'Accept-Language' : 'en-US'
            }

            filtered = _.filter_request_headers(input_headers)

            assert filtered == {'Cookie'         : 'session=abc123'          ,
                              'Accept-Language' : 'en-US'                    }

    def test_filter_request_headers__case_insensitive(self):                 # Test case-insensitive filtering
        with Service__Proxy__Filter() as _:
            input_headers = {
                'HOST'             : 'example.com'                ,           # Different case
                'connection'       : 'close'                      ,           # Lowercase
                'PROXY-CONNECTION' : 'keep-alive'                 ,           # Uppercase
                'Custom-Header'    : 'value'
            }

            filtered = _.filter_request_headers(input_headers)

            assert filtered == {'Custom-Header': 'value'}                    # Only custom header kept

    def test_filter_request_headers__empty_headers(self):                    # Test empty headers dict
        with Service__Proxy__Filter() as _:
            filtered = _.filter_request_headers({})
            assert filtered == {}

    def test_filter_response_headers(self):                                  # Test basic response filtering
        with Service__Proxy__Filter() as _:
            input_headers = {
                'Content-Type'     : 'application/json'           ,
                'Content-Length'   : '1234'                       ,           # Should be removed
                'Cache-Control'    : 'no-cache'                   ,
                'Set-Cookie'       : 'session=xyz'
            }

            filtered = _.filter_response_headers(input_headers)

            assert filtered == {'Content-Type'  : 'application/json'         ,
                              'Cache-Control' : 'no-cache'                   ,
                              'Set-Cookie'    : 'session=xyz'                }
            assert 'Content-Length' not in filtered

    def test_filter_response_headers__removes_connection_headers(self):      # Test connection header removal
        with Service__Proxy__Filter() as _:
            input_headers = {
                'Server'           : 'nginx/1.19.0'               ,
                'Connection'       : 'close'                      ,           # Should be removed
                'Keep-Alive'       : 'timeout=5'                  ,           # Should be removed
                'Transfer-Encoding': 'chunked'                     ,           # Should be removed
                'Date'             : 'Mon, 01 Jan 2024 12:00:00 GMT'
            }

            filtered = _.filter_response_headers(input_headers)

            assert filtered == {'Server' : 'nginx/1.19.0'                    ,
                              'Date'   : 'Mon, 01 Jan 2024 12:00:00 GMT'     }

    def test_filter_response_headers__removes_encoding(self):                # Test encoding header removal
        with Service__Proxy__Filter() as _:
            input_headers = {
                'Content-Type'     : 'text/html; charset=utf-8'   ,
                'Content-Encoding' : 'gzip'                       ,           # Should be removed (Lambda handles)
                'Vary'             : 'Accept-Encoding'             ,
                'ETag'             : '"abc123"'
            }

            filtered = _.filter_response_headers(input_headers)

            assert filtered == {'Content-Type' : 'text/html; charset=utf-8'  ,
                              'Vary'        : 'Accept-Encoding'              ,
                              'ETag'        : '"abc123"'                     }

    def test__both_filters_different_rules(self):                            # Test that filters have different rules
        with Service__Proxy__Filter() as _:
            # Header that should be removed from requests but not responses
            test_headers = {'Host': 'example.com'}

            request_filtered = _.filter_request_headers(test_headers)
            response_filtered = _.filter_response_headers(test_headers)

            assert request_filtered == {}                                    # Removed from requests
            assert response_filtered == {'Host': 'example.com'}              # Kept in responses

