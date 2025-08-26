from osbot_fast_api.api.routes.Routes__Set_Cookie               import Routes__Set_Cookie
from osbot_fast_api_serverless.fast_api.Serverless__Fast_API    import Serverless__Fast_API
from starlette.middleware.base                                  import BaseHTTPMiddleware
from mgraph_ai_service_proxy.config                             import FAST_API__TITLE
from mgraph_ai_service_proxy.fast_api.routes.Routes__Info       import Routes__Info
from mgraph_ai_service_proxy.fast_api.routes.Routes__Proxy      import Routes__Proxy
from mgraph_ai_service_proxy.utils.Version                      import version__mgraph_ai_service_proxy

# todo: refactor this into a separate class (and maybe even to the Fast_API class), once we confirm that it works ok
from fastapi import Request
class BodyReaderMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Only read body for certain methods
        if request.method in ["POST", "PUT", "PATCH"]:
            body = await request.body()
            # Store it in request state for later sync access
            request.state.body = body
        else:
            request.state.body = None

        response = await call_next(request)
        return response

class Service__Fast_API(Serverless__Fast_API):
    name    = FAST_API__TITLE
    version = version__mgraph_ai_service_proxy

    def setup_middlewares(self):
        super().setup_middlewares()
        self.app().add_middleware(BodyReaderMiddleware)
        return self

    def setup_routes(self):
        self.add_routes(Routes__Info  )
        self.add_routes(Routes__Set_Cookie)
        self.add_routes(Routes__Proxy )                                       # Add proxy routes