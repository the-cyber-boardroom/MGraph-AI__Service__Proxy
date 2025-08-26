from typing                                                             import Dict
from fastapi import Request, Response, Body
from osbot_fast_api.api.routes.Fast_API__Routes                         import Fast_API__Routes
from osbot_utils.type_safe.primitives.safe_str.identifiers.Random_Guid  import Random_Guid
from osbot_utils.type_safe.primitives.safe_str.web.Safe_Str__IP_Address import Safe_Str__IP_Address
from mgraph_ai_service_proxy.schemas.Schema__Proxy__Request             import Schema__Proxy__Request
from mgraph_ai_service_proxy.schemas.http.Safe_Str__Http__Host          import Safe_Str__Http__Host
from mgraph_ai_service_proxy.schemas.http.Safe_Str__Http__Method        import Safe_Str__Http__Method
from mgraph_ai_service_proxy.schemas.http.Safe_Str__Http__Path          import Safe_Str__Http__Path
from mgraph_ai_service_proxy.schemas.http.Safe_Str__Http__Query_String  import Safe_Str__Http__Query_String
from mgraph_ai_service_proxy.service.proxy.Service__Proxy               import Service__Proxy

TAG__ROUTES_PROXY = '/'

ROUTES_PATHS__PROXY   = [ '/{path:path}'  ,
                          '/proxy/stats'  ]

class Routes__Proxy(Fast_API__Routes):                                         # FastAPI routes for proxy functionality
    tag            : str           = TAG__ROUTES_PROXY
    proxy_service  : Service__Proxy

    # todo: move to a helper class
    def get_client_ip(self, request: Request            # Extract client IP address from request, checking proxy headers first.
                       ) -> Safe_Str__IP_Address:       # Returns None value if no valid IP can be determined.

        # Check for common proxy headers (in order of preference)
        proxy_headers = [   'X-Forwarded-For' ,  # Standard proxy header, may contain multiple IPs
                            'X-Real-IP'       ,  # Common nginx header
                            'CF-Connecting-IP',  # Cloudflare
                            'True-Client-IP'  ,  # Cloudflare Enterprise
                            'X-Client-IP'     ]  # Some proxies

        for header in proxy_headers:
            ip_value = request.headers.get(header, '').strip()
            if ip_value:
                if header == 'X-Forwarded-For' and ',' in ip_value:     # X-Forwarded-For can contain multiple IPs (client, proxy1, proxy2...) Take the first one (leftmost) which should be the original client
                    ip_value = ip_value.split(',')[0].strip()

                try:                                                    # Validate it's an actual IP address
                    return Safe_Str__IP_Address(ip_value)                      # This will validate

                except ValueError:
                    continue  # Try next header

        if request.client and request.client.host:                          # Fall back to request.client if no proxy headers found
            try:
                return Safe_Str__IP_Address(request.client.host)            # Check if it's already an IP address

            except ValueError:                                              # will happen for example when it is hostname (like "testclient" in tests)
                pass
        return None

    def proxy_request(self, request: Request                ,       # Main proxy endpoint
                            path   : str                    ,       # Path parameter from URL
                       ) -> Response:
        client_ip = self.get_client_ip(request)

        body = getattr(request.state, 'body', None)         # get body from middleware

        # Build proxy request from FastAPI request          # todo: there is too much happening below, refact this to an helper method that converts Request into Schema__Proxy__Request
        proxy_request = Schema__Proxy__Request( method       = Safe_Str__Http__Method(request.method)                   ,
                                                path         = Safe_Str__Http__Path  (path)                             ,
                                                host         = Safe_Str__Http__Host  (request.headers.get('host', ''))  ,
                                                headers      = dict(request.headers)                                    ,
                                                body         = body      ,# request.body() if request.method in ["POST", "PUT", "PATCH"] else None,
                                                query_string = Safe_Str__Http__Query_String(str(request.url.query)) if request.url.query else None,
                                                client_ip    = client_ip                                ,
                                                use_https    = request.url.scheme == 'https'            ,
                                                request_id   = Random_Guid()
        )

        proxy_response = self.proxy_service.execute_request(proxy_request)      # Execute proxy request

        return Response(content     = proxy_response.content      ,             # Return FastAPI response
                        status_code = proxy_response.status_code  ,
                        headers     = proxy_response.headers      )

    def proxy__stats(self) -> Dict[str, int]:                                   # Get proxy statistics
        return self.proxy_service.stats_service.get_stats()



    # todo: remove when next version of the osbot-fast-api has been configured
    def setup(self):
        self.setup_routes()
        if self.prefix == '/':
            self.app.include_router(self.router, tags=[self.tag])
        else:
            self.app.include_router(self.router, prefix=self.prefix, tags=[self.tag])
        return self

    def setup_routes(self):
        self.add_route_any(self.proxy_request, "/{path:path}")                # Catch-all route for proxy
        self.add_route_get(self.proxy__stats  )                                # Stats endpoint