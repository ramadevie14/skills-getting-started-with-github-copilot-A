from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)

@pytest.fixture(autouse=True)
def restore_activities():
    original_activities = deepcopy(activities)
    yield
    activities.clear()
    activities.update(original_activities)


def test_get_activities_returns_activity_list():
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert data["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"
    assert data["Chess Club"]["participants"] == ["michael@mergington.edu", "daniel@mergington.edu"]


def test_signup_adds_participant_successfully():
    response = client.post("/activities/Chess%20Club/signup?email=test@student.com")

    assert response.status_code == 200
    assert response.json()["message"] == "Signed up test@student.com for Chess Club"
    assert "test@student.com" in activities["Chess Club"]["participants"]


def test_signup_rejects_duplicate_participant():
    response = client.post("/activities/Chess%20Club/signup?email=michael@mergington.edu")

    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_remove_participant_successfully():
    response = client.delete("/activities/Chess%20Club/participants?email=michael@mergington.edu")

    assert response.status_code == 200
    assert response.json()["message"] == "Removed michael@mergington.edu from Chess Club"
    assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]


def test_remove_participant_not_found():
    response = client.delete("/activities/Chess%20Club/participants?email=missing@student.com")

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
