# Tests for Mergington High School Activities API

This directory contains comprehensive test suites for the FastAPI application using pytest.

## Test Structure

- **`conftest.py`** - Shared fixtures and test configuration
- **`test_api.py`** - Tests for all API endpoints (GET, POST, DELETE)
- **`test_static.py`** - Tests for static file serving and API documentation
- **`test_validation.py`** - Tests for data validation and edge cases

## Running Tests

### Run All Tests
```bash
cd /workspaces/skills-getting-started-with-github-copilot
python -m pytest tests/ -v
```

### Run Tests with Coverage
```bash
python -m pytest tests/ --cov=src --cov-report=term-missing
```

### Run Specific Test File
```bash
python -m pytest tests/test_api.py -v
```

### Run Specific Test Class
```bash
python -m pytest tests/test_api.py::TestRoot -v
```

### Run Specific Test Method
```bash
python -m pytest tests/test_api.py::TestRoot::test_root_redirect -v
```

## Test Coverage

The test suite provides 100% code coverage for the FastAPI application, testing:

### API Endpoints
- **Root endpoint** (`/`) - Redirect functionality
- **Activities endpoint** (`/activities`) - Retrieving all activities
- **Signup endpoint** (`/activities/{name}/signup`) - Student registration
- **Unregister endpoint** (`/activities/{name}/unregister`) - Student removal

### Static File Serving
- HTML, CSS, and JavaScript file serving
- 404 handling for missing files
- OpenAPI documentation endpoints

### Data Validation & Edge Cases
- Email format validation
- Activity name case sensitivity
- Concurrent operations
- Error recovery
- Malformed requests
- Activity capacity tracking

### Integration Scenarios
- Complete signup/unregister workflows
- Multiple activity registrations
- System state integrity

## Test Fixtures

### `client`
Provides a TestClient instance for making HTTP requests to the FastAPI app.

### `reset_activities`
Resets the activities data to its original state before and after each test to ensure test isolation.

### `sample_activity`
Provides sample activity data for testing purposes.

## Dependencies

The tests require the following packages (all listed in `requirements.txt`):

- `pytest` - Testing framework
- `pytest-asyncio` - Async test support
- `pytest-cov` - Coverage reporting
- `httpx` - HTTP client for FastAPI TestClient
- `fastapi` - Web framework being tested

## Test Configuration

Tests are configured via `pytest.ini` in the project root, which sets the Python path to include the project directory.