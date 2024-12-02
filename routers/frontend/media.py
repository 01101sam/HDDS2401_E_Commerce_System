import os
from hashlib import md5
from uuid import UUID

# noinspection PyPackageRequirements
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
# noinspection PyPackageRequirements
from azure.storage.blob import BlobServiceClient
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from dependencies.oauth import oauth_check_dep
from dependencies.roles import role_admin
from globals import BLOB_CONTAINER_NAME, BLOB_CONNECTION_STRING

router = APIRouter(prefix="/media", tags=["media"])

# Initialize the BlobServiceClient
blob_service_client = BlobServiceClient.from_connection_string(BLOB_CONNECTION_STRING)


def get_file_extension(filename: str) -> str:
    _, extension = os.path.splitext(filename)
    return extension


class UploadResponse(BaseModel):
    filename: str
    url: str


@router.post("/upload", response_model=UploadResponse, dependencies=[Depends(oauth_check_dep), Depends(role_admin)])
async def upload_image(file: UploadFile = File(...)):
    file_ext = get_file_extension(file.filename)

    # Get file md5
    file.file.seek(0)
    file_md5 = md5(file.file.read()).hexdigest()
    file.file.seek(0)

    file_name = f"{UUID(file_md5)}{file_ext}"
    try:
        blob_client = blob_service_client.get_blob_client(container=BLOB_CONTAINER_NAME, blob=file_name)
        blob_client.upload_blob(file.file)
        return UploadResponse(filename=file_name, url=f"/api/media/{file_name}")
    except ResourceExistsError:
        return UploadResponse(filename=file_name, url=f"/api/media/{file_name}")
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to upload image")


@router.get("/{filename}", response_class=StreamingResponse)
async def download_image(filename: str):
    try:
        file_name, _ = filename.rsplit(".", 1)
        if not UUID(file_name, version=4):
            raise HTTPException(status_code=400, detail="Invalid filename")

        blob_client = blob_service_client.get_blob_client(container=BLOB_CONTAINER_NAME, blob=filename)
        stream = blob_client.download_blob().readall()
        return StreamingResponse(iter([stream]), media_type="image/jpeg", headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Cache-Control": "public, max-age=3600",
            "Pragma": "public",
            "Expires": "3600"
        })
    except ResourceNotFoundError:
        raise HTTPException(status_code=404)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to download image")
