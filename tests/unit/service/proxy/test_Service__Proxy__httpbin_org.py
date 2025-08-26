from unittest                                           import TestCase
from osbot_fast_api_serverless.utils.testing.skip_tests import skip__if_not__in_github_actions
from tests.unit.Service__Fast_API__Test_Objs            import setup__service_fast_api_test_objs, TEST_API_KEY__NAME, TEST_API_KEY__VALUE


class test_Service__Proxy__httpbin_org(TestCase):

    @classmethod
    def setUpClass(cls):
        skip__if_not__in_github_actions()
        cls.test_objs = setup__service_fast_api_test_objs()
        cls.fast_api = cls.test_objs.fast_api
        cls.client   = cls.test_objs.fast_api__client
        cls.client.headers[TEST_API_KEY__NAME] = TEST_API_KEY__VALUE

    def test_proxy_to_httpbin(self):    # Test against httpbin.org for real HTTP behavior

        # Test GET
        response = self.client.get('https://httpbin.org/get?test=value')
        assert response.status_code == 200
        data = response.json()
        assert data['args']['test'] == 'value'

        # Test POST
        response = self.client.post('https://httpbin.org/post', json={'key': 'value'})
        assert response.status_code == 200
        data = response.json()
        assert data['json'] == {'key': 'value'}