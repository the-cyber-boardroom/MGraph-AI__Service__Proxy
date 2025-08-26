from typing                                                             import Dict
from osbot_utils.type_safe.Type_Safe                                    import Type_Safe
from osbot_utils.type_safe.primitives.safe_str.web.Safe_Str__Url        import Safe_Str__Url
from osbot_utils.type_safe.primitives.safe_uint.Safe_UInt               import Safe_UInt
from mgraph_ai_service_proxy.schemas.http.Safe_Str__Http__Header_Name   import Safe_Str__Http__Header_Name
from mgraph_ai_service_proxy.schemas.http.Safe_Str__Http__Header_Value  import Safe_Str__Http__Header_Value


class Schema__Proxy__Response(Type_Safe):                                           # Proxy response data
    status_code : Safe_UInt                                                         # HTTP status code
    headers     : Dict[Safe_Str__Http__Header_Name, Safe_Str__Http__Header_Value]   # Response headers with safe types
    content     : bytes                                                             # Response content
    target_url  : Safe_Str__Url                                                     # Final target URL used





