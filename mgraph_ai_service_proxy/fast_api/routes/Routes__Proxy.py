from typing                                                             import Dict
from fastapi                                                            import Request, Response
from osbot_fast_api.api.routes.Fast_API__Routes                         import Fast_API__Routes
from osbot_utils.type_safe.primitives.safe_str.Safe_Str                 import Safe_Str
from osbot_utils.type_safe.primitives.safe_str.identifiers.Random_Guid  import Random_Guid
from mgraph_ai_service_proxy.schemas.Schema__Proxy__Request             import Schema__Proxy__Request
from mgraph_ai_service_proxy.service.proxy.Service__Proxy               import Service__Proxy

TAG__ROUTES_PROXY = 'proxy'

ROUTES_PATHS__PROXY   = [ f'/{TAG__ROUTES_PROXY}/{{path:path}}'  ,
                          f'/{TAG__ROUTES_PROXY}/proxy/stats'  ]

class Routes__Proxy(Fast_API__Routes):                                         # FastAPI routes for proxy functionality
    tag            : str           = TAG__ROUTES_PROXY
    proxy_service  : Service__Proxy


    def proxy_request(self, request: Request                          ,       # Main proxy endpoint
                            path   : str                                       # Path parameter from URL
                      ) -> Response:
        # Build proxy request from FastAPI request
        proxy_request = Schema__Proxy__Request(
            method       = Safe_Str(request.method)               ,
            path         = Safe_Str(path)                        ,
            host         = Safe_Str(request.headers.get('host', '')),
            headers      = dict(request.headers)                 ,
            body         = request.body() if request.method in ["POST", "PUT", "PATCH"] else None,
            query_string = Safe_Str(str(request.url.query)) if request.url.query else None,
            client_ip    = Safe_Str(request.client.host if request.client else "unknown"),
            use_https    = request.url.scheme == 'https'         ,
            request_id   = Random_Guid()
        )

        # Execute proxy request
        proxy_response = self.proxy_service.execute_request(proxy_request)

        # Return FastAPI response
        return Response(
            content     = proxy_response.content                 ,
            status_code = proxy_response.status_code            ,
            headers     = proxy_response.headers
        )

    def proxy__stats(self) -> Dict[str, int]:                                  # Get proxy statistics
        return self.proxy_service.stats_service.get_stats()

    def setup_routes(self):
        self.add_route_any(self.proxy_request, "/{path:path}")                # Catch-all route for proxy
        self.add_route_get(self.proxy__stats  )                                # Stats endpoint