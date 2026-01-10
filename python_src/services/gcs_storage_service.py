"""Google Cloud Storage service for file uploads and downloads."""

import json
import os
import tempfile
from datetime import timedelta
from typing import Dict, Optional

from google.cloud import storage
from google.oauth2 import service_account


class GCSStorageService:
    """Service for Google Cloud Storage operations."""

    def __init__(
        self,
        bucket_name: Optional[str] = None,
        credentials_path: Optional[str] = None,
        credentials_json: Optional[str] = None,
    ) -> None:
        """Initialize GCS storage service.
        
        Args:
            bucket_name: GCS bucket name (or use GCS_BUCKET_NAME env var)
            credentials_path: Path to service account JSON (or use GOOGLE_APPLICATION_CREDENTIALS env var)
            credentials_json: Inline service account JSON string (or use GCS_SERVICE_ACCOUNT_JSON env var)
            
        Raises:
            RuntimeError: If bucket name or credentials are not provided
        """
        self.bucket_name = bucket_name or os.getenv("GCS_BUCKET_NAME")
        if not self.bucket_name:
            raise RuntimeError("GCS_BUCKET_NAME must be set")

        # Handle credentials - prefer inline JSON, then path, then default
        credentials = None
        if credentials_json or os.getenv("GCS_SERVICE_ACCOUNT_JSON"):
            creds_json = credentials_json or os.getenv("GCS_SERVICE_ACCOUNT_JSON")
            if creds_json:
                creds_dict = json.loads(creds_json)
                credentials = service_account.Credentials.from_service_account_info(creds_dict)
        elif credentials_path or os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
            creds_path = credentials_path or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            if creds_path and os.path.exists(creds_path):
                credentials = service_account.Credentials.from_service_account_file(creds_path)

        # Initialize client (will use default credentials if none provided)
        if credentials:
            self.client = storage.Client(credentials=credentials)
        else:
            self.client = storage.Client()

        self.bucket = self.client.bucket(self.bucket_name)

    def generate_signed_upload_url(
        self,
        blob_name: str,
        content_type: str,
        expires_minutes: int = 15,
    ) -> Dict[str, str]:
        """Generate a signed URL for uploading a file to GCS.
        
        Args:
            blob_name: Name/path of the blob in the bucket
            content_type: MIME type of the content
            expires_minutes: URL expiration time in minutes
            
        Returns:
            Dictionary with blob_name, url, method, and headers
        """
        blob = self.bucket.blob(blob_name)
        
        url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(minutes=expires_minutes),
            method="PUT",
            content_type=content_type,
        )

        return {
            "blob_name": blob_name,
            "url": url,
            "method": "PUT",
            "headers": {"Content-Type": content_type},
        }

    def generate_signed_download_url(
        self,
        blob_name: str,
        expires_minutes: int = 15,
    ) -> Dict[str, str]:
        """Generate a signed URL for downloading a file from GCS.
        
        Args:
            blob_name: Name/path of the blob in the bucket
            expires_minutes: URL expiration time in minutes
            
        Returns:
            Dictionary with blob_name, url, and method
        """
        blob = self.bucket.blob(blob_name)

        url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(minutes=expires_minutes),
            method="GET",
        )

        return {
            "blob_name": blob_name,
            "url": url,
            "method": "GET",
        }

    async def download_blob(self, blob_name: str) -> bytes:
        """Download blob content as bytes.
        
        Args:
            blob_name: Name/path of the blob in the bucket
            
        Returns:
            Blob content as bytes
        """
        blob = self.bucket.blob(blob_name)
        return blob.download_as_bytes()

    def upload_blob(
        self,
        blob_name: str,
        data: bytes,
        content_type: Optional[str] = None,
    ) -> str:
        """Upload data to GCS blob (server-side upload).
        
        Args:
            blob_name: Name/path of the blob in the bucket
            data: Data to upload
            content_type: Optional MIME type
            
        Returns:
            Public URL of the blob
        """
        blob = self.bucket.blob(blob_name)
        if content_type:
            blob.upload_from_string(data, content_type=content_type)
        else:
            blob.upload_from_string(data)
        
        return f"gs://{self.bucket_name}/{blob_name}"

    def blob_exists(self, blob_name: str) -> bool:
        """Check if a blob exists.
        
        Args:
            blob_name: Name/path of the blob in the bucket
            
        Returns:
            True if blob exists
        """
        blob = self.bucket.blob(blob_name)
        return blob.exists()

    def delete_blob(self, blob_name: str) -> None:
        """Delete a blob.
        
        Args:
            blob_name: Name/path of the blob in the bucket
        """
        blob = self.bucket.blob(blob_name)
        blob.delete()
