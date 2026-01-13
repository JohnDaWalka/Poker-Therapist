"""Tests for GCS storage service."""

import os
from unittest.mock import MagicMock, patch

import importlib.util
import pytest

# Detect whether google-cloud-storage is available without importing it
try:
    GCS_AVAILABLE = importlib.util.find_spec("google.cloud.storage") is not None
except ImportError:
    GCS_AVAILABLE = False


# Skip all tests if GCS is not available
pytestmark = pytest.mark.skipif(
    not GCS_AVAILABLE,
    reason="Google Cloud Storage library not installed"
)


@pytest.fixture
def mock_gcs_client():
    """Create a mock GCS client."""
    with patch("python_src.services.gcs_storage_service.storage.Client") as mock_client:
        mock_bucket = MagicMock()
        mock_client.return_value.bucket.return_value = mock_bucket
        yield mock_client, mock_bucket


@pytest.fixture
def gcs_service(mock_gcs_client):
    """Create a GCS storage service with mocked client."""
    from python_src.services.gcs_storage_service import GCSStorageService
    
    with patch.dict(os.environ, {"GCS_BUCKET_NAME": "test-bucket"}):
        service = GCSStorageService()
        return service


def test_init_requires_bucket_name():
    """Test that initialization requires bucket name."""
    from python_src.services.gcs_storage_service import GCSStorageService
    
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(RuntimeError, match="GCS bucket name not configured"):
            GCSStorageService()


def test_init_with_bucket_name(mock_gcs_client):
    """Test initialization with bucket name."""
    from python_src.services.gcs_storage_service import GCSStorageService
    
    service = GCSStorageService(bucket_name="test-bucket")
    assert service.bucket_name == "test-bucket"


def test_upload_audio(gcs_service, mock_gcs_client):
    """Test uploading audio file."""
    _, mock_bucket = mock_gcs_client
    mock_blob = MagicMock()
    mock_bucket.blob.return_value = mock_blob
    
    audio_data = b"fake audio data"
    user_id = "user123"
    filename = "test.mp3"
    
    blob_name = gcs_service.upload_audio(audio_data, user_id, filename)
    
    assert blob_name == f"audio/{user_id}/{filename}"
    mock_bucket.blob.assert_called_once_with(blob_name)
    mock_blob.upload_from_string.assert_called_once_with(
        audio_data,
        content_type="audio/mpeg",
    )


def test_upload_audio_custom_content_type(gcs_service, mock_gcs_client):
    """Test uploading audio with custom content type."""
    _, mock_bucket = mock_gcs_client
    mock_blob = MagicMock()
    mock_bucket.blob.return_value = mock_blob
    
    audio_data = b"fake audio data"
    
    gcs_service.upload_audio(
        audio_data,
        "user123",
        "test.wav",
        content_type="audio/wav",
    )
    
    mock_blob.upload_from_string.assert_called_once_with(
        audio_data,
        content_type="audio/wav",
    )


def test_download_audio(gcs_service, mock_gcs_client):
    """Test downloading audio file."""
    _, mock_bucket = mock_gcs_client
    mock_blob = MagicMock()
    mock_bucket.blob.return_value = mock_blob
    mock_blob.download_as_bytes.return_value = b"audio content"
    
    blob_name = "audio/user123/test.mp3"
    result = gcs_service.download_audio(blob_name)
    
    assert result == b"audio content"
    mock_bucket.blob.assert_called_once_with(blob_name)
    mock_blob.download_as_bytes.assert_called_once()


def test_download_audio_not_found(gcs_service, mock_gcs_client):
    """Test downloading non-existent audio file."""
    from google.cloud.exceptions import NotFound
    
    _, mock_bucket = mock_gcs_client
    mock_blob = MagicMock()
    mock_bucket.blob.return_value = mock_blob
    mock_blob.download_as_bytes.side_effect = NotFound("Not found")
    
    with pytest.raises(RuntimeError, match="Audio file not found"):
        gcs_service.download_audio("audio/user123/missing.mp3")


def test_upload_voice_profile(gcs_service, mock_gcs_client):
    """Test uploading voice profile samples."""
    _, mock_bucket = mock_gcs_client
    mock_blobs = [MagicMock() for _ in range(3)]
    mock_bucket.blob.side_effect = mock_blobs
    
    profile_id = "profile123"
    user_id = "user123"
    voice_samples = [b"sample1", b"sample2", b"sample3"]
    
    blob_names = gcs_service.upload_voice_profile(profile_id, user_id, voice_samples)
    
    assert len(blob_names) == 3
    assert blob_names[0] == f"voice_profiles/{user_id}/{profile_id}/sample_0.wav"
    assert blob_names[1] == f"voice_profiles/{user_id}/{profile_id}/sample_1.wav"
    assert blob_names[2] == f"voice_profiles/{user_id}/{profile_id}/sample_2.wav"
    
    # Verify all samples were uploaded
    for i, mock_blob in enumerate(mock_blobs):
        mock_blob.upload_from_string.assert_called_once_with(
            voice_samples[i],
            content_type="audio/wav",
        )


