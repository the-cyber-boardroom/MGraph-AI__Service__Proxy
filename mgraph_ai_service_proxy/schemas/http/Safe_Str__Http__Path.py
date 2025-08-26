import re
from osbot_utils.type_safe.primitives.safe_str.Safe_Str import Safe_Str

# Allow full URLs or paths with query strings, fragments, etc.
TYPE_SAFE_STR__HTTP__PATH__REGEX      = re.compile(r'[^\w\-\._~:/?#\[\]@!$&\'()*+,;=%]')
TYPE_SAFE_STR__HTTP__PATH__MAX_LENGTH = 2048  # Standard URL max length

class Safe_Str__Http__Path(Safe_Str):
    regex           = TYPE_SAFE_STR__HTTP__PATH__REGEX
    max_length      = TYPE_SAFE_STR__HTTP__PATH__MAX_LENGTH
    allow_empty     = True                                       # Root path "/" or empty
    trim_whitespace = True
    regex_mode      = 'REPLACE'                                  # Replace invalid chars rather than reject
