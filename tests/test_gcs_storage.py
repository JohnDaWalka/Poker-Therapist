"""Tests for GCS storage endpoints."""

import os
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def mock_gcs_storage():
    """Mock GCS storage service."""
    mock = MagicMock()
    mock.generate_signed_upload_url.return_value = {
        "blob_name": "test/uuid_test.png",
        "url": "https://storage.googleapis.com/test-bucket/test/uuid_test.png?signature=...",
        "method": "PUT",
        "headers": {"Content-Type": "image/png"},
    }
    mock.generate_signed_download_url.return_value = {
        "blob_name": "test/uuid_test.png",
        "url": "https://storage.googleapis.com/test-bucket/test/uuid_test.png?signature=...",
        "method": "GET",
    }
    mock.blob_exists.return_value = True
    return mock


def test_storage_endpoints_disabled():
    """Test storage endpoints return 400 when GCS is disabled."""
    from backend.api.main import app
    
    # Ensure GCS is disabled
    app.state.gcs_storage = None
    
    client = TestClient(app)
    
    # Test upload endpoint
    response = client.post(
        "/api/storage/signed-upload",
        json={
            "filename": "test.png",
            "content_type": "image/png",
        },
    )
    assert response.status_code == 400
    assert "not enabled" in response.json()["detail"].lower()
    
    # Test download endpoint
    response = client.get(
        "/api/storage/signed-download",
        params={"blob_name": "test/test.png"},
    )
    assert response.status_code == 400
    assert "not enabled" in response.json()["detail"].lower()


def test_signed_upload_url_generation(mock_gcs_storage):
    """Test signed upload URL generation."""
    from backend.api.main import app
    
    app.state.gcs_storage = mock_gcs_storage
    
    client = TestClient(app)
    
    response = client.post(
        "/api/storage/signed-upload",
        json={
            "filename": "test.png",
            "content_type": "image/png",
            "prefix": "uploads",
            "expires_minutes": 30,
        },
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "blob_name" in data
    assert "url" in data
    assert data["method"] == "PUT"
    assert "headers" in data
    assert data["headers"]["Content-Type"] == "image/png"


def test_signed_download_url_generation(mock_gcs_storage):
    """Test signed download URL generation."""
    from backend.api.main import app
    
    app.state.gcs_storage = mock_gcs_storage
    
    client = TestClient(app)
    
    response = client.get(
        "/api/storage/signed-download",
        params={
            "blob_name": "test/uuid_test.png",
            "expires_minutes": 15,
        },
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["blob_name"] == "test/uuid_test.png"
    assert "url" in data
    assert data["method"] == "GET"


def test_signed_download_blob_not_found(mock_gcs_storage):
    """Test download endpoint returns 404 when blob doesn't exist."""
    from backend.api.main import app
    
    mock_gcs_storage.blob_exists.return_value = False
    app.state.gcs_storage = mock_gcs_storage
    
    client = TestClient(app)
    
    response = client.get(
        "/api/storage/signed-download",
        params={"blob_name": "nonexistent.png"},
    )
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_signed_upload_without_prefix(mock_gcs_storage):
    """Test upload URL generation without prefix."""
    from backend.api.main import app
    
    app.state.gcs_storage = mock_gcs_storage
    
    client = TestClient(app)
    
    response = client.post(
        "/api/storage/signed-upload",
        json={
            "filename": "test.pdf",
            "content_type": "application/pdf",
        },
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "blob_name" in data
    # Should have UUID but no directory prefix (no "/" separator)
    assert "/" not in data["blob_name"]


@pytest.mark.skipif(
    not os.getenv("GCS_BUCKET_NAME"),
    reason="GCS credentials not available",
)
def test_gcs_integration():
    """Integration test with real GCS (only runs if credentials available)."""
    from python_src.services.gcs_storage_service import GCSStorageService
    
    # This will only run in environments with GCS configured
    service = GCSStorageService()
    
    # Test upload URL generation
    result = service.generate_signed_upload_url(
        blob_name="test/integration_test.txt",
        content_type="text/plain",
        expires_minutes=5,
    )
    
    assert "url" in result
    assert "blob_name" in result
    assert result["method"] == "PUT"
