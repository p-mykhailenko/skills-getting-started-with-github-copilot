"""
Tests for the FastAPI application endpoints
"""

import pytest
from fastapi import status
from src.app import activities


class TestRoot:
    """Test the root endpoint"""
    
    def test_root_redirect(self, client):
        """Test that root redirects to static/index.html"""
        # Test with follow_redirects=False to check the redirect response
        response = client.get("/", follow_redirects=False)
        assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
        assert response.headers["location"] == "/static/index.html"
        
        # Test that following redirects works
        response_followed = client.get("/", follow_redirects=True)
        assert response_followed.status_code == status.HTTP_200_OK


class TestGetActivities:
    """Test the activities GET endpoint"""
    
    def test_get_activities_success(self, client, reset_activities):
        """Test successful retrieval of activities"""
        response = client.get("/activities")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Check that we get a dictionary of activities
        assert isinstance(data, dict)
        assert len(data) > 0
        
        # Check structure of first activity
        first_activity = next(iter(data.values()))
        required_fields = ["description", "schedule", "max_participants", "participants"]
        for field in required_fields:
            assert field in first_activity
    
    def test_get_activities_structure(self, client, reset_activities):
        """Test the structure of returned activities data"""
        response = client.get("/activities")
        data = response.json()
        
        # Test specific activity exists
        assert "Chess Club" in data
        chess_club = data["Chess Club"]
        
        assert chess_club["description"] == "Learn strategies and compete in chess tournaments"
        assert chess_club["schedule"] == "Fridays, 3:30 PM - 5:00 PM"
        assert chess_club["max_participants"] == 12
        assert isinstance(chess_club["participants"], list)
        assert "michael@mergington.edu" in chess_club["participants"]


class TestSignupForActivity:
    """Test the activity signup endpoint"""
    
    def test_signup_success(self, client, reset_activities):
        """Test successful signup for an activity"""
        email = "newstudent@mergington.edu"
        activity_name = "Chess Club"
        
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == f"Signed up {email} for {activity_name}"
        
        # Verify the participant was added
        assert email in activities[activity_name]["participants"]
    
    def test_signup_activity_not_found(self, client, reset_activities):
        """Test signup for non-existent activity"""
        email = "student@mergington.edu"
        activity_name = "Non-Existent Activity"
        
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_signup_already_registered(self, client, reset_activities):
        """Test signup when student is already registered"""
        email = "michael@mergington.edu"  # Already in Chess Club
        activity_name = "Chess Club"
        
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert data["detail"] == "Student is already signed up for this activity"
    
    def test_signup_url_encoding(self, client, reset_activities):
        """Test signup with URL-encoded activity name and email"""
        email = "test@mergington.edu"
        activity_name = "Programming Class"
        
        # Test with URL encoding
        encoded_activity = "Programming%20Class"
        encoded_email = "test%40mergington.edu"
        
        response = client.post(f"/activities/{encoded_activity}/signup?email={encoded_email}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == f"Signed up {email} for {activity_name}"


class TestUnregisterFromActivity:
    """Test the activity unregister endpoint"""
    
    def test_unregister_success(self, client, reset_activities):
        """Test successful unregistration from an activity"""
        email = "michael@mergington.edu"  # Already in Chess Club
        activity_name = "Chess Club"
        
        # Verify student is initially registered
        assert email in activities[activity_name]["participants"]
        
        response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == f"Unregistered {email} from {activity_name}"
        
        # Verify the participant was removed
        assert email not in activities[activity_name]["participants"]
    
    def test_unregister_activity_not_found(self, client, reset_activities):
        """Test unregister from non-existent activity"""
        email = "student@mergington.edu"
        activity_name = "Non-Existent Activity"
        
        response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_unregister_student_not_registered(self, client, reset_activities):
        """Test unregister when student is not registered"""
        email = "notregistered@mergington.edu"
        activity_name = "Chess Club"
        
        response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert data["detail"] == "Student is not registered for this activity"
    
    def test_unregister_url_encoding(self, client, reset_activities):
        """Test unregister with URL-encoded activity name and email"""
        email = "emma@mergington.edu"  # Already in Programming Class
        activity_name = "Programming Class"
        
        # Test with URL encoding
        encoded_activity = "Programming%20Class"
        encoded_email = "emma%40mergington.edu"
        
        response = client.delete(f"/activities/{encoded_activity}/unregister?email={encoded_email}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == f"Unregistered {email} from {activity_name}"


class TestIntegrationScenarios:
    """Test complex scenarios involving multiple operations"""
    
    def test_signup_and_unregister_flow(self, client, reset_activities):
        """Test complete flow of signing up and then unregistering"""
        email = "flowtest@mergington.edu"
        activity_name = "Drama Club"
        
        # Initial state - student not registered
        assert email not in activities[activity_name]["participants"]
        
        # Sign up
        signup_response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert signup_response.status_code == status.HTTP_200_OK
        assert email in activities[activity_name]["participants"]
        
        # Unregister
        unregister_response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
        assert unregister_response.status_code == status.HTTP_200_OK
        assert email not in activities[activity_name]["participants"]
    
    def test_multiple_signups_different_activities(self, client, reset_activities):
        """Test signing up for multiple activities"""
        email = "multi@mergington.edu"
        activities_to_join = ["Chess Club", "Drama Club", "Science Club"]
        
        for activity_name in activities_to_join:
            response = client.post(f"/activities/{activity_name}/signup?email={email}")
            assert response.status_code == status.HTTP_200_OK
            assert email in activities[activity_name]["participants"]
    
    def test_activity_capacity_tracking(self, client, reset_activities):
        """Test that activity capacity is properly tracked"""
        # Get initial state
        response = client.get("/activities")
        initial_data = response.json()
        
        activity_name = "Chess Club"
        initial_participants = len(initial_data[activity_name]["participants"])
        max_participants = initial_data[activity_name]["max_participants"]
        
        # Add a new participant
        new_email = "capacity@mergington.edu"
        signup_response = client.post(f"/activities/{activity_name}/signup?email={new_email}")
        assert signup_response.status_code == status.HTTP_200_OK
        
        # Check updated state
        updated_response = client.get("/activities")
        updated_data = updated_response.json()
        
        new_participants_count = len(updated_data[activity_name]["participants"])
        assert new_participants_count == initial_participants + 1
        assert new_participants_count <= max_participants


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_missing_email_parameter(self, client, reset_activities):
        """Test signup without email parameter"""
        activity_name = "Chess Club"
        
        # This should fail due to missing required email parameter
        response = client.post(f"/activities/{activity_name}/signup")
        assert response.status_code == 422  # Unprocessable Entity
    
    def test_empty_email_parameter(self, client, reset_activities):
        """Test signup with empty email parameter"""
        activity_name = "Chess Club"
        
        response = client.post(f"/activities/{activity_name}/signup?email=")
        assert response.status_code == status.HTTP_200_OK
        # Empty string is treated as valid email in this simple implementation
    
    def test_special_characters_in_activity_name(self, client, reset_activities):
        """Test with special characters in activity name"""
        # Add a test activity with special characters
        special_activity = "Art & Crafts (Advanced)"
        activities[special_activity] = {
            "description": "Advanced art and crafts",
            "schedule": "Mondays, 3:00 PM",
            "max_participants": 10,
            "participants": []
        }
        
        email = "artist@mergington.edu"
        
        # Test signup
        response = client.post(f"/activities/{special_activity}/signup?email={email}")
        assert response.status_code == status.HTTP_200_OK
        
        # Clean up
        del activities[special_activity]