import json
from http.server import BaseHTTPRequestHandler, HTTPServer

# in-memory storage for now
todo = []

class ToDoHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/todo/GET":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(todo).encode())
        else:
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "path not found"}).encode())

    def do_POST(self):
        if self.path == "/todo/POST":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            todo.append(json.loads((post_data.decode())))
            self.send_response(201)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"message":"Task added sucessfully"}).encode())
        else:
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"Error":"Path not found"}).encode())
            
if __name__ == "__main__":
    server = HTTPServer(("localhost", 8000), ToDoHandler)
    print("Server started at http://localhost:8000")
    server.serve_forever()