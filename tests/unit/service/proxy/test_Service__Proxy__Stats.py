from unittest                                                            import TestCase
from osbot_utils.utils.Objects                                          import base_classes, __

from mgraph_ai_service_proxy.schemas.Schema__Proxy__Request import Schema__Proxy__Request
from mgraph_ai_service_proxy.schemas.http.Safe_Str__Http__Host import Safe_Str__Http__Host
from mgraph_ai_service_proxy.schemas.http.Safe_Str__Http__Method import Safe_Str__Http__Method
from mgraph_ai_service_proxy.schemas.http.Safe_Str__Http__Path import Safe_Str__Http__Path
from mgraph_ai_service_proxy.service.proxy.Service__Proxy__Stats        import Service__Proxy__Stats
from osbot_utils.type_safe.Type_Safe                                   import Type_Safe
from osbot_utils.type_safe.primitives.safe_uint.Safe_UInt              import Safe_UInt

class test_Service__Proxy__Stats(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_request = Schema__Proxy__Request(method = Safe_Str__Http__Method("GET"        ),
                                                  path   = Safe_Str__Http__Path  ("/test"      ),
                                                  host   = Safe_Str__Http__Host  ("example.com"))

    def test__init__(self):                                                   # Test auto-initialization
        with Service__Proxy__Stats() as _:
            assert type(_)         is Service__Proxy__Stats
            assert base_classes(_) == [Type_Safe, object]

            # Verify all counters start at zero
            assert _.obj() == __(total_requests = 0                          ,
                                total_errors   = 0                            ,
                                total_timeouts = 0                            )

            # Verify types
            assert type(_.total_requests) is Safe_UInt
            assert type(_.total_errors)   is Safe_UInt
            assert type(_.total_timeouts) is Safe_UInt

    def test_record_request(self):                                           # Test request counting
        with Service__Proxy__Stats() as _:
            _.record_request(self.test_request, 200)
            assert _.total_requests == 1

            _.record_request(self.test_request, 404)
            assert _.total_requests == 2

            _.record_request(self.test_request, 500)
            assert _.total_requests == 3

    def test_record_request__multiple_calls(self):                           # Test multiple request recording
        with Service__Proxy__Stats() as _:
            for i in range(10):
                _.record_request(self.test_request, 200)

            assert _.total_requests == 10
            assert type(_.total_requests) is Safe_UInt                       # Type preserved

    def test_record_error(self):                                             # Test error counting
        with Service__Proxy__Stats() as _:
            assert _.total_errors == 0

            _.record_error(self.test_request)
            assert _.total_errors == 1

            _.record_error(self.test_request)
            assert _.total_errors == 2

    def test_record_timeout(self):                                           # Test timeout counting
        with Service__Proxy__Stats() as _:
            assert _.total_timeouts == 0

            _.record_timeout(self.test_request)
            assert _.total_timeouts == 1

            for i in range(5):
                _.record_timeout(self.test_request)

            assert _.total_timeouts == 6

    def test_get_stats(self):                                                # Test stats retrieval as dict
        with Service__Proxy__Stats() as _:
            # Initial state
            stats = _.get_stats()
            assert stats == {'total_requests' : 0                            ,
                           'total_errors'   : 0                              ,
                           'total_timeouts' : 0                              }

            # Record various events
            _.record_request(self.test_request, 200)
            _.record_request(self.test_request, 500)
            _.record_error(self.test_request)
            _.record_timeout(self.test_request)

            # Verify updated stats
            stats = _.get_stats()
            assert stats == {'total_requests' : 2                            ,
                           'total_errors'   : 1                              ,
                           'total_timeouts' : 1                              }

    def test__mixed_operations(self):                                        # Test mixed stat operations
        with Service__Proxy__Stats() as _:
            # Simulate realistic usage pattern
            _.record_request(self.test_request, 200)                         # Success
            _.record_request(self.test_request, 200)                         # Success
            _.record_timeout(self.test_request)                              # Timeout
            _.record_request(self.test_request, 200)                         # Success
            _.record_error(self.test_request)                                # Connection error
            _.record_request(self.test_request, 404)                         # Not found
            _.record_request(self.test_request, 500)                         # Server error

            assert _.obj() == __(total_requests = 5                          ,
                                total_errors   = 1                            ,
                                total_timeouts = 1                            )
