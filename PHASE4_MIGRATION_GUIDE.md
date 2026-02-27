# Phase 4: PostgreSQL Migration Guide

This guide will help you migrate your Todo API from JSON file storage to PostgreSQL database.

## 📚 What You'll Learn

1. **Database Fundamentals** - Understanding tables, rows, and columns
2. **PostgreSQL Setup** - Installing and configuring a real database
3. **psycopg2** - Python's PostgreSQL driver for database connections
4. **SQL Queries** - INSERT, SELECT, UPDATE, DELETE operations
5. **Database Connections** - How to connect Python to PostgreSQL
6. **Transactions** - Commit and rollback concepts

---

## Step 1: Install PostgreSQL

### Windows
1. Download PostgreSQL from https://www.postgresql.org/download/windows/
2. Run the installer
3. During installation:
   - Set a password for the `postgres` user (remember this!)
   - Use default port: 5432
   - Install pgAdmin 4 (GUI tool for managing databases)

### Verify Installation
```bash
# Check PostgreSQL version
psql --version
```

---

## Step 2: Create Your Database

### Option A: Using pgAdmin (GUI - Easier for Beginners)
1. Open pgAdmin 4
2. Connect to your PostgreSQL server (use the password you set)
3. Right-click "Databases" → Create → Database
4. Name it: `todos_db`
5. Click Save

### Option B: Using psql (Command Line)
```bash
# Open psql command line
psql -U postgres

# Create database
CREATE DATABASE todos_db;

# Connect to it
\c todos_db

# You're now ready to create tables!
```

---

## Step 3: Create the Todos Table

Run this SQL in pgAdmin's Query Tool or in psql:

```sql
CREATE TABLE todos (
    id SERIAL PRIMARY KEY,
    task VARCHAR(500) NOT NULL,
    completed BOOLEAN DEFAULT false,
    description TEXT
);
```

### Understanding the Schema

| Column | Type | Explanation |
|--------|------|-------------|
| `id` | `SERIAL` | Auto-incrementing number (1, 2, 3...). PostgreSQL generates this automatically! |
| `task` | `VARCHAR(500)` | String with max 500 characters. This matches your validation! |
| `completed` | `BOOLEAN` | True/false value. Defaults to false if not provided |
| `description` | `TEXT` | Unlimited text for longer descriptions |

