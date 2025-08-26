import requests
import threading
from osbot_utils.type_safe.Type_Safe                                import Type_Safe
from osbot_utils.type_safe.primitives.safe_str.web.Safe_Str__Url    import Safe_Str__Url
from mgraph_ai_service_proxy.schemas.Schema__Proxy__Config          import Schema__Proxy__Config
from mgraph_ai_service_proxy.schemas.Schema__Proxy__Request         import Schema__Proxy__Request
from mgraph_ai_service_proxy.schemas.Schema__Proxy__Response        import Schema__Proxy__Response
from mgraph_ai_service_proxy.service.proxy.Service__Proxy__Filter   import Service__Proxy__Filter
from mgraph_ai_service_proxy.service.proxy.Service__Proxy__Stats    import Service__Proxy__Stats

thread_local = threading.local()                                                # Thread-local storage for session pooling

class Service__Proxy(Type_Safe):                                                # Core proxy service for forwarding HTTP requests
    config         : Schema__Proxy__Config                                      # Proxy configuration settings
    stats_service  : Service__Proxy__Stats                                      # Statistics tracking service
    filter_service : Service__Proxy__Filter                                     # Header and content filtering
    
    def setup(self) -> 'Service__Proxy':                                        # Initialize proxy service
        self.config          = Schema__Proxy__Config()
        self.stats_service   = Service__Proxy__Stats()
        self.filter_service  = Service__Proxy__Filter()
        return self

    # todo: see if need this pooling since this is running inside lambda
    def get_session(self) -> requests.Session:                               # Get thread-local requests session for pooling
        if not hasattr(thread_local, "session"):
            thread_local.session = requests.Session()
            adapter = requests.adapters.HTTPAdapter(pool_connections = self.config.pool_connections      ,
                                                    pool_maxsize     = self.config.pool_max_size        ,
                                                    max_retries      = requests.adapters.Retry(
                                                        total            = self.config.retry_count       ,
                                                        backoff_factor   = self.config.retry_backoff    ,
                                                        status_forcelist = [502, 503, 504]
                                                    )
            )
            thread_local.session.mount("http://" , adapter)
            thread_local.session.mount("https://", adapter)
            thread_local.session.timeout = (self.config.connect_timeout, self.config.read_timeout)
        return thread_local.session
    
    def build_target_url(self, request: Schema__Proxy__Request) -> Safe_Str__Url:  # Construct target URL from request
        if request.path.startswith('http://') or request.path.startswith('https://'):
            return Safe_Str__Url(request.path)
            
        if not request.host:
            raise ValueError("No target host specified in request")
            
        protocol   = 'https' if request.use_https else 'http'
        target_url = f"{protocol}://{request.host}{request.path}"
        
        if request.query_string:
            target_url += f"?{request.query_string}"
            
        return Safe_Str__Url(target_url)
    
    def execute_request(self, request: Schema__Proxy__Request) -> Schema__Proxy__Response:  # Execute proxied request
        target_url      = self.build_target_url(request)
        filtered_headers = self.filter_service.filter_request_headers(request.headers)
        
        # Add forwarding headers
        filtered_headers.update({ 'X-Forwarded-For'   : request.client_ip                       ,
                                  'X-Forwarded-Proto' : 'https' if request.use_https else 'http',
                                  'X-Forwarded-Host'  : request.host or ''                      })
        
        session = self.get_session()
        
        try:
            response = session.request( method          = request.method         ,
                                        url             = str(target_url)        ,
                                        headers         = filtered_headers       ,
                                        data            = request.body           ,
                                        allow_redirects = False                  ,
                                        stream          = True                   ,
                                        verify          = self.config.verify_ssl )
            
            response_headers = self.filter_service.filter_response_headers(dict(response.headers))
            
            # Update stats
            self.stats_service.record_request(request, response.status_code)
            
            return Schema__Proxy__Response( status_code = response.status_code ,
                                            headers     = response_headers     ,
                                            content     = response.content     ,
                                            target_url  = target_url           )
            
        except requests.Timeout:
            self.stats_service.record_timeout(request)
            raise ValueError(f"Gateway timeout for {target_url}")
        except requests.ConnectionError as e:
            self.stats_service.record_error(request)
            raise ValueError(f"Bad gateway - cannot connect to {target_url}: {str(e)}")

