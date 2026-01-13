"""Google Cloud Platform configuration and utilities."""

import os
from typing import Optional

from google.cloud import firestore
from google.cloud import storage
from google.auth import default as default_credentials
from google.auth.credentials import Credentials


class GCPConfig:
    """GCP configuration manager."""
    
    def __init__(self):
        """Initialize GCP configuration."""
        self.project_id = os.getenv("GCP_PROJECT_ID")
        self.credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        self.database_name = os.getenv("FIRESTORE_DATABASE", "(default)")
        self.bucket_name = os.getenv("GCS_BUCKET_NAME")
        
        self._credentials: Optional[Credentials] = None
        self._firestore_client: Optional[firestore.AsyncClient] = None
        self._storage_client: Optional[storage.Client] = None
    
    @property
    def credentials(self) -> Credentials:
        """Get GCP credentials.
        
        Returns:
            Google Cloud credentials
        """
        if self._credentials is None:
            if self.credentials_path and os.path.exists(self.credentials_path):
                # Use service account credentials
                from google.oauth2 import service_account
                self._credentials = service_account.Credentials.from_service_account_file(
                    self.credentials_path
                )
            else:
                # Use default credentials (for GCE, Cloud Run, etc.)
                self._credentials, _ = default_credentials()
        return self._credentials
    
    def get_firestore_client(self) -> firestore.AsyncClient:
        """Get Firestore async client.
        
        Returns:
            Firestore async client
        """
        if self._firestore_client is None:
            self._firestore_client = firestore.AsyncClient(
                project=self.project_id,
                credentials=self.credentials,
                database=self.database_name
            )
        return self._firestore_client
    
    def get_storage_client(self) -> storage.Client:
        """Get Cloud Storage client.
        
        Returns:
            Cloud Storage client
        """
        if self._storage_client is None:
            self._storage_client = storage.Client(
                project=self.project_id,
                credentials=self.credentials
            )
        return self._storage_client
    
    def get_bucket(self) -> Optional[storage.Bucket]:
        """Get the configured GCS bucket.
        
        Returns:
            GCS bucket or None if not configured
        """
        if not self.bucket_name:
            return None
        client = self.get_storage_client()
        return client.bucket(self.bucket_name)


# Global GCP config instance
gcp_config = GCPConfig()
