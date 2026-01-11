"""Google Cloud Storage service for binary data (audio files, voice profiles)."""

import os
from datetime import timedelta
from typing import Optional

try:
    from google.cloud import storage
    from google.cloud.exceptions import NotFound
    GCS_AVAILABLE = True
except ImportError:
    GCS_AVAILABLE = False


class GCSStorageService:
    """
    Service for storing and retrieving binary data in Google Cloud Storage.
    
    This service handles:
    - Audio files (voice recordings, TTS output)
    - Voice profiles (cloned voice samples)
    - Large binary data that shouldn't be stored in SQLite
    """
    
    def __init__(
        self,
        bucket_name: Optional[str] = None,
        credentials_path: Optional[str] = None,
    ) -> None:
        """
        Initialize GCS storage service.
        
        Args:
            bucket_name: GCS bucket name (defaults to env var GCS_BUCKET_NAME)
            credentials_path: Path to GCS credentials JSON (defaults to env var GOOGLE_APPLICATION_CREDENTIALS)
            
        Raises:
            RuntimeError: If GCS is not available or not configured
        """
        if not GCS_AVAILABLE:
            raise RuntimeError(
                "Google Cloud Storage is not available. "
                "Install with: pip install google-cloud-storage"
            )
        
        self.bucket_name = bucket_name or os.getenv("GCS_BUCKET_NAME")
        if not self.bucket_name:
            raise RuntimeError(
                "GCS bucket name not configured. "
                "Set GCS_BUCKET_NAME environment variable or pass bucket_name parameter."
            )
        
        # Set credentials path if provided
        if credentials_path:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
        
        # Initialize GCS client
        try:
            self.client = storage.Client()
            self.bucket = self.client.bucket(self.bucket_name)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize GCS client: {e}") from e
    
    def upload_audio(
        self,
        audio_data: bytes,
        user_id: str,
        filename: str,
        content_type: str = "audio/mpeg",
    ) -> str:
        """
        Upload audio file to GCS.
        
        Args:
            audio_data: Audio data as bytes
            user_id: User identifier for organizing files
            filename: Filename for the audio
            content_type: MIME type of audio file
            
        Returns:
            GCS object path (blob name)
            
        Raises:
            RuntimeError: If upload fails
        """
        try:
            # Create blob path: audio/{user_id}/{filename}
            blob_name = f"audio/{user_id}/{filename}"
            blob = self.bucket.blob(blob_name)
            
            # Upload with metadata
            blob.upload_from_string(
                audio_data,
                content_type=content_type,
            )
            
            return blob_name
        except Exception as e:
            raise RuntimeError(f"Failed to upload audio to GCS: {e}") from e
    
    def download_audio(self, blob_name: str) -> bytes:
        """
        Download audio file from GCS.
        
        Args:
            blob_name: GCS object path
            
        Returns:
            Audio data as bytes
            
        Raises:
            RuntimeError: If download fails or blob not found
        """
        try:
            blob = self.bucket.blob(blob_name)
            return blob.download_as_bytes()
        except NotFound:
            raise RuntimeError(f"Audio file not found: {blob_name}") from None
        except Exception as e:
            raise RuntimeError(f"Failed to download audio from GCS: {e}") from e
    
    def upload_voice_profile(
        self,
        profile_id: str,
        user_id: str,
        voice_samples: list[bytes],
    ) -> list[str]:
        """
        Upload voice profile samples to GCS.
        
        Args:
            profile_id: Unique profile identifier
            user_id: User identifier
            voice_samples: List of audio samples
            
        Returns:
            List of GCS blob names for each sample
            
        Raises:
            RuntimeError: If upload fails
        """
        try:
            blob_names = []
            
            for i, sample_data in enumerate(voice_samples):
                # Create blob path: voice_profiles/{user_id}/{profile_id}/sample_{i}.wav
                blob_name = f"voice_profiles/{user_id}/{profile_id}/sample_{i}.wav"
                blob = self.bucket.blob(blob_name)
                
                # Upload sample
                blob.upload_from_string(
                    sample_data,
                    content_type="audio/wav",
                )
                
                blob_names.append(blob_name)
            
            return blob_names
        except Exception as e:
            raise RuntimeError(f"Failed to upload voice profile to GCS: {e}") from e
    
    def download_voice_profile(self, blob_names: list[str]) -> list[bytes]:
        """
        Download voice profile samples from GCS.
        
        Args:
            blob_names: List of GCS object paths
            
        Returns:
            List of audio data as bytes
            
        Raises:
            RuntimeError: If download fails
        """
        try:
            samples = []
            
            for blob_name in blob_names:
                blob = self.bucket.blob(blob_name)
                sample_data = blob.download_as_bytes()
                samples.append(sample_data)
            
            return samples
        except NotFound as e:
            raise RuntimeError(f"Voice profile sample not found: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Failed to download voice profile from GCS: {e}") from e
    
    def delete_audio(self, blob_name: str) -> bool:
        """
        Delete audio file from GCS.
        
        Args:
            blob_name: GCS object path
            
        Returns:
            True if deleted, False if not found
        """
        try:
            blob = self.bucket.blob(blob_name)
            blob.delete()
            return True
        except NotFound:
            return False
        except Exception as e:
            raise RuntimeError(f"Failed to delete audio from GCS: {e}") from e
    
    def delete_voice_profile(self, blob_names: list[str]) -> int:
        """
        Delete voice profile samples from GCS.
        
        Args:
            blob_names: List of GCS object paths
            
        Returns:
            Number of files deleted
        """
        deleted_count = 0
        
        for blob_name in blob_names:
            if self.delete_audio(blob_name):
                deleted_count += 1
        
        return deleted_count
    
    def get_signed_url(
        self,
        blob_name: str,
        expiration_minutes: int = 60,
    ) -> str:
        """
        Get signed URL for temporary access to a blob.
        
        Args:
            blob_name: GCS object path
            expiration_minutes: URL expiration time in minutes
            
        Returns:
            Signed URL
            
        Raises:
            RuntimeError: If URL generation fails
        """
        try:
            blob = self.bucket.blob(blob_name)
            url = blob.generate_signed_url(
                expiration=timedelta(minutes=expiration_minutes),
                method="GET",
            )
            return url
        except Exception as e:
            raise RuntimeError(f"Failed to generate signed URL: {e}") from e
    
    def list_user_audio(self, user_id: str, prefix: str = "audio") -> list[str]:
        """
        List all audio files for a user.
        
        Args:
            user_id: User identifier
            prefix: Blob prefix (default: "audio")
            
        Returns:
            List of blob names
        """
        try:
            blob_prefix = f"{prefix}/{user_id}/"
            blobs = self.bucket.list_blobs(prefix=blob_prefix)
            return [blob.name for blob in blobs]
        except Exception as e:
            raise RuntimeError(f"Failed to list user audio: {e}") from e
    
    def is_available(self) -> bool:
        """
        Check if GCS is available and configured.
        
        Returns:
            True if GCS is available and bucket is accessible
        """
        try:
            # Try to get bucket metadata
            self.bucket.reload()
            return True
        except Exception:
            return False


def get_gcs_service(
    bucket_name: Optional[str] = None,
    credentials_path: Optional[str] = None,
    fallback_to_local: bool = True,
) -> Optional[GCSStorageService]:
    """
    Get GCS storage service instance with fallback.
    
    Args:
        bucket_name: GCS bucket name
        credentials_path: Path to GCS credentials
        fallback_to_local: If True, returns None on failure (allows local storage fallback)
        
    Returns:
        GCSStorageService instance or None if not available
    """
    if not GCS_AVAILABLE:
        if fallback_to_local:
            return None
        raise RuntimeError("Google Cloud Storage is not available")
    
    try:
        service = GCSStorageService(
            bucket_name=bucket_name,
            credentials_path=credentials_path,
        )
        
        # Verify bucket is accessible
        if not service.is_available():
            if fallback_to_local:
                return None
            raise RuntimeError("GCS bucket is not accessible")
        
        return service
    except Exception:
        if fallback_to_local:
            return None
        raise
