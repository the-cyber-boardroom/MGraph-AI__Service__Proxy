import re
from osbot_utils.type_safe.primitives.safe_str.Safe_Str import Safe_Str

# HTTP header names: alphanumeric, hyphens, underscores
TYPE_SAFE_STR__HTTP__HEADER_NAME__REGEX = re.compile(r'[^a-zA-Z0-9\-_]')
TYPE_SAFE_STR__HTTP__HEADER_NAME__MAX_LENGTH = 128

# todo: refactor to OSBot-Utils

class Safe_Str__Http__Header_Name(Safe_Str):
    regex          = TYPE_SAFE_STR__HTTP__HEADER_NAME__REGEX
    max_length     = TYPE_SAFE_STR__HTTP__HEADER_NAME__MAX_LENGTH
    allow_empty    = False
    trim_whitespace = True


