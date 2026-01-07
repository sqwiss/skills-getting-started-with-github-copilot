from fastapi.testclient import TestClient
import pytest

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    # Make a shallow copy of participants lists to restore after each test
    original = {k: v.copy() for k, v in activities.items()}
    yield
    activities.clear()
    activities.update(original)


def test_root_redirects_to_static_index():
    client = TestClient(app)
    resp = client.get("/")
    assert resp.status_code == 200
    # should return index html content from static; check content-type
    assert "text/html" in resp.headers.get("content-type", "")


def test_get_activities_returns_dict():
    client = TestClient(app)
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Basketball Team" in data


def test_signup_and_duplicate_signup():
    client = TestClient(app)
    email = "test.student@mergington.edu"
    resp = client.post("/activities/Basketball Team/signup", params={"email": email})
    assert resp.status_code == 200
    assert email in activities["Basketball Team"]["participants"]

    # duplicate signup should return 400
    resp2 = client.post("/activities/Basketball Team/signup", params={"email": email})
    assert resp2.status_code == 400


def test_signup_nonexistent_activity():
    client = TestClient(app)
    resp = client.post("/activities/Nonexistent/signup", params={"email": "x@x.com"})
    assert resp.status_code == 404


def test_unregister_participant():
    client = TestClient(app)
    email = "alex@mergington.edu"
    # alex is already a participant in Basketball Team per initial data
    resp = client.delete("/activities/Basketball Team/participants", params={"email": email})
    assert resp.status_code == 200
    assert email not in activities["Basketball Team"]["participants"]


def test_unregister_missing_participant():
    client = TestClient(app)
    resp = client.delete("/activities/Basketball Team/participants", params={"email": "noone@x.com"})
    assert resp.status_code == 404
