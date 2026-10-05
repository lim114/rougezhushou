import json
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from rouge.chat import ProviderConfig, stream_chat

class ChatTests(unittest.TestCase):
    def test_stream_without_completion_marker_is_not_reported_as_finished(self):
        class Handler(BaseHTTPRequestHandler):
            def log_message(self,*_):pass
            def do_POST(self):
                self.rfile.read(int(self.headers['Content-Length']))
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'data: {"choices":[{"delta":{"content":"partial"}}]}\n\n')
        server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        threading.Thread(target=server.serve_forever,daemon=True).start()
        try:
            config=ProviderConfig(f'http://127.0.0.1:{server.server_port}/v1','fixture')
            with self.assertRaises(ConnectionError):
                list(stream_chat(config,[{'role':'user','content':'q'}],'',threading.Event()))
        finally:
            server.shutdown();server.server_close()
    def test_responses_semantic_events_stream_text_and_send_full_input(self):
        received = []
        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *_): pass
            def do_POST(self):
                received.append((self.path, json.loads(self.rfile.read(int(self.headers['Content-Length'])))))
                self.send_response(200)
                self.send_header('Content-Type','text/event-stream')
                self.end_headers()
                self.wfile.write(b'event: response.output_text.delta\ndata: {"type":"response.output_text.delta","delta":"answer"}\n\n')
                self.wfile.write(b'event: response.completed\ndata: {"type":"response.completed"}\n\n')
        server = ThreadingHTTPServer(('127.0.0.1',0),Handler)
        threading.Thread(target=server.serve_forever,daemon=True).start()
        try:
            history = [{'role':'user','content':'question'}]
            config = ProviderConfig(f'http://127.0.0.1:{server.server_port}/v1', 'fixture-model','responses')
            self.assertEqual(''.join(stream_chat(config,history,'',threading.Event())),'answer')
            self.assertEqual(received[0][0],'/v1/responses')
            self.assertEqual(received[0][1]['input'],history)
        finally:
            server.shutdown()
            server.server_close()
    def test_chat_completions_stream_preserves_history_and_returns_text(self):
        received = []
        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *_): pass
            def do_POST(self):
                received.append((self.path, json.loads(self.rfile.read(int(self.headers['Content-Length'])))))
                self.send_response(200)
                self.send_header('Content-Type', 'text/event-stream')
                self.end_headers()
                self.wfile.write(b'data: {"choices":[{"delta":{"content":"hello"}}]}\n\n')
                self.wfile.write(b'data: {"choices":[{"delta":{"content":" world"}}]}\n\ndata: [DONE]\n\n')
        server = ThreadingHTTPServer(('127.0.0.1',0), Handler)
        thread = threading.Thread(target=server.serve_forever,daemon=True)
        thread.start()
        try:
            config = ProviderConfig(f'http://127.0.0.1:{server.server_port}/v1', 'fixture-model', 'chat_completions')
            history = [{'role':'user','content':'first'},{'role':'assistant','content':'prior'},{'role':'user','content':'next'}]
            self.assertEqual(''.join(stream_chat(config, history, '', threading.Event())), 'hello world')
            self.assertEqual(received[0][0], '/v1/chat/completions')
            self.assertEqual(received[0][1]['messages'], history)
        finally:
            server.shutdown()
            server.server_close()
