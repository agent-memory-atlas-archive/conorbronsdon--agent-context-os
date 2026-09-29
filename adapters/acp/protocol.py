"""Offline ACP message handling for future conformance clients.

No process, authentication, filesystem, terminal, or approval implementation.
The transport owner must enforce deadlines, bound input, and stop its own child
on EOF/protocol errors. Advertising no client tools does not sandbox an agent.
"""
from __future__ import annotations

from copy import deepcopy


class ProtocolError(ValueError):
    """The peer sent a message this bounded client cannot correlate."""


def _valid_id(value: object) -> bool:
    return type(value) in (int, str)


class Peer:
    """Correlate replies and refuse agent requests without implicit approval.

    receive returns (event, optional_reply). Events preserve provider payloads;
    callers consume them directly rather than accumulating an unbounded queue.
    This is a protocol foundation, not an installed-runtime conformance test.
    """

    def __init__(self) -> None:
        self._next_id = 1
        self._pending: dict[int, str] = {}

    def request(self, method: str, params: dict) -> dict:
        if not isinstance(method, str) or not method or not isinstance(params, dict):
            raise ProtocolError("request requires a method and object params")
        request_id = self._next_id
        self._next_id += 1
        self._pending[request_id] = method
        return {"jsonrpc": "2.0", "id": request_id, "method": method,
                "params": deepcopy(params)}

    def initialize(self) -> dict:
        return self.request("initialize", {
            "protocolVersion": 1,
            "clientInfo": {"name": "contextos-offline-conformance", "version": "0.1"},
            "clientCapabilities": {
                "fs": {"readTextFile": False, "writeTextFile": False},
                "terminal": False,
            },
        })

    @staticmethod
    def cancel(session_id: str) -> dict:
        if not isinstance(session_id, str) or not session_id:
            raise ProtocolError("cancel requires a session ID")
        return {"jsonrpc": "2.0", "method": "session/cancel",
                "params": {"sessionId": session_id}}

    def receive(self, message: object) -> tuple[dict, dict | None]:
        if not isinstance(message, dict) or message.get("jsonrpc") != "2.0":
            raise ProtocolError("expected one JSON-RPC 2.0 object")
        message = deepcopy(message)
        if "method" in message:
            method = message["method"]
            params = message.get("params", {})
            if (not isinstance(method, str) or not method
                    or not isinstance(params, dict)
                    or "result" in message or "error" in message):
                raise ProtocolError("malformed request or notification")
            if "id" not in message:
                return {"kind": "notification", "method": method, "params": params}, None
            request_id = message["id"]
            if not _valid_id(request_id):
                raise ProtocolError("invalid request ID")
            reply = {"jsonrpc": "2.0", "id": request_id}
            if method in ("session/request_permission", "cursor/ask_question",
                          "cursor/create_plan"):
                # ACP defines cancellation even when no reject option is offered.
                # Do not fabricate option IDs or choose allow_always/allow_once.
                reply["result"] = {"outcome": {"outcome": "cancelled"}}
            else:
                reply["error"] = {"code": -32601, "message": "Method not supported"}
            return {"kind": "refused_request", "method": method, "params": params}, reply

        request_id = message.get("id")
        if (type(request_id) is not int or request_id not in self._pending
                or ("result" in message) == ("error" in message)):
            raise ProtocolError("uncorrelated or malformed response")
        if "error" in message:
            error = message["error"]
            if (not isinstance(error, dict) or type(error.get("code")) is not int
                    or not isinstance(error.get("message"), str)):
                raise ProtocolError("malformed error response")
        method = self._pending.pop(request_id)
        return {"kind": "error" if "error" in message else "result",
                "method": method, "response": message}, None

    def close(self) -> dict[int, str]:
        """Return interrupted requests; EOF/cancel is never a successful result."""
        interrupted = self._pending.copy()
        self._pending.clear()
        return interrupted
