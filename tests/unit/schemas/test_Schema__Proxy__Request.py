from unittest                                                                   import TestCase
from osbot_utils.testing.__                                                     import __, __SKIP__
from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from osbot_utils.type_safe.primitives.safe_str.identifiers.Random_Guid          import Random_Guid
from osbot_utils.type_safe.primitives.safe_str.web.Safe_Str__IP_Address         import Safe_Str__IP_Address
from osbot_utils.type_safe.type_safe_core.collections.Type_Safe__Dict           import Type_Safe__Dict
from osbot_utils.utils.Objects                                                  import base_classes
from mgraph_ai_service_proxy.schemas.Schema__Proxy__Request                     import Schema__Proxy__Request
from mgraph_ai_service_proxy.schemas.http.Safe_Str__Http__Header_Name           import Safe_Str__Http__Header_Name
from mgraph_ai_service_proxy.schemas.http.Safe_Str__Http__Header_Value          import Safe_Str__Http__Header_Value
from mgraph_ai_service_proxy.schemas.http.Safe_Str__Http__Host                  import Safe_Str__Http__Host
from mgraph_ai_service_proxy.schemas.http.Safe_Str__Http__Method                import Safe_Str__Http__Method
from mgraph_ai_service_proxy.schemas.http.Safe_Str__Http__Path                  import Safe_Str__Http__Path
from mgraph_ai_service_proxy.schemas.http.Safe_Str__Http__Query_String          import Safe_Str__Http__Query_String


