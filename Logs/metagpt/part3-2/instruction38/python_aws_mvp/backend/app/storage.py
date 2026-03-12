import boto3
from botocore.exceptions import ClientError
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Dict
import uuid

from .models import FileUpload, User
from .config import get_settings
from .auth import get_current_user

settings = get_settings()

# AWS S3 client initialization
s3_client = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION,
)

class PresignedUrlRequest(BaseModel):
    filename: str
    content_type: str

class PresignedUrlResponse(BaseModel):
    presigned_url: str
    file_id: str

class FileMetadata(BaseModel):
    file_id: str
    filename: str
    content_type: str
    size: int

# In-memory file upload store for MVP (replace with DB in production)
fake_file_uploads_db: Dict[str, FileUpload] = {}

class StorageManager:
    @staticmethod
    def generate_presigned_url(user_id: str, filename: str, content_type: str) -> Dict[str, str]:
        file_id = str(uuid.uuid4())
        key = f"{user_id}/{file_id}/{filename}"
        try:
            presigned_url = s3_client.generate_presigned_url(
                "put_object",
                Params={
                    "Bucket": settings.AWS_S3_BUCKET,
                    "Key": key,
                    "ContentType": content_type,
                    "ACL": "private"
                },
                ExpiresIn=3600,
            )
        except ClientError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Could not generate presigned URL: {str(e)}"
            )
        # Store file upload metadata
        fake_file_uploads_db[file_id] = FileUpload(
            file_id=file_id,
            user_id=user_id,
            filename=filename,
            status="pending"
        )
        return {"presigned_url": presigned_url, "file_id": file_id}

    @staticmethod
    def validate_upload(user_id: str, file_metadata: dict) -> bool:
        file_id = file_metadata.get("file_id")
        file_upload = fake_file_uploads_db.get(file_id)
        if not file_upload or file_upload.user_id != user_id:
            return False
        # Optionally, check file exists in S3
        key = f"{user_id}/{file_id}/{file_upload.filename}"
        try:
            s3_client.head_object(Bucket=settings.AWS_S3_BUCKET, Key=key)
            file_upload.status = "uploaded"
            fake_file_uploads_db[file_id] = file_upload
            return True
        except ClientError:
            return False

# FastAPI router for storage
storage_router = APIRouter()

@storage_router.post("/presigned-url", response_model=PresignedUrlResponse, summary="Get S3 presigned upload URL")
async def get_presigned_url(
    request: PresignedUrlRequest,
    current_user: User = Depends(get_current_user)
):
    result = StorageManager.generate_presigned_url(
        user_id=current_user.user_id,
        filename=request.filename,
        content_type=request.content_type
    )
    return PresignedUrlResponse(**result)

@storage_router.post("/validate-upload", summary="Validate S3 upload and update status")
async def validate_upload(
    metadata: FileMetadata,
    current_user: User = Depends(get_current_user)
):
    success = StorageManager.validate_upload(
        user_id=current_user.user_id,
        file_metadata=metadata.dict()
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Upload validation failed"
        )
    return {"status": "uploaded", "file_id": metadata.file_id}

def get_storage_router():
    return storage_router