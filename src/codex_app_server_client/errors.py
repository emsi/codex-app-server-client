from __future__ import annotations

from typing import Any


class CodexError(Exception):
    """Base exception for the codex-app-server-client package."""


class CodexTransportError(CodexError):
    """Raised when the underlying transport fails or disconnects unexpectedly."""


class CodexTimeoutError(CodexError):
    """Raised when a request or turn completion exceeds its timeout."""


class CodexProtocolError(CodexError):
    """Raised when JSON-RPC or app-server protocol reports an error."""

    def __init__(
        self,
        message: str,
        *,
        code: int | None = None,
        data: Any = None,
    ) -> None:
        """Create a protocol error.

        Args:
            message: Human-readable description.
            code: Optional JSON-RPC error code.
            data: Optional protocol-provided error payload.
        """
        super().__init__(message)
        self.code = code
        self.data = data
