from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import app


client = TestClient(app)


def test_root_redirect():
    resp = client.get("/", follow_redirects=False)
    assert resp.status_code in (302, 307)
    assert resp.headers.get("location") == "/static/index.html"


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]


def test_signup_and_unregister():
    activity = "Chess Club"
    email = "testuser@example.com"
    signup_path = f"/activities/{quote(activity)}/signup"

    # Ensure the test email is not already a participant
    resp = client.get("/activities")
    assert resp.status_code == 200
    assert email not in resp.json()[activity]["participants"]

    # Sign up
    resp = client.post(signup_path, params={"email": email})
    assert resp.status_code == 200
    assert email in resp.json()["message"]

    # Duplicate signup should fail
    resp = client.post(signup_path, params={"email": email})
    assert resp.status_code == 400

    # Unregister
    del_path = f"/activities/{quote(activity)}/participants"
    resp = client.delete(del_path, params={"email": email})
    assert resp.status_code == 200

    # Confirm removed
    resp = client.get("/activities")
    assert email not in resp.json()[activity]["participants"]


def test_activity_not_found():
    bad = "NoSuchActivity"
    signup_path = f"/activities/{quote(bad)}/signup"
    resp = client.post(signup_path, params={"email": "x@example.com"})
    assert resp.status_code == 404
