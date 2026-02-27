# ========== IMPORTS ==========
import json  # For parsing JSON data from requests and responses
import os    # For reading environment variables
from http.server import BaseHTTPRequestHandler, HTTPServer  # Built-in HTTP server

# ========== FILE-BASED STORAGE (TO BE REPLACED WITH DATABASE) ==========
# Allow tests to specify a different file via environment variable
# This will be replaced with a database connection string
TODO_FILENAME = os.environ.get('TODO_FILE', 'todos.json')

# ========== DATA ACCESS FUNCTIONS (TO BE REPLACED WITH SQL QUERIES) ==========

def load_todos():
    """
    CURRENT: Reads all todos from a JSON file
    FUTURE: Will become a SQL SELECT query

    What this does:
    1. Opens the JSON file
    2. Parses it into a Python list
    3. Returns the list (or empty list if file doesn't exist)

    PostgreSQL equivalent will be:
    cursor.execute("SELECT * FROM todos;")
    rows = cursor.fetchall()
    return rows
    """
    try:
        with open(TODO_FILENAME, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_todos(todo):
    """
    CURRENT: Writes the ENTIRE todo list back to the JSON file
    FUTURE: Will be REMOVED - each operation will directly update the database

    What this does:
    1. Opens the file in write mode (overwrites everything)
    2. Dumps the entire Python list as JSON

    PostgreSQL equivalent:
    - POST will use: INSERT INTO todos (task, completed) VALUES (%s, %s)
    - PUT will use: UPDATE todos SET task=%s, completed=%s WHERE id=%s
    - DELETE will use: DELETE FROM todos WHERE id=%s

    Notice: With a database, you don't rewrite everything - you modify specific rows!
    """
    try:
        with open(TODO_FILENAME, "w") as f:
            json.dump(todo, f, indent = 2)
    except Exception as e:
        print(f"Error saving todos: {e}")

# ========== VALIDATION FUNCTIONS (WILL STAY THE SAME) ==========

def validate_todo_data(data):
    """
    Validates todo item data for POST (full object required).
    Returns: (is_valid, error_message)

    NOTE: This validation logic will work the same with PostgreSQL!
    You still need to validate data before inserting into the database.
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

def validate_partial_todo_data(data):
    """
    Validates partial todo data for PUT (only validates fields that are present).
    Returns: (is_valid, error_message)

    NOTE: This validation logic will also stay the same with PostgreSQL!
    """
    # Check if data is a dictionary
    if not isinstance(data, dict):
        return (False, "Todo must be a JSON object")

    # Check if at least one field is provided
    if len(data) == 0:
        return (False, "At least one field must be provided for update")

    # Validate 'task' field if present
    if 'task' in data:
        if not isinstance(data['task'], str):
            return (False, "Task must be a string")

        task = data['task'].strip()
        if len(task) == 0:
            return (False, "Task cannot be empty or whitespace")

        if len(task) > 500:
            return (False, "Task is too long (maximum 500 characters)")

    # Validate 'completed' field if present
    if 'completed' in data:
        if not isinstance(data['completed'], bool):
            return (False, "Completed field must be a boolean (true/false)")

    # Validate 'description' field if present
    if 'description' in data:
        if not isinstance(data['description'], str):
            return (False, "Description must be a string")
        if len(data['description']) > 1000:
            return (False, "Description is too long (maximum 1000 characters)")

    return (True, None)

# ========== IN-MEMORY TODO LIST (WILL BE REMOVED) ==========
# CURRENT: Load all todos into memory when server starts
# FUTURE: Remove this - query database directly for each request
todo = load_todos()

# ========== HTTP REQUEST HANDLER ==========

class ToDoHandler(BaseHTTPRequestHandler):
    """
    Handles HTTP requests for the Todo API
    Routes: GET, POST, PUT, DELETE for /todo and /todo/{index}

    CURRENT: Uses array index to identify todos (e.g., /todo/0, /todo/1)
    FUTURE: Will use database ID (e.g., /todo/1, /todo/2, /todo/5)
    """


    def send_json_response(self, status_code, data):
        """
        Helper method to send JSON responses
        NOTE: This will stay the same with PostgreSQL!
        """
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    # ========== GET REQUEST HANDLERS ==========

    def do_GET(self):
        """
        Handle GET requests to retrieve todos

        CURRENT APPROACH (FILE):
        - /todo → returns entire in-memory array
        - /todo/0 → returns array[0]

        FUTURE APPROACH (DATABASE):
        - /todo → SELECT * FROM todos;
        - /todo/5 → SELECT * FROM todos WHERE id = 5;

        Key difference: Array index vs Database ID
        """
        if self.path == "/todo":
            # Get ALL todos from the in-memory list
            # FUTURE: cursor.execute("SELECT * FROM todos;")
            #         todos = cursor.fetchall()
            self.send_json_response(200, todo)
        elif self.path.startswith("/todo/"):
            try:
                # Extract index from URL (e.g., "/todo/3" → 3)
                index = int(self.path.split("/")[-1])

                # Check if index is valid in the array
                # FUTURE: Will check if ID exists in database instead
                if 0<= index< len(todo):
                    # Return the todo at this index
                    # FUTURE: cursor.execute("SELECT * FROM todos WHERE id = %s;", (id,))
                    #         todo_item = cursor.fetchone()
                    self.send_json_response(200, todo[index])
                else:
                    self.send_json_response(404, {"error": "Task not found"})
            except ValueError:
                self.send_json_response(400, {"error": "Invalid index"})
        else:
            self.send_json_response(404, {"error": "Path not found"})

    # ========== POST REQUEST HANDLER ==========

    def do_POST(self):
        """
        Handle POST requests to create new todos

        CURRENT APPROACH (FILE):
        1. Parse JSON from request body
        2. Validate the data
        3. Append to in-memory array
        4. Write entire array back to file

        FUTURE APPROACH (DATABASE):
        1. Parse JSON from request body
        2. Validate the data
        3. INSERT INTO todos (task, completed) VALUES (%s, %s)
        4. Commit the transaction

        Key difference: INSERT one row vs rewrite entire file
        """
        if self.path == "/todo":

            try:
                # Read the request body
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                new_todo = json.loads(post_data.decode())

                # Validate the todo data (same for file or database!)
                is_valid, error_message = validate_todo_data(new_todo)
                if not is_valid:
                    self.send_json_response(400, {"error": error_message})
                    return

                # Add to in-memory array and save to file
                # FUTURE: cursor.execute(
                #     "INSERT INTO todos (task, completed, description) VALUES (%s, %s, %s);",
                #     (new_todo['task'], new_todo.get('completed', False), new_todo.get('description'))
                # )
                # conn.commit()
                todo.append(new_todo)
                save_todos(todo)
                self.send_json_response(201, {"message": "Task added successfully"})
            except (ValueError, json.JSONDecodeError):
                self.send_json_response(400, {"error": "Invalid JSON"})
        else:
            self.send_json_response(404, {"error": "Path not found"})

    # ========== DELETE REQUEST HANDLER ==========

    def do_DELETE(self):
        """
        Handle DELETE requests to remove todos

        CURRENT APPROACH (FILE):
        1. Extract index from URL
        2. Delete from array using del
        3. Write entire array back to file

        FUTURE APPROACH (DATABASE):
        1. Extract ID from URL
        2. DELETE FROM todos WHERE id = %s
        3. Commit the transaction

        Key difference: DELETE one row by ID vs delete from array and rewrite file
        """
        if self.path.startswith("/todo/"):
            try:
                # Extract index from URL
                index = int(self.path.split("/")[-1])
                if 0 <= index < len(todo):
                    # Remove from array
                    # FUTURE: cursor.execute("DELETE FROM todos WHERE id = %s;", (id,))
                    #         conn.commit()
                    del todo[index]
                    save_todos(todo)
                    self.send_json_response(200, {"message": "Task deleted successfully"})
                else:
                    self.send_json_response(404, {"error": "Task not found"})
            except ValueError:
                self.send_json_response(400, {"error": "Invalid index"})
        else:
            self.send_json_response(404, {"error": "Path not found"})

    # ========== PUT REQUEST HANDLER ==========

    def do_PUT(self):
        """
        Handle PUT requests to update existing todos

        CURRENT APPROACH (FILE):
        1. Extract index from URL
        2. Parse update data from request body
        3. Validate partial data
        4. Merge updates with existing todo in array
        5. Write entire array back to file

        FUTURE APPROACH (DATABASE):
        1. Extract ID from URL
        2. Parse update data from request body
        3. Validate partial data
        4. UPDATE todos SET field1=%s, field2=%s WHERE id=%s
        5. Commit the transaction

        Key difference: UPDATE specific row vs update in array and rewrite file
        """
        if self.path.startswith("/todo/"):
            try:
                # Extract index from URL
                index = int(self.path.split("/")[-1])
                if 0 <= index < len(todo):
                    try:
                        # Read and parse update data
                        content_length = int(self.headers['Content-Length'])
                        updated_fields = json.loads(self.rfile.read(content_length).decode())

                        # Validate the partial update data (same for file or database!)
                        is_valid, error_message = validate_partial_todo_data(updated_fields)
                        if not is_valid:
                            self.send_json_response(400, {"error": error_message})
                            return

                        # Merge the updated fields with existing todo
                        # This keeps fields that weren't sent in the update
                        # FUTURE: Build dynamic UPDATE query based on fields provided
                        # Example: UPDATE todos SET task=%s, completed=%s WHERE id=%s
                        existing_todo = todo[index]
                        for key, value in updated_fields.items():
                            existing_todo[key] = value

                        save_todos(todo)
                        # FUTURE: conn.commit()
                        self.send_json_response(200, {"message": "Task updated successfully"})
                    except (ValueError, json.JSONDecodeError):
                        self.send_json_response(400, {"error": "Invalid JSON"})
                else:
                    self.send_json_response(404, {"error": "Task not found"})
            except ValueError:
                self.send_json_response(400, {"error": "Invalid index"})

# ========== SERVER STARTUP ==========

# Runs server only if script is executed directly, if imported by another module it wont run
if __name__ == "__main__":
    # FUTURE: Add database connection here
    # conn = psycopg2.connect(
    #     host="localhost",
    #     database="todos_db",
    #     user="postgres",
    #     password="your_password"
    # )
    # cursor = conn.cursor()

    server = HTTPServer(("localhost", 8000), ToDoHandler)
    print("Server started at http://localhost:8000")
    server.serve_forever()

    # FUTURE: Close database connection when server shuts down
    # cursor.close()
    # conn.close()