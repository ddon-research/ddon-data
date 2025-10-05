# Output handlers for symbol exploration
#
# This module provides output handling capabilities for managing
# results in headless PyGhidra mode.


class HeadlessOutputHandler:
    """Simplified handler for managing output in headless PyGhidra mode"""

    def __init__(self):
        pass  # No buffering needed

    def write(self, content: str) -> None:
        """Write content directly to stdout"""
        print(content)

    def flush(self) -> None:
        """Flush is now a no-op since we write directly"""
        pass
