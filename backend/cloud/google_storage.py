"""Google Cloud Storage service for file storage and management."""

import os
from datetime import timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from google.cloud import storage
from google.oauth2 import service_account


class GoogleStorageService:
    """Handle Google Cloud Storage operations for Poker Therapist.
    
    Features:
    - Upload/download files (voice recordings, session data, etc.)
    - Generate signed URLs for secure file access
    - Manage bucket lifecycle
    - Support for different file types and access patterns
    """

    def __init__(self) -> None:
        """Initialize Google Cloud Storage service."""
        self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT_ID", "")
        self.bucket_name = os.getenv("GOOGLE_STORAGE_BUCKET_NAME", "")
        self.region = os.getenv("GOOGLE_STORAGE_REGION", "us-central1")
        
        # Authentication
        credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
        credentials_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "")
        
        if not self.project_id:
            raise ValueError("GOOGLE_CLOUD_PROJECT_ID must be set in environment")
        if not self.bucket_name:
            raise ValueError("GOOGLE_STORAGE_BUCKET_NAME must be set in environment")
        
        # Initialize credentials
        if credentials_path and os.path.exists(credentials_path):
            self.credentials = service_account.Credentials.from_service_account_file(
                credentials_path
            )
        elif credentials_json:
            import json
            credentials_dict = json.loads(credentials_json)
            self.credentials = service_account.Credentials.from_service_account_info(
                credentials_dict
            )
        else:
            # Use default credentials (e.g., from environment in GCP)
            self.credentials = None
        
        # Initialize storage client
        if self.credentials:
            self.client = storage.Client(
                project=self.project_id,
                credentials=self.credentials
            )
        else:
            self.client = storage.Client(project=self.project_id)
        
        self.bucket = self.client.bucket(self.bucket_name)

    def upload_file(
        self, 
        file_path: str, 
        destination_blob_name: str,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
        make_public: bool = False,
    ) -> str:
        """Upload a file to Google Cloud Storage.
        
        Args:
            file_path: Local path to file
            destination_blob_name: Destination path in bucket (e.g., 'users/123/recording.wav')
            content_type: MIME type of file (auto-detected if None)
            metadata: Optional metadata dictionary
            make_public: Whether to make file publicly accessible
            
        Returns:
            Public URL or gs:// URL of uploaded file
            
        Raises:
            FileNotFoundError: If local file doesn't exist
            google.cloud.exceptions.GoogleCloudError: If upload fails
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        blob = self.bucket.blob(destination_blob_name)
        
        # Set content type if provided
        if content_type:
            blob.content_type = content_type
        
        # Set metadata if provided
        if metadata:
            blob.metadata = metadata
        
        # Upload file
        blob.upload_from_filename(file_path)
        
        # Make public if requested
        if make_public:
            blob.make_public()
            return blob.public_url
        
        return f"gs://{self.bucket_name}/{destination_blob_name}"

    def upload_bytes(
        self,
        data: bytes,
        destination_blob_name: str,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
        make_public: bool = False,
    ) -> str:
        """Upload bytes data to Google Cloud Storage.
        
        Args:
            data: Bytes data to upload
            destination_blob_name: Destination path in bucket
            content_type: MIME type of data
            metadata: Optional metadata dictionary
            make_public: Whether to make file publicly accessible
            
        Returns:
            Public URL or gs:// URL of uploaded data
        """
        blob = self.bucket.blob(destination_blob_name)
        
        if content_type:
            blob.content_type = content_type
        
        if metadata:
            blob.metadata = metadata
        
        blob.upload_from_string(data, content_type=content_type)
        
        if make_public:
            blob.make_public()
            return blob.public_url
        
        return f"gs://{self.bucket_name}/{destination_blob_name}"

    def download_file(self, blob_name: str, destination_path: str) -> None:
        """Download a file from Google Cloud Storage.
        
        Args:
            blob_name: Name of blob in bucket
            destination_path: Local path to save file
            
        Raises:
            google.cloud.exceptions.NotFound: If blob doesn't exist
        """
        blob = self.bucket.blob(blob_name)
        
        # Create parent directory if it doesn't exist
        Path(destination_path).parent.mkdir(parents=True, exist_ok=True)
        
        blob.download_to_filename(destination_path)

    def download_bytes(self, blob_name: str) -> bytes:
        """Download blob as bytes.
        
        Args:
            blob_name: Name of blob in bucket
            
        Returns:
            Blob content as bytes
            
        Raises:
            google.cloud.exceptions.NotFound: If blob doesn't exist
        """
        blob = self.bucket.blob(blob_name)
        return blob.download_as_bytes()

    def generate_signed_url(
        self, 
        blob_name: str, 
        expiration_minutes: int = 60,
        method: str = "GET",
    ) -> str:
        """Generate a signed URL for temporary file access.
        
        Args:
            blob_name: Name of blob in bucket
            expiration_minutes: URL validity in minutes
            method: HTTP method (GET, PUT, POST)
            
        Returns:
            Signed URL
            
        Raises:
            google.cloud.exceptions.NotFound: If blob doesn't exist
        """
        blob = self.bucket.blob(blob_name)
        
        url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(minutes=expiration_minutes),
            method=method,
        )
        
        return url

    def delete_file(self, blob_name: str) -> bool:
        """Delete a file from Google Cloud Storage.
        
        Args:
            blob_name: Name of blob to delete
            
        Returns:
            True if deletion successful
        """
        try:
            blob = self.bucket.blob(blob_name)
            blob.delete()
            return True
        except Exception:
            return False

    def list_files(
        self, 
        prefix: Optional[str] = None, 
        max_results: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """List files in bucket.
        
        Args:
            prefix: Filter to blobs starting with this prefix
            max_results: Maximum number of results to return
            
        Returns:
            List of file information dictionaries
        """
        blobs = self.client.list_blobs(
            self.bucket_name, 
            prefix=prefix,
            max_results=max_results
        )
        
        files = []
        for blob in blobs:
            files.append({
                "name": blob.name,
                "size": blob.size,
                "content_type": blob.content_type,
                "created": blob.time_created,
                "updated": blob.updated,
                "metadata": blob.metadata,
            })
        
        return files

    def file_exists(self, blob_name: str) -> bool:
        """Check if a file exists in bucket.
        
        Args:
            blob_name: Name of blob to check
            
        Returns:
            True if file exists
        """
        blob = self.bucket.blob(blob_name)
        return blob.exists()

    def get_file_metadata(self, blob_name: str) -> Dict[str, Any]:
        """Get metadata for a file.
        
        Args:
            blob_name: Name of blob
            
        Returns:
            File metadata dictionary
            
        Raises:
            google.cloud.exceptions.NotFound: If blob doesn't exist
        """
        blob = self.bucket.blob(blob_name)
        blob.reload()
        
        return {
            "name": blob.name,
            "size": blob.size,
            "content_type": blob.content_type,
            "created": blob.time_created,
            "updated": blob.updated,
            "metadata": blob.metadata,
            "md5_hash": blob.md5_hash,
            "public_url": blob.public_url if blob.public_url else None,
        }

    def create_bucket_if_not_exists(self) -> None:
        """Create bucket if it doesn't exist.
        
        Raises:
            google.cloud.exceptions.GoogleCloudError: If bucket creation fails
        """
        if not self.bucket.exists():
            self.bucket = self.client.create_bucket(
                self.bucket_name,
                location=self.region,
            )
            print(f"Bucket {self.bucket_name} created in {self.region}")
        else:
            print(f"Bucket {self.bucket_name} already exists")
