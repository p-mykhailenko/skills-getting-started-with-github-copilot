"""
Tests for static file serving and frontend functionality
"""

import pytest
from fastapi import status


class TestStaticFiles:
    """Test static file serving"""
    
    def test_static_html_file(self, client):
        """Test serving static HTML file"""
        response = client.get("/static/index.html")
        
        assert response.status_code == status.HTTP_200_OK
        assert "text/html" in response.headers.get("content-type", "")
        
        # Check for basic HTML structure
        content = response.text
        assert "<!DOCTYPE html>" in content
        assert "<title>Mergington High School Activities</title>" in content
        assert "activities-list" in content
        assert "signup-form" in content
    
    def test_static_css_file(self, client):
        """Test serving static CSS file"""
        response = client.get("/static/styles.css")
        
        assert response.status_code == status.HTTP_200_OK
        assert "text/css" in response.headers.get("content-type", "")
        
        # Check for some CSS content
        content = response.text
        assert "body" in content
        assert "activity-card" in content
        assert "participants-list" in content
    
    def test_static_js_file(self, client):
        """Test serving static JavaScript file"""
        response = client.get("/static/app.js")
        
        assert response.status_code == status.HTTP_200_OK
        assert "javascript" in response.headers.get("content-type", "").lower()
        
        # Check for JavaScript content
        content = response.text
        assert "DOMContentLoaded" in content
        assert "fetchActivities" in content
        assert "unregisterParticipant" in content
    
    def test_static_file_not_found(self, client):
        """Test requesting non-existent static file"""
        response = client.get("/static/nonexistent.txt")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestAPIDocumentation:
    """Test FastAPI auto-generated documentation"""
    
    def test_openapi_schema(self, client):
        """Test OpenAPI schema endpoint"""
        response = client.get("/openapi.json")
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert data["info"]["title"] == "Mergington High School API"
        assert "paths" in data
        
        # Check that our endpoints are documented
        paths = data["paths"]
        assert "/activities" in paths
        assert "/activities/{activity_name}/signup" in paths
        assert "/activities/{activity_name}/unregister" in paths
    
    def test_docs_endpoint(self, client):
        """Test Swagger UI docs endpoint"""
        response = client.get("/docs")
        
        assert response.status_code == status.HTTP_200_OK
        assert "text/html" in response.headers.get("content-type", "")
        
        # Check for Swagger UI content
        content = response.text
        assert "swagger-ui" in content.lower()
    
    def test_redoc_endpoint(self, client):
        """Test ReDoc documentation endpoint"""
        response = client.get("/redoc")
        
        assert response.status_code == status.HTTP_200_OK
        assert "text/html" in response.headers.get("content-type", "")
        
        # Check for ReDoc content
        content = response.text
        assert "redoc" in content.lower()