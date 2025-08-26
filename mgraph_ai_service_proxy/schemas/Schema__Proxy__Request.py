from typing                                                                    import Dict
from osbot_utils.type_safe.Type_Safe                                           import Type_Safe
from osbot_utils.type_safe.primitives.safe_str.Safe_Str                        import Safe_Str
from osbot_utils.type_safe.primitives.safe_str.filesystem.Safe_Str__File__Path import Safe_Str__File__Path
from osbot_utils.type_safe.primitives.safe_str.identifiers.Safe_Id import Safe_Id


class Schema__Proxy__Request(Type_Safe):                                      # Incoming proxy request data
    method       : Safe_Str                                                   # HTTP method (GET, POST, etc.)
    path         : Safe_Str__File__Path                                       # Request path or full URL
    host         : Safe_Str          = None                                   # Target host (optional if full URL in path)
    headers      : Dict[str, str]                                             # Request headers
    body         : bytes             = None                                   # Request body for POST/PUT
    query_string : Safe_Str          = None                                   # Query parameters
    client_ip    : Safe_Str                                                   # Client IP address
    use_https    : bool              = True                                   # Use HTTPS for target
    request_id   : Safe_Id                                                    # Unique request identifier

