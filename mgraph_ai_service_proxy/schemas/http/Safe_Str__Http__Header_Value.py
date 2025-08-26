import re
from osbot_utils.type_safe.primitives.safe_str.Safe_Str import Safe_Str

# Header values can contain many characters but not control chars
TYPE_SAFE_STR__HTTP__HEADER_VALUE__REGEX        = re.compile(r'[\x00-\x1F\x7F]')  # Remove control characters
TYPE_SAFE_STR__HTTP__HEADER_VALUE__MAX_LENGTH   = 8192                            # Common header value limit

class Safe_Str__Http__Header_Value(Safe_Str):
    regex           = TYPE_SAFE_STR__HTTP__HEADER_VALUE__REGEX
    max_length      = TYPE_SAFE_STR__HTTP__HEADER_VALUE__MAX_LENGTH
    allow_empty     = True
    trim_whitespace = True
    regex_mode      = 'REPLACE'
