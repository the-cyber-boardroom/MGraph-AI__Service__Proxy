import re
from osbot_utils.type_safe.primitives.safe_str.Safe_Str import Safe_Str

# Allow domain names with ports (example.com:8080)
TYPE_SAFE_STR__HTTP__HOST__REGEX      = re.compile(r'[^a-zA-Z0-9\-.:_]')
TYPE_SAFE_STR__HTTP__HOST__MAX_LENGTH = 256                                 # Max domain name length

# todo: refactor to OSBot-Utils

class Safe_Str__Http__Host(Safe_Str):
    regex           = TYPE_SAFE_STR__HTTP__HOST__REGEX
    max_length      = TYPE_SAFE_STR__HTTP__HOST__MAX_LENGTH
    allow_empty     = True                                                  # Can be None for full URL in path
    trim_whitespace = True
    regex_mode      = 'REPLACE'

