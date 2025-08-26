import re
from osbot_utils.type_safe.primitives.safe_str.Safe_Str import Safe_Str

TYPE_SAFE_STR__HTTP__METHOD__REGEX      = re.compile(r'[^A-Z]')     # HTTP methods are uppercase letters only
TYPE_SAFE_STR__HTTP__METHOD__MAX_LENGTH = 10                        # Longest standard method is "OPTIONS" (7 chars)

class Safe_Str__Http__Method(Safe_Str):
    regex          = TYPE_SAFE_STR__HTTP__METHOD__REGEX
    max_length     = TYPE_SAFE_STR__HTTP__METHOD__MAX_LENGTH
    allow_empty    = False
    trim_whitespace = True

    def __new__(cls, value=None):
        if value:
            value = str(value).upper()  # Force uppercase for HTTP methods
        return super().__new__(cls, value)


