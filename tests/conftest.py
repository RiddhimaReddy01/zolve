"""Pytest configuration and fixtures."""

import pytest
import requests
import time


@pytest.fixture(scope="session", autouse=True)
def wait_for_backend():
    """Wait for backend to be ready before running tests."""
    max_retries = 30
    retry_count = 0

    while retry_count < max_retries:
        try:
            resp = requests.get("http://localhost:8000/health", timeout=2)
            if resp.status_code == 200:
                print("\n✓ Backend is ready")
                yield
                return
        except requests.exceptions.ConnectionError:
            retry_count += 1
            if retry_count < max_retries:
                time.sleep(1)

    pytest.fail(
        f"Backend not available after {max_retries} seconds. "
        "Ensure backend is running: python backend/main.py"
    )


@pytest.fixture
def api_base_url():
    """API base URL."""
    return "http://localhost:8000/api"


@pytest.fixture
def test_user_id():
    """Test user ID."""
    return 1


@pytest.fixture
def cleanup_ad_views():
    """Clear today's ad views for test user before running tests."""
    import sys
    import os
    from datetime import datetime
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
    from database import Database

    db = Database()
    # Delete today's ad_views for user 1 (just delete all for testing)
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM ad_views WHERE user_id = 1")
        conn.commit()
    yield
    # Cleanup after test
