from osbot_utils.type_safe.Type_Safe                        import Type_Safe
from osbot_utils.type_safe.primitives.safe_float.Safe_Float import Safe_Float
from osbot_utils.type_safe.primitives.safe_uint.Safe_UInt   import Safe_UInt


class Schema__Proxy__Config(Type_Safe):                                      # Configuration for proxy service
    pool_connections : Safe_UInt   = Safe_UInt (10 )                         # Connection pool size
    pool_max_size    : Safe_UInt   = Safe_UInt (100)                         # Max pool size
    retry_count      : Safe_UInt   = Safe_UInt (3  )                         # Number of retries
    retry_backoff    : Safe_Float  = Safe_Float(0.3)                         # Backoff factor for retries
    connect_timeout  : Safe_UInt   = Safe_UInt (5  )                         # Connection timeout in seconds
    read_timeout     : Safe_UInt   = Safe_UInt (25 )                         # Read timeout in seconds
    verify_ssl       : bool        = False                                   # SSL verification (disable for dev)
    max_content_size : Safe_UInt   = Safe_UInt(104857600)                    # Max content size (100MB)

