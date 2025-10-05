# Analyzer Configuration - Constants and settings for function analysis
# Contains all configuration constants used across the analyzer system


class AnalyzerConfig:
    """Configuration constants for the function decompilation analyzer.
    
    Centralizes all configuration values used throughout the function analyzer
    system, including timeouts, recursion limits, formatting settings, and
    function matching parameters. These constants ensure consistency across
    all analyzer components.
    """

    # Decompilation settings
    DECOMPILATION_TIMEOUT = 30

    # Recursion settings
    DEFAULT_RECURSION_DEPTH = 3
    MAX_RECURSION_DEPTH = 10

    # Output formatting
    OUTPUT_WIDTH = 80

    # Logging
    DEFAULT_LOG_LEVEL = "DEBUG"
    INFO_LOG_LEVEL = "INFO"

    # Function matching
    NAMESPACE_SEPARATOR = "::"
    TEMPLATE_START = "<"
    TEMPLATE_END = ">"

    # Function scoring weights
    SCORE_NAMESPACE_BONUS = 10
