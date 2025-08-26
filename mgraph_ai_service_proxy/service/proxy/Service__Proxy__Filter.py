from typing                                      import Dict
from osbot_utils.type_safe.Type_Safe             import Type_Safe


class Service__Proxy__Filter(Type_Safe):                                      # Filter headers and content for security

    REQUEST_SKIP_HEADERS = {                                                  # Headers to remove from requests
        'host', 'connection', 'upgrade', 'proxy-connection'     ,
        'proxy-authenticate', 'proxy-authorization'             ,
        'te', 'trailer', 'transfer-encoding', 'upgrade'         ,
        'keep-alive', 'x-forwarded-for', 'x-forwarded-proto'    ,
        'x-forwarded-host', 'x-real-ip', 'content-length'
    }

    RESPONSE_SKIP_HEADERS = {                                                 # Headers to remove from responses
        'connection', 'keep-alive', 'proxy-authenticate'        ,
        'proxy-authorization', 'te', 'trailer'                  ,
        'transfer-encoding', 'upgrade', 'content-encoding'      ,
        'content-length'
    }

    def filter_request_headers(self, headers: Dict[str, str]          ) -> Dict[str, str]:  # Filter request headers
        return {
            key: value for key, value in headers.items()
            if key.lower() not in self.REQUEST_SKIP_HEADERS
        }

    def filter_response_headers(self, headers: Dict[str, str]         ) -> Dict[str, str]:  # Filter response headers
        return {
            key: value for key, value in headers.items()
            if key.lower() not in self.RESPONSE_SKIP_HEADERS
        }

