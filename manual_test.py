import requests

BASE_URL = "http://localhost:8000"

# Test 1: Add a task
print("\n1. POST /todo - Add task")
r = requests.post(f"{BASE_URL}/todo",
                  json={"task": "Exercise4545", "completed": False})
print(f"   Status: {r.status_code}")
print(f"   Response: {r.json()}")

# Test 2: Get all tasks
print("\n2. GET /todo - Get all tasks")
r = requests.get(f"{BASE_URL}/todo")
print(f"   Status: {r.status_code}")
print(f"   Response: {r.json()}")

# Test 3: Add a second task
print("\n3. POST /todo - Add second task")
r = requests.post(f"{BASE_URL}/todo",
                  json={"task": "Read a book", "completed": False})
print(f"   Status: {r.status_code}")
print(f"   Response: {r.json()}")

# Test 4: Get all tasks
print("\n4. GET /todo - Get all tasks")
r = requests.get(f"{BASE_URL}/todo")
print(f"   Status: {r.status_code}")
print(f"   Response: {r.json()}")