from typing                                                                     import Dict
from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from osbot_utils.type_safe.primitives.safe_str.identifiers.Random_Guid          import Random_Guid
from osbot_utils.type_safe.primitives.safe_str.web.Safe_Str__IP_Address         import Safe_Str__IP_Address
from mgraph_ai_service_proxy.schemas.http.Safe_Str__Http__Header_Name           import Safe_Str__Http__Header_Name
from mgraph_ai_service_proxy.schemas.http.Safe_Str__Http__Header_Value          import Safe_Str__Http__Header_Value
from mgraph_ai_service_proxy.schemas.http.Safe_Str__Http__Host                  import Safe_Str__Http__Host
from mgraph_ai_service_proxy.schemas.http.Safe_Str__Http__Method                import Safe_Str__Http__Method
from mgraph_ai_service_proxy.schemas.http.Safe_Str__Http__Path                  import Safe_Str__Http__Path
from mgraph_ai_service_proxy.schemas.http.Safe_Str__Http__Query_String          import Safe_Str__Http__Query_String


class Schema__Proxy__Request(Type_Safe):                                                # Incoming proxy request data
    method       : Safe_Str__Http__Method       = None                                  # HTTP method (GET, POST, etc.)
    path         : Safe_Str__Http__Path                                                 # Request path or full URL
    host         : Safe_Str__Http__Host                                                 # Target host (optional if full URL in path)
    headers      : Dict[Safe_Str__Http__Header_Name, Safe_Str__Http__Header_Value]      # Request headers with safe types
    body         : bytes                        = None                                  # Request body for POST/PUT
    query_string : Safe_Str__Http__Query_String                                         # Query parameters
    client_ip    : Safe_Str__IP_Address                                                 # Client IP address
    use_https    : bool                         = True                                  # Use HTTPS for target
    request_id   : Random_Guid                                                          # Unique request identifier

