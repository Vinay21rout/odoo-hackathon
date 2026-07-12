import requests

BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_endpoint(endpoint, token=None):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
        print(f"GET {endpoint} | Token: {token} | Status: {response.status_code} | Response: {response.text[:200]}")
    except Exception as e:
        print(f"GET {endpoint} failed: {e}")

print("Testing endpoints with mock-admin-uid:")
test_endpoint("/organization/stats", "mock-admin-uid")
test_endpoint("/reports/dynamic", "mock-admin-uid")
test_endpoint("/notifications", "mock-admin-uid")
test_endpoint("/employees?search=admin", "mock-admin-uid")
test_endpoint("/departments?limit=100", "mock-admin-uid")

print("\nTesting endpoints with mock-email-user-uid:")
test_endpoint("/organization/stats", "mock-email-user-uid")
test_endpoint("/reports/dynamic", "mock-email-user-uid")
test_endpoint("/notifications", "mock-email-user-uid")
test_endpoint("/employees?search=admin", "mock-email-user-uid")
test_endpoint("/departments?limit=100", "mock-email-user-uid")

print("\nTesting endpoints without token:")
test_endpoint("/organization/stats")
test_endpoint("/reports/dynamic")
test_endpoint("/notifications")
