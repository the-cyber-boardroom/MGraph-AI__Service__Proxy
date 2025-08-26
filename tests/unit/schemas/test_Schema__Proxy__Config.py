import pytest
from unittest                                                import TestCase
from osbot_utils.utils.Objects                               import base_classes, __
from osbot_utils.type_safe.Type_Safe                         import Type_Safe
from osbot_utils.type_safe.primitives.safe_uint.Safe_UInt    import Safe_UInt
from osbot_utils.type_safe.primitives.safe_float.Safe_Float  import Safe_Float
from mgraph_ai_service_proxy.schemas.Schema__Proxy__Config   import Schema__Proxy__Config


class test_Schema__Proxy__Config(TestCase):

    def test__init__(self):                                                   # Test default configuration
        with Schema__Proxy__Config() as _:
            assert type(_)         is Schema__Proxy__Config
            assert base_classes(_) == [Type_Safe, object]

            # Verify all defaults with .obj()
            assert _.obj() == __(pool_connections = 10        ,
                                 pool_max_size    = 100       ,
                                 retry_count      = 3         ,
                                 retry_backoff    = 0.3       ,
                                 connect_timeout  = 5         ,
                                 read_timeout     = 25        ,
                                 verify_ssl       = False     ,
                                 max_content_size = 104857600 )

    def test__init__with_custom_values(self):                                # Test custom configuration
        with Schema__Proxy__Config(pool_connections = 20      ,
                                   retry_count      = 5       ,
                                   verify_ssl       = True    ) as _:

            assert _.pool_connections == 20
            assert _.retry_count      == 5
            assert _.verify_ssl       == True
            assert _.read_timeout     == 25                                  # Default preserved

    def test_type_safety(self):                                              # Test type enforcement
        with Schema__Proxy__Config() as _:
            # Verify initial types
            assert type(_.pool_connections) is Safe_UInt
            assert type(_.pool_max_size)    is Safe_UInt
            assert type(_.retry_count)      is Safe_UInt
            assert type(_.retry_backoff)    is Safe_Float
            assert type(_.connect_timeout)  is Safe_UInt
            assert type(_.read_timeout)     is Safe_UInt
            assert type(_.verify_ssl)       is bool
            assert type(_.max_content_size) is Safe_UInt

    def test_type_auto_conversion(self):                                     # Test Type_Safe auto-conversion
        with Schema__Proxy__Config() as _:
            # int -> Safe_UInt
            _.pool_connections = 50
            assert _.pool_connections == 50
            assert type(_.pool_connections) is Safe_UInt

            # float -> Safe_Float
            _.retry_backoff = 1.5
            assert _.retry_backoff == 1.5
            assert type(_.retry_backoff) is Safe_Float

            # string -> Safe_UInt (numeric string)
            _.read_timeout = "30"
            assert _.read_timeout == 30
            assert type(_.read_timeout) is Safe_UInt

    def test_type_validation_errors(self):                                   # Test invalid type conversions
        with Schema__Proxy__Config() as _:
            # Negative values for Safe_UInt
            with pytest.raises(ValueError):
                _.pool_connections = -1

            # Non-numeric string
            with pytest.raises(ValueError):
                _.connect_timeout = "not-a-number"

            # Invalid bool conversion
            expected_error = "Invalid type for attribute 'verify_ssl'. Expected '<class 'bool'>' but got '<class 'str'>'"
            with pytest.raises(ValueError, match=expected_error):
                _.verify_ssl = "true"                                        # String doesn't convert to bool

    def test_serialization_round_trip(self):                                 # Test JSON serialization
        with Schema__Proxy__Config(pool_connections = 30                     ,
                                  retry_backoff    = 0.5                     ,
                                  verify_ssl       = True                    ) as original:

            json_data = original.json()

            # Verify JSON structure
            assert json_data == {'pool_connections' : 30                     ,
                               'pool_max_size'    : 100                      ,
                               'retry_count'      : 3                        ,
                               'retry_backoff'    : 0.5                      ,
                               'connect_timeout'  : 5                        ,
                               'read_timeout'     : 25                       ,
                               'verify_ssl'       : True                     ,
                               'max_content_size' : 104857600                }

            # Round-trip
            with Schema__Proxy__Config.from_json(json_data) as restored:
                assert restored.obj() == original.obj()

                # Verify types preserved
                assert type(restored.pool_connections) is Safe_UInt
                assert type(restored.retry_backoff)    is Safe_Float
