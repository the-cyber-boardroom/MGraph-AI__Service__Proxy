# mgraph_ai_service_proxy/service/proxy/safe_types/Safe_Str__Http__Query_String.py

import re
from osbot_utils.type_safe.primitives.safe_str.Safe_Str import Safe_Str

# Allow typical query string characters
TYPE_SAFE_STR__HTTP__QUERY_STRING__REGEX      = re.compile(r'[^\w\-\._~:/?#\[\]@!$&\'()*+,;=%]')
TYPE_SAFE_STR__HTTP__QUERY_STRING__MAX_LENGTH = 2048

# todo: refactor to OSBot-Utils

class Safe_Str__Http__Query_String(Safe_Str):
    regex           = TYPE_SAFE_STR__HTTP__QUERY_STRING__REGEX
    max_length      = TYPE_SAFE_STR__HTTP__QUERY_STRING__MAX_LENGTH
    allow_empty     = True
    trim_whitespace = True
    regex_mode      = 'REPLACE'
