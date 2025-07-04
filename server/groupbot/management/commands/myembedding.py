from django.core.management.base import BaseCommand
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import threading
from sentence_transformers import SentenceTransformer
from urllib.parse import urlparse
import socketserver
from django.conf import settings

# Load model once globally
model = SentenceTransformer("all-MiniLM-L6-v2")

class EncoderHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != '/encode':
            self.send_error(404, "Not Found")
            return

        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        try:
            data = json.loads(body)
            text = data.get("text")
            if not text:
                raise ValueError("Missing 'text'")
            embedding = model.encode(text).tolist()

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"embedding": embedding}).encode())
        except Exception as e:
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

class Command(BaseCommand):
    help = "Run a simple HTTP server that encodes text to embeddings"

    def handle(self, *args, **options):
        host, port = settings.ENCODER_SERVER_HOST, settings.ENCODER_SERVER_PORT
        self.stdout.write(f"Starting encoder server at {settings.ENCODER_SERVER_SCHEME}://{host}:{port}/encode")

        httpd = HTTPServer((host, port), EncoderHandler)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            self.stdout.write("Shutting down encoder server.")
        httpd.server_close()
