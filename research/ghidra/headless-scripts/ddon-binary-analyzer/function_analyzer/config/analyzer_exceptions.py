# Analyzer Exceptions - Custom exception classes for error handling
# Provides structured exception handling for the analyzer system


class AnalyzerException(Exception):
    """Base exception for analyzer errors"""
    pass


class FunctionNotFoundException(AnalyzerException):
    """Function could not be found"""
    pass


class DecompilationException(AnalyzerException):
    """Decompilation failed"""
    pass


class ConfigurationException(AnalyzerException):
    """Configuration or setup error"""
    pass
