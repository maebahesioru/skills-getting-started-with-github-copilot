import copy
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def restore_activities():
    """Snapshot and restore the module-level activities dict around each test."""
    original = copy.deepcopy(activities)
    try:
        yield
    finally:
        activities.clear()
        activities.update(original)


def _find_activity_for_signup(email: str = "testuser@example.com"):
    """Find an activity where the email is not present and there is space."""
    for name, details in activities.items():
        participants = details.get("participants", [])
        maxp = details.get("max_participants", 0)
        if email not in participants and len(participants) < maxp:
            return name
    return None


def test_get_activities_returns_all_with_description():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert len(data) == len(activities)
    for name, details in data.items():
        assert "description" in details


def test_successful_signup_adds_participant():
    email = "newstudent@example.com"
    activity = _find_activity_for_signup(email)
    if activity is None:
        pytest.skip("No activity available for signup in current fixtures")
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 200
    assert email in activities[activity]["participants"]


def test_duplicate_signup_returns_400():
    email = "dupstudent@example.com"
    activity = _find_activity_for_signup(email)
    if activity is None:
        pytest.skip("No activity available for signup in current fixtures")
    resp1 = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp1.status_code == 200
    resp2 = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp2.status_code == 400
    body = resp2.json()
    assert "detail" in body


def test_signup_to_full_activity_returns_400():
    email = "fullstudent@example.com"
    activity = next(iter(activities.keys()))
    details = activities[activity]
    participants = details.get("participants", [])
    details["max_participants"] = len(participants)
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 400
    body = resp.json()
    assert "detail" in body


def test_signup_to_nonexistent_activity_returns_404():
    resp = client.post("/activities/NoSuchActivity/signup", params={"email": "x@y.com"})
    assert resp.status_code == 404
    body = resp.json()
    assert "detail" in body


def test_successful_unregister_removes_participant():
    email = "toremove@example.com"
    activity = _find_activity_for_signup(email)
    if activity is None:
        pytest.skip("No activity available for signup/unregister in current fixtures")
    resp_signup = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp_signup.status_code == 200
    assert email in activities[activity]["participants"]
    resp_del = client.delete(f"/activities/{activity}/participants/{email}")
    assert resp_del.status_code == 200
    assert email not in activities[activity]["participants"]


def test_unregister_nonexistent_participant_returns_404():
    activity = next(iter(activities.keys()))
    nonmember = "notjoined@example.com"
    assert nonmember not in activities[activity].get("participants", [])
    resp = client.delete(f"/activities/{activity}/participants/{nonmember}")
    assert resp.status_code == 404
    body = resp.json()
    assert "detail" in body
