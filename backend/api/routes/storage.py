"""Storage endpoints for Google Cloud Storage integration."""

import uuid
from typing import Dict, Optional

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field

router = APIRouter()


class SignedUploadRequest(BaseModel):
    """Request model for generating signed upload URL."""

    filename: str = Field(..., description="Original filename")
    content_type: str = Field(..., description="MIME type of the content")
    prefix: Optional[str] = Field(None, description="Optional path prefix in bucket")
    expires_minutes: Optional[int] = Field(15, ge=1, le=60, description="URL expiration in minutes")


class SignedUploadResponse(BaseModel):
    """Response model for signed upload URL."""

    blob_name: str = Field(..., description="Full path of blob in bucket")
    url: str = Field(..., description="Signed URL for PUT upload")
    method: str = Field("PUT", description="HTTP method to use")
    headers: Dict[str, str] = Field(..., description="Required headers for upload")


class SignedDownloadResponse(BaseModel):
    """Response model for signed download URL."""

    blob_name: str = Field(..., description="Full path of blob in bucket")
    url: str = Field(..., description="Signed URL for GET download")
    method: str = Field("GET", description="HTTP method to use")


@router.post("/storage/signed-upload", response_model=SignedUploadResponse)
async def generate_signed_upload_url(
    request: Request,
    upload_request: SignedUploadRequest,
) -> SignedUploadResponse:
    """Generate signed URL for direct-to-GCS upload.
    
    The client should:
    1. Call this endpoint to get a signed URL
    2. Use the URL to PUT the file directly to GCS
    3. Include the returned headers in the PUT request
    
    Args:
        request: FastAPI request (to access app state)
        upload_request: Upload request parameters
        
    Returns:
        Signed upload URL and metadata
        
    Raises:
        HTTPException: If GCS is disabled or not configured
    """
    gcs_storage = getattr(request.app.state, "gcs_storage", None)
    
    if gcs_storage is None:
        raise HTTPException(
            status_code=400,
            detail="GCS storage is not enabled. Set ENABLE_GCS_STORAGE=true and configure GCS_BUCKET_NAME.",
        )
    
    try:
        # Generate unique blob name with optional prefix
        unique_id = str(uuid.uuid4())
        if upload_request.prefix:
            blob_name = f"{upload_request.prefix}/{unique_id}_{upload_request.filename}"
        else:
            blob_name = f"{unique_id}_{upload_request.filename}"
        
        # Generate signed URL
        result = gcs_storage.generate_signed_upload_url(
            blob_name=blob_name,
            content_type=upload_request.content_type,
            expires_minutes=upload_request.expires_minutes or 15,
        )
        
        return SignedUploadResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate signed upload URL: {str(e)}",
        ) from e


@router.get("/storage/signed-download", response_model=SignedDownloadResponse)
async def generate_signed_download_url(
    request: Request,
    blob_name: str = Query(..., description="Full path of blob in bucket"),
    expires_minutes: int = Query(15, ge=1, le=60, description="URL expiration in minutes"),
) -> SignedDownloadResponse:
    """Generate signed URL for downloading from GCS.
    
    Args:
        request: FastAPI request (to access app state)
        blob_name: Full path of blob in bucket
        expires_minutes: URL expiration in minutes
        
    Returns:
        Signed download URL
        
    Raises:
        HTTPException: If GCS is disabled or blob not found
    """
    gcs_storage = getattr(request.app.state, "gcs_storage", None)
    
    if gcs_storage is None:
        raise HTTPException(
            status_code=400,
            detail="GCS storage is not enabled. Set ENABLE_GCS_STORAGE=true and configure GCS_BUCKET_NAME.",
        )
    
    try:
        # Check if blob exists
        if not gcs_storage.blob_exists(blob_name):
            raise HTTPException(
                status_code=404,
                detail=f"Blob '{blob_name}' not found in bucket.",
            )
        
        # Generate signed URL
        result = gcs_storage.generate_signed_download_url(
            blob_name=blob_name,
            expires_minutes=expires_minutes,
        )
        
        return SignedDownloadResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate signed download URL: {str(e)}",
        ) from e
