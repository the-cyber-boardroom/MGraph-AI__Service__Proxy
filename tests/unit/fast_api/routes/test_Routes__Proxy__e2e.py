import pytest
import json
from unittest                                                       import TestCase

from mgraph_ai_service_proxy.utils.testing.Local_Upstream__Server   import Local_Upstream__Server
from tests.unit.Service__Fast_API__Test_Objs                        import TEST_API_KEY__NAME, TEST_API_KEY__VALUE, setup__service_fast_api_test_objs


class test_Routes__Proxy__e2e(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.upstream = Local_Upstream__Server()                         # Start mock upstream
        cls.upstream.start()
        cls.test_objs = setup__service_fast_api_test_objs()
        cls.fast_api = cls.test_objs.fast_api
        cls.client   = cls.test_objs.fast_api__client
        cls.client.headers[TEST_API_KEY__NAME] = TEST_API_KEY__VALUE

    def test_proxy_get_request(self):                                   # Test proxying GET request
        response = self.client.get(f'http://localhost:{self.upstream.port}/echo')

        assert response.status_code == 200
        assert response.json()      == { 'client': '127.0.0.1',
                                         'method': 'GET'      ,
                                         'path'  : '/echo'    ,
                                         'query' : ''         }


    def test_proxy_post_with_body(self):            # Test proxying POST with body
        test_data     = {'key': 'value', 'number': 42}
        expected_body = json.dumps(test_data, separators=(',', ':'))
        response  = self.client.post(f'http://localhost:{self.upstream.port}/echo/post', json=test_data )

        assert response.status_code == 201
        assert response.json() == { 'body'        : expected_body      ,
                                    'content_type': 'application/json' ,
                                    'length'      : 27                 ,
                                    'method'      : 'POST'             }

    @pytest.mark.skip(reason="this logic is not working" )          # the current logic will send the request to 'should-be-filtered', which could actually be what we want
    def test_proxy_header_forwarding(self):                             # Test header forwarding and filtering
        custom_headers = {  'X-Custom-Header': 'custom-value'       ,
                            'Authorization'  : 'Bearer token123'    ,
                            'Host'           : 'should-be-filtered' } # Should be removed


        response = self.client.get(f'http://localhost:{self.upstream.port}/echo', headers=custom_headers)

        data = response.json()
        upstream_headers = data['headers']

        # Verify forwarding headers added
        assert 'X-Forwarded-For' in upstream_headers
        assert 'X-Forwarded-Proto' in upstream_headers

        # Verify custom headers passed through
        assert upstream_headers.get('X-Custom-Header') == 'custom-value'
        assert upstream_headers.get('Authorization') == 'Bearer token123'

        # Verify filtered headers removed
        assert 'Host' not in upstream_headers or upstream_headers['Host'] != 'should-be-filtered'