def test_download_voice_profile(gcs_service, mock_gcs_client):
    """Test downloading voice profile samples."""
    _, mock_bucket = mock_gcs_client
    
    # Set up mock blobs with different data
    sample_data = [b"sample1", b"sample2", b"sample3"]
    mock_blobs = []
    for data in sample_data:
        mock_blob = MagicMock()
        mock_blob.download_as_bytes.return_value = data
        mock_blobs.append(mock_blob)
    
    mock_bucket.blob.side_effect = mock_blobs
    
    blob_names = [
        "voice_profiles/user123/profile123/sample_0.wav",
        "voice_profiles/user123/profile123/sample_1.wav",
        "voice_profiles/user123/profile123/sample_2.wav",
    ]
    
    result = gcs_service.download_voice_profile(blob_names)
    
    assert result == sample_data
    assert len(result) == 3


def test_delete_audio(gcs_service, mock_gcs_client):
    """Test deleting audio file."""
    _, mock_bucket = mock_gcs_client
    mock_blob = MagicMock()
    mock_bucket.blob.return_value = mock_blob
    
    blob_name = "audio/user123/test.mp3"
    result = gcs_service.delete_audio(blob_name)
    
    assert result is True
    mock_blob.delete.assert_called_once()


def test_delete_audio_not_found(gcs_service, mock_gcs_client):
    """Test deleting non-existent audio file."""
    from google.cloud.exceptions import NotFound
    
    _, mock_bucket = mock_gcs_client
    mock_blob = MagicMock()
    mock_bucket.blob.return_value = mock_blob
    mock_blob.delete.side_effect = NotFound("Not found")
    
    result = gcs_service.delete_audio("audio/user123/missing.mp3")
    assert result is False


def test_delete_voice_profile(gcs_service, mock_gcs_client):
    """Test deleting voice profile samples."""
    _, mock_bucket = mock_gcs_client
    
    # Create mock blobs
    mock_blobs = [MagicMock() for _ in range(3)]
    mock_bucket.blob.side_effect = mock_blobs
    
    blob_names = [
        "voice_profiles/user123/profile123/sample_0.wav",
        "voice_profiles/user123/profile123/sample_1.wav",
        "voice_profiles/user123/profile123/sample_2.wav",
    ]
    
    deleted_count = gcs_service.delete_voice_profile(blob_names)
    
    assert deleted_count == 3
    for mock_blob in mock_blobs:
        mock_blob.delete.assert_called_once()


def test_get_signed_url(gcs_service, mock_gcs_client):
    """Test generating signed URL."""
    from datetime import timedelta
    
    _, mock_bucket = mock_gcs_client
    mock_blob = MagicMock()
    mock_bucket.blob.return_value = mock_blob
    mock_blob.generate_signed_url.return_value = "https://signed-url.example.com"
    
    blob_name = "audio/user123/test.mp3"
    url = gcs_service.get_signed_url(blob_name, expiration_minutes=30)
    
    assert url == "https://signed-url.example.com"
    mock_blob.generate_signed_url.assert_called_once()
    
    # Verify expiration parameter
    call_args = mock_blob.generate_signed_url.call_args
    assert call_args[1]["expiration"] == timedelta(minutes=30)
    assert call_args[1]["method"] == "GET"


def test_list_user_audio(gcs_service, mock_gcs_client):
    """Test listing user audio files."""
    _, mock_bucket = mock_gcs_client
    
    # Create mock blobs
    mock_blobs = [
        MagicMock(name="audio/user123/file1.mp3"),
        MagicMock(name="audio/user123/file2.mp3"),
        MagicMock(name="audio/user123/file3.mp3"),
    ]
    mock_bucket.list_blobs.return_value = mock_blobs
    
    user_id = "user123"
    blob_names = gcs_service.list_user_audio(user_id)
    
    assert len(blob_names) == 3
    mock_bucket.list_blobs.assert_called_once_with(prefix=f"audio/{user_id}/")


def test_is_available(gcs_service, mock_gcs_client):
    """Test checking if GCS is available."""
    _, mock_bucket = mock_gcs_client
    
    # Test when bucket is accessible
    result = gcs_service.is_available()
    assert result is True
    mock_bucket.reload.assert_called_once()


def test_is_available_failure(gcs_service, mock_gcs_client):
    """Test checking availability when bucket is not accessible."""
    _, mock_bucket = mock_gcs_client
    mock_bucket.reload.side_effect = Exception("Access denied")
    
    result = gcs_service.is_available()
    assert result is False


def test_get_gcs_service_with_fallback():
    """Test getting GCS service with fallback."""
    from python_src.services.gcs_storage_service import get_gcs_service
    
    with patch.dict(os.environ, {}, clear=True):
        # Should return None when not configured with fallback=True
        service = get_gcs_service(fallback_to_local=True)
        assert service is None


def test_get_gcs_service_without_fallback():
    """Test getting GCS service without fallback."""
    from python_src.services.gcs_storage_service import get_gcs_service
    
    with patch.dict(os.environ, {}, clear=True):
        # Should raise error when not configured with fallback=False
        with pytest.raises(RuntimeError):
            get_gcs_service(fallback_to_local=False)