class test_Schema__Proxy__Request(TestCase):

    def test__init__(self):                                                   # Test auto-initialization
        with Schema__Proxy__Request() as _:
            assert type(_)         is Schema__Proxy__Request
            assert base_classes(_) == [Type_Safe, object]

            assert _.obj() == __(method       = None     ,                  # Verify auto-initialization with .obj()
                                 path         = ''       ,
                                 host         = ''       ,
                                 headers      = __()     ,                  # Empty dict as __
                                 body         = None     ,
                                 query_string = ''       ,
                                 client_ip    = ''       ,
                                 use_https    = True     ,                  # Default to HTTPS
                                 request_id   = __SKIP__ )                  # Skip auto-generated ID

            # Verify types
            assert type(_.path)       is Safe_Str__Http__Path
            assert type(_.headers)    is Type_Safe__Dict
            assert type(_.client_ip)  is Safe_Str__IP_Address
            assert type(_.use_https)  is bool
            assert type(_.request_id) is Random_Guid

    def test__init__with_values(self):                                       # Test initialization with data
        test_id = Random_Guid()

        with Schema__Proxy__Request(method       = "POST"                           ,
                                    path         = "/api/users"                     ,
                                    host         = "api.example.com"                ,
                                    headers      = {"Authorization": "Bearer token"},
                                    body         = b'{"user": "test"}'              ,
                                    query_string = "filter=active"                  ,
                                    client_ip    = "192.168.1.100"                  ,
                                    use_https    = False                            ,
                                    request_id   = test_id                          ) as _:

            assert _.method        == "POST"                                  # Auto-converted to Safe_Str
            assert _.path          == "/api/users"
            assert _.host          == "api.example.com"
            assert _.headers       == { Safe_Str__Http__Header_Name("Authorization"): Safe_Str__Http__Header_Value("Bearer token") }    # OK these are equal
            assert _.headers       == { Safe_Str__Http__Header_Name("Authorization"):                              "Bearer token"  }    # OK these are equal
            assert _.headers       != {                             "Authorization" : Safe_Str__Http__Header_Value("Bearer token") }    # BUG these should be equal
            assert _.body          == b'{"user": "test"}'
            assert _.query_string  == "filter=active"
            assert _.client_ip     == "192.168.1.100"
            assert _.use_https     == False
            assert _.request_id    == test_id
            assert "Authorization" == Safe_Str__Http__Header_Name("Authorization")
            assert "Bearer token"  == Safe_Str__Http__Header_Value("Bearer token")

            # Verify type conversions
            assert type(_.method)       is Safe_Str__Http__Method
            assert type(_.path)         is Safe_Str__Http__Path
            assert type(_.host)         is Safe_Str__Http__Host
            assert type(_.query_string) is Safe_Str__Http__Query_String
            assert type(_.client_ip)    is Safe_Str__IP_Address

    def test_type_auto_conversion(self):                                     # Test Safe_Str auto-conversion
        with Schema__Proxy__Request() as _:
            # String to Safe_Str__Http__Method
            _.method = "GET"
            assert type(_.method) is Safe_Str__Http__Method
            assert _.method == "GET"

            # Integer to Safe_Str__Http__Path
            _.path = 123
            assert type(_.path) is Safe_Str__Http__Path
            assert _.path == "123"

            # Special characters in Safe_Str__Http__Host
            _.host = "example.com!@#"
            assert type(_.host) is Safe_Str__Http__Host
            # Safe_Str may sanitize special chars

    def test_headers_as_dict(self):                                          # Test headers dictionary behavior
        with Schema__Proxy__Request() as _:
            _.headers["Content-Type"] = "application/json"
            _.headers["Accept"] = "*/*"

            assert len(_.headers) == 2
            assert _.headers["Content-Type"] == "application/json"

    def test_body_as_bytes(self):                                            # Test body handling
        with Schema__Proxy__Request() as _:
            assert _.body is None
            _.body = b"raw bytes data"                                      # Bytes body
            assert _.body == b"raw bytes data"
            assert type(_.body) is bytes



    def test_request_id_auto_generation(self):                               # Test auto-generated request ID
        with Schema__Proxy__Request() as req1:
            with Schema__Proxy__Request() as req2:
                assert req1.request_id != req2.request_id                    # Different IDs
                assert type(req1.request_id) is Random_Guid
                assert type(req2.request_id) is Random_Guid

    def test_serialization_round_trip(self):                                 # Test JSON serialization
        test_id = Random_Guid('d2f92e2b-ff12-4f09-a9ba-b240085f5f63')

        with Schema__Proxy__Request(method     = "PUT"                 ,
                                    path       = "/api/update"         ,
                                    host       = "api.test.com"        ,
                                    headers    = {"X_Custom": "value"} ,
                                    client_ip  = "10.0.0.1"            ,
                                    request_id = test_id               ) as original:

            json_data = original.json()

            with Schema__Proxy__Request.from_json(json_data) as restored:
                assert restored.json() == original.json()
                assert restored.json() == { 'body'        : None,
                                            'client_ip'   : '10.0.0.1',
                                            'headers'     : {Safe_Str__Http__Header_Name('X_Custom'): 'value'},
                                            'host'        : 'api.test.com',
                                            'method'      : 'PUT',
                                            'path'        : '/api/update',
                                            'query_string': '',
                                            'request_id'  : 'd2f92e2b-ff12-4f09-a9ba-b240085f5f63',
                                            'use_https'   : True}

                assert restored.obj() != __(method       = "PUT"                ,
                                            path         = "/api/update"        ,
                                            host         = "api.test.com"       ,
                                            headers      = __(X_Custom="value") ,       # BUG: this is failing due to a bug in OSBot-Utils
                                            body         = None                 ,
                                            query_string = ''                   ,
                                            use_https    = True                 ,
                                            client_ip    = "10.0.0.1"           ,
                                            request_id   = test_id              )

                # Types preserved
                assert type(restored.method    ) is Safe_Str__Http__Method
                assert type(restored.request_id) is Random_Guid

    def test__bug__comparision_miss_in_osbot_primitive__equality(self):
        with Schema__Proxy__Request(headers      = {"Authorization": "Bearer token"}) as _:
            assert _.headers == { Safe_Str__Http__Header_Name("Authorization"): Safe_Str__Http__Header_Value("Bearer token") }    # OK these are equal
            assert _.headers == { Safe_Str__Http__Header_Name("Authorization"):                              "Bearer token"  }    # OK these are equal
            assert _.headers != {                             "Authorization" : Safe_Str__Http__Header_Value("Bearer token") }    # BUG these should be equal
