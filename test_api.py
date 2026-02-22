import requests
import json
import subprocess
import time
import os
import sys

BASE_URL = "http://localhost:8000"
TEST_FILE = "todos_test.json"
server_process = None

def start_server():
    """Start the server as a subprocess with test file"""
    global server_process
    print(f"Starting server with test file: {TEST_FILE}...")
    # Set environment variable to tell server to use test file
    env = os.environ.copy()
    env['TODO_FILE'] = TEST_FILE
    server_process = subprocess.Popen(
        [sys.executable, 'server.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env
    )
    time.sleep(2)  # Wait for server to start
    print("Server started.\n")
    return server_process

def stop_server():
    """Stop the server"""
    global server_process
    if server_process:
        print("\nStopping server...")
        server_process.terminate()
        server_process.wait()
        print("Server stopped.\n")

def restart_server():
    """Restart the server to test persistence"""
    global server_process
    print("\n" + "=" * 60)
    print("RESTARTING SERVER (Testing Persistence)...")
    print("=" * 60)
    stop_server()
    time.sleep(1)
    start_server()

def clear_data():
    """Delete test file to start fresh"""
    if os.path.exists(TEST_FILE):
        os.remove(TEST_FILE)
        print(f"Deleted existing {TEST_FILE}\n")

def verify_file_exists():
    """Check if test file was created"""
    if os.path.exists(TEST_FILE):
        print(f"   [OK] {TEST_FILE} file exists")
        return True
    else:
        print(f"   [FAIL] {TEST_FILE} file NOT found!")
        return False

def verify_file_contents(expected_count=None):
    """Read and validate test file"""
    try:
        with open(TEST_FILE, 'r') as f:
            data = json.load(f)
            print(f"   [INFO] File contains {len(data)} todo(s)")
            if expected_count is not None:
                assert len(data) == expected_count, f"Expected {expected_count} todos, found {len(data)}"
            return data
    except Exception as e:
        print(f"   [ERROR] Error reading file: {e}")
        raise

def test_persistence():
    print("=" * 60)
    print("TESTING TODO API WITH PERSISTENCE")
    print("=" * 60)

    # ============================================
    # SECTION 1: SETUP
    # ============================================
    print("\n" + "=" * 60)
    print("SETUP: Starting Fresh")
    print("=" * 60)
    clear_data()
    start_server()

    # ============================================
    # SECTION 2: BASIC CRUD TESTS
    # ============================================
    print("=" * 60)
    print("SECTION 1: Basic CRUD Operations")
    print("=" * 60)

    # 1. GET all (should be empty - no file yet)
    print("\n1. GET /todo (should be empty)")
    r = requests.get(f"{BASE_URL}/todo")
    print(f"   Status: {r.status_code}")
    print(f"   Response: {r.json()}")
    assert r.status_code == 200
    assert r.json() == []
    print("   [PASS] Correctly returns empty list when no file exists")

    # 2. POST - Add first task
    print("\n2. POST /todo - Add first task")
    r = requests.post(f"{BASE_URL}/todo",
                     json={"task": "Buy milk", "completed": False})
    print(f"   Status: {r.status_code}")
    print(f"   Response: {r.json()}")
    assert r.status_code == 201
    print("   [PASS] Task added successfully")

    # 3. Verify file was created
    print(f"\n3. Verify {TEST_FILE} file was created")
    assert verify_file_exists()

    # 4. POST - Add second task
    print("\n4. POST /todo - Add second task")
    r = requests.post(f"{BASE_URL}/todo",
                     json={"task": "Study Python", "completed": False})
    print(f"   Status: {r.status_code}")
    print(f"   Response: {r.json()}")
    assert r.status_code == 201

    # 5. POST - Add third task
    print("\n5. POST /todo - Add third task")
    r = requests.post(f"{BASE_URL}/todo",
                     json={"task": "Exercise", "completed": False})
    print(f"   Status: {r.status_code}")
    print(f"   Response: {r.json()}")
    assert r.status_code == 201

    print("\n5. POST /todo - Add fourth task")
    r = requests.post(f"{BASE_URL}/todo",
                     json={"task": "Exercise123", "completed": True})
    print(f"   Status: {r.status_code}")
    print(f"   Response: {r.json()}")
    assert r.status_code == 201

    # 6. GET all (should have 3 tasks)
    print("\n6. GET /todo (should have 3 tasks)")
    r = requests.get(f"{BASE_URL}/todo")
    print(f"   Status: {r.status_code}")
    print(f"   Response: {r.json()}")
    assert r.status_code == 200
    assert len(r.json()) == 3
    print("   [PASS] All 3 tasks present in memory")

    # 7. Verify file contents
    print("\n7. Verify file contains all 3 tasks")
    file_data = verify_file_contents(expected_count=3)
    print("   [PASS] File correctly saved all tasks")

    # ============================================
    # SECTION 3: PERSISTENCE TEST #1 (CRITICAL!)
    # ============================================
    print("\n" + "=" * 60)
    print("SECTION 2: PERSISTENCE TEST #1 - Data Survives Restart")
    print("=" * 60)

    restart_server()

    print("\n8. GET /todo after restart (should STILL have 3 tasks)")
    r = requests.get(f"{BASE_URL}/todo")
    print(f"   Status: {r.status_code}")
    print(f"   Response: {r.json()}")
    assert r.status_code == 200
    assert len(r.json()) == 3
    assert r.json()[0]["task"] == "Buy milk"
    assert r.json()[1]["task"] == "Study Python"
    assert r.json()[2]["task"] == "Exercise"
    print("   [SUCCESS] Data survived server restart!")

    # ============================================
    # SECTION 4: GET SPECIFIC TASK
    # ============================================
    print("\n" + "=" * 60)
    print("SECTION 3: Get Specific Task")
    print("=" * 60)

    print("\n9. GET /todo/0 - Get first task")
    r = requests.get(f"{BASE_URL}/todo/0")
    print(f"   Status: {r.status_code}")
    print(f"   Response: {r.json()}")
    assert r.status_code == 200
    assert r.json()["task"] == "Buy milk"
    print("   [PASS] Specific task retrieval works")

    # ============================================
    # SECTION 5: UPDATE TASK
    # ============================================
    print("\n" + "=" * 60)
    print("SECTION 4: Update Task")
    print("=" * 60)

    print("\n10. PUT /todo/0 - Update first task")
    r = requests.put(f"{BASE_URL}/todo/0",
                    json={"task": "Buy eggs instead", "completed": True})
    print(f"   Status: {r.status_code}")
    print(f"   Response: {r.json()}")
    assert r.status_code == 200
    print("   [PASS] Task updated")

    print("\n11. GET /todo/0 - Verify update in memory")
    r = requests.get(f"{BASE_URL}/todo/0")
    print(f"   Status: {r.status_code}")
    print(f"   Response: {r.json()}")
    assert r.status_code == 200
    assert r.json()["task"] == "Buy eggs instead"
    assert r.json()["completed"] == True
    print("   [PASS] Update confirmed in memory")

    # ============================================
    # SECTION 6: PERSISTENCE TEST #2
    # ============================================
    print("\n" + "=" * 60)
    print("SECTION 5: PERSISTENCE TEST #2 - Updates Survive Restart")
    print("=" * 60)

    restart_server()

    print("\n12. GET /todo/0 after restart - Verify update persisted")
    r = requests.get(f"{BASE_URL}/todo/0")
    print(f"   Status: {r.status_code}")
    print(f"   Response: {r.json()}")
    assert r.status_code == 200
    assert r.json()["task"] == "Buy eggs instead"
    assert r.json()["completed"] == True
    print("   [SUCCESS] Update survived server restart!")

    # ============================================
    # SECTION 7: DELETE TASK
    # ============================================
    print("\n" + "=" * 60)
    print("SECTION 6: Delete Task")
    print("=" * 60)

    print("\n13. DELETE /todo/1 - Delete second task")
    r = requests.delete(f"{BASE_URL}/todo/1")
    print(f"   Status: {r.status_code}")
    print(f"   Response: {r.json()}")
    assert r.status_code == 200
    print("   [PASS] Task deleted")

    print("\n14. GET /todo - Verify deletion in memory (should have 2 tasks)")
    r = requests.get(f"{BASE_URL}/todo")
    print(f"   Status: {r.status_code}")
    print(f"   Response: {r.json()}")
    assert r.status_code == 200
    assert len(r.json()) == 2
    print("   [PASS] Deletion confirmed in memory")

    # ============================================
    # SECTION 8: PERSISTENCE TEST #3
    # ============================================
    print("\n" + "=" * 60)
    print("SECTION 7: PERSISTENCE TEST #3 - Deletions Survive Restart")
    print("=" * 60)

    restart_server()

    print("\n15. GET /todo after restart - Verify deletion persisted (should have 2)")
    r = requests.get(f"{BASE_URL}/todo")
    print(f"   Status: {r.status_code}")
    print(f"   Response: {r.json()}")
    assert r.status_code == 200
    assert len(r.json()) == 2
    print("   [SUCCESS] Deletion survived server restart!")

    print("\n16. Verify final file contents")
    file_data = verify_file_contents(expected_count=2)
    assert file_data[0]["task"] == "Buy eggs instead"
    assert file_data[0]["completed"] == True
    print("   [PASS] File contents match expected state")

    # ============================================
    # SECTION 9: ERROR HANDLING TESTS
    # ============================================
    print("\n" + "=" * 60)
    print("SECTION 8: Error Handling")
    print("=" * 60)

    # Invalid index (not a number)
    print("\n17. GET /todo/abc - Invalid index")
    r = requests.get(f"{BASE_URL}/todo/abc")
    print(f"    Status: {r.status_code}")
    print(f"    Response: {r.json()}")
    assert r.status_code == 400
    print("    [PASS] Correctly rejects invalid index")

    # Index out of range
    print("\n18. GET /todo/999 - Index out of range")
    r = requests.get(f"{BASE_URL}/todo/999")
    print(f"    Status: {r.status_code}")
    print(f"    Response: {r.json()}")
    assert r.status_code == 404
    print("    [PASS] Correctly handles out of range index")

    # Invalid JSON
    print("\n19. POST /todo - Invalid JSON")
    r = requests.post(f"{BASE_URL}/todo",
                     headers={"Content-Type": "application/json"},
                     data='{bad json}')
    print(f"    Status: {r.status_code}")
    print(f"    Response: {r.json()}")
    assert r.status_code == 400
    print("    [PASS] Correctly rejects malformed JSON")

    # Invalid path
    print("\n20. GET /invalid - Invalid path")
    r = requests.get(f"{BASE_URL}/invalid")
    print(f"    Status: {r.status_code}")
    print(f"    Response: {r.json()}")
    assert r.status_code == 404
    print("    [PASS] Correctly handles invalid paths")

    # ============================================
    # FINAL SUMMARY
    # ============================================
    print("\n" + "=" * 60)
    print(" ALL TESTS PASSED! ")
    print("=" * 60)
    print("\n[PASS] CRUD operations work correctly")
    print("[PASS] Data persists across server restarts")
    print("[PASS] File I/O working properly")
    print("[PASS] Error handling robust")
    print("\nYour Todo API with persistence is fully functional!")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_persistence()
    except AssertionError as e:
        print(f"\n Test failed!")
        print(f"Assertion Error: {e}")
        import traceback
        traceback.print_exc()
    except requests.exceptions.ConnectionError:
        print("\n Cannot connect to server.")
        print("The test script starts the server automatically, but there may be an issue.")
    except Exception as e:
        print(f"\n Unexpected error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Always stop the server
        stop_server()
        print("\nTest script completed.")
