from typing                                                 import Dict
from osbot_utils.type_safe.Type_Safe                        import Type_Safe
from osbot_utils.type_safe.primitives.safe_uint.Safe_UInt   import Safe_UInt
from mgraph_ai_service_proxy.schemas.Schema__Proxy__Request import Schema__Proxy__Request


class Service__Proxy__Stats(Type_Safe):                                       # Statistics tracking for proxy requests
    total_requests  : Safe_UInt                                               # Total number of requests processed
    total_errors    : Safe_UInt                                               # Total number of errors
    total_timeouts  : Safe_UInt                                               # Total number of timeouts

    def record_request(self, request  : Schema__Proxy__Request        ,       # Record successful request
                             status_code : int                                 # HTTP status code
                       ) -> None:
        self.total_requests = Safe_UInt(self.total_requests + 1)

    def record_error(self, request: Schema__Proxy__Request            ) -> None:  # Record connection error
        self.total_errors = Safe_UInt(self.total_errors + 1)

    def record_timeout(self, request: Schema__Proxy__Request          ) -> None:  # Record timeout error
        self.total_timeouts = Safe_UInt(self.total_timeouts + 1)

    def get_stats(self) -> Dict[str, int]:                                    # Get current statistics
        return { 'total_requests' : self.total_requests  ,
                 'total_errors'   : self.total_errors    ,
                 'total_timeouts' : self.total_timeouts  }



