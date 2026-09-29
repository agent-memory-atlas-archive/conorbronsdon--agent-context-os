import unittest

from adapters.acp.protocol import Peer, ProtocolError


class AcpProtocolTest(unittest.TestCase):
    def test_interleaved_stream_and_out_of_order_responses(self):
        peer = Peer()
        init = peer.initialize()
        listing = peer.request("session/list", {})
        update = {"sessionId": "s1", "update": {
            "sessionUpdate": "agent_message_chunk", "content": {"type": "text", "text": "hello"}}}
        event, reply = peer.receive({"jsonrpc": "2.0", "method": "session/update", "params": update})
        self.assertEqual(update, event["params"])
        self.assertIsNone(reply)
        for request in (listing, init):
            event, reply = peer.receive({"jsonrpc": "2.0", "id": request["id"], "result": {}})
            self.assertEqual(request["method"], event["method"])
            self.assertIsNone(reply)
        self.assertEqual({}, peer.close())

    def test_permission_never_selects_an_allow_option(self):
        peer = Peer()
        for options in ([], [{"optionId": "provider-specific", "kind": "allow_always"}],
                        [{"optionId": "reject", "kind": "reject_once"}]):
            _, reply = peer.receive({"jsonrpc": "2.0", "id": "permission:9",
                "method": "session/request_permission", "params": {"options": options}})
            self.assertEqual("permission:9", reply["id"])
            self.assertEqual({"outcome": {"outcome": "cancelled"}}, reply["result"])

    def test_blocking_cursor_extensions_are_answered_without_approval(self):
        for method in ("cursor/ask_question", "cursor/create_plan"):
            event, reply = Peer().receive({"jsonrpc": "2.0", "id": 7, "method": method})
            self.assertEqual("refused_request", event["kind"])
            self.assertEqual("cancelled", reply["result"]["outcome"]["outcome"])

    def test_unsupported_tools_return_method_not_found(self):
        for method in ("fs/write_text_file", "fs/read_text_file", "terminal/create", "vendor/new"):
            _, reply = Peer().receive({"jsonrpc": "2.0", "id": 1, "method": method})
            self.assertEqual(-32601, reply["error"]["code"])

    def test_initialize_advertises_no_client_tools(self):
        caps = Peer().initialize()["params"]["clientCapabilities"]
        self.assertEqual({"fs": {"readTextFile": False, "writeTextFile": False},
                          "terminal": False}, caps)

    def test_cancel_is_notification_and_does_not_complete_pending_prompt(self):
        peer = Peer()
        prompt = peer.request("session/prompt", {"sessionId": "s1", "prompt": []})
        self.assertNotIn("id", peer.cancel("s1"))
        self.assertEqual({prompt["id"]: "session/prompt"}, peer.close())
        with self.assertRaises(ProtocolError):
            peer.receive({"jsonrpc": "2.0", "id": prompt["id"], "result": {}})

    def test_error_and_duplicate_response(self):
        peer = Peer()
        request = peer.request("session/load", {})
        message = {"jsonrpc": "2.0", "id": request["id"],
                   "error": {"code": -32000, "message": "Unavailable"}}
        event, _ = peer.receive(message)
        self.assertEqual("error", event["kind"])
        with self.assertRaises(ProtocolError):
            peer.receive(message)

    def test_malformed_messages_do_not_consume_pending_request(self):
        for malformed in ([], {}, {"jsonrpc": "2.0", "id": True, "result": {}},
                {"jsonrpc": "2.0", "id": [], "result": {}},
                {"jsonrpc": "2.0", "id": 1, "result": {}, "error": {}},
                {"jsonrpc": "2.0", "id": 1, "error": "oops"},
                {"jsonrpc": "2.0", "id": 1, "method": "x", "result": {}},
                {"jsonrpc": "2.0", "method": "x", "params": []}):
            with self.subTest(message=malformed):
                peer = Peer()
                peer.initialize()
                with self.assertRaises(ProtocolError):
                    peer.receive(malformed)
                self.assertEqual({1: "initialize"}, peer.close())


if __name__ == "__main__":
    unittest.main()
