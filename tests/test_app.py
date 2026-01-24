import sys
from pathlib import Path

# Add src directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from fastapi.testclient import TestClient
from app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state after each test"""
    yield
    # Reset to initial state
    activities.clear()
    activities.update({
        "Tennis Club": {
            "description": "Learn tennis skills and participate in friendly matches",
            "schedule": "Wednesdays and Saturdays, 4:00 PM - 5:30 PM",
            "max_participants": 16,
            "participants": ["alex@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball training and games",
            "schedule": "Mondays and Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu", "lucas@mergington.edu"]
        },
        "Debate Club": {
            "description": "Develop critical thinking and public speaking skills through debate",
            "schedule": "Tuesdays, 4:00 PM - 5:30 PM",
            "max_participants": 20,
            "participants": ["sara@mergington.edu"]
        },
        "Robotics Team": {
            "description": "Build and program robots for competitions",
            "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["noah@mergington.edu", "mia@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore painting, drawing, and sculpture techniques",
            "schedule": "Mondays and Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["isabella@mergington.edu"]
        },
        "Drama Club": {
            "description": "Act in school plays and develop theatrical skills",
            "schedule": "Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["grace@mergington.edu", "henry@mergington.edu"]
        },
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    })


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities(self, client, reset_activities):
        """Test retrieving all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Tennis Club" in data
        assert data["Tennis Club"]["description"] == "Learn tennis skills and participate in friendly matches"

    def test_get_activities_contains_all_fields(self, client, reset_activities):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        data = response.json()
        tennis = data["Tennis Club"]
        
        assert "description" in tennis
        assert "schedule" in tennis
        assert "max_participants" in tennis
        assert "participants" in tennis

    def test_get_activities_participants_list(self, client, reset_activities):
        """Test that participants are returned as a list"""
        response = client.get("/activities")
        data = response.json()
        
        assert isinstance(data["Tennis Club"]["participants"], list)
        assert "alex@mergington.edu" in data["Tennis Club"]["participants"]


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_new_participant(self, client, reset_activities):
        """Test signing up a new participant"""
        response = client.post(
            "/activities/Tennis%20Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert "newstudent@mergington.edu" in data["message"]

    def test_signup_adds_participant_to_activity(self, client, reset_activities):
        """Test that signup actually adds the participant"""
        client.post(
            "/activities/Tennis%20Club/signup?email=test@mergington.edu"
        )
        response = client.get("/activities")
        participants = response.json()["Tennis Club"]["participants"]
        assert "test@mergington.edu" in participants

    def test_signup_duplicate_participant_fails(self, client, reset_activities):
        """Test that signing up an already registered participant fails"""
        # Alex is already registered for Tennis Club
        response = client.post(
            "/activities/Tennis%20Club/signup?email=alex@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_nonexistent_activity_fails(self, client, reset_activities):
        """Test signing up for a non-existent activity"""
        response = client.post(
            "/activities/Nonexistent%20Activity/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_signup_multiple_students_same_activity(self, client, reset_activities):
        """Test multiple students can sign up for the same activity"""
        client.post(
            "/activities/Tennis%20Club/signup?email=student1@mergington.edu"
        )
        response2 = client.post(
            "/activities/Tennis%20Club/signup?email=student2@mergington.edu"
        )
        
        assert response2.status_code == 200
        response = client.get("/activities")
        participants = response.json()["Tennis Club"]["participants"]
        assert "student1@mergington.edu" in participants
        assert "student2@mergington.edu" in participants


class TestRemoveParticipant:
    """Tests for DELETE /activities/{activity_name}/participant endpoint"""

    def test_remove_participant(self, client, reset_activities):
        """Test removing a participant from an activity"""
        response = client.delete(
            "/activities/Tennis%20Club/participant?email=alex@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Removed" in data["message"]

    def test_remove_participant_actually_removes(self, client, reset_activities):
        """Test that remove actually removes the participant"""
        client.delete(
            "/activities/Tennis%20Club/participant?email=alex@mergington.edu"
        )
        response = client.get("/activities")
        participants = response.json()["Tennis Club"]["participants"]
        assert "alex@mergington.edu" not in participants

    def test_remove_nonexistent_participant_fails(self, client, reset_activities):
        """Test removing a participant who isn't in the activity"""
        response = client.delete(
            "/activities/Tennis%20Club/participant?email=notregistered@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Participant not found" in data["detail"]

    def test_remove_from_nonexistent_activity_fails(self, client, reset_activities):
        """Test removing from a non-existent activity"""
        response = client.delete(
            "/activities/Nonexistent%20Activity/participant?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_signup_then_remove(self, client, reset_activities):
        """Test signing up and then removing a participant"""
        # Sign up
        client.post(
            "/activities/Basketball%20Team/signup?email=test@mergington.edu"
        )
        response1 = client.get("/activities")
        assert "test@mergington.edu" in response1.json()["Basketball Team"]["participants"]
        
        # Remove
        client.delete(
            "/activities/Basketball%20Team/participant?email=test@mergington.edu"
        )
        response2 = client.get("/activities")
        assert "test@mergington.edu" not in response2.json()["Basketball Team"]["participants"]
