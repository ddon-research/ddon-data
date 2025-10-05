# Core configuration for symbol exploration
#
# This module contains the centralized configuration constants and environment
# variable handling for DWARF symbol exploration.


class ExplorerConfig:
    """Centralized configuration constants for symbol exploration and C++ generation"""

    # Logging settings
    DEBUG_ENABLED = True
    LOG_LEVEL = "DEBUG"

    # Output formatting
    OUTPUT_WIDTH = 80
    INDENT_SIZE = 4
    MAX_LINE_LENGTH = 100

    # Type filtering and formatting
    BUILTIN_TYPES = frozenset({
        'void', 'char', 'short', 'int', 'long', 'float', 'double',
        'signed', 'unsigned', 'bool', 'wchar_t', 'char16_t', 'char32_t',
        'int8_t', 'int16_t', 'int32_t', 'int64_t',
        'uint8_t', 'uint16_t', 'uint32_t', 'uint64_t',
        'size_t', 'ptrdiff_t', 'nullptr_t'
    })

    MAX_INHERITANCE_DEPTH = 10
    MAX_TEMPLATE_PARAMS = 20

    # Search patterns
    IGNORED_NAMESPACES = frozenset({'std', '__gnu_cxx', '__cxxabiv1'})
    DEFAULT_TEMPLATE_FILTER = ".*<.*>.*"

    # Simplified environment access - use os.environ.get() directly instead of these wrappers
