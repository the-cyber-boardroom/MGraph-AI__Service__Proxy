from unittest                                                       import TestCase
from osbot_utils.type_safe.primitives.safe_str.web.Safe_Str__Url    import Safe_Str__Url
from osbot_utils.type_safe.type_safe_core.collections.Type_Safe__Dict import Type_Safe__Dict
from osbot_utils.utils.Objects                                      import base_classes, __
from osbot_utils.type_safe.Type_Safe                                import Type_Safe
from osbot_utils.type_safe.primitives.safe_uint.Safe_UInt           import Safe_UInt
from mgraph_ai_service_proxy.schemas.Schema__Proxy__Response        import Schema__Proxy__Response
from mgraph_ai_service_proxy.schemas.http.Safe_Str__Http__Header_Name import Safe_Str__Http__Header_Name


class test_Schema__Proxy__Response(TestCase):

    def test__init__(self):                                                     # Test auto-initialization
        with Schema__Proxy__Response() as _:
            assert type(_)         is Schema__Proxy__Response
            assert base_classes(_) == [Type_Safe, object]

            assert _.obj() == __(status_code = 0    ,                           # Verify auto-initialization
                                 headers     = __() ,
                                 content     = b''  ,
                                 target_url  = ''   )

            # Verify types
            assert type(_.status_code) is Safe_UInt
            assert type(_.headers)     is Type_Safe__Dict
            assert type(_.content)     is bytes
            assert type(_.target_url)  is Safe_Str__Url

    def test__init__with_values(self):                                          # Test initialization with data
        test_url = Safe_Str__Url("https://api.example.com/data")

        with Schema__Proxy__Response(status_code = 200                                  ,
                                     headers     = {"Content-Type": "application/json" },
                                     content     = b'{"result": "success"}'             ,
                                     target_url  = test_url                             ) as _:

            assert _.status_code == 200
            assert _.headers     == {Safe_Str__Http__Header_Name("Content-Type"): "application/json"}
            assert _.content     == b'{"result": "success"}'
            assert _.target_url  == test_url

    def test_type_auto_conversion(self):                                     # Test Type_Safe auto-conversion
        with Schema__Proxy__Response() as _:
            # int -> Safe_UInt
            _.status_code = 404
            assert _.status_code == 404
            assert type(_.status_code) is Safe_UInt

            # string -> Safe_UInt
            _.status_code = "500"
            assert _.status_code == 500
            assert type(_.status_code) is Safe_UInt

            # string -> Safe_Str__Url
            _.target_url = "http://example.com/api"
            assert type(_.target_url) is Safe_Str__Url
            assert _.target_url == "http://example.com/api"

    def test_headers_manipulation(self):                                     # Test headers dictionary
        with Schema__Proxy__Response() as _:
            _.headers["Server"] = "nginx/1.19.0"
            _.headers["Cache-Control"] = "no-cache"

            assert len(_.headers) == 2
            assert _.headers["Server"] == "nginx/1.19.0"

    def test_content_types(self):                                            # Test different content types
        with Schema__Proxy__Response() as _:
            # Binary content
            _.content = b'\x89PNG\r\n\x1a\n'
            assert _.content == b'\x89PNG\r\n\x1a\n'

            # Text as bytes
            _.content = b"Hello World"
            assert _.content == b"Hello World"

            # Empty content
            _.content = b''
            assert _.content == b''

    def test_serialization_round_trip(self):                                 # Test JSON serialization
        with Schema__Proxy__Response(status_code = 201                          ,
                                     headers     = {"Location": "/resource/123"},
                                     content     = b'created'                   ,
                                     target_url  = "https://api.test.com/create") as original:

            json_data = original.json()

            # Note: bytes may not round-trip perfectly through JSON
            assert json_data['status_code'] == 201
            assert json_data['headers'    ] == {Safe_Str__Http__Header_Name("Location"): "/resource/123"}
            assert json_data['target_url' ] == "https://api.test.com/create"

            with Schema__Proxy__Response.from_json(json_data) as restored:
                assert restored.status_code == original.status_code
                assert restored.headers == original.headers
                assert restored.target_url == original.target_url

                # Types preserved
                assert type(restored.status_code) is Safe_UInt
                assert type(restored.target_url) is Safe_Str__Url