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

    def filter_request_headers(self, headers: Dict[str, str]
                                ) -> Dict[str, str]:                        # Filter request headers
        filtered_headers: Dict[str, str] = {}                                   # Build a new dictionary with only the headers we want to keep

        for key, value in headers.items():
            lowercase_key = key.lower()  # normalize for comparison
            if lowercase_key not in self.REQUEST_SKIP_HEADERS:
                filtered_headers[key] = value  # preserve original casing

        return filtered_headers

    def filter_response_headers(self, headers: Dict[str, str]
                                 ) -> Dict[str, str]:                   # Filter response headers
        filtered_headers: Dict[str, str] = {}

        for key, value in headers.items():                              # Normalize the header key to lowercase for comparison
            lowercase_key = key.lower()
            if lowercase_key not in self.RESPONSE_SKIP_HEADERS:         # Only keep the header if it's not in the skip list
                filtered_headers[key] = value

        return filtered_headers

