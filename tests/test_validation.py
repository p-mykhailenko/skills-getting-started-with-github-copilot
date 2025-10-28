"""
Tests for data validation and edge cases
"""

import pytest
from fastapi import status
from src.app import activities


class TestDataValidation:
    """Test data validation and edge cases"""
    
    def test_activity_data_integrity(self, client, reset_activities):
        """Test that activity data maintains integrity after operations"""
        original_activities = dict(activities)
        
        # Perform various operations
        client.post("/activities/Chess Club/signup?email=test1@mergington.edu")
        client.post("/activities/Drama Club/signup?email=test2@mergington.edu")
        client.delete("/activities/Chess Club/unregister?email=michael@mergington.edu")
        
        # Check that data structure is still intact
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)
            assert isinstance(activity_data["max_participants"], int)
            assert activity_data["max_participants"] > 0
    
    def test_concurrent_signups_same_activity(self, client, reset_activities):
        """Test multiple signups for the same activity"""
        activity_name = "Science Club"
        emails = [
            "student1@mergington.edu",
            "student2@mergington.edu", 
            "student3@mergington.edu"
        ]
        
        initial_count = len(activities[activity_name]["participants"])
        
        # Sign up multiple students
        for email in emails:
            response = client.post(f"/activities/{activity_name}/signup?email={email}")
            assert response.status_code == status.HTTP_200_OK
        
        # Verify all were added
        final_count = len(activities[activity_name]["participants"])
        assert final_count == initial_count + len(emails)
        
        for email in emails:
            assert email in activities[activity_name]["participants"]
    
    def test_email_format_variations(self, client, reset_activities):
        """Test various email formats"""
        activity_name = "Art Workshop"
        test_emails = [
            "simple@mergington.edu",
            "with.dots@mergington.edu",
            "with-dashes@mergington.edu",
            "with_underscores@mergington.edu",
            "numbers123@mergington.edu"
        ]
        
        for email in test_emails:
            response = client.post(f"/activities/{activity_name}/signup?email={email}")
            assert response.status_code == status.HTTP_200_OK
            assert email in activities[activity_name]["participants"]
    
    def test_activity_name_case_sensitivity(self, client, reset_activities):
        """Test that activity names are case sensitive"""
        # These should be treated as different activities
        response1 = client.post("/activities/chess club/signup?email=test@mergington.edu")
        response2 = client.post("/activities/Chess Club/signup?email=test@mergington.edu")
        
        # First should fail (lowercase 'chess club' doesn't exist)
        assert response1.status_code == status.HTTP_404_NOT_FOUND
        
        # Second should succeed (proper case 'Chess Club' exists)
        assert response2.status_code == status.HTTP_200_OK


class TestActivityLimits:
    """Test activity participant limits and capacity"""
    
    def test_activity_at_capacity_behavior(self, client, reset_activities):
        """Test behavior when adding participants near capacity"""
        # Find an activity with room for more participants
        activity_name = "Math Olympiad"  # max_participants: 15
        activity = activities[activity_name]
        
        initial_participants = len(activity["participants"])
        max_participants = activity["max_participants"]
        available_spots = max_participants - initial_participants
        
        # Fill up to capacity
        new_emails = [f"student{i}@mergington.edu" for i in range(available_spots)]
        
        for email in new_emails:
            response = client.post(f"/activities/{activity_name}/signup?email={email}")
            assert response.status_code == status.HTTP_200_OK
        
        # Verify we're at capacity
        assert len(activity["participants"]) == max_participants
        
        # Try to add one more (this should still work as we don't enforce limits in the API)
        overflow_response = client.post(f"/activities/{activity_name}/signup?email=overflow@mergington.edu")
        assert overflow_response.status_code == status.HTTP_200_OK
        
        # Verify it was added (showing current implementation doesn't enforce limits)
        assert len(activity["participants"]) == max_participants + 1
    
    def test_empty_activity_operations(self, client, reset_activities):
        """Test operations on activities with no participants"""
        # Create a temporary empty activity
        empty_activity = "Empty Test Activity"
        activities[empty_activity] = {
            "description": "Test activity with no participants",
            "schedule": "Never",
            "max_participants": 10,
            "participants": []
        }
        
        try:
            # Test getting activities includes empty ones
            response = client.get("/activities")
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert empty_activity in data
            assert len(data[empty_activity]["participants"]) == 0
            
            # Test signing up for empty activity
            signup_response = client.post(f"/activities/{empty_activity}/signup?email=first@mergington.edu")
            assert signup_response.status_code == status.HTTP_200_OK
            assert len(activities[empty_activity]["participants"]) == 1
            
            # Test unregistering from activity with one participant
            unregister_response = client.delete(f"/activities/{empty_activity}/unregister?email=first@mergington.edu")
            assert unregister_response.status_code == status.HTTP_200_OK
            assert len(activities[empty_activity]["participants"]) == 0
            
        finally:
            # Clean up
            if empty_activity in activities:
                del activities[empty_activity]


class TestErrorRecovery:
    """Test error recovery and system stability"""
    
    def test_system_state_after_errors(self, client, reset_activities):
        """Test that system remains stable after various errors"""
        initial_state = dict(activities)
        
        # Generate various errors
        error_requests = [
            ("POST", "/activities/NonExistent/signup?email=test@mergington.edu"),
            ("DELETE", "/activities/NonExistent/unregister?email=test@mergington.edu"),
            ("DELETE", "/activities/Chess Club/unregister?email=notregistered@mergington.edu"),
            ("POST", "/activities/Chess Club/signup?email=michael@mergington.edu"),  # Already registered
        ]
        
        for method, url in error_requests:
            if method == "POST":
                response = client.post(url)
            else:
                response = client.delete(url)
            
            # Should be an error response
            assert response.status_code >= 400
        
        # Verify system state is unchanged after errors
        assert activities == initial_state
        
        # Verify system still works normally
        normal_response = client.get("/activities")
        assert normal_response.status_code == status.HTTP_200_OK
    
    def test_malformed_requests(self, client, reset_activities):
        """Test handling of malformed requests"""
        # Test various malformed requests
        malformed_requests = [
            "/activities//signup?email=test@mergington.edu",  # Empty activity name
            "/activities/Chess Club/signup",  # Missing email parameter
            "/activities/Chess Club/signup?email=",  # Empty email
            "/activities/Chess%20Club/signup?email=test%40mergington.edu",  # URL encoded (should work)
        ]
        
        for url in malformed_requests:
            response = client.post(url)
            # System should handle these gracefully (not crash)
            assert response.status_code in [200, 400, 404, 422]