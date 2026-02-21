import json
from http.server import BaseHTTPRequestHandler, HTTPServer

# in-memory storage for now
todo = []

class ToDoHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/todo":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(todo).encode())
        else:
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "path not found"}).encode())

if __name__ == "__main__":
    server = HTTPServer(("localhost", 8000), ToDoHandler)
    print("Server started at http://localhost:8000")
    server.serve_forever()