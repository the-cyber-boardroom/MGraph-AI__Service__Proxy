from unittest                                               import TestCase
from osbot_fast_api.api.Fast_API                            import Fast_API
from mgraph_ai_service_proxy.fast_api.routes.Routes__Proxy import Routes__Proxy, ROUTES_PATHS__PROXY


class test_Routes__Proxy(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.routes_proxy = Routes__Proxy()


    def test_route_paths(self):
        with Fast_API() as _:
            _.add_routes(Routes__Proxy)

            assert _.routes_paths() == sorted(ROUTES_PATHS__PROXY)