import requests
import json

BASE_URL = "http://localhost:8000"

def test_api():
    print("=" * 50)
    print("Testing Todo API")
    print("=" * 50)
    
    # 1. GET all (should be empty)
    print("\n1. GET /todo (should be empty)")
    r = requests.get(f"{BASE_URL}/todo")
    print(f"   Status: {r.status_code}")
    print(f"   Response: {r.json()}")
    assert r.status_code == 200
    assert r.json() == []
    
    # 2. POST - Add task
    print("\n2. POST /todo - Add task")
    r = requests.post(f"{BASE_URL}/todo", 
                     json={"task": "Buy milk", "completed": False})
    print(f"   Status: {r.status_code}")
    print(f"   Response: {r.json()}")
    assert r.status_code == 201
    
    # 3. GET all (should have 1 task)
    print("\n3. GET /todo (should have 1 task)")
    r = requests.get(f"{BASE_URL}/todo")
    print(f"   Status: {r.status_code}")
    print(f"   Response: {r.json()}")
    assert r.status_code == 200
    assert len(r.json()) == 1
    
    # 4. POST - Add another task
    print("\n4. POST /todo - Add another task")
    r = requests.post(f"{BASE_URL}/todo",
                     json={"task": "Study Python", "completed": False})
    print(f"   Status: {r.status_code}")
    print(f"   Response: {r.json()}")
    assert r.status_code == 201
    
    # 5. GET specific task
    print("\n5. GET /todo/0 - Get first task")
    r = requests.get(f"{BASE_URL}/todo/0")
    print(f"   Status: {r.status_code}")
    print(f"   Response: {r.json()}")
    assert r.status_code == 200
    assert r.json()["task"] == "Buy milk"
    
    # 6. PUT - Update task
    print("\n6. PUT /todo/0 - Update task")
    r = requests.put(f"{BASE_URL}/todo/0",
                    json={"task": "Buy eggs", "completed": True})
    print(f"   Status: {r.status_code}")
    print(f"   Response: {r.json()}")
    assert r.status_code == 200
    
    # 7. GET to verify update
    print("\n7. GET /todo/0 - Verify update")
    r = requests.get(f"{BASE_URL}/todo/0")
    print(f"   Status: {r.status_code}")
    print(f"   Response: {r.json()}")
    assert r.status_code == 200
    assert r.json()["task"] == "Buy eggs"
    assert r.json()["completed"] == True
    
    # 8. DELETE task
    print("\n8. DELETE /todo/0 - Delete task")
    r = requests.delete(f"{BASE_URL}/todo/0")
    print(f"   Status: {r.status_code}")
    print(f"   Response: {r.json()}")
    assert r.status_code == 200
    
    # 9. GET all (should have 1 task left)
    print("\n9. GET /todo (should have 1 task)")
    r = requests.get(f"{BASE_URL}/todo")
    print(f"   Status: {r.status_code}")
    print(f"   Response: {r.json()}")
    assert r.status_code == 200
    assert len(r.json()) == 1
    
    # Error cases
    print("\n" + "=" * 50)
    print("Testing Error Cases")
    print("=" * 50)
    
    # 10. Invalid index
    print("\n10. GET /todo/abc - Invalid index")
    r = requests.get(f"{BASE_URL}/todo/abc")
    print(f"    Status: {r.status_code}")
    print(f"    Response: {r.json()}")
    assert r.status_code == 400
    
    # 11. Index out of range
    print("\n11. GET /todo/999 - Index out of range")
    r = requests.get(f"{BASE_URL}/todo/999")
    print(f"    Status: {r.status_code}")
    print(f"    Response: {r.json()}")
    assert r.status_code == 404
    
    # 12. Invalid JSON
    print("\n12. POST /todo - Invalid JSON")
    r = requests.post(f"{BASE_URL}/todo",
                     headers={"Content-Type": "application/json"},
                     data='{bad json}')
    print(f"    Status: {r.status_code}")
    print(f"    Response: {r.json()}")
    assert r.status_code == 400
    
    # 13. Invalid path
    print("\n13. GET /invalid - Invalid path")
    r = requests.get(f"{BASE_URL}/invalid")
    print(f"    Status: {r.status_code}")
    print(f"    Response: {r.json()}")
    assert r.status_code == 404
    
    print("\n" + "=" * 50)
    print("✅ All tests passed!")
    print("=" * 50)

if __name__ == "__main__":
    try:
        test_api()
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
    except requests.exceptions.ConnectionError:
        print("\n❌ Cannot connect to server. Is it running on http://localhost:8000?")