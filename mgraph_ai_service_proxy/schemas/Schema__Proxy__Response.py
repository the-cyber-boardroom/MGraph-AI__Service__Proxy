from typing                                                         import Dict
from osbot_utils.type_safe.Type_Safe                                import Type_Safe
from osbot_utils.type_safe.primitives.safe_str.web.Safe_Str__Url    import Safe_Str__Url
from osbot_utils.type_safe.primitives.safe_uint.Safe_UInt           import Safe_UInt


class Schema__Proxy__Response(Type_Safe):                                     # Proxy response data
    status_code : Safe_UInt                                                   # HTTP status code
    headers     : Dict[str, str]                                              # Response headers
    content     : bytes                                                       # Response content
    target_url  : Safe_Str__Url                                               # Final target URL used





