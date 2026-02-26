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

def validate_todo_data(data):
    """
    Validates todo item data.
    Returns: (is_valid, error_message)
    """
    # Check if data is a dictionary
    if not isinstance(data, dict):
        return (False, "Todo must be a JSON object")

    # Check if 'task' field exists
    if 'task' not in data:
        return (False, "Task field is required")

    # Check if 'task' is a string
    if not isinstance(data['task'], str):
        return (False, "Task must be a string")

    # Check if 'task' is not empty or just whitespace
    task = data['task'].strip()
    if len(task) == 0:
        return (False, "Task cannot be empty or whitespace")

    # Check task length (1-500 characters)
    if len(task) > 500:
        return (False, "Task is too long (maximum 500 characters)")

    # Check optional 'completed' field if present
    if 'completed' in data:
        if not isinstance(data['completed'], bool):
            return (False, "Completed field must be a boolean (true/false)")

    # Check optional 'description' field if present
    if 'description' in data:
        if not isinstance(data['description'], str):
            return (False, "Description must be a string")
        if len(data['description']) > 1000:
            return (False, "Description is too long (maximum 1000 characters)")

    return (True, None)

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
                new_todo = json.loads(post_data.decode())

                # Validate the todo data
                is_valid, error_message = validate_todo_data(new_todo)
                if not is_valid:
                    self.send_json_response(400, {"error": error_message})
                    return

                todo.append(new_todo)
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
                        updated_todo = json.loads(self.rfile.read(content_length).decode())

                        # Validate the todo data
                        is_valid, error_message = validate_todo_data(updated_todo)
                        if not is_valid:
                            self.send_json_response(400, {"error": error_message})
                            return

                        todo[index] = updated_todo
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