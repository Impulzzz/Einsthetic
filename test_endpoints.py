import requests
import json

# Test question generation
print("Testing question generation...")
try:
    response = requests.post(
        "http://127.0.0.1:5000/api/generate_question",
        json={
            "subject": "Algorithms",
            "difficulty": "Medium",
            "topic": None
        },
        cookies={"session": "test"}  # Will fail auth but that's ok, we're testing the endpoint
    )
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("✓ Question generated successfully!")
        print(json.dumps(response.json(), indent=2)[:500])
    elif response.status_code == 401:
        print("⚠ Auth required (expected) - endpoint is working")
    else:
        print(f"✗ Error: {response.text[:200]}")
except Exception as e:
    print(f"✗ Connection error: {e}")

print("\n" + "="*50 + "\n")

# Test dev login and analytics
print("Testing dev login and analytics...")
try:
    # Login first
    session = requests.Session()
    login_resp = session.get("http://127.0.0.1:5000/dev/login", allow_redirects=False)
    print(f"Dev login status: {login_resp.status_code}")
    
    # Get analytics
    analytics_resp = session.get("http://127.0.0.1:5000/api/analytics/dev_tester")
    print(f"Analytics status: {analytics_resp.status_code}")
    if analytics_resp.status_code == 200:
        data = analytics_resp.json()
        print(f"✓ Analytics retrieved:")
        print(f"  - Total attempts: {data.get('total_attempts', 0)}")
        print(f"  - Success rate: {data.get('success_rate', 0)}%")
        print(f"  - Proficiency: {data.get('proficiency', {})}")
        print(f"  - Recent activity count: {len(data.get('recent_activity', []))}")
    else:
        print(f"✗ Analytics error: {analytics_resp.text[:200]}")
except Exception as e:
    print(f"✗ Error: {e}")