**Key Points:**
- `PRIMARY KEY` means each id is unique and identifies one todo
- `NOT NULL` means task is required (can't be empty)
- `DEFAULT false` means completed will be false unless you specify otherwise
- `SERIAL` automatically increments: first todo gets id=1, second gets id=2, etc.

---

## Step 4: Install psycopg2

This is the Python library that lets you talk to PostgreSQL:

```bash
# Activate your virtual environment first!
.\venv\Scripts\activate

# Install psycopg2-binary (binary version is easier to install)
pip install psycopg2-binary
```

---

## Step 5: Understanding Database Connections

### The Connection Pattern

Every time you want to talk to the database:

```python
import psycopg2

# 1. CONNECT to the database
conn = psycopg2.connect(
    host="localhost",      # Database is on your computer
    database="todos_db",   # The database you created
    user="postgres",       # Default admin user
    password="your_password_here"  # Password you set during installation
)

# 2. CREATE A CURSOR (like a pointer to execute queries)
cursor = conn.cursor()

# 3. EXECUTE SQL QUERIES
cursor.execute("SELECT * FROM todos;")

# 4. FETCH RESULTS (for SELECT queries)
results = cursor.fetchall()

# 5. COMMIT (save changes for INSERT/UPDATE/DELETE)
conn.commit()

# 6. CLOSE when done (good practice)
cursor.close()
conn.close()
```

### Why Cursor?
Think of a cursor like a "worker" that executes SQL commands for you. You give it SQL, it talks to the database.

### Why Commit?
- `SELECT` (read) doesn't need commit
- `INSERT`, `UPDATE`, `DELETE` (write) need `conn.commit()` to save changes
- If you don't commit, changes are lost!

---

## Step 6: The SQL Queries You Need

### 1. CREATE (Insert a new todo)
```python
cursor.execute(
    "INSERT INTO todos (task, completed, description) VALUES (%s, %s, %s);",
    ("Buy milk", False, "From the grocery store")
)
conn.commit()
```

**Important:** The `%s` are placeholders. psycopg2 safely inserts your values to prevent SQL injection!

### 2. READ ALL (Get all todos)
```python
cursor.execute("SELECT * FROM todos;")
all_todos = cursor.fetchall()
# Returns: [(1, 'Buy milk', False, 'From store'), (2, 'Study', True, None), ...]
```

### 3. READ ONE (Get todo by ID)
```python
cursor.execute("SELECT * FROM todos WHERE id = %s;", (5,))
todo = cursor.fetchone()
# Returns: (5, 'Exercise', False, None) or None if not found
```

### 4. UPDATE (Modify existing todo)
```python
cursor.execute(
    "UPDATE todos SET completed = %s WHERE id = %s;",
    (True, 5)
)
conn.commit()
```

### 5. DELETE (Remove a todo)
```python
cursor.execute("DELETE FROM todos WHERE id = %s;", (5,))
conn.commit()
```

---

## Step 7: Mapping Your Current Code to SQL

### Current File-Based Approach
```python
# Load everything into memory
todos = load_todos()  # Reads entire JSON file

# Get all todos
return todos

# Get one todo
return todos[index]

# Add todo
todos.append(new_todo)
save_todos(todos)  # Rewrites entire file

# Update todo
todos[index]['completed'] = True
save_todos(todos)  # Rewrites entire file

# Delete todo
del todos[index]
save_todos(todos)  # Rewrites entire file
```

### New Database Approach
```python
# No loading into memory!

# Get all todos
cursor.execute("SELECT * FROM todos;")
return cursor.fetchall()

# Get one todo
cursor.execute("SELECT * FROM todos WHERE id = %s;", (id,))
return cursor.fetchone()

# Add todo
cursor.execute(
    "INSERT INTO todos (task, completed) VALUES (%s, %s);",
    (task, completed)
)
conn.commit()

# Update todo
cursor.execute(
    "UPDATE todos SET completed = %s WHERE id = %s;",
    (True, id)
)
conn.commit()

# Delete todo
cursor.execute("DELETE FROM todos WHERE id = %s;", (id,))
conn.commit()
```

**Key Differences:**
- No more `load_todos()` and `save_todos()`
- No in-memory array
- Each operation directly modifies the database
- Much more efficient for large datasets!

---

## Step 8: Migration Checklist

- [ ] Install PostgreSQL
- [ ] Create `todos_db` database
- [ ] Create `todos` table with the schema above
- [ ] Install `psycopg2-binary` package
- [ ] Test connection with a simple script
- [ ] Replace `load_todos()` with SELECT query
- [ ] Remove `save_todos()` function
- [ ] Update `do_GET` to query database
- [ ] Update `do_POST` to INSERT into database
- [ ] Update `do_PUT` to UPDATE in database
- [ ] Update `do_DELETE` to DELETE from database
- [ ] Change from array index to database ID in URLs
- [ ] Test all CRUD operations
- [ ] Handle database connection errors

---

## Step 9: Practice Exercises

Before modifying your API, practice SQL in psql or pgAdmin:

```sql
-- Practice INSERT
INSERT INTO todos (task, completed) VALUES ('Learn SQL', false);

-- Practice SELECT
SELECT * FROM todos;
SELECT * FROM todos WHERE completed = true;

-- Practice UPDATE
UPDATE todos SET completed = true WHERE id = 1;

-- Practice DELETE
DELETE FROM todos WHERE id = 1;

-- Check what's in your table
SELECT * FROM todos;
```

---

## Common Pitfalls to Avoid

1. **Forgetting to commit** - Your changes won't save!
2. **SQL injection** - Always use `%s` placeholders, never string concatenation
3. **Not closing connections** - Can cause memory leaks
4. **Confusing array index with database ID** - IDs don't change when you delete items!
5. **Not handling None results** - `fetchone()` returns None if no match found

---

## Need Help?

- PostgreSQL Documentation: https://www.postgresql.org/docs/
- psycopg2 Tutorial: https://www.psycopg.org/docs/usage.html
- SQL Tutorial: https://www.w3schools.com/sql/

---

## Next Steps

1. Read through the commented code in `server.py`
2. Install PostgreSQL and create your database
3. Practice SQL queries manually
4. Start replacing one function at a time
5. Test after each change!

Good luck! 🚀
