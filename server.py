import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

# Allow tests to specify a different file via environment variable
TODO_FILENAME = os.environ.get('TODO_FILE', 'todos.json')

def load_todos():
        try:
            with open(TODO_FILENAME, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

def save_todos(todo):
    try:
        with open(TODO_FILENAME, "w") as f:
            json.dump(todo, f, indent = 2)
    except Exception as e:
        print(f"Error saving todos: {e}")

todo = load_todos()

class ToDoHandler(BaseHTTPRequestHandler):


    def send_json_response(self, status_code, data):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    

    def do_GET(self):
        if self.path == "/todo":
        # Get ALL todos
            self.send_json_response(200, todo)
        elif self.path.startswith("/todo/"):
            try:
                index = int(self.path.split("/")[-1])

                if 0<= index< len(todo):
                    self.send_json_response(200, todo[index])
                else:
                    self.send_json_response(404, {"error": "Task not found"})
            except ValueError:
                self.send_json_response(400, {"error": "Invalid index"})
        else:
            self.send_json_response(404, {"error": "Path not found"})

    def do_POST(self):
        if self.path == "/todo":
            
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                todo.append(json.loads((post_data.decode())))
                save_todos(todo)
                self.send_json_response(201, {"message": "Task added successfully"})
            except (ValueError, json.JSONDecodeError):
                self.send_json_response(400, {"error": "Invalid JSON"})
        else:
            self.send_json_response(404, {"error": "Path not found"})

    def do_DELETE(self):
        if self.path.startswith("/todo/"):
            try:
                index = int(self.path.split("/")[-1])
                if 0 <= index < len(todo):
                    del todo[index]
                    save_todos(todo)
                    self.send_json_response(200, {"message": "Task deleted successfully"})
                else:
                    self.send_json_response(404, {"error": "Task not found"})       
            except ValueError:
                self.send_json_response(400, {"error": "Invalid index"})       
        else:
            self.send_json_response(404, {"error": "Path not found"})

    def do_PUT(self):    
        if self.path.startswith("/todo/"):
            try:
                index = int(self.path.split("/")[-1])
                if 0 <= index < len(todo):
                    try:
                        content_length = int(self.headers['Content-Length'])
                        todo[index] = json.loads(self.rfile.read(content_length).decode())
                        save_todos(todo)
                        self.send_json_response(200, {"message": "Task updated successfully"})
                    except (ValueError, json.JSONDecodeError):
                        self.send_json_response(400, {"error": "Invalid JSON"})
                else:
                    self.send_json_response(404, {"error": "Task not found"})       
            except ValueError:
                self.send_json_response(400, {"error": "Invalid index"})

# Runs server only if script is executed directly, if imported by another module it wont run
if __name__ == "__main__":
    server = HTTPServer(("localhost", 8000), ToDoHandler)
    print("Server started at http://localhost:8000")
    server.serve_forever()